# -*- coding: utf-8 -*-
"""
实验一 Word 报告生成脚本 v3 —— WPS 最大兼容版
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

REPORT_DIR = r'd:\rain_android\lab1\docs'
OUT_PATH = os.path.join(REPORT_DIR, '实验一报告_Kotlin_Compose基础界面.docx')

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
style_run(p.add_run('实验一  Kotlin + Compose 开发环境及基础界面'), cn='黑体', size=15, bold=True)

info = doc.add_table(rows=4, cols=4)
info.style = 'Table Grid'
info_rows = [
    ['姓名', '李春雨', '学号', '202305567128'],
    ['班级', '计科2班', '完成日期', '2026-09-14'],
    ['专业', '计算机科学与技术', '课程', '移动应用开发'],
    ['实验编号', '实验一', '实验名称', 'Kotlin + Compose 开发环境及基础界面'],
]
for i, row in enumerate(info_rows):
    for j, val in enumerate(row):
        cp = info.rows[i].cells[j].paragraphs[0]
        style_run(cp.add_run(val), size=10.5, bold=(j % 2 == 0))
doc.add_paragraph()

# 一、目标
h1(doc, '一、实验目标')
for i, g in enumerate([
    '验证 Android Studio、Android SDK、模拟器的开发环境，确认 Compose 项目可正常编译运行。',
    '掌握 Kotlin data class 的定义与空安全处理，理解可空类型 String? 与 Elvis 运算符的配合。',
    '熟悉 Jetpack Compose 基本组件（Card、Row、Column、Text、Icon）的用法，能编写可复用的 TaskCard Composable。',
    '理解 Compose 单向数据流的思想：Composable 不持有业务状态，数据从外层参数传入，事件通过回调向上传递。',
], 1):
    numbered(doc, i, g)

# 二、环境
h1(doc, '二、实验环境')
table(doc, ['项目', '信息'], [
    ['操作系统', 'Windows 11'],
    ['开发工具', 'Android Studio（Lab1Compose 工程，AGP 8.7.2）'],
    ['Android SDK', 'API 37（Android 16），路径 D:\\Android\\Sdk'],
    ['JDK', '17（Android Studio 自带 JBR 17）'],
    ['Kotlin', '2.0.21'],
    ['Compose BOM', '2024.10.01'],
    ['Android Gradle Plugin', '8.7.2'],
    ['Gradle', '8.10.2'],
    ['运行设备', 'Android 模拟器 Pixel 7（系统镜像 API 37.1，Google Play x86_64）'],
    ['构建结果', 'BUILD SUCCESSFUL in 26s，35 actionable tasks: 14 executed, 21 up-to-date'],
], widths=[4, 12])

# 三、设计
h1(doc, '三、设计')
h2(doc, '3.1 页面结构')
body(doc, '实验一只有一个主页面（MainActivity），内部使用 Scaffold + TopAppBar + LazyColumn 布局。LazyColumn 中每个条目是一个 TaskCard，展示一条 CourseTask 任务的标题、负责人、完成状态与优先级。')
body(doc, '页面结构简图：', indent=False, bold=True)
code_lines(doc, '\n'.join([
    'Scaffold',
    '+-- TopAppBar("实验一 · Compose 任务卡片")',
    '+-- LazyColumn(稳定 key = task.id)',
    '    +-- TaskCard[0]  (完成实验报告 / 张三 / 进行中 / 高优先级-红)',
    '    +-- TaskCard[1]  (提交代码到 Git / 李四 / 已完成 / 普通优先级)',
    '    +-- TaskCard[2]  (复习 Kotlin 空安全 / 未分配 / 进行中 / 低优先级-灰)',
]))

h2(doc, '3.2 数据流')
body(doc, '实验一是纯静态 UI，数据从顶层 List<CourseTask>（sampleTasks）单向流向 Composable，没有反向状态更新：')
code_lines(doc, '\n'.join([
    'sampleTasks (List<CourseTask>, 顶层常量)',
    '      |  传入',
    '      v',
    'AppScreen(tasks, onTaskClick)',
    '      |  items(tasks, key=id)',
    '      v',
    'TaskCard(title, owner, completed, priority, onClick)',
    '      |  点击时回调',
    '      v',
    'onTaskClick(task.id) -> Log.d（实验二会接 navController.navigate）',
]))
body(doc, '自问自答（实验指导书 H 部分）：', indent=False, bold=True)
for qa in [
    '数据在哪里？sampleTasks 是顶层 List<CourseTask> 常量，实验一只关心 UI，数据固定；实验三会把数据移到 ViewModel + Repository。',
    '状态在哪里？Composable 都是无状态的，数据通过参数从外层传入，符合 Compose 单向数据流的准备要求。',
    '事件从哪里来、到哪里去？TaskCard.onClick 是回调，由 AppScreen 的 onTaskClick 接收，目前只打日志；实验二会接 navController.navigate。',
    '错误在哪里处理？实验一数据都是本地不可变常量，无错误路径；实验三接入 Repository 后会出现 Loading/Error/Empty/Content 四态。',
]:
    bullet(doc, qa)

h2(doc, '3.3 类关系')
code_lines(doc, '\n'.join([
    'CourseTask (data class)',
    '    +-- id: Int',
    '    +-- title: String',
    '    +-- owner: String?        <- 可空，用 displayOwner() 安全转换',
    '    +-- completed: Boolean',
    '    +-- priority: Int',
    '',
    'displayOwner(task): String   <- 纯函数：owner?.trim()?.takeIf{...} ?: "未分配"',
    '',
    'TaskCard(@Composable)        <- 无状态展示组件',
    '    +-- 入参：title, owner, completed, priority, onClick',
    '    +-- 不持有状态，只根据入参渲染 UI',
]))

h2(doc, '3.4 关键决策')
for i, d in enumerate([
    'owner 声明为 String? 而非 String，显式表达"可能无人负责"的业务语义，用 Kotlin 空安全链加 Elvis 运算符处理 null，全程不使用 !!。',
    'TaskCard 不持有任何业务状态，数据通过参数传入，点击通过 onClick 回调向上传递，为实验二的导航解耦做准备。',
    '使用 LazyColumn 而非 Column，即使只有 3 条数据，也复用了实验二的列表结构，并使用稳定 key = task.id 提升重组性能。',
    '优先级用 MaterialTheme.colorScheme（红/默认/灰）而非硬编码颜色，字号用 titleMedium / bodySmall，符合拓展任务要求。',
], 1):
    numbered(doc, i, d)

# 四、实现
h1(doc, '四、实现')
LAB1 = r'd:\rain_android\lab1'
course_task_kt = read_code(os.path.join(LAB1, r'app\src\main\java\edu\example\mobilecourse\lab1\data\CourseTask.kt'))
task_card_kt = read_code(os.path.join(LAB1, r'app\src\main\java\edu\example\mobilecourse\lab1\ui\TaskCard.kt'))
main_activity_kt = read_code(os.path.join(LAB1, r'app\src\main\java\edu\example\mobilecourse\lab1\MainActivity.kt'))

h2(doc, '4.1 CourseTask data class 与 displayOwner 空安全处理')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab1/data/CourseTask.kt', indent=False)
code_lines(doc, course_task_kt[course_task_kt.index('data class'):course_task_kt.index('val sampleTasks')].strip())
body(doc, '空安全解释链：', indent=False, bold=True)
numbered(doc, 1, 'task.owner?.trim() —— owner 为 null 时整条链返回 null，后面不再执行；')
numbered(doc, 2, '?.takeIf { it.isNotEmpty() } —— trim 后如果是空字符串，返回 null；')
numbered(doc, 3, '?: "未分配" —— Elvis 运算符，左侧为 null 时取右侧默认值。')

h2(doc, '4.2 TaskCard 可复用 Composable（使用 4 种基本组件）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab1/ui/TaskCard.kt', indent=False)
code_lines(doc, task_card_kt[task_card_kt.index('@Composable'):task_card_kt.index('/**\n * Preview 1')].strip())
body(doc, '用到的基本组件（4 种，满足"至少 3 种"要求）：', indent=False, bold=True)
numbered(doc, 1, 'Card —— Material3 卡片容器，自带 onClick（实验二接导航）；')
numbered(doc, 2, 'Row / Column —— 线性布局；')
numbered(doc, 3, 'Text —— 文字；')
numbered(doc, 4, 'Icon —— 图标（完成状态图标 + 负责人图标）。')

h2(doc, '4.3 MainActivity 用 LazyColumn 展示 3 个 TaskCard')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab1/MainActivity.kt', indent=False)
code_lines(doc, main_activity_kt[main_activity_kt.index('LazyColumn'):main_activity_kt.index('Preview')].strip())
body(doc, '关键点：', indent=False, bold=True)
bullet(doc, '用 displayOwner(task) 把 owner=null 转为"未分配"；')
bullet(doc, 'key = { it.id } 给 LazyColumn 稳定键，提升重组性能（实验二会再强调）；')
bullet(doc, '实验一只有 3 条数据，但 LazyColumn 能平滑扩展到上百条（实验二验收点）。')

h2(doc, '4.4 Preview（3 个，可独立预览）')
body(doc, '文件：app/src/main/java/edu/example/mobilecourse/lab1/ui/TaskCard.kt', indent=False)
bullet(doc, 'PreviewTaskCardInProgress：进行中状态（张三、未完成、普通优先级）；')
bullet(doc, 'PreviewTaskCardCompleted：已完成状态（李四、completed=true）；')
bullet(doc, 'PreviewTaskCardUnassigned：未分配状态（owner=null，显示"未分配"，低优先级灰色标题）。')

# 五、结果
h1(doc, '五、结果')
h2(doc, '5.1 成功截图')
shot_placeholder(doc, '图 1  MainActivity 运行截图（3 张 TaskCard 列表，含进行中/已完成/未分配三种状态）')
shot_placeholder(doc, '图 2  TaskCard Preview 截图（进行中 + 已完成 + 未分配三个 Preview 并列）')
shot_placeholder(doc, '图 3  模拟器实际运行截图（可看到桌面绿色应用图标）')

h2(doc, '5.2 边界与错误状态')
table(doc, ['边界/错误状态', '表现'], [
    ['owner = null', 'displayOwner 返回"未分配"，不会崩溃'],
    ['owner = "   "（全空格）', 'trim() 后 isNotEmpty() 为 false，返回"未分配"'],
    ['优先级 priority = 1', '标题显示为 MaterialTheme.colorScheme.error（红色）'],
    ['优先级 priority = 3', '标题显示为 MaterialTheme.colorScheme.outline（灰色）'],
    ['completed = true', '左侧图标为 CheckCircle，颜色为主色'],
    ['completed = false', '左侧图标为 RadioButtonUnchecked，颜色为 outline'],
], widths=[6, 10])

# 六、故障
h1(doc, '六、故障与调试')
body(doc, '本次实验过程中遇到三个真实故障，均已解决。', indent=False, bold=True)

h2(doc, '故障一：模拟器系统镜像下载超时（Read timed out）')
h3(doc, '现象')
body(doc, '在 Device Manager 中创建 Pixel 7 模拟器时，SDK Component Installer 下载 16 KB Page Size Google Play Intel x86_64 Atom System Image（API 37.1，共 2.0 GB）到 2% 后失败，日志报 "An error occurred while preparing SDK package ... Read timed out."，安装失败。')
h3(doc, '定位')
body(doc, '查看下载地址为 https://dl.google.com/ 下的 x86_64-playstore-ps16k-37.1_r09.zip。用 Test-NetConnection 测试 dl.google.com 的 443 端口可达，但大文件传输中途断流；尝试清华、阿里云等国内镜像，均无该 API 37.1 小版本镜像（返回 404）。')
h3(doc, '原因')
body(doc, '国内直连 Google 官方下载服务器不稳定，长连接传输 2GB 大文件时被中途重置；而该 37.1 小版本镜像较新，国内镜像尚未同步。')
h3(doc, '修复')
body(doc, '连接 Cisco AnyConnect VPN（日本专线，全局模式）后重新下载，SDK 安装器支持断点续传，下载从 2% 继续，最终 100% 完成并解压，模拟器成功开机。')

h2(doc, '故障二：Failed to find Platform SDK with path: platforms;android-37')
h3(doc, '现象')
body(doc, '模拟器已开机，点 Run 后 Build 失败，Build Output 报错 "Failed to find Platform SDK with path: platforms;android-37"，构建停在 :app 阶段。')
h3(doc, '定位')
body(doc, '查看 D:\\Android\\Sdk\\platforms 目录，发现平台包实际安装在 android-37.0 目录，而不是 AGP 期望的 android-37；进一步查看该目录下 source.properties 与 package.xml，发现 AndroidVersion.ApiLevel=37.0、api-level 为 37.0、localPackage path 为 platforms;android-37.0，即该平台以"Minor API Level 37.0"的新格式安装。')
h3(doc, '原因')
body(doc, 'Android 16 引入 Minor API Level 机制，新版 SDK 安装器把平台目录命名为 android-37.0 并把 api-level 记为 37.0；而项目使用的 AGP 8.7.2 仍按传统整数 API 级别查找名为 android-37、api-level 为整数 37 的平台包，两者命名与元数据不匹配，导致即使文件已下载仍判定平台缺失。')
h3(doc, '修复')
body(doc, '将 platforms 下的 android-37.0 整目录复制为 android-37，并在副本中修改三处元数据——package.xml 的 localPackage path 改为 platforms;android-37、api-level 改为 37，source.properties 的 AndroidVersion.ApiLevel 改为 37（保留原 android-37.0 目录不动）；再执行 gradlew --stop 结束缓存了旧扫描结果的 Gradle Daemon，重新 Run 后平台被正确识别，Build 通过。')

h2(doc, '故障三：AAPT error: resource mipmap/ic_launcher 找不到')
h3(doc, '现象')
body(doc, '平台问题解决后，Build 又报 4 个 AAPT 错误，均指向 AndroidManifest.xml 第 6、8 行的 @mipmap/ic_launcher 与 @mipmap/ic_launcher_round 资源找不到。')
h3(doc, '定位')
body(doc, '检查 app/src/main/res 目录，只有 values 文件夹（colors.xml、strings.xml、themes.xml），没有任何 mipmap 或图标资源。')
h3(doc, '原因')
body(doc, '工程骨架生成时只创建了文本资源，缺少启动图标 PNG/XML；Manifest 引用了不存在的资源，AAPT 链接阶段直接失败。')
h3(doc, '修复')
body(doc, '在 res 下新增 mipmap-anydpi-v26 自适应图标（ic_launcher.xml、ic_launcher_round.xml，引用 adaptive-icon），在 drawable 下新增前后景矢量图（ic_launcher_background.xml 绿色底、ic_launcher_foreground.xml 白色任务卡加对勾），并在 mipmap 目录放 API 24-25 的回退矢量图标。全部用 XML 矢量图实现，无需二进制 PNG。重新 Run 后 BUILD SUCCESSFUL。')

# 七、思考
h1(doc, '七、思考')
h2(doc, '7.1 Kotlin 空安全的作用')
body(doc, '在 Android 开发中，空指针异常（NPE）是最常见的崩溃原因之一。Kotlin 在类型系统层面区分 String（非空）与 String?（可空），强制开发者在编译期处理 null 情况。本实验中 owner 声明为 String?，调用时必须用 ?. 安全调用或显式非空断言 !!。displayOwner 函数使用 owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未分配" 的安全调用链，既处理了 null 又处理了空白字符串，全程避免了 !! 带来的运行时崩溃风险。')
h2(doc, '7.2 Composable 无状态与有状态的区别')
body(doc, 'Compose 推荐将状态提升（State Hoisting）到上层 Composable。本实验的 TaskCard 完全无状态：title、owner、completed 等全部由参数传入，onClick 是回调。这样做的好处是 TaskCard 可复用、可独立 Preview、易于测试。实验三会进一步把状态从 Composable 提升到 ViewModel，通过 StateFlow 向下传递，形成完整的单向数据流（UDF）。')
h2(doc, '7.3 data class 与普通 class 的区别')
body(doc, 'Kotlin 的 data class 自动生成 equals()、hashCode()、toString()、componentN() 和 copy() 方法，适合用作数据载体。CourseTask 作为 UI 数据模型，用 data class 可以方便地比较两个任务是否相等（Compose 重组时依赖 equals 判断状态是否变化），也可以用 copy() 生成只修改了部分字段的新实例，这在实验二的不可变状态更新中会用到。')

# 附录
h1(doc, '附录：提交物清单')
table(doc, ['提交物', '状态'], [
    ['源代码', '已提交至 https://github.com/lcyspring/Android 仓库 lcy 分支的 lab1/ 目录'],
    ['Git 提交节点', '起始提交已完成；主要功能、最终修复两个节点待补充'],
    ['实验报告', '本报告'],
    ['运行截图', '3 张，待插入第五章'],
], widths=[4, 12])

# ================= 保存 =================
os.makedirs(REPORT_DIR, exist_ok=True)
saved = OUT_PATH
try:
    doc.save(OUT_PATH)
except PermissionError:
    saved = OUT_PATH.replace('.docx', '_v3.docx')
    doc.save(saved)

# ================= schema 顺序自检 =================
PPR_ORDER = ['pStyle','keepNext','keepLines','pageBreakBefore','framePr','widowControl','numPr',
    'suppressLineNumbers','pBdr','shd','tabs','suppressAutoHyphens','kinsoku','wordWrap',
    'overflowPunct','topLinePunct','autoSpaceDE','autoSpaceDN','bidi','adjustRightInd',
    'snapToGrid','spacing','ind','contextualSpacing','mirrorIndents','suppressOverlap','jc',
    'textDirection','textAlignment','textboxTightWrap','outlineLvl','divId','cnfStyle',
    'rPr','sectPr','pPrChange']
RPR_ORDER = ['rStyle','rFonts','b','bCs','i','iCs','caps','smallCaps','strike','dstrike',
    'outline','shadow','emboss','imprint','noProof','snapToGrid','vanish','webHidden','color',
    'spacing','w','kern','position','sz','szCs','highlight','u','effect','bdr','shd',
    'fitText','vertAlign','rtl','cs','em','lang','eastAsianLayout','specVanish','oMath']

def check_order(parent, order, label, problems):
    tags = [child.tag.split('}')[1] for child in parent if child.tag.startswith('{' + W_NS + '}')]
    idxs = [order.index(t) for t in tags if t in order]
    if idxs != sorted(idxs):
        problems.append(f'{label} 子元素顺序错误: {tags}')

import zipfile
from lxml import etree
with zipfile.ZipFile(saved) as z:
    root = etree.fromstring(z.read('word/document.xml'))
problems = []
shd_count = 0
for el in root.iter('{%s}shd' % W_NS):
    shd_count += 1
for ppr in root.iter('{%s}pPr' % W_NS):
    check_order(ppr, PPR_ORDER, 'w:pPr', problems)
for rpr in root.iter('{%s}rPr' % W_NS):
    check_order(rpr, RPR_ORDER, 'w:rPr', problems)

print(f'OK 报告已生成: {saved}')
print(f'文件大小: {os.path.getsize(saved)} 字节')
print(f'自检: w:shd 数量 = {shd_count} (应为 0)')
print(f'自检: schema 顺序问题 = {len(problems)}')
for pmsg in problems:
    print('  [问题]', pmsg)
# 读回验证
d2 = Document(saved)
print(f'自检: 读回段落数 = {len(d2.paragraphs)}, 表格数 = {len(d2.tables)}')
