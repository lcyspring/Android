// pages/detail/detail.js
// 步骤 32:onLoad(options) 读取列表页 navigateTo 传来的 id,再用统一 request 拉单条详情。

const { getTodoById } = require('../../utils/api')

Page({
  data: {
    id: null,
    isLoading: true,
    todo: null,
    error: ''
  },

  onLoad(options) {
    // options.id 即 wx.navigateTo({ url: 'detail?id=' + id }) 中携带的参数
    const id = options && options.id
    if (!id) {
      this.setData({ isLoading: false, error: '缺少任务 id 参数' })
      return
    }
    this.setData({ id })
    this.loadDetail(id)
  },

  loadDetail(id) {
    this.setData({ isLoading: true, error: '', todo: null })
    getTodoById(id)
      .then((todo) => {
        this.setData({ isLoading: false, todo })
      })
      .catch((err) => {
        this.setData({
          isLoading: false,
          error: (err && err.message) || '未知网络错误'
        })
      })
  },

  onRetry() {
    if (this.data.id != null) {
      this.loadDetail(this.data.id)
    }
  },

  onBack() {
    wx.navigateBack()
  }
})
