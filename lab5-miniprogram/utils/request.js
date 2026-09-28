// utils/request.js
// 指导书 D 起始代码:统一的 request 封装,把 wx.request 包成 Promise。
//
// 验收点:"网络代码没有在多个页面复制 wx.request" —— index/detail 两个页面都只调这里,
// 不直接写 wx.request。对应 Android 实验四的 RetrofitClient + NetworkTaskRepository。

const { BASE_URL } = require('./config')

/**
 * 统一网络请求
 * @param {Object} options
 * @param {string} options.url    相对路径,如 'todos'、'todos/1'
 * @param {string} [options.method='GET']
 * @param {Object} [options.data={}]
 * @param {string} [options.baseUrl] 可选,步骤 33 传入错误基址模拟失败
 * @returns {Promise<any>} resolve 业务数据;reject Error(message)
 */
function request({ url, method = 'GET', data = {}, baseUrl }) {
  const fullUrl = (baseUrl || BASE_URL) + url
  return new Promise((resolve, reject) => {
    wx.request({
      url: fullUrl,
      method,
      data,
      timeout: 10000,
      success: (res) => {
        // HTTP 状态码在 2xx 才算成功,否则 reject 交给页面 catch
        if (res.statusCode >= 200 && res.statusCode < 300) {
          resolve(res.data)
        } else {
          reject(new Error('HTTP ' + res.statusCode))
        }
      },
      // 断网 / 域名解析失败 / 超时走这里(步骤 33 的错误地址会进这个分支)
      fail: (err) => {
        reject(new Error((err && err.errMsg) || '网络请求失败'))
      }
    })
  })
}

module.exports = {
  request
}
