package edu.example.mobilecourse.lab4.data.model

/**
 * 课程任务数据类(实验三沿用实验二的数据模型,字段不变)。
 *
 * 实验三关键变化:数据访问从"顶层常量直接被 UI 读"改为"由 [edu.example.mobilecourse.lab4.data.repository.TaskRepository]
 * 统一提供",本文件只负责**模型定义**和**示例数据样本**,不再被 UI 直接 import。
 *
 * @param id         任务 ID,作为导航参数 taskId 在 Home -> TaskDetail 之间传递
 * @param title      任务标题
 * @param owner      任务负责人,可能为 null 表示未分配
 * @param completed  是否完成,false 表示进行中
 * @param priority   优先级,1 最高,3 最低,默认 2
 */
data class CourseTask(
    val id: Int,
    val title: String,
    val owner: String?,
    val completed: Boolean = false,
    val priority: Int = 2,
)

/**
 * 把 [CourseTask.owner] 转为安全的展示文字。
 *
 * 空安全处理链(从左到右短路返回):
 * 1. `task.owner?.`               —— owner 是 null,整条链直接返回 null
 * 2. `?.trim()?.takeIf { ... }`   —— 去空格,空字符串返回 null
 * 3. `?: "未分配"`                —— Elvis,左侧 null 返回右侧默认
 *
 * 全程不使用 `!!`,所有可空类型都用安全调用链。
 */
fun displayOwner(task: CourseTask): String =
    task.owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未分配"

/**
 * 示例数据,共 100 条,用来验证长列表滚动。
 *
 * 前 3 条沿用实验一的真实业务数据(含 owner=null 演示空安全分支);
 * 第 4-100 条由循环生成,owner 用轮换的方式让一部分任务处于"未分配"状态。
 *
 * 实验三:这份数据由 [edu.example.mobilecourse.lab4.data.repository.FakeTaskRepository]
 * 在 `getTasks()` 中返回,**不再被 UI 直接引用**,满足验收点"Screen 不直接调用 repository 之外的数据源"。
 */
val sampleTasks: List<CourseTask> = buildList {
    // 前 3 条:沿用实验一,保证验收时"owner=null 显示未分配"分支可见。
    add(CourseTask(id = 1, title = "完成实验三报告", owner = "张三", completed = false, priority = 1))
    add(CourseTask(id = 2, title = "提交代码到 Git", owner = "李四", completed = true, priority = 2))
    add(CourseTask(id = 3, title = "复习 ViewModel 与 StateFlow", owner = null, completed = false, priority = 3))
    // 第 4-100 条:循环填充,每 7 条让 1 条 owner=null,模拟"未分配"任务。
    val owners = listOf("王五", "赵六", "孙七", "周八", "吴九", "郑十")
    for (i in 4..100) {
        val owner: String? = if (i % 7 == 0) null else owners[(i - 4) % owners.size]
        add(
            CourseTask(
                id = i,
                title = "任务 #$i",
                owner = owner,
                completed = i % 11 == 0,           // 每 11 条 1 条已完成
                priority = when (i % 3) {          // 优先级轮换
                    0 -> 1
                    2 -> 3
                    else -> 2
                },
            )
        )
    }
}

/**
 * 空列表样本:实验三步骤 20 要求把 repository 返回 emptyList 测试 Empty 状态。
 * 由 [edu.example.mobilecourse.lab4.data.repository.FakeTaskRepository] 在 emptyMode 开启时返回。
 */
val emptyTasks: List<CourseTask> = emptyList()

/**
 * 根据 taskId 查询单个任务,用于 TaskDetailScreen 展示详情。
 *
 * 实验三:TaskDetail 暂不接入 ViewModel(实验三只要求 Home 四态),仍用此同步函数
 * 从 [sampleTasks] 线性查找;找不到返回 null,TaskDetailScreen 走"任务不存在"边界状态。
 *
 * @return 找不到时返回 null
 */
fun taskById(taskId: Int): CourseTask? =
    sampleTasks.firstOrNull { it.id == taskId }
