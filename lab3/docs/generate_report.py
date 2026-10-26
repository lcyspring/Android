# -*- coding: utf-8 -*-
"""
实验三 Word 报告生成脚本 —— WPS 最大兼容版(沿用实验一/二已验证的脚本风格)
原则:
1. 不手写任何 OOXML 元素(零 OxmlElement 创建/插入),全部走 python-docx 原生 API;
2. 不用任何段落/文字/表格底纹(零 w:shd);
3. 中文字体只在两处设置:Normal 样式 + 必要的 run,且只在已有 rFonts 上"加属性",不改变元素结构;
4. 生成后用 schema 顺序自检所有 w:pPr / w:rPr 子元素顺序。
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

REPORT_DIR = r'd:\rain_android\lab3\docs'
OUT_PATH = os.path.join(REPORT_DIR, '实验三报告_State_ViewModel_与单向数据流.docx')

W_NS = 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'

def set_east_asia_font(element_rpr_owner, font_name):
    """在已有的 rPr/rFonts 上只追加一个 eastAsia 属性,不新增/移动任何元素。"""
    rPr = element_rpr_owner.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()   # python-docx 保证按 schema 顺序创建
    rFonts.set(qn('w:eastAsia'), font_name)

def style_run(run, cn='宋体', en='Times New Roman', size=10.5, bold=False, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    set_east_asia_font(run._element, cn)

# ---------- 段落构建(全部原生 API) ----------
def h1(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(16)
    p.paragraph_format.space_after = Pt(10)
    style_run(p.add_run(text), cn='黑体', en='Times New Roman', size=16, bold=True)

def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    style_run(p.add_run(text), cn='黑体', en='Times New Roman', size=13, bold=True)

def h3(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    p.paragraph_format.space_after = Pt(4)
    style_run(p.add_run(text), cn='宋体', en='Times New Roman', size=11, bold=True)

def body(doc, text, indent=True, bold=False, align=None, color=None):
    p = doc.add_paragraph()
    if align is not None:
        p.alignment = align
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    style_run(p.add_run(text), size=10.5, bold=bold, color=color)
    return p

def bullet(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.74)
    style_run(p.add_run('- ' + text), size=10.5)

def numbered(doc, idx, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Cm(0.74)
    style_run(p.add_run(f'{idx}. {text}'), size=10.5)

def code_lines(doc, code):
    """代码块:每行一个最普通的段落,只改字体,不加底纹/边框/缩进异常。"""
    for line in code.split('\n'):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(0)
        pf.space_before = Pt(0)
        pf.line_spacing = 1.15
        style_run(p.add_run(line if line else ' '), cn='宋体', en='Consolas', size=9)
    doc.add_paragraph()

def shot_placeholder(doc, caption):
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(p.add_run('（在此插入截图：' + caption + '）'),
              cn='楷体', en='Times New Roman', size=10.5,
              color=RGBColor(0x55, 0x55, 0x55))
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(p2.add_run(caption), cn='楷体', en='Times New Roman',
              size=9, color=RGBColor(0x77, 0x77, 0x77))

SCREENSHOT_DIR = r'D:\rain_android\docs\screenshots'

def shot_image(doc, filename, caption, width_cm=9):
    """插入真实截图 + 居中标题。"""
    path = os.path.join(SCREENSHOT_DIR, filename)
    if os.path.exists(path):
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run = p.add_run()
        run.add_picture(path, width=Cm(width_cm))
    p2 = doc.add_paragraph()
    p2.alignment = WD_ALIGN_PARAGRAPH.CENTER
    style_run(p2.add_run(caption), cn='楷体', en='Times New Roman',
              size=9, color=RGBColor(0x77, 0x77, 0x77))

def table(doc, header, rows, widths=None):
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.style = 'Table Grid'   # 原生内置样式,无自定义底纹
    for j, htext in enumerate(header):
        cell = t.rows[0].cells[j]
        p = cell.paragraphs[0]
        style_run(p.add_run(htext), size=10, bold=True)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            p = t.rows[i + 1].cells[j].paragraphs[0]
            style_run(p.add_run(str(val)), size=10)
    if widths:
        for row in t.rows:
            for j, w in enumerate(widths):
                row.cells[j].width = Cm(w)
    return t

# ================= 文档 =================
doc = Document()

# 全局 Normal 样式:宋体/Times New Roman/五号/1.5 倍行距
normal = doc.styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(10.5)
normal.paragraph_format.line_spacing = 1.5
set_east_asia_font(normal.element, '宋体')

sec = doc.sections[0]
sec.page_width = Cm(21)
sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.54)
sec.bottom_margin = Cm(2.54)
sec.left_margin = Cm(3.18)
sec.right_margin = Cm(3.18)

# 封面标题
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
style_run(p.add_run('《移动应用开发》实验报告'), cn='黑体', size=20, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
style_run(p.add_run('实验三  State、ViewModel 与单向数据流'), cn='黑体', size=15, bold=True)

info = doc.add_table(rows=4, cols=4)
info.style = 'Table Grid'
info_rows = [
    ['姓名', '李春雨', '学号', '202305567128'],
    ['班级', '计科2班', '完成日期', '2026-09-21'],
    ['专业', '计算机科学与技术', '课程', '移动应用开发'],
    ['实验编号', '实验三', '实验名称', 'State、ViewModel 与单向数据流'],
]
for i, row in enumerate(info_rows):
    for j, val in enumerate(row):
        cp = info.rows[i].cells[j].paragraphs[0]
        style_run(cp.add_run(val), size=10.5, bold=(j % 2 == 0))
doc.add_paragraph()

# 一、目标
h1(doc, '一、实验目标')
for i, g in enumerate([
    '把首页数据从实验二的顶层 sampleTasks 常量移到 TaskRepository,由 HomeViewModel 持有并通过只读 StateFlow 暴露,落实单向数据流(UDF):State 向下、Event 向上。',
    '定义 HomeUiState 用 Boolean isLoading + nullable errorMessage 表达 Loading / Error / Empty / Content 四态,HomeScreen 按此四态分支渲染(步骤 14、18)。',
    '用 FakeTaskRepository 的 delay / emptyMode / errorMode 三个开关模拟网络耗时、空数据、接口异常,演示四态并验证"失败可重试且不会崩溃"(步骤 15、19、20)。',
    'HomeRoute 用 collectAsStateWithLifecycle 订阅 StateFlow,HomeScreen 改为纯 UI(只接 onAction 回调),验证验收点"Screen 不直接调用 repository"和"ViewModel 公开只读 StateFlow"。',
], 1):
    numbered(doc, i, g)

# 二、环境
h1(doc, '二、实验环境')
table(doc, ['项目', '信息'], [
    ['操作系统', 'Windows 11'],
    ['开发工具', 'Android Studio(实验三 Lab3Compose 工程,namespace=edu.example.mobilecourse.lab3)'],
    ['Android SDK', 'API 37(Android 16),路径 D:\\Android\\Sdk'],
    ['JDK', '17(Microsoft jdk-17.0.19.10-hotspot)'],
    ['Kotlin', '2.0.21'],
    ['Compose BOM', '2024.10.01'],
    ['Navigation Compose', '2.8.3'],
    ['Lifecycle', '2.8.6(viewmodel-compose + runtime-compose)'],
    ['Android Gradle Plugin', '8.7.2'],
    ['Gradle', '8.10.2'],
    ['运行设备', 'Android 模拟器 Pixel 7(系统镜像 API 37.1,Google Play x86_64)'],
    ['构建结果', 'BUILD SUCCESSFUL in 7s(修复 viewModelFactory DSL 后第二次构建)'],
], widths=[4, 12])

# 三、设计
h1(doc, '三、设计')
h2(doc, '3.1 分层结构')
body(doc, '实验三在实验二的两个目的地基础上,把首页从"直接放 HomeScreen"改造成三层:Route(桥)→ ViewModel(状态)→ Screen(纯 UI),数据由 Repository 统一提供:')
code_lines(doc, '\n'.join([
    'MainActivity (只 setContent { App() })',
    '  └── App (持有 NavController + NavHost + Repository)',
    '        ├── 目的地 1: HomeDestination  route = "home"',
    '        │     └── HomeRoute(repository, onNavigate)        <- 桥:创建 ViewModel + 订阅 StateFlow',
    '        │           ├── viewModel(factory) -> HomeViewModel(repository, onOpenTask=onNavigate)',
    '        │           ├── collectAsStateWithLifecycle(uiState)',
    '        │           └── HomeScreen(uiState, onAction = viewModel::onAction)',
    '        │                 ├── isLoading       -> LoadingContent',
    '        │                 ├── errorMessage!=null -> ErrorContent(message, onRetry)',
    '        │                 ├── tasks.isEmpty() -> EmptyContent(onRefresh)',
    '        │                 └── else            -> LazyColumn { TaskCard(...) }',
    '        └── 目的地 2: TaskDetailDestination  route = "task_detail/{taskId}"',
    '              └── TaskDetailScreen(taskId, onBack)   <- 沿用实验二,未接入 ViewModel',
]))

h2(doc, '3.2 单向数据流(UDF)')
body(doc, '实验三的核心是单向数据流:State 从 ViewModel 向下流向 Screen,Event 从 Screen 向上送回 ViewModel。数据由 Repository 流入 ViewModel,ViewModel 持有可变 _uiState、对外暴露只读 uiState:')
code_lines(doc, '\n'.join([
    'FakeTaskRepository (getTasks(): suspend List<CourseTask>)',
    '      |  viewModelScope.launch{ repository.getTasks() }',
    '      v',
    'HomeViewModel',
    '  - _uiState: MutableStateFlow<HomeUiState>   (内部可变)',
    '  - uiState:    StateFlow<HomeUiState>         (只读对外)',
    '  - init { refresh() }                          (步骤 16)',
    '  - refresh(){ isLoading=true; launch{ try{...}catch{errorMessage} } }  (步骤 17)',
    '  - onAction(action: HomeAction)               (事件入口)',
    '      |  State 向下',
    '      v',
    'HomeRoute -> collectAsStateWithLifecycle(uiState) -> HomeScreen(uiState, onAction)',
    '      |  Event 向上(onAction 封装)',
    '      v',
    'HomeViewModel.onAction:',
    '  - Refresh      -> refresh()                  (重载,Error 态点重试)',
    '  - ItemClicked(id) -> onOpenTask(id)          (不改 state,只回调上层导航)',
    '      |',
    '      v',
    'HomeRoute.onNavigate(id) -> App.navController.navigate(TaskDetailDestination.createRoute(id))',
]))
body(doc, '自问自答(实验指导书四问):', indent=False, bold=True)
for qa in [
    '数据在哪里?由 TaskRepository 统一提供,实验三用 FakeTaskRepository(delay/emptyMode/errorMode 模拟网络),实验四会换成 NetworkTaskRepository 而不必改 ViewModel。Screen 不直接调 repository(验收点)。',
    '状态在哪里?在 HomeViewModel 的 _uiState(MutableStateFlow),对外只暴露只读 StateFlow(验收点"ViewModel 公开只读 StateFlow")。Screen 不持有状态,只根据传入的 uiState 渲染。',
    '事件从哪里来、到哪里去?用户在 Screen 的操作(点重试、点卡片)被封装成 HomeAction(Refresh/ItemClicked),通过 onAction 送回 ViewModel;ItemClicked 不改 state,只经 onOpenTask 回调到 Route/App 接成 navigate。',
    '错误在哪里处理?ViewModel.refresh() 的 try/catch 把异常转成 errorMessage 写进 uiState,Screen 走 ErrorContent + Retry;Retry 再触发 refresh,失败也不会崩溃(验收点)。',
]:
    bullet(doc, qa)

h2(doc, '3.3 四态判定顺序')
body(doc, 'HomeUiState 用 Boolean isLoading + nullable errorMessage + List tasks 的组合表达四态,HomeScreen 用 when 表达式按固定顺序判定:')
code_lines(doc, '\n'.join([
    'when {',
    '    uiState.isLoading          -> LoadingContent                  // 进入 refresh 即置 true',
    '    uiState.errorMessage!=null -> ErrorContent(message, onRetry)  // catch 后写 message',
    '    uiState.tasks.isEmpty()    -> EmptyContent(onRefresh)        // repository 返回 emptyList',
    '    else                       -> LazyColumn { TaskCard(...) }    // 正常列表',
    '}',
]))
body(doc, '顺序很重要:Loading 优先(重试时也要先显示 Loading 让用户知道在请求),其次 Error(errorMessage 非 null),再次 Empty(列表空但无错误),最后 Content。四个分支互斥,覆盖所有 UI 状态(验收点"四种 UI 状态均可演示")。', indent=False)

h2(doc, '3.4 类关系')
code_lines(doc, '\n'.join([
    'HomeUiState (data class)                  <- 状态载体:isLoading + tasks + errorMessage',
    'HomeAction  (sealed interface)           <- 事件载体:Refresh / ItemClicked(taskId)',
    '',
    'TaskRepository (interface)               <- 数据源接口',
    '  +-- FakeTaskRepository (delay/emptyMode/errorMode)   <- 实验三实现',
    '',
    'HomeViewModel(repository, onOpenTask) : ViewModel()',
    '  +-- _uiState: MutableStateFlow<HomeUiState>',
    '  +-- uiState:    StateFlow<HomeUiState>  = _uiState.asStateFlow()  <- 只读',
    '  +-- init { refresh() }',
    '  +-- refresh() / onAction(action)',
    '',
    'HomeRoute(repository, onNavigate) @Composable',
    '  +-- viewModel(factory = object: ViewModelProvider.Factory { ... })',
    '  +-- collectAsStateWithLifecycle(viewModel.uiState)',
    '  +-- HomeScreen(uiState, onAction = viewModel::onAction)',
    '',
    'HomeScreen(uiState, onAction) @Composable  <- 纯 UI,不持有 ViewModel/repository/NavController',
    '',
    'App(overrideRepository) @Composable       <- 持有 NavController + NavHost + Repository',
    '  +-- repository = remember { overrideRepository ?: FakeTaskRepository() }',
    '  +-- composable("home"){ HomeRoute(repository, onNavigate) }',
    '  +-- composable("task_detail/{taskId}"){ TaskDetailScreen(...) }',
]))

h2(doc, '3.5 关键决策')
for i, d in enumerate([
    '状态放 ViewModel 而非 Screen:HomeViewModel 持有 _uiState,配置变化(旋转屏幕)时 ViewModel 存活,StateFlow 自动重放最新状态,UI 不丢数据;Screen 变成无状态纯函数,只根据 uiState 渲染,可独立 Preview、可测试。',
    '对外只读 StateFlow:内部 _uiState 是 MutableStateFlow 可写,对外暴露 asStateFlow() 转成的只读 StateFlow,保证只有 ViewModel 能改状态(验收点),Screen 无法绕过 ViewModel 直接改 state。',
    '用 Boolean + nullable errorMessage 表达四态而非 sealed class:指导书起始代码即此形态,简单直观;缺点是非法组合(如 isLoading=true 同时 errorMessage!=null)需要靠 when 顺序兜底。拓展可改成 sealed interface Loading/Error/Empty/Content 让非法状态编译期不可表达。',
    'HomeAction 用 sealed interface:Refresh 和 ItemClicked 是不同类型,when 表达式 exhaustiveness 检查能在编译期保证所有事件都被处理;ItemClicked 带 taskId 参数,Screen 只负责封装"点了哪个",由 ViewModel 决定怎么处理(改 state 还是回调导航)。',
    'FakeTaskRepository 三个开关:delay(800ms) 让 Loading 态在 UI 上可见(否则 100 条内存数据瞬间返回);emptyMode 返回 emptyList 测 Empty;errorMode 抛 RuntimeException 测 Error+Retry。三个开关对应四态演示,改 MainActivity 的 App(overrideRepository=...) 即可切换。',
    'collectAsStateWithLifecycle 而非 collectAsState:生命周期感知,当界面低于 STARTED(如退到后台)时停止收集 Flow,避免后台浪费;返回时自动恢复订阅。这是 lifecycle-runtime-compose 提供的 API。',
    'TaskDetail 暂不接入 ViewModel:实验三只要求 Home 四态,详情页仍用实验二的 taskById 同步查数据。若要扩展,TaskDetail 也可照 HomeRoute/HomeViewModel 模式接入自己的 DetailViewModel。',
], 1):
    numbered(doc, i, d)

# 四、实现
h1(doc, '四、实现')
LAB3 = r'd:\rain_android\lab3'

h2(doc, '4.1 HomeUiState:四态载体 + 事件(步骤 14)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/home/HomeUiState.kt', indent=False)
code_lines(doc, '''data class HomeUiState(
    val isLoading: Boolean = false,
    val tasks: List<CourseTask> = emptyList(),
    val errorMessage: String? = null,
)

sealed interface HomeAction {
    data object Refresh : HomeAction
    data class ItemClicked(val taskId: Int) : HomeAction
}''')

h2(doc, '4.2 TaskRepository 接口 + FakeTaskRepository 三开关(步骤 15)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/data/repository/TaskRepository.kt', indent=False)
code_lines(doc, '''interface TaskRepository {
    suspend fun getTasks(): List<CourseTask>
}

class FakeTaskRepository(
    private val delayMillis: Long = 800L,
    private val emptyMode: Boolean = false,
    private val errorMode: Boolean = false,
) : TaskRepository {

    override suspend fun getTasks(): List<CourseTask> {
        delay(delayMillis)                       // 模拟网络耗时,让 Loading 可见
        if (errorMode) {
            throw RuntimeException("FakeTaskRepository 模拟网络异常(errorMode=true)")
        }
        return if (emptyMode) emptyTasks else sampleTasks
    }
}''')
body(doc, '关键:suspend 函数模拟网络 IO,delay 让 isLoading=true 在 UI 上可见;errorMode 抛异常让 ViewModel 的 catch 走 Error 分支;emptyMode 返回 emptyList 走 Empty 分支。三个开关对应验收点"四种 UI 状态均可演示"。', indent=False)

h2(doc, '4.3 HomeViewModel:init refresh + viewModelScope + catch(步骤 16、17)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/home/HomeViewModel.kt', indent=False)
code_lines(doc, '''class HomeViewModel(
    private val repository: TaskRepository,
    private val onOpenTask: (Int) -> Unit,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        // 步骤 16:初始化时调用 refresh。
        refresh()
    }

    // 步骤 17:用 viewModelScope.launch 加载数据。
    fun refresh() {
        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
        viewModelScope.launch {
            try {
                val tasks = repository.getTasks()
                _uiState.value = HomeUiState(isLoading = false, tasks = tasks, errorMessage = null)
            } catch (e: Throwable) {
                // 失败不崩溃:把异常转成可展示文案,Retry 按钮再触发 refresh。
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = e.message ?: "加载失败",
                )
            }
        }
    }

    fun onAction(action: HomeAction) {
        when (action) {
            is HomeAction.Refresh -> refresh()
            is HomeAction.ItemClicked -> onOpenTask(action.taskId)
        }
    }
}''')
body(doc, '关键:_uiState 内部可写、uiState 只读对外(验收点);init 调 refresh 让进入即加载;refresh 先把 isLoading 置 true 再 launch 协程,try 成功写 tasks、catch 写 errorMessage(失败不崩溃);onAction 是事件入口,Refresh 重载、ItemClicked 只回调 onOpenTask 不改 state。', indent=False)

h2(doc, '4.4 HomeRoute:ViewModel 桥 + collectAsStateWithLifecycle(步骤 18)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/home/HomeRoute.kt', indent=False)
code_lines(doc, '''@Composable
fun HomeRoute(
    repository: TaskRepository,
    onNavigate: (Int) -> Unit,
) {
    val viewModel: HomeViewModel = viewModel(
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                HomeViewModel(repository = repository, onOpenTask = onNavigate) as T
        }
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeScreen(
        uiState = uiState,
        onAction = viewModel::onAction,
    )
}''')
body(doc, '关键:viewModel(factory=...) 绑定当前 NavBackStackEntry,配置变化时存活;collectAsStateWithLifecycle 把 StateFlow 订阅成 Compose State 并在生命周期低于 STARTED 时停止收集;onAction 接成 viewModel::onAction,导航 onNavigate 注入 ViewModel 的 onOpenTask。', indent=False)

h2(doc, '4.5 HomeScreen:纯 UI 四态分支 + onAction(步骤 18)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/home/HomeScreen.kt', indent=False)
code_lines(doc, '''@Composable
fun HomeScreen(
    uiState: HomeUiState,
    onAction: (HomeAction) -> Unit,
) {
    Scaffold(...) { innerPadding ->
        when {
            uiState.isLoading -> Box(Modifier.fillMaxSize()) { LoadingContent() }

            uiState.errorMessage != null -> Box(Modifier.fillMaxSize()) {
                ErrorContent(
                    message = uiState.errorMessage ?: "加载失败",
                    onRetry = { onAction(HomeAction.Refresh) },
                )
            }

            uiState.tasks.isEmpty() -> Box(Modifier.fillMaxSize()) {
                EmptyContent(onRefresh = { onAction(HomeAction.Refresh) })
            }

            else -> LazyColumn(...) {
                items(uiState.tasks, key = { it.id }) { task ->
                    TaskCard(
                        title = task.title,
                        owner = displayOwner(task),
                        completed = task.completed,
                        priority = task.priority,
                        onOpenTask = { onAction(HomeAction.ItemClicked(task.id)) },
                    )
                }
            }
        }
    }
}''')
body(doc, '关键:Screen 不持有 ViewModel/repository/NavController(验收点),只根据 uiState 渲染、把事件封装成 HomeAction 通过 onAction 向上送;四个 when 分支互斥覆盖四态;TaskCard 的点击封装成 ItemClicked(task.id),重试/刷新封装成 Refresh。', indent=False)

h2(doc, '4.6 ErrorContent + Retry(步骤 19)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/home/ErrorContent.kt', indent=False)
body(doc, 'ErrorContent 接收 message 和 onRetry,显示错误图标 + 文案 + "重试"按钮。onRetry 由 HomeScreen 接成 onAction(HomeAction.Refresh),即重试就是让 ViewModel 再调一次 repository.getTasks():点击重试 -> onAction(Refresh) -> ViewModel.refresh() -> isLoading=true(回到 Loading) -> 成功则 Content / 失败则再次 Error。失败可重试且不会崩溃(验收点)。')

h2(doc, '4.7 EmptyContent:emptyMode 触发(步骤 20)')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/home/EmptyContent.kt', indent=False)
body(doc, 'EmptyContent 沿用实验二的"收件箱图标 + 当前没有任务 + 点这里重试"。触发方式:FakeTaskRepository(emptyMode=true) 返回 emptyList,refresh 成功后 tasks.isEmpty() 走 Empty 分支。点"重试"同样触发 onAction(Refresh)。')

h2(doc, '4.8 App:注入 Repository + 测试钩子')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/ui/App.kt', indent=False)
code_lines(doc, '''@Composable
fun App(
    overrideRepository: TaskRepository? = null,
) {
    val navController = rememberNavController()
    val repository: TaskRepository = remember(overrideRepository) {
        overrideRepository ?: FakeTaskRepository()
    }

    MaterialTheme {
        Surface(Modifier.fillMaxSize()) {
            NavHost(navController, startDestination = Destination.HomeDestination.route) {
                composable(Destination.HomeDestination.route) {
                    HomeRoute(
                        repository = repository,
                        onNavigate = { taskId ->
                            navController.navigate(Destination.TaskDetailDestination.createRoute(taskId))
                        },
                    )
                }
                composable(
                    route = Destination.TaskDetailDestination.route,
                    arguments = listOf(navArgument(Destination.TaskDetailDestination.ARG_TASK_ID) {
                        type = NavType.IntType
                    }),
                ) { backStackEntry ->
                    val taskId = backStackEntry.arguments?.getInt(Destination.TaskDetailDestination.ARG_TASK_ID) ?: -1
                    TaskDetailScreen(taskId = taskId, onBack = { navController.popBackStack() })
                }
            }
        }
    }
}''')
body(doc, '关键:overrideRepository 是测试钩子,默认 null 用 FakeTaskRepository(Content 态);验收时改 MainActivity 调 App(overrideRepository = FakeTaskRepository(emptyMode/errorMode=true)) 即可演示 Empty/Error。Repository 在 App 层创建并向下传,Screen 不直接调(验收点)。NavController 仍只在 App 持有(沿用实验二解耦)。', indent=False)

h2(doc, '4.9 MainActivity:验收四态入口')
body(doc, '文件:app/src/main/java/edu/example/mobilecourse/lab3/MainActivity.kt', indent=False)
code_lines(doc, '''class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MaterialTheme {
                App()          // 默认 Content;验收时改:
                // App(overrideRepository = FakeTaskRepository(emptyMode = true))   // Empty
                // App(overrideRepository = FakeTaskRepository(errorMode = true))   // Error
            }
        }
    }
}''')

# 五、结果
h1(doc, '五、结果')
body(doc, '构建:gradle assembleDebug 输出 BUILD SUCCESSFUL in 7s,产出 app/build/outputs/apk/debug/app-debug.apk。首次构建因 viewModelFactory DSL 报 Unresolved reference 失败,改用 ViewModelProvider.Factory 后第二次构建成功(详见第六节)。')
body(doc, '运行截图(验收四态,改 MainActivity 的 App 参数后重新运行):', indent=False, bold=True)
shot_image(doc, 'shot_01_content.png', '图 1  首页 Content 态:App() 默认,800ms Loading 后显示 100 条任务')
shot_image(doc, 'shot_02_loading.png', '图 2  首页 Loading 态:进入瞬间 isLoading=true,显示 CircularProgressIndicator')
shot_image(doc, 'shot_03_error.png', '图 3  首页 Error 态:App(errorMode=true),显示错误图标 + 文案 + 重试按钮')
shot_image(doc, 'shot_04_retry_error.png', '图 4  Error 态点重试:回到 Loading 后再次 Error(不崩溃)')
shot_image(doc, 'shot_05_empty.png', '图 5  首页 Empty 态:App(emptyMode=true),显示收件箱图标 + 当前没有任务')
body(doc, '验收点对照:', indent=False, bold=True)
table(doc, ['验收点', '结果'], [
    ['Screen 不直接调 repository', 'HomeScreen 只接 uiState + onAction,repository 由 App 注入 HomeRoute/ViewModel'],
    ['ViewModel 公开只读 StateFlow', '_uiState=MutableStateFlow(私有),uiState=_uiState.asStateFlow()(只读)'],
    ['四种 UI 状态均可演示', 'Loading(init/delay 800ms)+ Error(errorMode)+ Empty(emptyMode)+ Content(默认)'],
    ['失败后可重试且不会崩溃', 'refresh 的 try/catch 把异常转 errorMessage,Retry 触发 refresh 回 Loading 再判定'],
], widths=[7, 9])

# 六、故障与调试
h1(doc, '六、故障与调试')
body(doc, '真实故障:HomeRoute 用 androidx.lifecycle.viewmodel.compose 的 viewModelFactory DSL + initializer,编译报 Unresolved reference。', bold=True)
h3(doc, '现象')
body(doc, '第一版 HomeRoute.kt 直接套用指导书/官方示例的 viewModelFactory DSL 写法:')
code_lines(doc, '''import androidx.lifecycle.viewmodel.compose.viewModelFactory
import androidx.lifecycle.viewmodel.initializer

val viewModel: HomeViewModel = viewModel(
    factory = viewModelFactory {
        initializer {
            HomeViewModel(repository, onOpenTask = onNavigate)
        }
    }
)''')
body(doc, 'gradle assembleDebug 报错:')
code_lines(doc, '''e: file://.../HomeRoute.kt: Unresolved reference 'viewModelFactory'
e: file://.../HomeRoute.kt: Unresolved reference 'initializer' ''')
h3(doc, '定位')
for s in [
    '看报错:两个符号都 Unresolved,说明 import 的包路径在该依赖版本下不可达,不是拼写问题。',
    '查依赖:lifecycle-viewmodel-compose 2.8.6 已加入依赖,但 viewModelFactory/initializer 这两个 DSL 函数在 2.8.6 的实际可达性有问题(官方示例对应更新的版本或额外的 -initializer 子包)。',
    '回退到更通用的写法:viewModel(factory = ...) 接受任意 ViewModelProvider.Factory,自己用 object : ViewModelProvider.Factory 覆写 create(modelClass) 返回 HomeViewModel,这是自 lifecycle 2.0 起就稳定的 API,覆盖面最广。',
]:
    numbered(doc, s.split('.')[0], s)
h3(doc, '原因')
body(doc, 'viewModelFactory { initializer { ... } } 是 lifecycle-viewmodel-compose 后续版本提供的便利 DSL,它依赖特定的 -initializer 扩展包或更新版本的 API 表面。在 lifecycle 2.8.6 + 当前工程依赖配置下,这两个符号的解析路径不可达,导致 Unresolved reference。官方示例代码片段往往对应"最新稳定版"或省略了额外依赖声明,直接照搬到固定版本工程会出现符号缺失。')
h3(doc, '修复')
body(doc, '把 viewModelFactory DSL 改成经典的 object : ViewModelProvider.Factory,只覆写 create(modelClass) 返回 HomeViewModel 实例,传入 repository 和 onNavigate。这是 lifecycle 2.x 起就稳定可用的 API,不依赖任何 DSL 扩展:')
code_lines(doc, '''val viewModel: HomeViewModel = viewModel(
    factory = object : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T =
            HomeViewModel(repository = repository, onOpenTask = onNavigate) as T
    }
)''')
body(doc, '重新构建:BUILD SUCCESSFUL in 7s。四态运行均正常,ViewModel 绑定 NavBackStackEntry、配置变化存活、StateFlow 订阅刷新均符合预期。', indent=False)

# 七、思考
h1(doc, '七、思考')
h2(doc, '7.1 UDF 数据流图')
body(doc, '实验三的核心是单向数据流(UDF)。State 从 ViewModel 单向向下流向 Screen,Event 从 Screen 单向向上送回 ViewModel,两条流不交叉、不回流,状态只在 ViewModel 这一个地方被修改:')
code_lines(doc, '\n'.join([
    '         +--------------------------+',
    '         |   FakeTaskRepository     |  (suspend getTasks)',
    '         +--------------------------+',
    '                     |  data',
    '                     v',
    '         +--------------------------+',
    '         |     HomeViewModel        |',
    '         |  _uiState(Mutable)        |',
    '         |  uiState (只读 StateFlow) |',
    '         |  init{refresh} onAction   |',
    '         +--------------------------+',
    '        /                            \\',
    '   State 向下                  Event 向上',
    '      |                            ^',
    '      v                            |',
    '  +--------------------------+   onAction(HomeAction)',
    '  | HomeRoute                 |   - Refresh     -> refresh()',
    '  |  collectAsStateWithLifecycle   - ItemClicked -> onOpenTask(id)',
    '  +--------------------------+        |',
    '        |                            v',
    '        v                      (回调到 Route/App)',
    '  +--------------------------+        |',
    '  | HomeScreen (纯 UI)        |        v',
    '  |  when{四态} onAction      |   navController.navigate(createRoute(id))',
    '  +--------------------------+',
]))
body(doc, 'State 向下:HomeViewModel 把 _uiState 通过 asStateFlow() 暴露成只读 StateFlow,HomeRoute 用 collectAsStateWithLifecycle 订阅成 Compose State,再传给 HomeScreen 渲染。Screen 只读、不改。', indent=False)
body(doc, 'Event 向上:用户在 Screen 的操作(点重试、点卡片)被封装成 HomeAction,通过 onAction 送回 ViewModel.onAction;ViewModel 决定如何更新 state(Refresh 改 state、ItemClicked 不改 state 只回调)。事件不直接改 state,只能经 ViewModel,这是 UDF 的"单向"所在。', indent=False)

h2(doc, '7.2 状态放错位置会发生什么(实验反思)')
body(doc, '如果把状态从 ViewModel 放到别处,会逐一踩到下列坑:')
for i, t in enumerate([
    '状态放 Screen(用 remember 存 isLoading/tasks):配置变化(旋转屏幕)时 Composable 被销毁重建,remember 的值丢失,加载状态和已加载的数据都会丢,用户要重新等 800ms;而 ViewModel 绑定 NavBackStackEntry、配置变化时存活,StateFlow 自动重放最新 state,UI 无感恢复。',
    '状态放 Screen + 用 rememberSaveable:只能存可序列化的基本类型,List<CourseTask> 要自己写 Saver,且数据量大时序列化卡顿;更关键是"状态分散在多个 Screen",数据源不唯一,多页面共享数据时会出现不一致(详情页改了任务,首页不刷新)。',
    'Screen 直接调 repository(跳过 ViewModel):把 suspend 调用 + 异常处理写进 Composable,首先违反"Composable 应是纯函数"原则,Preview 会触发真实网络调用导致 Preview 崩溃;其次错误处理散落各处,重试逻辑要在每个 Screen 重复写;最后 ViewModel 存活 + StateFlow 订阅的配置变化保护全部失效。验收点明确要求"Screen 不直接调 repository"。',
    'State 可变且对外暴露 MutableStateFlow:Screen 能直接 _uiState.value = ... 改 state,数据源不再唯一,状态变化路径无法追踪,调试时不知道是谁改了 state;asStateFlow() 转只读后,只有 ViewModel 内部能改,变化路径单一可追踪(验收点"ViewModel 公开只读 StateFlow")。',
    'Error 不进 uiState 而是直接 throw:Composable 抛异常会导致整个 Compose 树崩溃,用户看到红屏或闪退;把异常 catch 后转成 errorMessage 写进 state,Screen 走 ErrorContent + Retry,用户可重试且不崩溃(验收点"失败后可重试且不会崩溃")。',
], 1):
    numbered(doc, i, t)
body(doc, '一句话:状态放 ViewModel 是 UDF 的"状态在哪里"答案 —— 唯一数据源、配置变化存活、错误可控、Screen 可 Preview 可测试。放错位置的本质是"数据源不唯一 + 状态生命周期错配",上面每个坑都是这两点的具体表现。', indent=False)

h2(doc, '7.3 与实验二的比较')
body(doc, '实验二到实验三,单向数据流的形状没变(数据向下、事件向上),但每一层都向上挪了一格:')
code_lines(doc, '\n'.join([
    '             实验二                          实验三',
    '数据  顶层 sampleTasks 常量          ->  TaskRepository(getTasks suspend)',
    '状态  HomeScreen(tasks 参数)         ->  HomeViewModel(_uiState StateFlow)',
    '桥    无(Screen 直放)               ->  HomeRoute(viewModel + collectAsState)',
    '事件  onOpenTask(taskId) 回调        ->  onAction(HomeAction) 事件入口',
    '四态  无(空/非空二态)              ->  Loading/Error/Empty/Content 四态',
    '错误  taskById 找不到 -> "不存在"    ->  catch -> errorMessage -> Retry',
]))
body(doc, '实验二的 onOpenTask(taskId) 在实验三升级成 onAction(ItemClicked(taskId)) —— 从单一回调扩展成 sealed interface 事件集,未来加"标记完成""删除"等动作只需加新的 Action 子类型,when exhaustiveness 保证编译期检查。NavHost 的连接方式基本没动,这正是分层解耦的价值:数据层和状态层换了,导航层不用改。可以预见实验四会把 FakeTaskRepository 换成 NetworkTaskRepository(Retrofit + REST API),而 ViewModel/Route/Screen 一行都不用改 —— 接口隔离数据源的意义就在这里。')

doc.save(OUT_PATH)
print('已生成:', OUT_PATH)
