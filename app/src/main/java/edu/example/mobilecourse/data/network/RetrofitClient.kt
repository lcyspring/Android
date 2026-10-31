package edu.example.mobilecourse.data.network

import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

/**
 * Retrofit 实例的集中创建点。
 *
 * 默认使用 JSONPlaceholder（无密钥教学 API）：
 *   https://jsonplaceholder.typicode.com/todos
 *
 * 若校园网络访问不通，可把 [BASE_URL] 改为本地 mock 服务地址，
 * 或者继续用 FakeTaskRepository 离线演示。
 */
object RetrofitClient {

    /** 模拟断网/错误地址时，把这里改成非法地址即可验证 Error + Retry */
    private const val BASE_URL = "https://jsonplaceholder.typicode.com/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        // BODY 级别会打印请求/响应体，便于调试；Release 时应降级为 NONE 以防泄露敏感信息
        level = HttpLoggingInterceptor.Level.BODY
    }

    private val okHttpClient = OkHttpClient.Builder()
        .addInterceptor(loggingInterceptor)
        .build()

    val todoApi: TodoApi by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(TodoApi::class.java)
    }
}
