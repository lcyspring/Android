package edu.example.mobilecourse.ui.navigation

import androidx.navigation.NavGraphBuilder
import androidx.navigation.NavHostController
import androidx.navigation.NavType
import androidx.navigation.compose.composable
import androidx.navigation.navArgument

/**
 * 导航目的地抽象。每个页面只暴露自己的 route 与参数定义，
 * 不直接接触 [NavHostController]，由上层 [composable] 拼装时注入。
 */
interface Destination {
    val route: String
}

/**
 * 首页目的地：不带参数。
 */
object HomeDestination : Destination {
    override val route: String = "home"
}

/**
 * 任务详情目的地：携带 taskId 整型参数。
 * route 字符串中的占位 `{taskId}` 与 [taskIdArg] 的名称保持一致。
 */
object TaskDetailDestination : Destination {
    const val ARG_TASK_ID: String = "taskId"
    override val route: String = "task_detail/{taskId}"

    fun buildRoute(taskId: Int): String = "task_detail/$taskId"

    val taskIdArg = navArgument(ARG_TASK_ID) { type = NavType.IntType }
}

/**
 * 把首页目的地接入 [NavGraphBuilder]。
 * [onNavigateToDetail] 由调用方传入，真正调用 navController.navigate，
 * 这样 HomeScreen 自身永远不持有 NavController。
 */
fun NavGraphBuilder.homeDestination(
    onNavigateToDetail: (Int) -> Unit
) {
    composable(route = HomeDestination.route) {
        // HomeRoute 内部使用 viewModel() 默认创建 HomeViewModel
        edu.example.mobilecourse.ui.home.HomeRoute(
            onNavigate = onNavigateToDetail
        )
    }
}

/**
 * 把详情页目的地接入 [NavGraphBuilder]。NavBackStackEntry 中取参数后传入页面。
 */
fun NavGraphBuilder.taskDetailDestination(
    onBack: () -> Unit
) {
    composable(
        route = TaskDetailDestination.route,
        arguments = listOf(TaskDetailDestination.taskIdArg)
    ) { backStackEntry ->
        val taskId: Int? = backStackEntry.arguments
            ?.getInt(TaskDetailDestination.ARG_TASK_ID)
        edu.example.mobilecourse.ui.taskdetail.TaskDetailRoute(
            taskId = taskId ?: -1,
            onBack = onBack
        )
    }
}
