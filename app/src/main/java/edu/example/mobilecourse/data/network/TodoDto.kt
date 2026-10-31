package edu.example.mobilecourse.data.network

import com.google.gson.annotations.SerializedName

/**
 * 与 JSONPlaceholder /todos 接口对应的 DTO（Data Transfer Object）。
 *
 * 注意：DTO 字段名必须与接口返回的 JSON 键一一对应；
 * 若字段名与 JSON 键不同，需用 [SerializedName] 显式映射。
 */
data class TodoDto(
    @SerializedName("id")
    val id: Int,

    @SerializedName("title")
    val title: String,

    @SerializedName("completed")
    val completed: Boolean,
)
