package edu.example.mobilecourse.lab1.data

/**
 * 课程任务数据类。
 *
 * 实验一关键点:
 * - owner 字段类型是 String? (可空),用来演示 Kotlin 空安全。
 * - 任务可能暂时没人负责,owner 用 null 表示。
 *
 * @param id         任务 ID
 * @param title      任务标题
 * @param owner      任务负责人,可能为 null 表示未分配
 * @param completed  是否完成,false 表示进行中
 * @param priority   优先级(拓展任务用),1 最高,3 最低,默认 2
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
 * 1. `task.owner?.`      —— owner 是 null,整条链直接返回 null,后面不再执行
 * 2. `?.trim()?.takeIf { it.isNotEmpty() }` —— 去掉首尾空格,如果是空字符串则返回 null
 * 3. `?: "未分配"`       —— Elvis 运算符,左侧为 null 时返回右侧默认值
 *
 * 实验一关键验收点:无无理由 `!!`,所有可空类型都用安全调用链处理。
 */
fun displayOwner(task: CourseTask): String =
    task.owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未分配"

/**
 * 三条示例数据,其中第 3 条的 owner = null,用来演示 [displayOwner] 的空安全分支。
 */
val sampleTasks: List<CourseTask> = listOf(
    CourseTask(id = 1, title = "完成实验报告", owner = "张三", completed = false, priority = 1),
    CourseTask(id = 2, title = "提交代码到 Git", owner = "李四", completed = true, priority = 2),
    CourseTask(id = 3, title = "复习 Kotlin 空安全", owner = null, completed = false, priority = 3),
)
