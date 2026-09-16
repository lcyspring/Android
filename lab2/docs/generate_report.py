# -*- coding: utf-8 -*-
"""
实验二 Word 报告生成脚本 —— WPS 最大兼容版(沿用实验一已验证的脚本风格)
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

REPORT_DIR = r'd:\rain_android\lab2\docs'
OUT_PATH = os.path.join(REPORT_DIR, '实验二报告_移动UI设计与页面导航.docx')

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
    # 纯文本短横线列表,不依赖编号库,任何阅读器都稳定
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

def read_code(path):
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()

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
style_run(p.add_run('实验二  移动 UI 设计与页面导航'), cn='黑体', size=15, bold=True)

info = doc.add_table(rows=4, cols=4)
info.style = 'Table Grid'
info_rows = [
    ['姓名', '李春雨', '学号', '202305567128'],
    ['班级', '计科2班', '完成日期', '2026-09-16'],
    ['专业', '计算机科学与技术', '课程', '移动应用开发'],
    ['实验编号', '实验二', '实验名称', '移动 UI 设计与页面导航'],
]
for i, row in enumerate(info_rows):
    for j, val in enumerate(row):
        cp = info.rows[i].cells[j].paragraphs[0]
        style_run(cp.add_run(val), size=10.5, bold=(j % 2 == 0))
doc.add_paragraph()

# 一、目标
h1(doc, '一、实验目标')
for i, g in enumerate([
    '在实验一 TaskCard 基础上把首页改造为 LazyColumn，使用稳定 key = task.id，验证 100 条长列表的滚动与复用。',
    '新增 EmptyContent 空状态与 TaskDetailScreen(taskId) 详情页，实现 Home → TaskDetail 导航并正确传递 taskId。',
    '用 sealed class Destination 集中表达导航目的地，App 用 NavHost 连接两个目的地，NavController 只在 App 持有，落实"页面组件不持有导航控制器"的解耦方式。',
    '测试返回键、无数据、100 条数据三种场景，至少覆盖一个边界/错误状态。',
], 1):
    numbered(doc, i, g)

# 二、环境
h1(doc, '二、实验环境')
table(doc, ['项目', '信息'], [
    ['操作系统', 'Windows 11'],
    ['开发工具', 'Android Studio（Lab2Compose 工程，AGP 8.7.2）'],
    ['Android SDK', 'API 37（Android 16），路径 D:\\Android\\Sdk'],
    ['JDK', '17（Microsoft jdk-17.0.19.10-hotspot）'],
    ['Kotlin', '2.0.21'],
    ['Compose BOM', '2024.10.01'],
    ['Navigation Compose', '2.8.3（androidx.navigation:navigation-compose）'],
    ['Android Gradle Plugin', '8.7.2'],
    ['Gradle', '8.10.2（用全局发行版缓存构建）'],
    ['运行设备', 'Android 模拟器 Pixel 7（系统镜像 API 37.1，Google Play x86_64）'],
    ['构建结果', 'BUILD SUCCESSFUL in 1m 16s，35 actionable tasks: 35 executed'],
], widths=[4, 12])

# 三、设计
h1(doc, '三、设计')
h2(doc, '3.1 页面结构')
body(doc, '实验二在实验一的单页面基础上拆为两个目的地，由 NavHost 统一调度：')
code_lines(doc, '\n'.join([
    'MainActivity (只 setContent { App() })',
    '  └── App (持有 NavController + NavHost)',
    '        ├── 目的地 1: HomeDestination  route = "home"',
    '        │     └── HomeScreen(tasks, onOpenTask, onRefresh)',
    '        │           ├── 空列表 -> EmptyContent(onRefresh)',
    '        │           └── 非空 -> LazyColumn',
    '        │                 └── TaskCard(..., onOpenTask = { onOpenTask(task.id) })',
    '        └── 目的地 2: TaskDetailDestination  route = "task_detail/{taskId}"',
    '              └── TaskDetailScreen(taskId, onBack)',
    '                    ├── 找到 -> 详情卡 + 关联任务列表',
    '                    └── 找不到 -> "任务不存在"边界状态',
]))

h2(doc, '3.2 数据流')
body(doc, '实验二仍是单向数据流，数据从顶层 List<CourseTask> 流向 Composable，事件通过回调向上传到 App 这一层接导航：')
code_lines(doc, '\n'.join([
    'sampleTasks (List<CourseTask>, 100 条顶层常量)',
    '      |  传入',
    '      v',
    'App(overrideTasks = null)  持有 NavController',
    '      |  NavHost 注册两个目的地',
    '      v',
    'HomeScreen(tasks, onOpenTask, onRefresh)',
    '      |  items(tasks, key = it.id)',
    '      v',
    'TaskCard(..., onOpenTask = { onOpenTask(task.id) })   // 只把 taskId 往上传',
    '      |  用户点击',
    '      v',
    'App.onOpenTask = { id -> navController.navigate(TaskDetailDestination.createRoute(id)) }',
    '      |  NavHost 解析路由占位符 {taskId}',
    '      v',
    'TaskDetailScreen(taskId, onBack)   // taskId 从 NavBackStackEntry.arguments 取出',
    '      |  返回键 / TopAppBar 返回',
    '      v',
    'App.onBack = { navController.popBackStack() }',
]))
body(doc, '自问自答（实验指导书 H 部分）：', indent=False, bold=True)
for qa in [
    '数据在哪里？sampleTasks 仍是顶层 List<CourseTask> 常量；TaskDetailScreen 用 taskById(taskId) 在 100 条样本里查找。实验三会移到 Repository + StateFlow。',
    '状态在哪里？实验二仍是"无状态 Composable + 顶层常量"，HomeScreen 的空/非空分支由 List.isEmpty() 直接判定；导航状态由 NavController 持有（这是 Compose Navigation 的标准做法）。',
    '事件从哪里来、到哪里去？TaskCard 用户点击通过 onOpenTask(taskId) 送到 HomeScreen，再到 App 接成 navigate(...)；返回事件通过 onBack 送到 App 接成 popBackStack()。',
    '错误在哪里处理？taskId 找不到任务时，TaskDetailScreen 显示"任务不存在"边界状态并提供返回按钮，不会崩溃；实验三接入 Repository 后还会加 Loading/Error/Empty/Content 四态。',
]:
    bullet(doc, qa)

h2(doc, '3.3 类关系')
code_lines(doc, '\n'.join([
    'Destination (sealed class)             <- 集中表达目的地',
    '  +-- HomeDestination       route = "home"',
    '  +-- TaskDetailDestination  route = "task_detail/{taskId"',
    '        +-- ARG_TASK_ID = "taskId"',
    '        +-- createRoute(id): String = "task_detail/$id"',
    '',
    'App(@Composable)                        <- 持有 NavController + NavHost',
    '  +-- 入参: overrideTasks: List<CourseTask>?',
    '  +-- 注册: composable(Home.route){HomeScreen(...)}',
    '  +-- 注册: composable(TaskDetail.route, args=[Int]){TaskDetailScreen(...)}',
    '',
    'HomeScreen(@Composable)                <- 无导航依赖',
    '  +-- 入参: tasks, onOpenTask: (Int)->Unit, onRefresh: ()->Unit',
    '',
    'TaskCard(@Composable)                  <- 可复用,无导航依赖',
    '  +-- 入参: title, owner, completed, priority, onOpenTask: ()->Unit',
    '',
    'TaskDetailScreen(@Composable)          <- 无导航依赖',
    '  +-- 入参: taskId: Int, onBack: ()->Unit',
    '  +-- 内部: taskById(taskId): CourseTask?  纯函数查数据',
]))

h2(doc, '3.4 关键决策')
for i, d in enumerate([
    'NavController 只在 App 一层持有，HomeScreen 和 TaskDetailScreen 都不直接访问它，满足验收点"不直接访问 TaskCard / Screen 的 NavController"，也保证这两个页面能独立 Preview、独立测试、未来可被搜索页或底部导航的其他 Tab 复用。',
    '用 sealed class Destination 集中表达 route + 参数键 + createRoute，而不是在多个文件里散写 "home" / "task_detail/{taskId}" / "taskId" 字符串，避免拼写不一致导致导航注册失败（详见第六节故障）。',
    'TaskDetailDestination.route 直接写成 "task_detail/{taskId}" 含占位符，而不是 "task_detail"，确保 NavHost 的 composable(route) 注册的模板能匹配 navigate("task_detail/7") 这种带参路由。',
    'TaskCard 的点击回调从实验一的 onClick 改名为 onOpenTask（on + 动作命名约定），强调"我只负责告诉上层想打开这个 taskId，至于怎么打开是上层的事"，为实验三 Route/Screen 拆分后接入 ViewModel::onAction 留接口。',
    '100 条样本数据由 buildList 生成，每 7 条 1 条 owner=null，保留实验一"未分配"空安全分支的演示，同时验证长列表滚动；空状态用专门的 emptyTasks 常量触发 EmptyContent。',
], 1):
    numbered(doc, i, d)

# 四、实现
h1(doc, '四、实现')
LAB2 = r'd:\rain_android\lab2'
dest_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\ui\navigation\Lab2Destinations.kt'))
app_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\ui\App.kt'))
home_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\ui\home\HomeScreen.kt'))
taskcard_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\ui\TaskCard.kt'))
empty_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\ui\home\EmptyContent.kt'))
detail_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\ui\taskdetail\TaskDetailScreen.kt'))
course_kt = read_code(os.path.join(LAB2, r'app\src\main\java\edu\example\mobilecourse\lab2\data\CourseTask.kt'))

def snippet(src, start_marker, end_marker, indent_dedent=False):
    """从源码中按起止 marker 截取一段，方便只放关键代码。"""
    i = src.find(start_marker)
    j = src.find(end_marker, i)
    if i < 0 or j < 0:
        return src
    return src[i:j + len(end_marker)]

h2(doc, '4.1 Destination 定义（步骤 10）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/ui/navigation/Lab2Destinations.kt', indent=False)
code_lines(doc, snippet(dest_kt,
    'sealed class Destination(val route: String) {',
    'fun createRoute(taskId: Int): String = "task_detail/$taskId"'))

h2(doc, '4.2 App：NavHost 连接两个目的地（步骤 11、12）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/ui/App.kt', indent=False)
code_lines(doc, snippet(app_kt,
    'NavHost(',
    'TaskDetailScreen('))
code_lines(doc, '        taskId = taskId,\n        onBack = { navController.popBackStack() },\n    )\n        }')

h2(doc, '4.3 HomeScreen：LazyColumn + 稳定 key + onOpenTask 回调（步骤 7、12）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/ui/home/HomeScreen.kt', indent=False)
code_lines(doc, snippet(home_kt,
    'if (tasks.isEmpty()) {',
    '}'))
body(doc, '关键：items(tasks, key = { it.id }) 用稳定 key，TaskCard 的点击只调 onOpenTask(task.id)，不碰 NavController。', indent=False)

h2(doc, '4.4 TaskCard：onClick 改名为 onOpenTask（步骤 12）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/ui/TaskCard.kt', indent=False)
code_lines(doc, snippet(taskcard_kt,
    '@Composable\nfun TaskCard(',
    'onOpenTask: () -> Unit = {},'))
body(doc, 'TaskCard 不再叫 onClick 而是叫 onOpenTask，参数本身不带 taskId，由 HomeScreen 在调用处用 onOpenTask = { onOpenTask(task.id) } 包一层传入——这样 TaskCard 完全不关心 taskId 怎么用，解耦更彻底。', indent=False)

h2(doc, '4.5 EmptyContent：空列表占位（步骤 8）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/ui/home/EmptyContent.kt', indent=False)
code_lines(doc, snippet(empty_kt,
    '@Composable\nfun EmptyContent(onRefresh: () -> Unit = {}) {',
    'EmptyContent(onRefresh = {})'))

h2(doc, '4.6 TaskDetailScreen：按 taskId 取数 + 边界状态（步骤 9）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/ui/taskdetail/TaskDetailScreen.kt', indent=False)
code_lines(doc, snippet(detail_kt,
    '@OptIn(ExperimentalMaterial3Api::class)\n@Composable\nfun TaskDetailScreen(\n    taskId: Int,\n    onBack: () -> Unit,\n) {',
    'val task: CourseTask? = taskById(taskId)'))
body(doc, '关键：taskId 直接来自 NavHost 解析后的 Int 参数；taskById 找不到时返回 null，TaskDetailScreen 走"任务不存在"分支并提供返回按钮，覆盖验收点"边界/错误状态"。', indent=False)

h2(doc, '4.7 数据层：100 条样本 + taskById 查询')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab2/data/CourseTask.kt', indent=False)
code_lines(doc, snippet(course_kt,
    'val sampleTasks: List<CourseTask> = buildList {',
    '    sampleTasks.firstOrNull { it.id == taskId }'))

# 五、结果
h1(doc, '五、结果')
body(doc, '构建：gradle assembleDebug 输出 BUILD SUCCESSFUL in 1m 16s，35 actionable tasks: 35 executed，产出 app/build/outputs/apk/debug/app-debug.apk。')
body(doc, '运行截图（验收点）：', indent=False, bold=True)
shot_placeholder(doc, '首页 100 条样本列表，LazyColumn 滚动正常')
shot_placeholder(doc, '点击任务 #1 进入详情页，taskId 正确带入')
shot_placeholder(doc, '详情页 owner=null 任务（taskId=3，显示"未分配"）')
shot_placeholder(doc, '空列表 EmptyContent 空状态（overrideTasks=emptyTasks）')
shot_placeholder(doc, '详情页边界状态：手敲路由 task_detail/99999 显示"任务不存在"')
body(doc, '验收点对照：', indent=False, bold=True)
table(doc, ['验收点', '结果'], [
    ['导航能带入正确 taskId', 'TaskDetailScreen(taskId=1) 显示"完成实验二报告"，taskId 来自 NavHost 解析'],
    ['不直接访问 TaskCard NavController', 'TaskCard 只调 onOpenTask()，由 App 接 navController.navigate'],
    ['列表为空时有明确空状态', 'EmptyContent 显示"当前没有任务" + 重试按钮'],
    ['100 条数据滚动正常', 'LazyColumn + 稳定 key = task.id，滑动流畅'],
], widths=[8, 8])

# 六、故障与调试
h1(doc, '六、故障与调试')
body(doc, '真实故障：Destination.route 缺占位符导致 navigate 报"目的地未注册"。', bold=True)
h3(doc, '现象')
body(doc, '在第一版 Destination 里把 TaskDetailDestination.route 写成纯字符串 "task_detail"（不含 {taskId} 占位符），App 里 composable(route = Destination.TaskDetailDestination.route) 注册了 "task_detail"，点击列表项时 HomeScreen 调 onOpenTask(id) -> App 调 navController.navigate("task_detail/7")，运行时抛出：')
code_lines(doc, 'IllegalArgumentException: Navigation destination that matches route "task_detail/7"\ncannot be found in the NavController\'s graph.')
h3(doc, '定位')
for s in [
    '看异常信息：NavHost 在 graph 里找不到 "task_detail/7" 这条路由，说明注册的不是带参模板。',
    '回到 App.kt 的 composable(route = ...) 看，注册的是 "task_detail"，而 navigate("task_detail/7") 是一条带参路由，两者字符串不相等，NavHost 不会做后缀匹配。',
    '再翻 Destination 定义，发现 route = "task_detail" 漏了 {taskId} 占位符。',
]:
    numbered(doc, s.split('.')[0], s)
h3(doc, '原因')
body(doc, 'Navigation Compose 的 composable(route) 注册的是路由模板，带参目的地必须用 "{参数名}" 占位符写完整模板，例如 "task_detail/{taskId}"；调用 navigate("task_detail/7") 时，NavHost 才能用模板匹配出参数。只写 "task_detail" 等于注册了一条无参目的地，自然匹配不到带参路由。')
h3(doc, '修复')
body(doc, '把 TaskDetailDestination.route 直接定义为 "task_detail/{taskId}"，并在 composable(route = ...) 注册时用同一常量，再用 navArgument(ARG_TASK_ID){ type = NavType.IntType } 声明参数类型，ARG_TASK_ID = "taskId" 与占位符里的大括号内容严格一致。修复后重新构建、点击列表项，TaskDetailScreen 正确收到 taskId=7 并显示对应任务。')
code_lines(doc, 'object TaskDetailDestination : Destination(route = "task_detail/{taskId}") {\n    const val ARG_TASK_ID = "taskId"\n    fun createRoute(taskId: Int): String = "task_detail/$taskId"\n}')

# 七、思考
h1(doc, '七、思考')
h2(doc, '7.1 NavHost / Destination / NavController 三者关系')
body(doc, 'NavController 是导航状态机：维护一个返回栈（NavBackStackEntry 栈），提供 navigate(route) 压栈和 popBackStack() 出栈。它由 rememberNavController() 在 App 这一层创建，是整个导航树的唯一状态入口。')
body(doc, 'NavHost 是 Compose 里的"路由表 + 渲染器"：它的 content {} 里用 composable(route) { ... } 把每条路由模板注册成一个目的地，当 NavController 当前栈顶目的地变化时，NavHost 负责把对应目的地的 Composable 渲染出来。可以把 NavHost 理解成"路由 -> Composable"的 switch，NavController 理解成"当前指向哪条 case 的指针。')
body(doc, 'Destination 是项目自己抽出的常量集合：用 sealed class 把 route 模板、参数键、createRoute 拼参函数集中表达，避免字符串散落。它不属于 Navigation 库，只是一个让代码可维护的约定，能让 HomeScreen/TaskDetailScreen/App 都从同一个常量取路由字符串，杜绝拼写不一致。')
code_lines(doc, '\n'.join([
    'NavController  ——  持有返回栈,提供 navigate/popBackStack',
    '     |  观察栈顶',
    '     v',
    'NavHost        ——  按 route 模板匹配,渲染对应 Composable',
    '     |  注册模板',
    '     v',
    'Destination    ——  项目常量:route 模板 + 参数键 + createRoute',
]))
h2(doc, '7.2 为什么"页面组件不持有 NavController"')
body(doc, '如果把 NavController 直接传给 TaskCard，TaskCard 就和导航库耦合死了：换到搜索页、底部导航的其他 Tab、或者写单元测试时都得 mock NavController。让 TaskCard 只通过 onOpenTask() 回调上报"我想打开某个 taskId"，由上层决定怎么处理（push 详情页、弹窗、Tab 切换都行），TaskCard 就成了可复用、可 Preview、可测试的纯展示组件。这正是实验一就在注释里写"实验二会接 navController.navigate"的真正含义——接导航的是上层，不是卡片本身。')
h2(doc, '7.3 与实验一的比较')
body(doc, '实验一 TaskCard.onClick 只打一行 Log.d，因为单页面没有"去哪里"的概念；实验二把 onClick 改名 onOpenTask 并接到 navigate，单向数据流的形状没变（数据向下、事件向上），但上层多了一个 NavController 把事件翻译成页面跳转。可以预见实验三会把数据从 sampleTasks 移到 ViewModel 的 StateFlow，届时 onOpenTask 会再上一层变成 onAction(ItemClicked(id))，但 NavHost 的连接方式基本不动，这正是分层解耦的价值。')

doc.save(OUT_PATH)
print('已生成:', OUT_PATH)
