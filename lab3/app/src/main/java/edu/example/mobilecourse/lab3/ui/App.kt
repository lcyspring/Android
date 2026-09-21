package edu.example.mobilecourse.lab3.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import edu.example.mobilecourse.lab3.data.repository.FakeTaskRepository
import edu.example.mobilecourse.lab3.data.repository.TaskRepository
import edu.example.mobilecourse.lab3.ui.home.HomeRoute
import edu.example.mobilecourse.lab3.ui.navigation.Destination
import edu.example.mobilecourse.lab3.ui.taskdetail.TaskDetailScreen

/**
 * 实验三应用根 Composable。
 *
 * 实验三相对实验二的变化:
 * - 数据不再由顶层常量 `sampleTasks` 直接喂给 HomeScreen,改为 [TaskRepository] 统一提供;
 * - Home 目的地从"直接放 HomeScreen"改为放 [HomeRoute],Route 内创建 [HomeViewModel]
 *   并用 `collectAsStateWithLifecycle` 订阅 `StateFlow<HomeUiState>`;
 * - HomeScreen 变成纯 UI,根据 uiState 的 Loading/Error/Empty/Content 四态渲染;
 * - NavController 仍只在本层持有,HomeRoute 通过 onNavigate 回调上报"想打开 taskId"。
 *
 * 导航关系简图(实验三):
 *
 *     NavController (rememberNavController 持有)
 *          |
 *          v
 *     NavHost(startDestination = HomeDestination.route)
 *       ├── composable("home")            -> HomeRoute(repository, onNavigate)
 *       |     HomeRoute 内 viewModel() -> HomeViewModel(refresh init) -> StateFlow<HomeUiState>
 *       |     HomeScreen(uiState, onAction = viewModel::onAction)
 *       |     onNavigate = { id -> navigate(TaskDetailDestination.createRoute(id)) }
 *       └── composable("task_detail/{taskId}") -> TaskDetailScreen(taskId, onBack)
 *               onBack = { popBackStack() }
 *
 * 验收四态的测试钩子(改 MainActivity 调用参数后重新运行):
 * - Content: `App()`(默认 [FakeTaskRepository],800ms 后返回 100 条)
 * - Loading: 进入瞬间即见(默认进入即 refresh,isLoading=true)
 * - Empty:  `App(overrideRepository = FakeTaskRepository(emptyMode = true))`
 * - Error:  `App(overrideRepository = FakeTaskRepository(errorMode = true))`
 *
 * @param overrideRepository 测试钩子:默认 null 时用 [FakeTaskRepository](Content 态);
 *   传 `FakeTaskRepository(emptyMode = true)` 或 `errorMode = true` 可触发 Empty / Error 态。
 */
@Composable
fun App(
    overrideRepository: TaskRepository? = null,
) {
    val navController = rememberNavController()
    // repository 在 App 层创建并向下传;remember 让它在 overrideRepository 不变时复用同一实例。
    val repository: TaskRepository = remember(overrideRepository) {
        overrideRepository ?: FakeTaskRepository()
    }

    MaterialTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            NavHost(
                navController = navController,
                startDestination = Destination.HomeDestination.route,
            ) {
                // 目的地 1:首页列表(实验三:改用 HomeRoute,内含 ViewModel + StateFlow + 四态 Screen)。
                composable(Destination.HomeDestination.route) {
                    HomeRoute(
                        repository = repository,
                        onNavigate = { taskId ->
                            // ItemClicked 事件最终落到这里:由 App 接成 navigate(...)。
                            navController.navigate(Destination.TaskDetailDestination.createRoute(taskId))
                        },
                    )
                }

                // 目的地 2:任务详情,taskId 是必填 Int 参数(实验三未改造,沿用实验二实现)。
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
