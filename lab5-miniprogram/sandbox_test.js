// sandbox_test.js —— 实验五沙箱验证脚本
// 用 Node 模拟微信小程序运行时(Page/App/wx),把 wx.request 桥接到真实 fetch,
// 在沙箱(无微信开发者工具)中验证 lab5-miniprogram 的核心逻辑:
//   ① index 页 onLoad -> isLoading -> todos(100 条)
//   ② 点击列表项 -> wx.navigateTo 传 id -> detail 页 onLoad 读 options.id
//   ③ detail 页加载单条 todo
//   ④ 模拟错误地址 -> fail -> error 状态
//
// 运行:node sandbox_test.js
'use strict'

const path = require('path')
const ROOT = __dirname

// ---------- 全局运行时 Mock ----------
const logs = []
function rec(...args) {
  const line = args.map(a => (typeof a === 'object' ? JSON.stringify(a) : String(a))).join(' ')
  logs.push(line)
  console.log(line)
}

// 导航记录,验证 navigateTo 传参
const navStack = []

global.wx = {
  // 桥接真实网络:把 wx.request(options) 映射到 fetch
  request(options) {
    const url = options.url
    const timeout = options.timeout || 10000
    const ctrl = new AbortController()
    const timer = setTimeout(() => ctrl.abort(), timeout)
    fetch(url, { method: options.method || 'GET', signal: ctrl.signal })
      .then(async (res) => {
        clearTimeout(timer)
        let data
        const text = await res.text()
        try { data = JSON.parse(text) } catch { data = text }
        // 模拟 wx.request 的 success 回调结构 { statusCode, data }
        options.success && options.success({ statusCode: res.status, data })
      })
      .catch((err) => {
        clearTimeout(timer)
        // 模拟 fail 回调结构 { errMsg }
        const msg = err.name === 'AbortError'
          ? `request:fail timeout`
          : `request:fail ${err.cause ? err.cause.code || err.cause.message : err.message}`
        options.fail && options.fail({ errMsg: msg })
      })
  },
  navigateTo({ url }) {
    navStack.push(url)
    rec(`[wx.navigateTo] ${url}`)
  },
  navigateBack() {
    navStack.pop()
    rec(`[wx.navigateBack]`)
  }
}

// Page 构造器:收集页面定义,返回可实例化的页面对象
global.Page = function (def) { global.__lastPageDef = def }
global.App = function () {}
global.getApp = () => ({ globalData: {} })

// ---------- 页面对象工厂 ----------
function createPage(def) {
  // 模拟 Page 实例:data + setData(合并并触发视图层,这里仅记录)
  const page = Object.create(def)
  page.data = JSON.parse(JSON.stringify(def.data || {}))
  page.setData = function (patch) {
    Object.assign(this.data, patch)
  }
  return page
}

const sleep = (ms) => new Promise(r => setTimeout(r, ms))
// 轮询直到某条件满足或超时(等异步 Promise 链落地)
async function until(fn, timeout = 15000, label = '') {
  const t0 = Date.now()
  while (Date.now() - t0 < timeout) {
    if (fn()) return true
    await sleep(60)
  }
  throw new Error('超时等待: ' + label)
}

// ---------- 测试用例 ----------
const results = []
function assert(name, cond, extra = '') {
  results.push({ name, pass: !!cond, extra })
  rec(`${cond ? '✅' : '❌'} [${name}] ${extra}`)
}

