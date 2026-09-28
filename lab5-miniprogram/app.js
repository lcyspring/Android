// app.js —— 实验五小程序入口
// 全局只放极少量通用逻辑;网络访问统一走 utils/request.js(验收点:不在多个页面复制 wx.request)
App({
  globalData: {
    // 与实验四 Android 端一致的数据源,方便对照
    appName: '实验五·微信小程序'
  },
  onLaunch() {
    console.log('[lab5] 小程序启动')
  }
})
