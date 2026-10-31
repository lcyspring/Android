// main.js - WebRTC 客户端逻辑
const localVideo = document.getElementById('localVideo')
const remoteVideo = document.getElementById('remoteVideo')
const getMediaBtn = document.getElementById('getMediaBtn')
const callBtn = document.getElementById('callBtn')
const hangupBtn = document.getElementById('hangupBtn')
const statusEl = document.getElementById('status')
const logEl = document.getElementById('log')

let localStream = null
let peerConnection = null
let ws = null
let isCaller = false

// Google 公共 STUN 服务器（仅用于 NAT 穿透发现，不中转媒体）
const ICE_CONFIG = {
  iceServers: [
    { urls: 'stun:stun.l.google.com:19302' }
  ]
}

// ============ 日志 ============
function log(msg, type = 'info') {
  const time = new Date().toLocaleTimeString()
  const div = document.createElement('div')
  div.className = `log-entry log-${type}`
  div.textContent = `[${time}] ${msg}`
  logEl.appendChild(div)
  logEl.scrollTop = logEl.scrollHeight
  console.log(`[webrtc] ${msg}`)
}

function setStatus(text) {
  statusEl.textContent = text
}

// ============ WebSocket 信令 ============
function connectSignaling() {
  const proto = location.protocol === 'https:' ? 'wss' : 'ws'
  ws = new WebSocket(`${proto}://${location.host}`)

  ws.onopen = () => {
    log('WebSocket 信令连接已建立', 'success')
    setStatus('已连接信令服务器')
  }

  ws.onclose = () => {
    log('WebSocket 断开', 'warn')
    setStatus('信令断开')
  }

  ws.onerror = (e) => {
    log('WebSocket 错误: ' + e.message, 'error')
  }

  ws.onmessage = (event) => {
    const msg = JSON.parse(event.data)
    handleSignalingMessage(msg)
  }
}

function handleSignalingMessage(msg) {
  switch (msg.type) {
    case 'offer':
      log(`收到 Offer (from ${msg.from})`, 'info')
      handleOffer(msg)
      break
    case 'answer':
      log(`收到 Answer (from ${msg.from})`, 'info')
      handleAnswer(msg)
      break
    case 'ice-candidate':
      log(`收到 ICE Candidate (from ${msg.from})`, 'info')
      handleIceCandidate(msg)
      break
    case 'hangup':
      log(`收到挂断通知 (from ${msg.from})`, 'warn')
      closePeerConnection()
      break
    case 'member-join':
      log(`新成员加入: ${msg.id}, 当前在线 ${msg.count}`, 'info')
      break
    case 'member-leave':
      log(`成员离开: ${msg.id}, 剩余 ${msg.count}`, 'warn')
      break
  }
}

function sendSignaling(msg) {
  if (ws && ws.readyState === WebSocket.OPEN) {
    ws.send(JSON.stringify(msg))
  }
}

// ============ 媒体获取 ============
getMediaBtn.addEventListener('click', async () => {
  try {
    log('正在请求摄像头/麦克风权限...')
    localStream = await navigator.mediaDevices.getUserMedia({
      video: true,
      audio: true
    })
    localVideo.srcObject = localStream
    log('已获取本地媒体流（视频 + 音频）', 'success')
    getMediaBtn.disabled = true
    callBtn.disabled = false
    setStatus('本地媒体已就绪，可发起呼叫')
  } catch (err) {
    log(`获取媒体失败: ${err.name} - ${err.message}`, 'error')
    alert('无法访问摄像头/麦克风：' + err.message + '\n请检查浏览器权限设置。')
  }
})

// ============ 发起呼叫 ============
callBtn.addEventListener('click', async () => {
  if (!localStream) {
    log('请先获取媒体', 'warn')
    return
  }
  isCaller = true
  createPeerConnection()
  addLocalTracks()

  try {
    log('正在创建 Offer...')
    const offer = await peerConnection.createOffer()
    await peerConnection.setLocalDescription(offer)
    log('Offer 已创建并设置为本地描述', 'success')
    sendSignaling({ type: 'offer', sdp: offer.sdp })
    log('Offer 已通过信令发送', 'success')
    setStatus('呼叫中...')
  } catch (err) {
    log(`创建 Offer 失败: ${err.message}`, 'error')
  }
})

