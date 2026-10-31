// pages/detail/detail.js
const { api } = require('../../utils/request')

Page({
  data: {
    todo: null,
    isLoading: true,
    error: '',
    id: ''
  },

  onLoad(options) {
    const id = options.id
    if (!id) {
      this.setData({
        isLoading: false,
        error: '缺少 id 参数'
      })
      return
    }
    this.setData({ id })
    this.loadDetail(id)
  },

  loadDetail(id) {
    this.setData({ isLoading: true, error: '' })
    api.getTodoById(id)
      .then((data) => {
        this.setData({
          todo: {
            id: data.id,
            title: data.title,
            completed: data.completed,
            userId: data.userId
          },
          isLoading: false
        })
      })
      .catch((err) => {
        console.error('加载详情失败：', err)
        const msg = (err && (err.errMsg || err.message)) || '加载详情失败'
        this.setData({
          isLoading: false,
          error: msg
        })
      })
  },

  onRetry() {
    this.loadDetail(this.data.id)
  }
})
