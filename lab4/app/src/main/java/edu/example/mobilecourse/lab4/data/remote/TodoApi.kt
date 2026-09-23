package edu.example.mobilecourse.lab4.data.remote

import retrofit2.http.GET
import retrofit2.http.Path

/**
 * Retrofit 接口:JSONPlaceholder 公开免费 API,无密钥、无需注册。
 *
 * 指导书步骤 21:定义 TodoApi。
 * base URL 由 [RetrofitClient] 统一配置,这里只声明相对路径。
 */
interface TodoApi {

    /** 获取全部 todos(200 条)。 */
    @GET("todos")
    suspend fun getTodos(): List<TodoDto>

    /** 获取单条 todo(给 TaskDetail 备用)。 */
    @GET("todos/{id}")
    suspend fun getTodoById(@Path("id") id: Int): TodoDto
}
