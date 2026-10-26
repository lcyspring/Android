// server.js —— 实验六 WebRTC 信令服务器
// 职责：仅转发 SDP / ICE 协商消息，不参与媒体传输
const express = require('express');
const http = require('http');
const { Server } = require('socket.io');

const app = express();
const server = http.createServer(app);
const io = new Server(server);

// 静态文件服务（前端 index.html）
app.use(express.static(__dirname + '/public'));

// ---------- 信令服务器逻辑 ----------
// signaling 只负责"转发协商消息"，不触碰音视频流
const users = {};          // socket.id -> socket.id（在线用户表）

io.on('connection', (socket) => {
    console.log(`[用户上线] ${socket.id}`);

    // 1) 新用户上线，广播给除自己以外的所有人
    socket.on('new user greet', (data) => {
        console.log(`[新用户打招呼] ${data.sender}: ${data.msg}`);
        // 通知其他用户：有新人来了
        socket.broadcast.emit('need connect', {
            sender: data.sender,
            msg: data.msg
        });
    });

    // 2) 接收方确认连接
    socket.on('ok we connect', (data) => {
        console.log(`[确认连接] ${data.sender} -> ${data.receiver}`);
        // 把确认消息转发给目标用户
        io.to(data.receiver).emit('ok we connect', {
            sender: data.sender
        });
    });

    // 3) 转发 SDP（offer / answer）—— 信令核心
    socket.on('sdp', (data) => {
        console.log(`[SDP 转发] ${data.sender} -> ${data.to}  类型=${data.description.type}`);
        io.to(data.to).emit('sdp', data);
    });

    // 4) 转发 ICE candidate
    socket.on('ice candidates', (data) => {
        console.log(`[ICE 转发] ${data.sender} -> ${data.to}`);
        io.to(data.to).emit('ice candidates', data);
    });

    // 5) 用户断开
    socket.on('disconnect', () => {
        console.log(`[用户下线] ${socket.id}`);
        socket.broadcast.emit('user disconnected', socket.id);
    });
});

// ---------- 启动 ----------
const PORT = 8181;
server.listen(PORT, () => {
    console.log(`\n========================================`);
    console.log(`  实验六 WebRTC 信令服务器已启动`);
    console.log(`  打开浏览器访问: http://localhost:${PORT}`);
    console.log(`  验收步骤:`);
    console.log(`    1. 标签页1 打开上面的地址，允许摄像头权限`);
    console.log(`    2. 标签页2 打开同一地址，也允许摄像头`);
    console.log(`    3. 在标签页1 的用户列表中点"通话"按钮呼叫标签页2`);
    console.log(`    4. 打开 F12 控制台观察 offer / answer / candidate 日志`);
    console.log(`========================================\n`);
});
