package edu.example.mobilecourse.lab2.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import edu.example.mobilecourse.lab2.data.emptyTasks
import edu.example.mobilecourse.lab2.data.sampleTasks
import edu.example.mobilecourse.lab2.ui.home.HomeScreen
import edu.example.mobilecourse.lab2.ui.navigation.Destination
import edu.example.mobilecourse.lab2.ui.taskdetail.TaskDetailScreen

/**
 * 实验二应用根 Composable(指导书步骤 11:在 App 中连接 NavHost 两个目的地)。
 *
 * 导航关系简图:
 *
 *     NavController (本函数用 rememberNavController 持有)
 *          |
 *          v
 *     NavHost(startDestination = HomeDestination.route)
 *       ├── composable("home")            -> HomeScreen
 *       |       onOpenTask = { id -> navigate(TaskDetailDestination.createRoute(id)) }
 *       └── composable("task_detail/{taskId}") -> TaskDetailScreen
 *               taskId 由 NavBackStackEntry.arguments 解析后传入
 *               onBack = { popBackStack() }
 *
 * 实验二关键解耦点:
 * - NavController 只在 App 这一层持有,HomeScreen 和 TaskDetailScreen 都不直接访问它,
 *   满足验收点"不直接访问 TaskCard / Screen 的 NavController"。
 * - HomeScreen 通过 onOpenTask(id) 回调上报"用户想打开哪个 taskId",
 *   App 把它接成 navigate(...);TaskDetailScreen 通过 onBack 回调上报"用户想返回"。
 * - 100 条样本由 App 一次性传入,EmptyContent 由 HomeScreen 内部分支渲染。
 *
 * 实验三预告:这一层会改成 Route/Screen 拆分 + HomeViewModel 注入,数据从 sampleTasks 改为
 * StateFlow<HomeUiState>,但 NavHost 的连接方式与本函数结构基本一致。
 *
 * @param overrideTasks 测试钩子:默认 null 时用 100 条样本;传 [emptyTasks] 可触发空状态。
 */
@Composable
fun App(
    overrideTasks: List<edu.example.mobilecourse.lab2.data.CourseTask>? = null,
) {
    val navController = rememberNavController()
    val tasks = overrideTasks ?: sampleTasks

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            NavHost(
                navController = navController,
                startDestination = Destination.HomeDestination.route,
            ) {
                // 目的地 1:首页列表。
                composable(Destination.HomeDestination.route) {
                    HomeScreen(
                        tasks = tasks,
                        onOpenTask = { taskId ->
                            // 步骤 12:把 TaskCard.onOpenTask 接到导航。
                            navController.navigate(Destination.TaskDetailDestination.createRoute(taskId))
                        },
                        onRefresh = {
                            // 空状态重试:实验二直接切回 100 条样本。
                            // 这里通过返回再进 Home 触发重组(实验三会改成 ViewModel.refresh)。
                        },
                    )
                }

                // 目的地 2:任务详情,taskId 是必填 Int 参数。
                composable(
                    route = Destination.TaskDetailDestination.route,
                    arguments = listOf(
                        navArgument(Destination.TaskDetailDestination.ARG_TASK_ID) {
                            type = NavType.IntType
                        }
                    ),
                ) { backStackEntry ->
                    val taskId: Int = backStackEntry.arguments
                        ?.getInt(Destination.TaskDetailDestination.ARG_TASK_ID)
                        ?: -1
                    TaskDetailScreen(
                        taskId = taskId,
                        onBack = { navController.popBackStack() },
                    )
                }
            }
        }
    }
}
