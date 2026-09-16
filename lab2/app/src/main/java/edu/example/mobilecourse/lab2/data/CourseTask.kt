package edu.example.mobilecourse.lab2.data

/**
 * 课程任务数据类。
 *
 * 实验二沿用实验一的数据模型,字段不变,只把示例数据从 3 条扩到 100 条,
 * 用来验证 [LazyColumn] 在长列表下的滚动与稳定 key 复用。
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
 * 实验二示例数据,共 100 条,用来验证长列表滚动。
 *
 * 前 3 条沿用实验一的真实业务数据(含 owner=null 演示空安全分支);
 * 第 4-100 条由循环生成,owner 用轮换的方式让一部分任务处于"未分配"状态,
 * 便于在 TaskDetailScreen 演示不同的展示分支。
 */
val sampleTasks: List<CourseTask> = buildList {
    // 前 3 条:沿用实验一,保证验收时"owner=null 显示未分配"分支可见。
    add(CourseTask(id = 1, title = "完成实验二报告", owner = "张三", completed = false, priority = 1))
    add(CourseTask(id = 2, title = "提交代码到 Git", owner = "李四", completed = true, priority = 2))
    add(CourseTask(id = 3, title = "复习 Kotlin 空安全", owner = null, completed = false, priority = 3))
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
 * 空列表样本:实验二步骤 13 要求测试"无数据"状态,EmptyContent 必须能展示。
 * 由 [edu.example.mobilecourse.lab2.ui.home.HomeScreen] 在传入空 List 时触发。
 */
val emptyTasks: List<CourseTask> = emptyList()

/**
 * 根据 taskId 查询单个任务,用于 TaskDetailScreen 展示详情。
 *
 * 实验二验收点:导航能带入正确 taskId,TaskDetail 能据此拿到对应数据。
 * 这里对 100 条样本做线性查找;实验三会把数据移到 Repository,改成分组查找。
 *
 * @return 找不到时返回 null,TaskDetailScreen 走"任务不存在"分支。
 */
fun taskById(taskId: Int): CourseTask? =
    sampleTasks.firstOrNull { it.id == taskId }
