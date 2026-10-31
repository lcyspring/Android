package edu.example.mobilecourse.data.repository

import edu.example.mobilecourse.CourseTask
import kotlinx.coroutines.delay

/**
 * 任务数据源的统一抽象。
 *
 * UI 层不直接接触网络或本地存储，所有数据访问都通过 Repository 接口完成，
 * 便于在 Fake / Network / Local 实现之间切换而不影响 ViewModel 与 Screen。
 */
interface TaskRepository {
    suspend fun getTasks(): List<CourseTask>
    suspend fun getTaskById(id: Int): CourseTask?
}

/**
 * 用于实验 3 的假数据实现，可在初始化时通过开关模拟：
 *   - [delayMillis] 网络时延，用于观察 Loading 状态；
 *   - [shouldFail]  抛出异常，用于验证 Error + Retry 状态；
 *   - [shouldReturnEmpty]  返回空列表，用于验证 Empty 状态。
 *
 * 默认配置仅 delay，不抛错且返回示例数据，可作为正常 Content 路径演示。
 */
class FakeTaskRepository(
    private val delayMillis: Long = 800L,
    private val shouldFail: Boolean = false,
    private val shouldReturnEmpty: Boolean = false,
) : TaskRepository {

    private val sampleTasks: List<CourseTask> = List(100) { index ->
        CourseTask(
            id = index + 1,
            title = "示例任务 #${index + 1} · 状态流与 ViewModel",
            owner = if (index % 3 == 0) null else "学号-${1000 + index}",
            completed = index % 2 == 0
        )
    }

    override suspend fun getTasks(): List<CourseTask> {
        delay(delayMillis)
        if (shouldFail) {
            throw RuntimeException("FakeTaskRepository 模拟网络异常：获取任务列表失败")
        }
        return if (shouldReturnEmpty) emptyList() else sampleTasks
    }

    override suspend fun getTaskById(id: Int): CourseTask? {
        delay(delayMillis)
        if (shouldFail) {
            throw RuntimeException("FakeTaskRepository 模拟网络异常：获取任务详情失败")
        }
        return sampleTasks.firstOrNull { it.id == id }
    }
}