// ============ 挂断 ============
hangupBtn.addEventListener('click', () => {
  log('主动挂断')
  sendSignaling({ type: 'hangup' })
  closePeerConnection()
})

// ============ RTCPeerConnection ============
function createPeerConnection() {
  peerConnection = new RTCPeerConnection(ICE_CONFIG)
  log('RTCPeerConnection 已创建', 'success')

  // ICE candidate 收集
  peerConnection.onicecandidate = (event) => {
    if (event.candidate) {
      log(`收集到 ICE Candidate: ${event.candidate.candidate.substring(0, 60)}...`, 'info')
      sendSignaling({
        type: 'ice-candidate',
        candidate: event.candidate.toJSON()
      })
    } else {
      log('ICE candidate 收集完毕', 'info')
    }
  }

  // 远端媒体流到达
  peerConnection.ontrack = (event) => {
    log(`收到远端媒体轨道: ${event.track.kind}`, 'success')
    if (remoteVideo.srcObject !== event.streams[0]) {
      remoteVideo.srcObject = event.streams[0]
      log('远端视频已显示', 'success')
    }
  }

  // ICE 连接状态变化
  peerConnection.oniceconnectionstatechange = () => {
    log(`ICE 连接状态: ${peerConnection.iceConnectionState}`, 'info')
    if (peerConnection.iceConnectionState === 'connected') {
      setStatus('已连接（媒体传输中）')
      hangupBtn.disabled = false
      callBtn.disabled = true
    } else if (peerConnection.iceConnectionState === 'failed') {
      log('ICE 连接失败', 'error')
    }
  }

  peerConnection.onconnectionstatechange = () => {
    log(`PeerConnection 状态: ${peerConnection.connectionState}`, 'info')
  }
}

function addLocalTracks() {
  localStream.getTracks().forEach((track) => {
    peerConnection.addTrack(track, localStream)
    log(`已添加本地轨道: ${track.kind}`, 'info')
  })
}

// ============ 处理远端信令 ============
async function handleOffer(msg) {
  isCaller = false
  createPeerConnection()
  addLocalTracks()

  try {
    await peerConnection.setRemoteDescription(new RTCSessionDescription({
      type: 'offer',
      sdp: msg.sdp
    }))
    log('远端 Offer 已设置为远程描述', 'success')

    const answer = await peerConnection.createAnswer()
    await peerConnection.setLocalDescription(answer)
    log('Answer 已创建并设置为本地描述', 'success')
    sendSignaling({ type: 'answer', sdp: answer.sdp })
    log('Answer 已通过信令发送', 'success')
  } catch (err) {
    log(`处理 Offer 失败: ${err.message}`, 'error')
  }
}

async function handleAnswer(msg) {
  try {
    await peerConnection.setRemoteDescription(new RTCSessionDescription({
      type: 'answer',
      sdp: msg.sdp
    }))
    log('远端 Answer 已设置为远程描述', 'success')
  } catch (err) {
    log(`处理 Answer 失败: ${err.message}`, 'error')
  }
}

async function handleIceCandidate(msg) {
  try {
    await peerConnection.addIceCandidate(new RTCIceCandidate(msg.candidate))
    log('ICE Candidate 已添加', 'success')
  } catch (err) {
    log(`添加 ICE Candidate 失败: ${err.message}`, 'error')
  }
}

// ============ 清理 ============
function closePeerConnection() {
  if (peerConnection) {
    peerConnection.close()
    log('RTCPeerConnection 已关闭', 'warn')
    peerConnection = null
  }
  remoteVideo.srcObject = null
  callBtn.disabled = false
  hangupBtn.disabled = true
  setStatus(localStream ? '已挂断，可重新呼叫' : '未连接')
}

// ============ 启动 ============
connectSignaling()
window.addEventListener('beforeunload', () => {
  if (peerConnection) peerConnection.close()
  if (ws) ws.close()
})
