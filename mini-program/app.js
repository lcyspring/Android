// app.js
App({
  globalData: {
    // 使用 JSONPlaceholder 公共 API（与实验四相同的数据源）
    baseUrl: 'https://jsonplaceholder.typicode.com'
  },
  onLaunch() {
    console.log('小程序启动，baseUrl =', this.globalData.baseUrl)
  }
})
