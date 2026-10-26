package edu.example.mobilecourse.lab3.ui.navigation

/**
 * 实验二导航目的地定义(指导书步骤 10)。
 *
 * 设计动机(指导书"统一模板" + 验收点"导航参数正确"):
 * - 每个目的地用一个 [Destination] 对象集中表达 route 模板 + 参数键 + 拼参方法,
 *   HomeScreen 不需要拼字符串,TaskDetailScreen 不需要自己解析参数名,避免拼写不一致。
 * - HomeDestination 无参,route = "home",作为 NavHost 的 startDestination。
 * - TaskDetailDestination 带一个 taskId,route = "task_detail/{taskId}",占位符由 NavHost 自动解析。
 * - 命名遵循指导书统一约定:XxxDestination。
 *
 * 关系简图(实验报告"设计/类关系"栏目会贴):
 *
 *     NavHost (startDestination = HomeDestination.route)
 *       ├── composable(HomeDestination.route)        -> HomeScreen(onOpenTask = navigate(...))
 *       └── composable(TaskDetailDestination.route)   -> TaskDetailScreen(taskId)
 *
 *     NavController 由 App 持有,Screen 不直接访问 —— 满足验收点"不直接访问 NavController"。
 */
sealed class Destination(val route: String) {
    /** 首页(列表),无参。 */
    object HomeDestination : Destination(route = "home")

    /** 任务详情页,带 taskId 参数,route 模板含占位符。 */
    object TaskDetailDestination : Destination(route = "task_detail/{taskId}") {
        /** 参数键,NavBackStackEntry 取参数时用,TaskDetailScreen 也用它读取。 */
        const val ARG_TASK_ID = "taskId"

        /** HomeScreen 拼参时调用,把 taskId 代入占位符,生成形如 "task_detail/7" 的具体路由。 */
        fun createRoute(taskId: Int): String = "task_detail/$taskId"
    }
}
