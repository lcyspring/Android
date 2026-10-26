// utils/config.js
// 统一 API 配置。所有网络地址只在这里出现一次(对应 Android 实验四 RetrofitClient.BASE_URL)。

// 正常地址:JSONPlaceholder 公开免费 API,与实验四 Android 端同一个数据源,便于对照
const BASE_URL = 'https://jsonplaceholder.typicode.com/'

// 步骤 33:模拟错误地址(DNS 必然解析失败),用来验证 wx.request fail -> error UI
const ERROR_BASE_URL = 'https://invalid-lab5-demo.example.com/'

module.exports = {
  BASE_URL,
  ERROR_BASE_URL
}
