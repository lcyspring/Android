# -*- coding: utf-8 -*-
"""
实验六 Word 报告生成脚本 —— WebRTC 实时通信
"""
import os
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn

REPORT_DIR = r'd:\rain_android\lab6-webrtc\docs'
OUT_PATH = os.path.join(REPORT_DIR, '实验六报告_WebRTC实时通信.docx')
SCREENSHOT_DIR = os.path.join(REPORT_DIR, 'screenshots')

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
    style_run(p.add_run(text), cn='黑体', size=16, bold=True)

def h2(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(12)
    p.paragraph_format.space_after = Pt(6)
    style_run(p.add_run(text), cn='黑体', size=13, bold=True)

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
    style_run(p2.add_run(caption), cn='楷体', size=9, color=RGBColor(0x77, 0x77, 0x77))

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
style_run(p.add_run('实验六  WebRTC 实时通信'), cn='黑体', size=15, bold=True)

info = doc.add_table(rows=4, cols=4); info.style = 'Table Grid'
for i, row in enumerate([
    ['姓名', '李春雨', '学号', '202305567128'],
    ['班级', '计科2班', '完成日期', '2026-09-30'],
    ['专业', '计算机科学与技术', '课程', '移动应用开发'],
    ['实验编号', '实验六', '实验名称', 'WebRTC 实时通信'],
]):
    for j, val in enumerate(row):
        cp = info.rows[i].cells[j].paragraphs[0]
        style_run(cp.add_run(val), size=10.5, bold=(j % 2 == 0))
doc.add_paragraph()

# 一、目标
h1(doc, '一、实验目标')
for i, g in enumerate([
    '获得摄像头/麦克风权限，理解 MediaStream 的获取与绑定过程。',
    '理解 RTCPeerConnection 的建立过程，包括 createOffer/createAnswer、setLocalDescription/setRemoteDescription。',
    '通过 WebSocket(Socket.io) 观察 Offer/Answer/ICE candidate 的信令交换流程。',
    '理解安全上下文(HTTPS/WSS)、权限策略与 STUN/TURN 的作用边界。',
    '在 onicecandidate/ontrack 回调中增加自定义日志，区分信令各阶段。',
], 1):
    numbered(doc, i, g)

# 二、环境
h1(doc, '二、实验环境')
table(doc, ['项目', '信息'], [
    ['操作系统', 'Windows 11'],
    ['运行环境', 'Node.js v24.12.0 + Express 4.18 + Socket.io 3.0'],
    ['浏览器', 'Chromium 内核浏览器(支持 WebRTC API)'],
    ['信令服务器', 'Express + Socket.io(localhost:8181,仅转发 SDP/ICE)'],
    ['WebRTC 配置', 'STUN: stun:ss-turn1.xirsys.com; TURN: ss-turn1.xirsys.com'],
    ['前端依赖', 'Socket.io 3.0.4 客户端 + jQuery 3.4.1(CDN)'],
    ['验证方式', '同机两个浏览器标签页完成 P2P 通话'],
    ['报告工具', 'python-docx 1.2.0(WPS 兼容版式)'],
], widths=[4, 12])

# 三、设计
h1(doc, '三、设计')

h2(doc, '3.1 项目结构')
body(doc, '工程分为信令服务器(server.js)和前端页面(public/index.html)两部分。'
          '信令服务器仅负责转发协商消息，不参与音视频传输。')
code_lines(doc, '\n'.join([
    'lab6-webrtc/',
    '├── server.js          # Express + Socket.io 信令服务器',
    '│                        转发: new user / SDP / ICE candidate',
    '├── package.json',
    '├── public/',
    '│   └── index.html     # 前端: getUserMedia + RTCPeerConnection + Socket.io',
    '└── docs/              # 报告 + 截图 + 生成脚本',
]))

h2(doc, '3.2 A/B/Signaling 三者交互流程')
body(doc, 'WebRTC 通话需要信令服务器协调双方交换 SDP(Session Description Protocol)和 ICE candidate，'
          '但信令服务器本身不传输音视频——媒体流走 P2P 直连。')
shot_image(doc, 'lab6_fig_signaling.png', '图3-1  A/B/Signaling 三者交互流程图', width_cm=14)

h2(doc, '3.3 核心对象职责')
table(doc, ['对象', '职责', '是否传输媒体'], [
    ['getUserMedia', '获取本地摄像头/麦克风 MediaStream', '否(仅获取)'],
    ['RTCPeerConnection', '建立 P2P 连接，协商编码器/传输音视频', '是(P2P 直连)'],
    ['Socket.io(信令)', '转发 SDP offer/answer 和 ICE candidate', '否(仅转发协商消息)'],
    ['STUN 服务器', '帮助端点发现自己的公网地址(NAT 穿透)', '否(仅地址发现)'],
    ['TURN 服务器', '在 P2P 不通时作为中继转发媒体流', '是(中继)'],
], widths=[4, 8, 3])

# 四、实现
h1(doc, '四、实现')

h2(doc, '4.1 信令服务器(server.js)')
body(doc, '信令服务器用 Express 提供静态页面，用 Socket.io 转发四类消息：'
          '新用户上线、确认连接、SDP 交换、ICE candidate 交换。')
code_lines(doc, '\n'.join([
    'io.on(\'connection\', (socket) => {',
    '    // 1) 新用户上线，广播给其他人',
    '    socket.on(\'new user greet\', (data) => {',
    '        socket.broadcast.emit(\'need connect\', data)',
    '    })',
    '    // 2) 转发 SDP(offer / answer)',
    '    socket.on(\'sdp\', (data) => {',
    "        io.to(data.to).emit('sdp', data)  // 只转发不处理",
    '    })',
    '    // 3) 转发 ICE candidate',
    '    socket.on(\'ice candidates\', (data) => {',
    '        io.to(data.to).emit(\'ice candidates\', data)',
    '    })',
    '})',
]))

h2(doc, '4.2 获取本地媒体(步骤 36)')
body(doc, '使用 navigator.mediaDevices.getUserMedia 获取音视频流，绑定到 localVideo 元素。'
          '权限被拒绝时弹出 alert 提示。')
code_lines(doc, '\n'.join([
    'function InitCamera() {',
    '    getUserMedia({ video: true, audio: true }, (stream) => {',
    '        localStream = stream;',
    '        localVideoElm.srcObject = stream;',
    '    }, (err) => {',
    '        alert(\'摄像头/麦克风权限被拒绝，请允许后刷新\')',
    '    })',
    '}',
]))

h2(doc, '4.3 RTCPeerConnection 与信令交换(步骤 38)')
body(doc, '呼叫方创建 Offer 并通过信令服务器发送；被叫方收到后创建 Answer 回传。'
          '双方交换 ICE candidate 以找到可连通路径。')
code_lines(doc, '\n'.join([
    'pc[parterName] = new RTCPeerConnection(iceServer)',
    'localStream.getTracks().forEach(track => pc[parterName].addTrack(track, localStream))',
    '',
    '// 呼叫方: createOffer -> setLocalDescription -> 通过信令发送',
    'pc[parterName].onnegotiationneeded = () => {',
    '    pc[parterName].createOffer().then(offer => pc[parterName].setLocalDescription(offer))',
    '        .then(() => socket.emit(\'sdp\', { description: pc[parterName].localDescription, to: parterName }))',
    '}',
    '',
    '// 被叫方收到 offer: setRemoteDescription -> createAnswer -> setLocalDescription -> 回传',
    'pc[data.sender].setRemoteDescription(desc).then(() => pc[data.sender].createAnswer())',
    '    .then(answer => pc[data.sender].setLocalDescription(answer))',
    '    .then(() => socket.emit(\'sdp\', { description: pc[data.sender].localDescription, to: data.sender }))',
]))

h2(doc, '4.4 自定义日志(步骤 39)')
body(doc, '在 onicecandidate 和 ontrack 回调中添加了带颜色和步骤编号的自定义日志，'
          '便于在控制台区分 ICE 协商、媒体接收等不同阶段。')
code_lines(doc, '\n'.join([
    'pc[parterName].onicecandidate = ({ candidate }) => {',
    '    if (candidate) {',
    '        console.log(\'[步骤39-ICE] onicecandidate 触发，候选地址: \' + candidate.candidate)',
    '        socket.emit(\'ice candidates\', { candidate, to: parterName, sender: socket.id })',
    '    } else {',
    '        console.log(\'[步骤39-ICE] candidate 为 null —— 本轮 ICE 协商结束\')',
    '    }',
    '}',
    '',
    'pc[parterName].ontrack = (ev) => {',
    '    console.log(\'[步骤39-TRACK] ontrack 触发，track kind=\' + ev.track.kind)',
    '    document.getElementById(parterName + \'-video\').srcObject = ev.streams[0]',
    '}',
]))

h2(doc, '4.5 连接状态监听与挂断(步骤 40)')
body(doc, '监听 oniceconnectionstatechange，在 disconnected/failed 时关闭 RTCPeerConnection。')
code_lines(doc, '\n'.join([
    'pc[parterName].oniceconnectionstatechange = () => {',
    '    console.log(\'[步骤40-ICE状态] \' + pc[parterName].iceConnectionState)',
    '    if (pc[parterName].iceConnectionState === \'disconnected\') {',
    '        pc[parterName].close()',
    '        delete pc[parterName]',
    '    }',
    '}',
]))

# 五、结果
h1(doc, '五、实验结果(浏览器双标签页)')

h2(doc, '5.1 本地视频显示(步骤 36)')
body(doc, '标签页1打开 localhost:8181，授权摄像头后本地视频正常显示，'
          '页面标题显示当前 socket.id。')
shot_image(doc, 'lab6_tab1_local.png', '图5-1  标签页1:本地视频正常显示', width_cm=13)

h2(doc, '5.2 双标签页在线(步骤 37)')
body(doc, '标签页2打开同一地址，也获取到本地视频。用户列表中互相可见对方 socket.id 和"通话"按钮。')
shot_image(doc, 'lab6_tab2_local.png', '图5-2  标签页2:本地视频正常，用户列表显示对方', width_cm=13)

h2(doc, '5.3 通话建立(步骤 38)')
body(doc, '在标签页1点击"通话"按钮呼叫标签页2，WebRTC 完成 Offer/Answer/ICE 协商后，'
          '双方均可在页面下方看到对方的远程视频画面。')
shot_image(doc, 'lab6_call_state.png', '图5-3  通话建立:页面下方显示远程视频', width_cm=13)

h2(doc, '5.4 控制台日志:区分 Offer/Answer/Candidate(步骤 39)')
body(doc, '控制台共输出 18 条日志，完整覆盖信令交换全流程：'
          'createOffer → 发送 Offer → ICE candidate 生成(6 条 host candidate) → '
          '收到 Answer → setRemoteDescription → ICE 状态 checking → '
          '收到远端 candidate → ontrack(audio+video) → ICE connected → 协商结束。')
shot_image(doc, 'lab6_fig_console.png', '图5-4  控制台日志:完整信令流程(18条)', width_cm=14)

body(doc, '关键日志解读:')
for b in [
    'Offer 阶段: onnegotiationneeded 触发 → createOffer → setLocalDescription → 通过信令服务器发送给被叫方。',
    'Answer 阶段: 被叫方 setRemoteDescription(offer) → createAnswer → setLocalDescription → 回传给呼叫方。',
    'ICE candidate 阶段: onicecandidate 触发 6 次(3 个本地 IP 各 2 次)，最后一条 candidate 为 null 表示协商结束。',
    'Track 阶段: ontrack 触发 2 次，分别收到 audio 和 video 远端媒体流。',
    'ICE 状态: checking → connected，表示 P2P 连接已建立。',
]:
    bullet(doc, b)

# 六、STUN 与 TURN
h1(doc, '六、STUN 与 TURN 的不同用途')
body(doc, 'STUN(Session Traversal Utilities for NAT)和 TURN(Traversal Using Relays around NAT)'
          '都是 NAT 穿透技术，但用途不同：')
body(doc, 'STUN 的作用是"地址发现"：位于 NAT 后的设备通过向 STUN 服务器发送请求，'
          '得知自己的公网 IP 和端口(反射地址)。这个地址会被作为 ICE candidate 交换给对端，'
          '对端可以直接向这个公网地址发媒体包。STUN 本身不转发任何媒体数据，'
          '它只在连接初期提供一次地址查询服务。适用于大多数 NAT 类型(如圆锥型 NAT)。',
          indent=True)
body(doc, 'TURN 的作用是"中继转发"：当两端 NAT 类型不兼容(如对称型 NAT)或防火墙阻止 P2P 直连时，'
          'TURN 服务器作为中继，把双方的媒体流转发给对方。TURN 是最后的兜底方案，'
          '因为中继会占用服务器带宽和延迟，应尽量避免。本实验代码中同时配置了 STUN 和 TURN：'
          'STUN 优先用于地址发现，TURN 在直连不通时自动接管中继。', indent=True)

table(doc, ['维度', 'STUN', 'TURN'], [
    ['用途', '地址发现(得知公网 IP)', '中继转发(转发媒体流)'],
    ['是否转发媒体', '否', '是(带宽消耗大)'],
    ['使用时机', '优先使用', 'P2P 不通时兜底'],
    ['网络要求', '低(仅查询)', '高(持续转发)'],
    ['NAT 兼容性', '圆锥型 NAT 可用', '所有 NAT 类型可用'],
], widths=[3, 6, 6])

body(doc, '跨设备通信需要 HTTPS/WSS 的原因：getUserMedia API 只在安全上下文(HTTPS 或 localhost)下可用，'
          'HTTP 站点会直接被浏览器拒绝摄像头权限。WSS(WebSocket Secure)保证信令消息在传输中不被窃听篡改，'
          '与 WebRTC 内置的 DTLS-SRTP 加密共同保障通信安全。', indent=True)

# 七、故障与调试
h1(doc, '七、故障与调试')
for i, item in enumerate([
    '端口冲突: server.js 初次启动时 8080 端口被其他进程占用，改为 8181 后正常启动。'
    '排查用 netstat -ano | findstr :8080 定位占用 PID。',
    'Socket.io 版本: package.json 中 socket.io 版本需与前端 CDN 的 socket.io.js 版本匹配(3.0.4)，'
    '不匹配时前端连接会报 protocol mismatch 错误。',
    'CDN 引用: 前端代码中 Socket.io 和 jQuery 的 CDN 引用地址最初被反引号包裹导致无法加载，'
    '去掉反引号后正常加载。',
    'ICE candidate 重复: 日志中观察到每个本地 IP 生成 2 次 host candidate(端口递增)，'
    '这是因为 RTCPeerConnection 会为每个网络接口尝试多个端口。属于正常行为。',
    '权限拒绝处理: 当浏览器拒绝摄像头权限时，getUserMedia 的 error 回调被触发，'
    '代码中用 alert 弹出提示。在沙箱环境(非 HTTPS)下 getUserMedia 也会失败，'
    '需在 localhost 或 HTTPS 下运行。',
], 1):
    numbered(doc, i, item)

# 八、思考与收获
h1(doc, '八、思考与收获')
body(doc, '本实验通过双标签页 WebRTC 通话，完整走过了信令交换→媒体协商→P2P 连接建立的全流程。'
          '最核心的理解是：信令服务器只负责"协调双方认识对方"，不参与实际音视频传输；'
          '音视频流通过 RTCPeerConnection 走 P2P 直连，这是 WebRTC 区别于传统流媒体服务器的关键。')
body(doc, 'onicecandidate/ontrack 回调是理解 ICE 协商过程的关键入口。'
          'onicecandidate 在本地收集到候选地址时触发，需通过信令转发给远端；'
          'ontrack 在远端媒体到达时触发，此时可以绑定到 video 元素显示。'
          'candidate 为 null 标志一轮 ICE 收集结束，这是一个容易忽略但重要的信号。')
body(doc, 'STUN 与 TURN 的分工体现了"先尝试直连，兜底中继"的工程哲学：'
          '尽可能走 P2P(低延迟、省带宽)，实在不通才用 TURN 中继(保证可用性)。'
          '这种分层兜底设计在分布式系统中非常常见。')

doc.save(OUT_PATH)
print('SAVED:', OUT_PATH)
