// utils/api.js
// 业务 API 层:页面只调 getTodos/getTodoById,不关心 URL 拼接。
// 对应 Android 实验四的 TodoApi(@GET("todos"))。

const { request } = require('./request')

/** 获取全部 todos(对应 TodoApi.getTodos()) */
function getTodos() {
  return request({ url: 'todos' })
}

/** 按 id 获取单条 todo(对应 TodoApi.getTodoById(id)) */
function getTodoById(id) {
  return request({ url: 'todos/' + id })
}

module.exports = {
  getTodos,
  getTodoById
}
