package edu.example.mobilecourse.data.network

import retrofit2.http.GET

/**
 * 任务相关的网络接口。
 *
 * 使用 Retrofit 注解描述 HTTP 语义；接口由 Retrofit 动态代理实现，
 * 函数声明为 suspend 以便在协程中直接调用。
 */
interface TodoApi {

    /**
     * 获取全部待办任务。
     * 完整 URL = BASE_URL + "todos"
     */
    @GET("todos")
    suspend fun getTodos(): List<TodoDto>
}
