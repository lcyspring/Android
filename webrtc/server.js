// server.js - WebRTC 信令服务器
// 使用 Express 提供静态文件，使用 ws 提供 WebSocket 信令
const express = require('express')
const http = require('http')
const { WebSocketServer } = require('ws')
const path = require('path')

const app = express()
const server = http.createServer(app)
const wss = new WebSocketServer({ server })

const PORT = process.env.PORT || 8080

// 静态资源
app.use(express.static(path.join(__dirname, 'public')))

// 保存所有连接的客户端
const clients = new Map() // ws -> { id, name }

wss.on('connection', (ws) => {
  const id = Math.random().toString(36).substring(2, 9)
  clients.set(ws, { id })

  console.log(`[server] 客户端连接: id=${id}, 当前在线=${clients.size}`)

  // 通知所有客户端有新成员加入
  broadcast({ type: 'member-join', id, count: clients.size })

  ws.on('message', (raw) => {
    let msg
    try {
      msg = JSON.parse(raw.toString())
    } catch (e) {
      console.error('[server] 消息解析失败:', e)
      return
    }

    console.log(`[server] 收到消息 from ${id}:`, msg.type)

    switch (msg.type) {
      // 信令消息转发：offer / answer / ice-candidate
      case 'offer':
      case 'answer':
      case 'ice-candidate':
        // 转发给除自己外的所有客户端（简化模型，同机两标签页）
        clients.forEach((client, socket) => {
          if (socket !== ws && socket.readyState === ws.OPEN) {
            socket.send(JSON.stringify({ ...msg, from: id }))
          }
        })
        break

      // 挂断通知
      case 'hangup':
        clients.forEach((client, socket) => {
          if (socket !== ws && socket.readyState === ws.OPEN) {
            socket.send(JSON.stringify({ type: 'hangup', from: id }))
          }
        })
        break

      default:
        console.log('[server] 未知消息类型:', msg.type)
    }
  })

  ws.on('close', () => {
    clients.delete(ws)
    console.log(`[server] 客户端断开: id=${id}, 剩余=${clients.size}`)
    broadcast({ type: 'member-leave', id, count: clients.size })
  })
})

function broadcast(data) {
  const json = JSON.stringify(data)
  clients.forEach((client, socket) => {
    if (socket.readyState === socket.OPEN) {
      socket.send(json)
    }
  })
}

server.listen(PORT, () => {
  console.log(`[server] WebRTC 信令服务器已启动`)
  console.log(`[server] HTTP:  http://localhost:${PORT}`)
  console.log(`[server] WS:    ws://localhost:${PORT}`)
  console.log(`[server] 请在浏览器打开两个标签页进行测试`)
})
