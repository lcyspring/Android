package edu.example.mobilecourse.lab4.data.repository

import edu.example.mobilecourse.lab4.data.model.CourseTask
import edu.example.mobilecourse.lab4.data.model.emptyTasks
import edu.example.mobilecourse.lab4.data.model.sampleTasks
import kotlinx.coroutines.delay

/**
 * 任务数据仓库接口(指导书 3.2 统一 Repository 模板 + 实验三步骤 15)。
 *
 * 设计动机(单向数据流 UDF 的"数据在哪里"那一问):
 * - 所有 UI 数据都从 Repository 流出,ViewModel 只持有 Repository 引用 + 暴露 StateFlow,
 *   Screen 不直接调用 Repository(验收点)。
 * - 用接口隔离数据来源,实验三用 [FakeTaskRepository] 模拟 delay 与异常,
 *   实验四会换成 NetworkTaskRepository(Retrofit + REST API)而不需改 ViewModel。
 *
 * 实验三只覆盖 Home 列表的 getTasks();TaskDetail 仍用 model 包的同步 [edu.example.mobilecourse.lab4.data.model.taskById]
 * (实验三未要求详情页接入 ViewModel)。
 */
interface TaskRepository {
    /**
     * 拉取任务列表(suspend 模拟网络/磁盘 IO)。
     *
     * @throws RuntimeException 当 [FakeTaskRepository] 的 errorMode 开启时抛出,
     *   用来验证 HomeUiState 的 Error + Retry 分支(验收点"失败后可重试且不会崩溃")。
     */
    suspend fun getTasks(): List<CourseTask>
}

/**
 * 假数据仓库(指导书实验准备 B:教师提供 FakeTaskRepository,可模拟 delay 和异常)。
 *
 * 三个测试开关,对应实验三验收点"四种 UI 状态均可演示":
 * - 默认(全 false):delay 800ms 后返回 100 条样本 → Loading -> Content
 * - [emptyMode] = true:返回 emptyList → Loading -> Empty(步骤 20)
 * - [errorMode] = true:抛 RuntimeException → Loading -> Error + Retry(步骤 19)
 *
 * delay 模拟网络耗时,让 Loading 状态在 UI 上可见(否则 100 条内存数据瞬间返回,看不到 Loading)。
 *
 * @param delayMillis 模拟网络延迟毫秒数,默认 800
 * @param emptyMode   true 时返回空列表,测试 Empty 状态
 * @param errorMode   true 时抛异常,测试 Error + Retry 状态
 */
class FakeTaskRepository(
    private val delayMillis: Long = 800L,
    private val emptyMode: Boolean = false,
    private val errorMode: Boolean = false,
) : TaskRepository {

    override suspend fun getTasks(): List<CourseTask> {
        // 模拟网络/磁盘 IO 耗时,让 HomeUiState.isLoading = true 在 UI 上可见。
        delay(delayMillis)
        if (errorMode) {
            // 模拟接口失败。ViewModel 的 catch 会把异常转成 errorMessage,UI 走 ErrorContent + Retry。
            throw RuntimeException("FakeTaskRepository 模拟网络异常(errorMode=true)")
        }
        return if (emptyMode) emptyTasks else sampleTasks
    }
}
