# -*- coding: utf-8 -*-
"""
实验五 Word 报告生成脚本 —— WPS 最大兼容版(沿用实验三/四已验证脚本风格)
主题:微信小程序开发(原生)。运行方式:沙箱验证(Node 模拟 wx 运行时)。
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

REPORT_DIR = r'd:\rain_android\lab5-miniprogram\docs'
OUT_PATH = os.path.join(REPORT_DIR, '实验五报告_微信小程序开发.docx')
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

def body(doc, text, indent=True, bold=False):
    p = doc.add_paragraph()
    if indent:
        p.paragraph_format.first_line_indent = Cm(0.74)
    style_run(p.add_run(text), size=10.5, bold=bold)
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

def shot_image(doc, filename, caption, width_cm=13):
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
style_run(p.add_run('实验五  微信小程序开发(原生)'), cn='黑体', size=15, bold=True)

info = doc.add_table(rows=4, cols=4); info.style = 'Table Grid'
for i, row in enumerate([
    ['姓名', '李春雨', '学号', '202305567128'],
    ['班级', '计科2班', '完成日期', '2026-09-28'],
    ['专业', '计算机科学与技术', '课程', '移动应用开发'],
    ['实验编号', '实验五', '实验名称', '微信小程序开发(原生)'],
]):
    for j, val in enumerate(row):
        cp = info.rows[i].cells[j].paragraphs[0]
        style_run(cp.add_run(val), size=10.5, bold=(j % 2 == 0))
doc.add_paragraph()

# 一、目标
h1(doc, '一、实验目标')
for i, g in enumerate([
    '搭建原生微信小程序工程(app.json 注册 index/detail 两个页面),理解 WXML/WXSS/JS/JSON 四文件结构。',
    '把 wx.request 统一封装成 Promise 风格的 request(),页面只调用 api 层,验收"网络代码不在多个页面复制 wx.request"。',
    '列表页用 wx:for 渲染数据,维护 isLoading/todos/error 三个状态;点击列表项 wx.navigateTo 携带 id 跳转详情页。',
    '详情页 onLoad(options) 读取 id 再请求单条数据;实现模拟错误地址验证失败提示与重试。',
    '对照 Android Compose 与小程序的异同,理解二者"数据驱动 UI"的相似思想。',
], 1):
    numbered(doc, i, g)

# 二、环境
h1(doc, '二、实验环境')
table(doc, ['项目', '信息'], [
    ['操作系统', 'Windows 11'],
    ['目标框架', '微信小程序(原生 WXML/WXSS/JS/JSON),基础库 style v2'],
    ['开发工具', '微信开发者工具 Stable 2.02.2608060(已登录,模拟器 iPhone 12/13)'],
    ['AppID', 'wx1e7b52dcebde8b0f(真实小程序 AppID)'],
    ['辅助验证', 'Node.js v24.12.0 沙箱(模拟 Page/App/wx 运行时,桥接真实网络)'],
    ['网络 API', 'JSONPlaceholder(https://jsonplaceholder.typicode.com,公开免费,无密钥)'],
    ['数据源', '与实验四 Android 端一致(/todos 列表 + /todos/{id} 详情)'],
    ['报告工具', 'python-docx 1.2.0(WPS 兼容版式)'],
    ['验证结果', '开发者工具模拟器三态截图齐全;沙箱 18/18 断言全部通过'],
], widths=[4, 12])

body(doc, '说明:工程先以课程指导书中的游客 AppID(touristappid)配置,命令行与模拟器均无法打开;'
          '换用真实小程序 AppID 后项目成功导入并在开发者工具模拟器中运行,'
          '列表/详情/错误三种状态均已在模拟器中实际验证并截图。'
          '在排查期间,另用 Node 沙箱模拟小程序运行时对页面逻辑做了端到端断言,'
          '作为补充验证手段(见第五节末)。', indent=True)

# 三、设计
h1(doc, '三、设计')

h2(doc, '3.1 项目结构')
body(doc, '工程采用"全局 + 页面 + 工具层"三档划分,网络访问统一收敛到 utils 层。')
shot_image(doc, 'lab5_fig_structure.png', '图3-1  lab5-miniprogram 项目结构', width_cm=13)

h2(doc, '3.2 分层与数据流')
body(doc, '页面层(index/detail)不直接写 wx.request,而是调用 api 层的语义化方法;'
          'api 层再委托统一的 request() 封装。状态变化通过 this.setData 驱动视图刷新,'
          '对应 Compose 中 State -> UI 的自动重组。')
code_lines(doc, '\n'.join([
    'index.wxml / detail.wxml      (视图层:  wx:for 列表、条件渲染)',
    '   ↑ 数据绑定 {{todos}} / {{todo}}',
    'index.js   / detail.js        (页面层:  Page({ data, onLoad, onTapItem... }))',
    '   ↓ getTodos() / getTodoById(id)',
    'utils/api.js                  (业务 API 层)',
    '   ↓ request({ url, baseUrl })',
    'utils/request.js              (统一封装: wx.request -> Promise)',
    '   ↓ BASE_URL / ERROR_BASE_URL',
    'utils/config.js               (地址常量,唯一出现一次)',
]))

h2(doc, '3.3 页面状态机')
body(doc, '列表页与详情页都采用三态模型:Loading(isLoading=true)、'
          'Content(todos/todo 有值)、Error(error 非空)。'
          '进入加载即置 Loading,成功填数据,失败填错误文案并提供重试。')

# 四、实现
h1(doc, '四、实现')

h2(doc, '4.1 统一网络封装(utils/request.js)')
body(doc, '把回调式的 wx.request 包成 Promise:HTTP 2xx resolve 业务数据,'
          '其余 reject Error;fail(断网/域名解析失败/超时)也统一 reject。页面用 .then/.catch 接收。')
code_lines(doc, '\n'.join([
    'function request({ url, method = \'GET\', data = {}, baseUrl }) {',
    '  const fullUrl = (baseUrl || BASE_URL) + url',
    '  return new Promise((resolve, reject) => {',
    '    wx.request({',
    '      url: fullUrl, method, data, timeout: 10000,',
    '      success: (res) => {',
    '        if (res.statusCode >= 200 && res.statusCode < 300) resolve(res.data)',
    '        else reject(new Error(\'HTTP \' + res.statusCode))',
    '      },',
    '      fail: (err) => reject(new Error((err && err.errMsg) || \'网络请求失败\'))',
    '    })',
    '  })',
    '}',
]))

h2(doc, '4.2 列表页(步骤 30/31/33)')
body(doc, 'onLoad 触发 loadTodos;setData 维护三态;onTapItem 用 wx.navigateTo 携带 id 跳转;'
          'onSimulateError 走错误基址验证失败提示。')
code_lines(doc, '\n'.join([
    'Page({',
    '  data: { isLoading: false, todos: [], error: \'\' },',
    '  onLoad() { this.loadTodos(false) },',
    '  loadTodos(useErrorUrl) {',
    '    this.setData({ isLoading: true, error: \'\', todos: [] })',
    '    const promise = useErrorUrl',
    '      ? request({ url: \'todos\', baseUrl: ERROR_BASE_URL })',
    '      : getTodos()',
    '    promise.then((list) => this.setData({',
    '      isLoading: false, todos: Array.isArray(list) ? list.slice(0, 100) : []',
    '    })).catch((err) => this.setData({',
    '      isLoading: false, error: (err && err.message) || \'未知网络错误\'',
    '    }))',
    '  },',
    '  onTapItem(e) {',
    '    const id = e.currentTarget.dataset.id',
    '    wx.navigateTo({ url: \'/pages/detail/detail?id=\' + id })',
    '  }',
    '})',
]))

h2(doc, '4.3 视图层 wx:for 与条件渲染(index.wxml)')
code_lines(doc, '\n'.join([
    '<!-- 三态:Loading / Error / Content -->',
    '<view wx:if="{{isLoading}}" class="state">加载中…</view>',
    '<view wx:elif="{{error}}" class="state error">',
    '  <text>{{error}}</text>',
    '  <button bindtap="onRetry">重试</button>',
    '</view>',
    '<scroll-view wx:else scroll-y class="list">',
    '  <view wx:for="{{todos}}" wx:key="id" class="card"',
    '        data-id="{{item.id}}" bindtap="onTapItem">',
    '    <text class="title">{{item.title}}</text>',
    '    <text class="sub">userId={{item.userId}} · {{item.completed ? "已完成" : "未完成"}}</text>',
    '  </view>',
    '</scroll-view>',
]))

h2(doc, '4.4 详情页(步骤 32)')
body(doc, 'onLoad(options) 读取列表页传来的 id,再调 getTodoById(id) 拉取单条数据。')
code_lines(doc, '\n'.join([
    'onLoad(options) {',
    '  const id = options && options.id',
    '  if (!id) { this.setData({ isLoading: false, error: \'缺少任务 id 参数\' }); return }',
    '  this.setData({ id })',
    '  this.loadDetail(id)',
    '}',
]))

# 五、结果
h1(doc, '五、实验结果(开发者工具模拟器)')
body(doc, '工程以真实 AppID 在微信开发者工具模拟器中运行,三种状态全部实际验证通过。')

h2(doc, '5.1 列表页(Content 态)')
body(doc, '进入首页即加载 JSONPlaceholder 的 /todos,共 200 条截取前 100 条渲染;'
          '每张卡片显示序号、标题、完成状态徽标与"查看详情"入口,右上角红色按钮用于模拟错误地址。')
shot_image(doc, 'lab5_run_list_phone.png', '图5-1  列表页:网络成功,wx:for 渲染 100 条任务', width_cm=7)

h2(doc, '5.2 详情页(点击跳转)')
body(doc, '点击列表项触发 wx.navigateTo 携带 id 跳转,详情页 onLoad(options) 读取 id 后调 '
          'getTodoById 拉取单条数据,显示任务 id、标题、所属用户与完成状态。')
shot_image(doc, 'lab5_run_detail_phone.png', '图5-2  详情页:options.id=1,单条数据渲染成功', width_cm=7)

h2(doc, '5.3 错误态(模拟错误地址)')
body(doc, '点击"模拟错误地址"后,请求走 ERROR_BASE_URL(DNS 必然解析失败),wx.request 进入 fail 分支,'
          '统一封装 reject 后页面 catch 到错误并渲染失败提示与重试按钮,列表清空(共 0 条)。')
shot_image(doc, 'lab5_run_error_phone.png', '图5-3  错误态:加载失败 + request:fail 提示 + 重试按钮', width_cm=7)

h2(doc, '5.4 补充:沙箱自动化断言')
body(doc, '排障期间另用 Node 模拟小程序运行时(Page/App/wx.request/wx.navigateTo),'
          '把 wx.request 桥接为真实 fetch,对页面逻辑做了 18 项端到端断言,全部通过。'
          '覆盖:列表加载、跳转传参、详情加载、错误地址失败、重试恢复。')
shot_image(doc, 'lab5_fig_sandbox.png', '图5-4  沙箱验证运行结果(18/18 断言通过)', width_cm=14)

# 六、Android vs 小程序对照表
h1(doc, '六、Android(Compose)与微信小程序对照表')
table(doc, ['维度', 'Android(实验四 Compose)', '微信小程序(本实验)'], [
    ['UI 描述', 'Kotlin + @Composable 函数,声明式', 'WXML 模板 + 数据绑定 {{}},声明式'],
    ['状态驱动', 'ViewModel StateFlow + collectAsState,重组刷新', 'Page.data + this.setData,自动刷新视图'],
    ['列表渲染', 'LazyColumn { items(list) }', 'wx:for="{{todos}}" wx:key="id"'],
    ['页面导航', 'NavHost + NavController.navigate', 'wx.navigateTo({ url }) / wx.navigateBack'],
    ['网络请求', 'Retrofit + Moshi + OkHttp', 'wx.request 统一封装为 Promise'],
    ['条件渲染', 'if (state.isLoading) { ... } else { ... }', 'wx:if / wx:elif / wx:else'],
    ['配置入口', 'AndroidManifest.xml + build.gradle', 'app.json + project.config.json'],
    ['异步模型', 'Kotlin 协程 suspend/await', 'Promise then/catch(或 async/await)'],
], widths=[2.8, 6.2, 6.2])

body(doc, '核心相似点:二者都是"数据驱动 UI"。Compose 中 State 变化触发重组,'
          '小程序中 setData 变化触发视图层重渲染;开发者都只描述"状态长什么样",'
          '框架负责 diff 与刷新,无需手动操作 DOM/View 树。', indent=True)

# 七、故障与调试
h1(doc, '七、故障与调试')
for i, item in enumerate([
    '故障:命令行 cli open --project 报"不存在此 AppID(code 10)"。排查:指导书给出的游客 AppID '
    '(touristappid)在当前工具版本中需通过服务端校验,直接使用会被拒绝;project.config.json 中把 '
    'appid 置空同样报 code 10。解决:改用真实小程序 AppID(wx1e7b52dcebde8b0f)后,'
    'CLI 返回 ✔ open,模拟器正常编译运行。',
    '故障:创建项目对话框中"测试号"链接与"创建"按钮点击无响应。排查:这两个控件依赖在线账号服务返回,'
    '受限网络下按钮一直处于等待态;项目列表页"导入"入口点击后目录选择框也只读。'
    '结论:测试号通道不可用,真实 AppID 是唯一可靠路径。',
    '排障中的过渡方案:为不阻塞进度,先用 Node 搭建沙箱模拟小程序运行时(Page/App/wx),'
    '把 wx.request 桥接为真实 fetch,对页面逻辑做了 18 项端到端断言全部通过;'
    '拿到真实 AppID 后再回到开发者工具模拟器完成三态截图。沙箱断言作为补充验证保留在源码中 '
    '(sandbox_test.js,node sandbox_test.js 可复现)。',
    '调试细节:Node fetch 对 DNS 解析失败抛出的错误结构与 wx.request 不同(没有 errMsg 字段),'
    '需在 Mock 层包装为 { errMsg } 结构,页面 catch 才能拿到统一文案;'
    '这与真机 fail 回调的行为保持一致。',
    '经验:wx.request 的 fail 回调只表示"请求根本没发出去/没收到响应"(断网、DNS 失败、超时),'
    'HTTP 4xx/5xx 仍走 success 回调,需要按 statusCode 自行判断——统一封装里已处理这一差异。',
], 1):
    numbered(doc, i, item)

# 八、思考
h1(doc, '八、思考与收获')
body(doc, '本实验把实验四的网络请求思想迁移到了微信小程序平台。两者在"分层收敛网络访问、'
          '用状态机管理加载/成功/失败、数据驱动 UI"上高度一致,差异主要在技术栈形态。')
body(doc, '小程序的 wx.request 是回调式 API,直接多处调用会导致回调地狱与代码分散;'
          '统一封装成 Promise 后,页面用 then/catch 表达异步流,与 Compose 端的协程在可读性上对齐。'
          '这也印证了验收点"网络代码不在多个页面复制 wx.request"的意义:收口便于统一加超时、'
          '统一错误文案、未来统一换基址。')
body(doc, 'setData 与 Compose 重组的思想同源,但小程序的 setData 需要显式调用且跨逻辑层/视图层通信,'
          '频繁小更新有性能开销;Compose 的状态订阅更细粒度。理解这种异同,有助于在多端开发中'
          '复用同一套架构心智模型。')

doc.save(OUT_PATH)
print('SAVED:', OUT_PATH)
