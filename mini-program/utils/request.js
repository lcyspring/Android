// utils/request.js
// 统一网络请求封装 —— 所有页面共用，避免在多个页面复制 wx.request
// 注意：getApp() 必须在函数内调用，模块顶层调用时 App() 可能尚未初始化完成

function getBaseUrl() {
  const app = getApp()
  return app && app.globalData ? app.globalData.baseUrl : 'https://jsonplaceholder.typicode.com'
}

function request({ url, method = 'GET', data = {} }) {
  return new Promise((resolve, reject) => {
    wx.request({
      url: getBaseUrl() + url,
      method,
      data,
      header: {
        'Content-Type': 'application/json'
      },
      success: (res) => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error(`HTTP ${res.statusCode}`))
        }
      },
      fail: (err) => {
        reject(err)
      }
    })
  })
}

// 对外暴露的便捷方法
const api = {
  getTodos: () => request({ url: '/todos' }),
  getTodoById: (id) => request({ url: `/todos/${id}` }),
  getTodoComments: (id) => request({ url: `/todos/${id}/comments` }),
  // 更新待办（用于切换完成状态）
  updateTodo: (id, data) => request({ url: `/todos/${id}`, method: 'PUT', data })
}

module.exports = { request, api, getBaseUrl }
