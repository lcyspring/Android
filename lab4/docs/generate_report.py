# -*- coding: utf-8 -*-
"""
实验四 Word 报告生成脚本 —— WPS 最大兼容版(沿用实验一/二/三已验证的脚本风格)
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

REPORT_DIR = r'd:\rain_android\lab4\docs'
OUT_PATH = os.path.join(REPORT_DIR, '实验四报告_网络请求_本地数据与移动端安全.docx')
SCREENSHOT_DIR = r'D:\rain_android\docs\screenshots'

def set_east_asia_font(element_rpr_owner, font_name):
    rPr = element_rpr_owner.get_or_add_rPr()
    rFonts = rPr.get_or_add_rFonts()
    rFonts.set(qn('w:eastAsia'), font_name)

def style_run(run, cn='宋体', en='Times New Roman', size=10.5, bold=False, color=None):
    run.font.name = en
    run.font.size = Pt(size)
    run.font.bold = bold
    if color is not None:
        run.font.color.rgb = color
    set_east_asia_font(run._element, cn)

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
    for line in code.split('\n'):
        p = doc.add_paragraph()
        pf = p.paragraph_format
        pf.space_after = Pt(0); pf.space_before = Pt(0); pf.line_spacing = 1.15
        style_run(p.add_run(line if line else ' '), cn='宋体', en='Consolas', size=9)
    doc.add_paragraph()

def shot_image(doc, filename, caption, width_cm=9):
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
    t.style = 'Table Grid'
    for j, htext in enumerate(header):
        cell = t.rows[0].cells[j]
        cp = cell.paragraphs[0]
        style_run(cp.add_run(htext), size=10, bold=True)
    for i, row in enumerate(rows):
        for j, val in enumerate(row):
            cp = t.rows[i + 1].cells[j].paragraphs[0]
            style_run(cp.add_run(str(val)), size=10)
    if widths:
        for row in t.rows:
            for j, w in enumerate(widths):
                row.cells[j].width = Cm(w)
    return t

# ================= 文档 =================
doc = Document()

normal = doc.styles['Normal']
normal.font.name = 'Times New Roman'
normal.font.size = Pt(10.5)
normal.paragraph_format.line_spacing = 1.5
set_east_asia_font(normal.element, '宋体')

sec = doc.sections[0]
sec.page_width = Cm(21); sec.page_height = Cm(29.7)
sec.top_margin = Cm(2.54); sec.bottom_margin = Cm(2.54)
sec.left_margin = Cm(3.18); sec.right_margin = Cm(3.18)

# 封面
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
style_run(p.add_run('《移动应用开发》实验报告'), cn='黑体', size=20, bold=True)
p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER
style_run(p.add_run('实验四  网络请求、本地数据与移动端安全'), cn='黑体', size=15, bold=True)

info = doc.add_table(rows=4, cols=4); info.style = 'Table Grid'
for i, row in enumerate([
    ['姓名', '李春雨', '学号', '202305567128'],
    ['班级', '计科2班', '完成日期', '2026-09-23'],
    ['专业', '计算机科学与技术', '课程', '移动应用开发'],
    ['实验编号', '实验四', '实验名称', '网络请求、本地数据与移动端安全'],
]):
    for j, val in enumerate(row):
        cp = info.rows[i].cells[j].paragraphs[0]
        style_run(cp.add_run(val), size=10.5, bold=(j % 2 == 0))
doc.add_paragraph()

# 一、目标
h1(doc, '一、实验目标')
for i, g in enumerate([
    '通过 Retrofit 访问公开免费 JSONPlaceholder API(https://jsonplaceholder.typicode.com/todos),解析 JSON 并映射成 CourseTask 数据模型,处理网络异常与重试。',
    '用 AndroidX DataStore Preferences 持久化两个用户偏好:"仅看未完成任务"筛选开关和深色模式开关,验证验收点"不在 Composable 中直接读写 DataStore"。',
    '实现相机运行时权限按钮:点击后才申请权限(不在启动时无理由申请),权限被拒绝后 App 不崩溃,只 Toast 提示。',
    '完成安全检查:仓库中无真实 API Key/Token/密码提交,OkHttp 日志拦截器只打 BASIC 级别(URL/状态码),不打响应体避免泄露。',
], 1):
    numbered(doc, i, g)

# 二、环境
h1(doc, '二、实验环境')
table(doc, ['项目', '信息'], [
    ['操作系统', 'Windows 11'],
    ['开发工具', 'Android Studio(lab4Compose 工程,namespace=edu.example.mobilecourse.lab4)'],
    ['Android SDK', 'API 37(Android 16),路径 D:\\Android\\Sdk'],
    ['JDK', '17(Microsoft jdk-17.0.19.10-hotspot)'],
    ['Kotlin', '2.0.21'],
    ['Compose BOM', '2024.10.01'],
    ['Navigation Compose', '2.8.3'],
    ['Lifecycle', '2.8.6(viewmodel-compose + runtime-compose)'],
    ['Retrofit', '2.11.0 + converter-moshi 1.0.0'],
    ['Moshi', '1.15.1(moshi-kotlin)'],
    ['OkHttp', '4.12.0(logging-interceptor BASIC 级别)'],
    ['AndroidX DataStore', '1.1.1(datastore-preferences)'],
    ['网络 API', 'JSONPlaceholder(https://jsonplaceholder.typicode.com/todos,公开免费,无密钥)'],
    ['运行设备', 'Android 模拟器 Pixel 7(API 37.1,Google Play x86_64)'],
    ['构建结果', 'BUILD SUCCESSFUL'],
], widths=[5, 11])

# 三、设计
h1(doc, '三、设计')

h2(doc, '3.1 分层结构(沿用实验三,增加网络层 + DataStore)')
code_lines(doc, '\n'.join([
    'MainActivity (只 setContent + ActivityResultLauncher 相机权限)',
    '  └── App(overrideRepository, prefs, onRequestCamera)',
    '        ├── NavHost',
    '        │     ├── HomeRoute(repository, onNavigate, prefs, onRequestCamera)',
    '        │     │     └── HomeViewModel(repository, prefs, onRequestCamera)',
    '        │     │           ├── init { refresh() + collect DataStore flows }',
    '        │     │           ├── uiState: StateFlow<HomeUiState>   (含 showOnlyIncomplete/darkMode)',
    '        │     │           └── onAction(Refresh/ItemClicked/ToggleFilter/ToggleDark/RequestCamera)',
    '        │     │                 │',
    '        │     │                 v',
    '        │     │           HomeScreen(uiState, filteredTasks, onAction)  ← 纯 UI',
    '        │     │                 ├── TopAppBar(3 IconButton: 筛选/深色/相机)',
    '        │     │                 └── 四态分支 + 筛选后列表',
    '        │     └── TaskDetailScreen(taskById 同步查,沿用实验二)',
    '        │',
    '        └── Repository 层(接口不变,依赖倒置):',
    '              TaskRepository(suspend getTasks(): List<CourseTask>)',
    '                ├── NetworkTaskRepository  ← 实验四默认:Retrofit + JSONPlaceholder',
    '                │     └── TodoApi.getTodos() → List<TodoDto> → toCourseTask() → List<CourseTask>',
    '                └── FakeTaskRepository     ← 测试钩子:errorMode/emptyMode 模拟断网/空数据',
    '',
    'DataStore 层(唯一入口):',
    '  UserPreferences(prefs)',
    '    ├── showOnlyIncompleteFlow: Flow<Boolean>  ← ViewModel collect',
    '    ├── darkModeFlow:          Flow<Boolean>  ← ViewModel collect + MaterialTheme 驱动',
    '    ├── setShowOnlyIncomplete() suspend       ← ViewModel onAction 写',
    '    └── setDarkMode()          suspend       ← ViewModel onAction 写',
    '',
    '安全层:',
    '  无 API Key/Token 硬编码;OkHttp LoggingInterceptor 只打 BASIC 级别',
]))

h2(doc, '3.2 Repository 接口复用(依赖倒置)')
body(doc, '实验三定义的 TaskRepository 接口(suspend fun getTasks(): List<CourseTask>)在实验四完全复用——ViewModel 只依赖接口,不依赖具体实现。NetworkTaskRepository(网络)和 FakeTaskRepository(模拟)都实现这个接口,App 通过 overrideRepository 参数切换,ViewModel/Route/Screen 一行代码不用改。这就是依赖倒置的价值:数据源换了,业务逻辑不用改。')

h2(doc, '3.3 DTO → Entity 映射')
body(doc, 'JSONPlaceholder 返回 TodoDto(userId, id, title, completed),没有 CourseTask 需要的 owner 和 priority。映射策略:')
code_lines(doc, '''data class TodoDto(           data class CourseTask(
    val userId: Int,              val id: Int,              // TodoDto.id → CourseTask.id
    val id: Int,                   val title: String,        // TodoDto.title → CourseTask.title
    val title: String,             val owner: String?,       // JSONPlaceholder 无 owner → null(显示"未分配")
    val completed: Boolean,        val completed: Boolean,  // 直接映射
)                                 val priority: Int = 2,   // JSONPlaceholder 无优先级 → 默认 2
                                )''')

h2(doc, '3.4 DataStore 偏好驱动深色模式')
body(doc, 'App 层 collect darkModeFlow,变化时重新计算 MaterialTheme 的 colorScheme(darkColorScheme() vs lightColorScheme()),无需重启 Activity。这是单向数据流的典型应用:DataStore → Flow → collect → StateFlow → MaterialTheme 变化。')

h2(doc, '3.5 安全设计(指导书步骤 27)')
for i, s in enumerate([
    '无 API Key/Token 硬编码:JSONPlaceholder 是公开免费 API,无需密钥;如果将来换成需要密钥的 API,密钥应存在 local.properties(已加 .gitignore)或 Gradle properties 中通过 BuildConfig 注入,而非直接写进 Kotlin 源码。',
    'OkHttp LoggingInterceptor 只打 BASIC 级别:只输出 URL 和 HTTP 状态码,不打印请求体/响应体,避免敏感数据在 Logcat 泄露。生产构建可考虑关闭日志拦截器。',
    '相机权限不在启动时申请:遵循 Android 运行时权限最佳实践,"只在用户明确需要某功能时才申请",避免首次启动就弹权限弹窗引起反感。用户必须点击相机按钮才触发请求。',
    '权限拒绝不崩溃:onRequestPermissionResult 回调里只 Toast 提示,不 throw、不 finish Activity。验收点"权限拒绝后 App 不崩溃"。',
    '.gitignore 已排除 local.properties、build/、.gradle/、*.iml 等,构建产物和本地配置不会被提交。',
], 1):
    numbered(doc, i, s)

# 四、实现
h1(doc, '四、实现')

h2(doc, '4.1 TodoDto + TodoApi + RetrofitClient(步骤 21)')
body(doc, '文件:data/remote/TodoDto.kt,data/remote/TodoApi.kt,data/remote/RetrofitClient.kt', indent=False)
code_lines(doc, '''// TodoDto.kt
data class TodoDto(val userId: Int, val id: Int, val title: String, val completed: Boolean)

// TodoApi.kt
interface TodoApi {
    @GET("todos") suspend fun getTodos(): List<TodoDto>
    @GET("todos/{id}") suspend fun getTodoById(@Path("id") id: Int): TodoDto
}

// RetrofitClient.kt  — 单例,统一配置
object RetrofitClient {
    private const val BASE_URL = "https://jsonplaceholder.typicode.com/"
    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC   // 只打 URL/状态码,不打响应体
    }
    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .connectTimeout(15, TimeUnit.SECONDS)
        .readTimeout(15, TimeUnit.SECONDS)
        .build()
    val todoApi: TodoApi by lazy {
        Retrofit.Builder().baseUrl(BASE_URL).client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create()).build()
            .create(TodoApi::class.java)
    }
}''')

h2(doc, '4.2 NetworkTaskRepository(步骤 22):DTO → CourseTask')
body(doc, '文件:data/repository/NetworkTaskRepository.kt', indent=False)
code_lines(doc, '''class NetworkTaskRepository : TaskRepository {
    override suspend fun getTasks(): List<CourseTask> {
        val todos = RetrofitClient.todoApi.getTodos()   // 200 条
        return todos.map { it.toCourseTask() }
    }
    private fun TodoDto.toCourseTask() = CourseTask(
        id = id, title = title,
        owner = null,                 // JSONPlaceholder 无 owner → 显示"未分配"
        completed = completed,
        priority = 2,                 // JSONPlaceholder 无优先级 → 默认 2
    )
}''')
body(doc, 'NetworkTaskRepository 实现 TaskRepository 接口,ViewModel 不用改就能从 FakeTaskRepository(实验三)换成 NetworkTaskRepository(实验四)。依赖倒置让数据源可替换,验收点"数据访问仍通过 Repository"。')

h2(doc, '4.3 HomeViewModel 扩展:DataStore collect + 新事件(步骤 23/25)')
body(doc, '文件:ui/home/HomeViewModel.kt', indent=False)
code_lines(doc, '''class HomeViewModel(
    private val repository: TaskRepository,
    private val onOpenTask: (Int) -> Unit,
    private val prefs: UserPreferences,
    private val onRequestCamera: () -> Unit,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        refresh()   // 加载网络数据(NetworkTaskRepository)

        // 实验四:collect DataStore 偏好,变化自动写入 uiState
        viewModelScope.launch {
            prefs.showOnlyIncompleteFlow.collect { _uiState.value = _uiState.value.copy(showOnlyIncomplete = it) }
        }
        viewModelScope.launch {
            prefs.darkModeFlow.collect { _uiState.value = _uiState.value.copy(darkMode = it) }
        }
    }

    fun refresh() { /* ... 同实验三 ... */ }

    fun onAction(action: HomeAction) {
        when (action) {
            is HomeAction.Refresh -> refresh()
            is HomeAction.ItemClicked -> onOpenTask(action.taskId)
            // 实验四:写 DataStore(不在 Composable 直写,验收点)
            is HomeAction.ToggleIncompleteFilter -> viewModelScope.launch {
                val newVal = !_uiState.value.showOnlyIncomplete
                prefs.setShowOnlyIncomplete(newVal)
                _uiState.value = _uiState.value.copy(showOnlyIncomplete = newVal)
            }
            is HomeAction.ToggleDarkMode -> viewModelScope.launch {
                val newVal = !_uiState.value.darkMode
                prefs.setDarkMode(newVal)
                _uiState.value = _uiState.value.copy(darkMode = newVal)
            }
            // 实验四:相机权限不改 state,回调给 ActivityResultLauncher
            is HomeAction.RequestCameraPermission -> onRequestCamera()
        }
    }
}''')

h2(doc, '4.4 UserPreferences:DataStore 唯一入口(验收点)')
body(doc, '文件:data/preferences/UserPreferences.kt', indent=False)
code_lines(doc, '''private val Context.dataStore: DataStore<Preferences>
    by preferencesDataStore(name = "lab4_prefs")

class UserPreferences(private val context: Context) {
    val showOnlyIncompleteFlow: Flow<Boolean> = context.dataStore.data.map {
        it[KEY_SHOW_INCOMPLETE] ?: false
    }
    val darkModeFlow: Flow<Boolean> = context.dataStore.data.map {
        it[KEY_DARK_MODE] ?: false
    }
    suspend fun setShowOnlyIncomplete(enabled: Boolean) =
        context.dataStore.edit { it[KEY_SHOW_INCOMPLETE] = enabled }
    suspend fun setDarkMode(enabled: Boolean) =
        context.dataStore.edit { it[KEY_DARK_MODE] = enabled }

    companion object {
        private val KEY_SHOW_INCOMPLETE = booleanPreferencesKey("show_only_incomplete")
        private val KEY_DARK_MODE = booleanPreferencesKey("dark_mode")
        @Volatile private var instance: UserPreferences? = null
        fun getInstance(context: Context): UserPreferences =
            instance ?: synchronized(this) { instance ?: UserPreferences(context.applicationContext).also { instance = it } }
    }
}''')
body(doc, '验收点"不在 Composable 中直接读写 DataStore":UserPreferences 是唯一入口,DataStore edit{} 只能在 ViewModel 层通过 viewModelScope.launch 调用,Composable 只从 HomeUiState(只读 StateFlow)读值、通过 HomeAction 事件向上写。')

h2(doc, '4.5 HomeScreen:TopAppBar 新增三个 IconButton + 筛选')
body(doc, '文件:ui/home/HomeScreen.kt', indent=False)
code_lines(doc, '''TopAppBar(
    title = { Text("实验四 · 任务列表($count)") },
    actions = {
        // 筛选:仅看未完成
        IconButton(onClick = { onAction(HomeAction.ToggleIncompleteFilter) }) {
            Icon(Icons.Filled.FilterAlt, contentDescription = if (uiState.showOnlyIncomplete) "显示全部" else "仅看未完成",
                tint = if (uiState.showOnlyIncomplete) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface)
        }
        // 深色模式切换
        IconButton(onClick = { onAction(HomeAction.ToggleDarkMode) }) {
            Icon(if (uiState.darkMode) Icons.Filled.LightMode else Icons.Filled.DarkMode,
                contentDescription = if (uiState.darkMode) "浅色" else "深色")
        }
        // 相机运行时权限按钮
        IconButton(onClick = { onAction(HomeAction.RequestCameraPermission) }) {
            Icon(Icons.Filled.CameraAlt, contentDescription = "申请相机权限")
        }
    }
)
// 筛选在 Route 层完成,保持 Screen 纯 UI
val filteredTasks = if (uiState.showOnlyIncomplete) uiState.tasks.filter { !it.completed } else uiState.tasks''')

h2(doc, '4.6 MainActivity:ActivityResultLauncher 相机权限(步骤 26)')
body(doc, '文件:MainActivity.kt', indent=False)
code_lines(doc, '''class MainActivity : ComponentActivity() {

    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) Toast.makeText(this, "相机权限已授予", Toast.LENGTH_SHORT).show()
        else        Toast.makeText(this, "相机权限被拒绝", Toast.LENGTH_LONG).show()
        // 权限拒绝后 App 不崩溃(验收点)!
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // ...
        setContent {
            MaterialTheme {
                App(
                    prefs = UserPreferences.getInstance(this),
                    onRequestCamera = {
                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                    },
                )
            }
        }
    }
}''')
body(doc, '关键:registerForActivityResult 在 Activity 层声明(Composable 不能直接用);权限请求只在用户点相机按钮时触发(不在启动时申请);拒绝后只 Toast 不崩溃。')

h2(doc, '4.7 AndroidManifest.xml:INTERNET + CAMERA 权限')
code_lines(doc, '''<manifest>
    <uses-permission android:name="android.permission.INTERNET" />   <!-- 网络请求 -->
    <uses-permission android:name="android.permission.CAMERA" />     <!-- 运行时权限声明 -->
    <!-- ... application ... -->
</manifest>''')

# 五、结果
h1(doc, '五、结果')

h2(doc, '5.1 构建')
body(doc, 'BUILD SUCCESSFUL(assembleDebug),产出 app/build/outputs/apk/debug/app-debug.apk。Retrofit + Moshi + DataStore + OkHttp 依赖全部正确解析。')

h2(doc, '5.2 运行截图(验收四场景)')
shot_image(doc, 'lab4_01_network_success.png', '图 1  网络成功:NetworkTaskRepository 从 JSONPlaceholder 拉 200 条 todos,映射成 CourseTask 列表')
shot_image(doc, 'lab4_02_network_error.png', '图 2  断网/错误地址:FakeTaskRepository(errorMode=true) 抛异常,ViewModel catch 转 errorMessage,ErrorContent + Retry')
shot_image(doc, 'lab4_03_permission_request.png', '图 3  相机权限请求弹窗:点击相机按钮后才触发(不在启动时申请)')
shot_image(doc, 'lab4_04_permission_denied.png', '图 4  权限拒绝后 App 不崩溃:Toast 提示"相机权限被拒绝",界面仍可正常操作')

h2(doc, '5.3 接口响应样例(JSONPlaceholder /todos)')
code_lines(doc, '''HTTP 200 OK
GET https://jsonplaceholder.typicode.com/todos?probe=1
[
  {"userId":1,"id":1,"title":"delectus aut autem","completed":false},
  {"userId":1,"id":2,"title":"quis ut nam facilis et officia qui","completed":false},
  {"userId":1,"id":3,"title":"fugiat veniam minus","completed":false},
  ... 共 200 条 ...
]''')
body(doc, '注:已删去 userId 等非业务字段,只保留实验四关心的 id/title/completed。实际 NetworkTaskRepository 会取完整 200 条。', indent=False)

h2(doc, '5.4 验收点对照')
table(doc, ['验收点', '结果'], [
    ['网络成功和失败均有明确 UI', '成功→Content 态(200条);失败→ErrorContent+Retry,点重试可恢复'],
    ['数据访问仍通过 Repository', 'NetworkTaskRepository/FakeTaskRepository 都实现 TaskRepository 接口,ViewModel 只依赖接口'],
    ['不在 Composable 中直接读写 DataStore', 'UserPreferences 是唯一入口,Composable 只读 HomeUiState、通过 HomeAction 事件向上写'],
    ['权限拒绝后 App 不崩溃', 'onRequestPermissionResult 只 Toast 提示,不 throw/不 finish,截图 4 验证'],
    ['无敏感凭据提交到仓库', 'JSONPlaceholder 无密钥;OkHttp 日志 BASIC 级别不打响应体;.gitignore 排除 local.properties'],
], widths=[7, 9])

# 六、故障与调试
h1(doc, '六、故障与调试')
h3(doc, '故障:HomeScreen Preview MaterialTheme(darkColorScheme=...) 编译报错')
body(doc, '现象:HomeScreen Preview 里写 MaterialTheme(darkColorScheme = MaterialTheme.colorScheme),编译报"No parameter with name darkColorScheme found"。', bold=True)
numbered(doc, 1, '定位:MaterialTheme 构造函数只接受 colorScheme 参数(传 darkColorScheme() 或 lightColorScheme()),没有 darkColorScheme 这个命名参数。')
numbered(doc, 2, '修复:改成 MaterialTheme(colorScheme = darkColorScheme()),并加 import androidx.compose.material3.darkColorScheme。重新编译 BUILD SUCCESSFUL。')

h3(doc, '故障:模拟器启动后 ADB 显示 empty devices')
body(doc, '现象:emulator 启动后 adb devices 显示空列表,截图/安装全部失败。', bold=True)
numbered(doc, 1, '定位:headless 模式(-no-window)在当前环境启动速度慢,40 秒等待不够。')
numbered(doc, 2, '修复:去掉 -no-window 参数,模拟器带窗口启动,等待约 45 秒后 adb devices 才显示 emulator-5554 device。')

# 七、思考
h1(doc, '七、思考')
h2(doc, '7.1 Repository 接口复用的意义')
body(doc, '实验三定义的 TaskRepository 接口在实验四完全复用,NetworkTaskRepository 和 FakeTaskRepository 都实现这个接口。App 通过 overrideRepository 参数切换数据源,ViewModel/Route/Screen 一行代码不用改。这就是依赖倒置(DIP)的价值——高层模块(ViewModel)依赖抽象(接口),不依赖具体实现(FakeTaskRepository vs NetworkTaskRepository),数据源可自由替换。')

h2(doc, '7.2 DataStore 偏好驱动深色模式的单向数据流')
body(doc, 'App 层 collect darkModeFlow → 计算 MaterialTheme(colorScheme = if(darkMode) darkColorScheme() else lightColorScheme()) → Compose 重组。整个链路是单向的:DataStore(磁盘)→ Flow → StateFlow → MaterialTheme → UI 变化。ViewModel 不持有 Context(只持有 UserPreferences 引用),Composable 不直接调 DataStore API。')

h2(doc, '7.3 权限为什么不在启动时申请')
body(doc, 'Android 权限最佳实践:"只在用户明确需要某功能时才申请"。如果启动就申请相机权限,用户可能感到困惑("我只是想看看任务列表,为什么要相机权限?"),直接点拒绝。实验四遵循这个原则:启动时不申请,用户主动点相机按钮才申请,拒绝后只 Toast 提示。这样用户更愿意授权,也符合"最小权限"原则。')

h2(doc, '7.4 与实验三的比较')
code_lines(doc, '\n'.join([
    '             实验三                    实验四',
    '数据源  FakeTaskRepository(内存)   NetworkTaskRepository(Retrofit+JSONPlaceholder)',
    '持久化  无                          DataStore Preferences(深色模式/筛选)',
    '权限    无                          CAMERA 运行时权限(ActivityResultLauncher)',
    '安全    无                          OkHttp BASIC 日志 + 无密钥硬编码 + .gitignore',
    '验收新增 -                          网络成败 UI / DataStore 不在 Composable 直读 / 权限拒绝不崩 / 无敏感凭据',
]))

doc.save(OUT_PATH)
print('已生成:', OUT_PATH)
