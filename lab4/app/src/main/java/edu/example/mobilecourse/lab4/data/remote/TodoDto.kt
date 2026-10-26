package edu.example.mobilecourse.lab4.data.remote

import com.squareup.moshi.Json

/**
 * 网络层 DTO:JSONPlaceholder /todos 接口返回的每条记录结构。
 *
 * 指导书步骤 21:定义 TodoDto 与 TodoApi。
 * JSONPlaceholder 返回示例:
 *   {"userId":1,"id":1,"title":"delectus aut autem","completed":false}
 */
data class TodoDto(
    val userId: Int,
    val id: Int,
    val title: String,
    val completed: Boolean,
)
