// pages/index/index.js
const { api } = require('../../utils/request')

Page({
  data: {
    todos: [],
    isLoading: true,
    error: ''
  },

  onLoad() {
    this.loadTodos()
  },

  // 下拉刷新
  onPullDownRefresh() {
    this.loadTodos(() => {
      wx.stopPullDownRefresh()
    })
  },

  loadTodos(done) {
    this.setData({ isLoading: true, error: '' })
    api.getTodos()
      .then((data) => {
        // 只取前 20 条，避免列表过长
        const todos = (data || []).slice(0, 20).map((item) => ({
          id: item.id,
          title: item.title,
          completed: item.completed
        }))
        this.setData({ todos, isLoading: false })
      })
      .catch((err) => {
        console.error('加载列表失败：', err)
        const msg = (err && (err.errMsg || err.message)) || '网络请求失败，请重试'
        this.setData({
          isLoading: false,
          error: msg
        })
      })
      .finally(() => {
        if (typeof done === 'function') done()
      })
  },

  onRetry() {
    this.loadTodos()
  },

  // 点击左侧圆圈切换完成状态
  onToggleComplete(e) {
    const id = e.currentTarget.dataset.id
    const todos = this.data.todos
    const index = todos.findIndex((t) => t.id === id)
    if (index === -1) return

    // 先乐观更新本地状态，让用户立即看到反馈
    const newCompleted = !todos[index].completed
    todos[index].completed = newCompleted
    this.setData({ todos })

    // 调用接口更新（JSONPlaceholder 是模拟接口，实际不会真改数据）
    api.updateTodo(id, { completed: newCompleted })
      .then(() => {
        wx.showToast({
          title: newCompleted ? '已标记完成' : '已标记未完成',
          icon: 'success',
          duration: 1000
        })
      })
      .catch((err) => {
        console.error('更新失败：', err)
        // 回滚本地状态
        todos[index].completed = !newCompleted
        this.setData({ todos })
        wx.showToast({
          title: '更新失败',
          icon: 'none'
        })
      })
  },

  // 点击列表项内容跳转详情页，传递 id
  onItemTap(e) {
    const id = e.currentTarget.dataset.id
    wx.navigateTo({
      url: `/pages/detail/detail?id=${id}`
    })
  }
})
