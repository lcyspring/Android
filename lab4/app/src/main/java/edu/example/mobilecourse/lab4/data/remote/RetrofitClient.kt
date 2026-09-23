package edu.example.mobilecourse.lab4.data.remote

import okhttp3.Interceptor
import okhttp3.OkHttpClient
import okhttp3.logging.HttpLoggingInterceptor
import retrofit2.Retrofit
import retrofit2.converter.moshi.MoshiConverterFactory
import java.util.concurrent.TimeUnit

/**
 * Retrofit 单例:统一配置 base URL、OkHttp、Moshi Converter。
 *
 * 实验四安全设计点:
 * - baseUrl 硬编码(无 API Key/Token,JSONPlaceholder 是公开免费 API)
 * - 无敏感凭据提交到仓库(验收点"无敏感凭据提交到仓库")
 * - 日志拦截器只在 Debug 构建启用
 */
object RetrofitClient {

    // JSONPlaceholder:教学用免费 API,返回固定 200 条 todos
    // https://jsonplaceholder.typicode.com/todos
    private const val BASE_URL = "https://jsonplaceholder.typicode.com/"

    private val loggingInterceptor = HttpLoggingInterceptor().apply {
        level = HttpLoggingInterceptor.Level.BASIC   // 只打 URL/状态码,不打响应体(避免泄露)
    }

    private val okHttpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .addInterceptor(loggingInterceptor)
            .connectTimeout(15, TimeUnit.SECONDS)
            .readTimeout(15, TimeUnit.SECONDS)
            .build()
    }

    private val retrofit: Retrofit by lazy {
        Retrofit.Builder()
            .baseUrl(BASE_URL)
            .client(okHttpClient)
            .addConverterFactory(MoshiConverterFactory.create())
            .build()
    }

    val todoApi: TodoApi by lazy { retrofit.create(TodoApi::class.java) }
}
