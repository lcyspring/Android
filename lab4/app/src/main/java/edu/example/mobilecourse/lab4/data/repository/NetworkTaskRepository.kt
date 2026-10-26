package edu.example.mobilecourse.lab4.data.repository

import edu.example.mobilecourse.lab4.data.model.CourseTask
import edu.example.mobilecourse.lab4.data.remote.RetrofitClient

/**
 * 实验四:基于 Retrofit + JSONPlaceholder 的网络实现。
 *
 * 指导书步骤 22:实现 NetworkTaskRepository,把 DTO 转成 CourseTask。
 * 指导书步骤 23:HomeViewModel 的 repository 替换为网络实现。
 *
 * DTO → CourseTask 映射:
 * - TodoDto.id         → CourseTask.id
 * - TodoDto.title      → CourseTask.title
 * - TodoDto.completed  → CourseTask.completed
 * - owner: JSONPlaceholder 没有 owner 字段,统一为 null → 显示"未分配"
 * - priority: JSONPlaceholder 没有优先级,默认 2
 *
 * Repository 接口不变,ViewModel 不用改就能换数据源(依赖倒置)。
 */
class NetworkTaskRepository : TaskRepository {

    override suspend fun getTasks(): List<CourseTask> {
        val todos = RetrofitClient.todoApi.getTodos()
        return todos.map { it.toCourseTask() }
    }

    private fun edu.example.mobilecourse.lab4.data.remote.TodoDto.toCourseTask(): CourseTask = CourseTask(
        id = id,
        title = title,
        owner = null,              // JSONPlaceholder 无 owner,统一显示"未分配"
        completed = completed,
        priority = 2,              // JSONPlaceholder 无优先级,默认 2
    )
}