async function main() {
  rec('=========== 实验五 沙箱验证 ===========\n')

  // ---- 用例 1:index 页正常加载 ----
  rec('--- 用例1: index 页加载列表(正常地址) ---')
  require(path.join(ROOT, 'pages/index/index.js'))
  const indexPage = createPage(global.__lastPageDef)
  indexPage.onLoad() // 触发 loadTodos(false)

  assert('index 进入 Loading 态', indexPage.data.isLoading === true,
    `isLoading=${indexPage.data.isLoading}`)

  await until(() => indexPage.data.isLoading === false, 15000, 'index 加载完成')
  assert('index 加载完成 isLoading=false', indexPage.data.isLoading === false)
  assert('index 无错误', indexPage.data.error === '', `error="${indexPage.data.error}"`)
  assert('index 拿到 todos', Array.isArray(indexPage.data.todos) && indexPage.data.todos.length > 0,
    `todos.length=${indexPage.data.todos.length}`)
  assert('todos 截取为前 100 条', indexPage.data.todos.length === 100,
    `todos.length=${indexPage.data.todos.length}`)
  const first = indexPage.data.todos[0]
  assert('首条含 id/title/userId/completed',
    first && 'id' in first && 'title' in first && 'userId' in first && 'completed' in first,
    `first=${JSON.stringify(first)}`)

  // ---- 用例 2:点击列表项 -> navigateTo 传 id -> detail 接收 ----
  rec('\n--- 用例2: 点击列表项跳转详情 ---')
  const tapId = indexPage.data.todos[4].id // 取第 5 条
  indexPage.onTapItem({ currentTarget: { dataset: { id: tapId } } })
  const navUrl = navStack[navStack.length - 1]
  assert('navigateTo 被调用', !!navUrl, `url=${navUrl}`)
  assert('navigateTo 携带正确 id', navUrl === `/pages/detail/detail?id=${tapId}`, `url=${navUrl}`)

  // 模拟框架:解析 url 中的 id,实例化 detail 页并调 onLoad(options)
  const idParam = parseInt(navUrl.split('id=')[1], 10)
  require(path.join(ROOT, 'pages/detail/detail.js'))
  const detailPage = createPage(global.__lastPageDef)
  detailPage.onLoad({ id: String(idParam) })
  assert('detail 读取 options.id', String(detailPage.data.id) === String(idParam),
    `detail.data.id=${detailPage.data.id}`)

  // ---- 用例 3:detail 加载单条 ----
  rec('\n--- 用例3: detail 页加载单条详情 ---')
  await until(() => detailPage.data.isLoading === false, 15000, 'detail 加载完成')
  assert('detail 加载完成', detailPage.data.isLoading === false)
  assert('detail 无错误', detailPage.data.error === '', `error="${detailPage.data.error}"`)
  assert('detail 拿到 todo 且 id 匹配',
    detailPage.data.todo && Number(detailPage.data.todo.id) === Number(idParam),
    `todo=${JSON.stringify(detailPage.data.todo)}`)

  // ---- 用例 4:模拟错误地址 -> fail -> error ----
  rec('\n--- 用例4: 模拟错误地址验证失败提示 ---')
  indexPage.onSimulateError() // 走 ERROR_BASE_URL
  assert('错误路径进入 Loading 态', indexPage.data.isLoading === true)
  await until(() => indexPage.data.isLoading === false, 20000, '错误路径返回')
  assert('错误路径 isLoading 复位', indexPage.data.isLoading === false)
  assert('错误路径产生 error 文案', typeof indexPage.data.error === 'string' && indexPage.data.error.length > 0,
    `error="${indexPage.data.error}"`)
  assert('错误路径 todos 已清空', indexPage.data.todos.length === 0,
    `todos.length=${indexPage.data.todos.length}`)

  // ---- 用例 5:错误后重试恢复正常 ----
  rec('\n--- 用例5: 错误后 onRetry 恢复正常 ---')
  indexPage.onRetry()
  await until(() => indexPage.data.isLoading === false, 15000, '重试完成')
  assert('重试后恢复 todos', indexPage.data.todos.length === 100, `todos.length=${indexPage.data.todos.length}`)
  assert('重试后 error 清空', indexPage.data.error === '')

  // ---- 汇总 ----
  const passed = results.filter(r => r.pass).length
  rec(`\n=========== 结果:${passed}/${results.length} 通过 ===========`)
  process.exit(passed === results.length ? 0 : 1)
}

main().catch(e => { console.error('沙箱运行异常:', e); process.exit(2) })
