// pages/index/index.js
// 步骤 30:调用统一 request(经 api 层),维护 isLoading/todos/error 三个页面状态。
// 步骤 31:点击列表项 wx.navigateTo 携带 id 跳转 detail。
// 步骤 33:onSimulateError 走错误地址,验证失败提示。

const { getTodos } = require('../../utils/api')
const { request } = require('../../utils/request')
const { ERROR_BASE_URL } = require('../../utils/config')

Page({
  data: {
    isLoading: false,   // Loading 态
    todos: [],          // Content 态数据
    error: ''           // Error 态文案(空串表示无错误)
  },

  onLoad() {
    this.loadTodos(false)
  },

  /**
   * 加载任务列表
   * @param {boolean} useErrorUrl true 时请求错误基址(步骤 33)
   */
  loadTodos(useErrorUrl) {
    // 进入即 Loading,清空旧数据/旧错误(对应 Android HomeViewModel.refresh)
    this.setData({ isLoading: true, error: '', todos: [] })

    // 正常路径走 api 层;错误路径直接用 request 传错误 baseUrl —— 两种路径都复用统一封装
    const promise = useErrorUrl
      ? request({ url: 'todos', baseUrl: ERROR_BASE_URL })
      : getTodos()

    promise.then((list) => {
      this.setData({
        isLoading: false,
        // JSONPlaceholder 返回 200 条,截取前 100 条展示(与实验三 sampleTasks 数量一致)
        todos: Array.isArray(list) ? list.slice(0, 100) : []
      })
    }).catch((err) => {
      // 错误只在页面状态里体现,不弹崩溃(对应 Android catch -> errorMessage)
      this.setData({
        isLoading: false,
        error: (err && err.message) || '未知网络错误'
      })
    })
  },

  // 重试:重新请求正常地址
  onRetry() {
    this.loadTodos(false)
  },

  // 步骤 33:模拟错误地址
  onSimulateError() {
    this.loadTodos(true)
  },

  // 步骤 31:携带 id 跳转详情页
  onTapItem(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: '/pages/detail/detail?id=' + id
    })
  }
})
