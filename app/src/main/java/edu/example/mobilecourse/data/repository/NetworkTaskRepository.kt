package edu.example.mobilecourse.data.repository

import edu.example.mobilecourse.CourseTask
import edu.example.mobilecourse.data.network.RetrofitClient

/**
 * 基于 Retrofit 的网络实现：调用 [TodoApi] 拉取远程 JSON，
 * 把 [TodoDto] 映射成 UI 层使用的 [CourseTask]。
 *
 * 映射规则：
 *   - id        → CourseTask.id
 *   - title     → CourseTask.title
 *   - completed → CourseTask.completed
 *   - owner     → 接口无此字段，用 null 表示"未指派"
 *
 * 网络异常（无网/超时/5xx）会由 Retrofit/OkHttp 抛出，
 * 在 ViewModel 中被捕获并写入 [HomeUiState.errorMessage]。
 */
class NetworkTaskRepository : TaskRepository {

    private val api = RetrofitClient.todoApi

    override suspend fun getTasks(): List<CourseTask> {
        return api.getTodos().map { dto ->
            CourseTask(
                id = dto.id,
                title = dto.title,
                owner = null, // /todos 接口不含 owner 字段
                completed = dto.completed,
            )
        }
    }

    override suspend fun getTaskById(id: Int): CourseTask? {
        // /todos/{id} 单条接口与列表语义一致；若需要可再定义 @GET("todos/{id}")。
        // 此处直接复用列表 + 内存查找，减少接口数量。
        return getTasks().firstOrNull { it.id == id }
    }
}
