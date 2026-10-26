package edu.example.mobilecourse.lab4.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.remember
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import edu.example.mobilecourse.lab4.data.preferences.UserPreferences
import edu.example.mobilecourse.lab4.data.repository.FakeTaskRepository
import edu.example.mobilecourse.lab4.data.repository.NetworkTaskRepository
import edu.example.mobilecourse.lab4.data.repository.TaskRepository
import edu.example.mobilecourse.lab4.ui.home.HomeRoute
import edu.example.mobilecourse.lab4.ui.navigation.Destination
import edu.example.mobilecourse.lab4.ui.taskdetail.TaskDetailScreen

/**
 * 实验四应用根 Composable(扩展:深色模式 + DataStore + 相机权限)。
 *
 * 实验四相对实验三的变化:
 * - 默认数据源从 FakeTaskRepository 换成 NetworkTaskRepository(JSONPlaceholder 网络 API)
 * - 注入 [UserPreferences],HomeRoute collect DataStore 的 darkModeFlow,驱动 MaterialTheme 切换
 * - 注入 [onRequestCamera] 回调,HomeRoute/ViewModel 接收相机按钮事件后向上送出
 *
 * 验收点:
 * - 网络成功/失败均有明确 UI(HomeUiState 四态,NetworkTaskRepository 抛异常走 Error + Retry)
 * - 数据访问仍通过 Repository(NetworkTaskRepository 实现 TaskRepository 接口)
 * - DataStore 不在 Composable 中直接读写(UserPreferences 是唯一入口,Composable 只看 StateFlow)
 *
 * 验收四态测试钩子(改 MainActivity 调用 App 参数后重新运行):
 * - 网络成功:  App()                         (默认 NetworkTaskRepository)
 * - 网络断网:  App(overrideRepository = FakeTaskRepository(errorMode = true))  (模拟网络失败)
 * - 空数据:    App(overrideRepository = FakeTaskRepository(emptyMode = true))
 *
 * @param overrideRepository 测试钩子:默认 null 时用 NetworkTaskRepository(网络实现);
 *   传 FakeTaskRepository(errorMode = true) 可模拟断网/错误地址,验证 Error + Retry。
 * @param prefs               DataStore 偏好存储,由 MainActivity 初始化后传入
 * @param onRequestCamera     点击相机按钮时的回调,由 MainActivity 接 ActivityResultLauncher
 */
@Composable
fun App(
    overrideRepository: TaskRepository? = null,
    prefs: UserPreferences,
    onRequestCamera: () -> Unit = {},
) {
    val navController = rememberNavController()
    val repository: TaskRepository = remember(overrideRepository) {
        overrideRepository ?: NetworkTaskRepository()
    }

    // 深色模式:从 DataStore collect,变化自动驱动 MaterialTheme 切换
    val darkMode by prefs.darkModeFlow.collectAsStateWithLifecycle(initialValue = false)

    val colorScheme = if (darkMode) darkColorScheme() else lightColorScheme()

    MaterialTheme(colorScheme = colorScheme) {
        Surface(modifier = Modifier.fillMaxSize()) {
            NavHost(
                navController = navController,
                startDestination = Destination.HomeDestination.route,
            ) {
                // 目的地 1:首页(实验四:网络 Repository + DataStore 偏好 + 相机权限)
                composable(Destination.HomeDestination.route) {
                    HomeRoute(
                        repository = repository,
                        onNavigate = { taskId ->
                            navController.navigate(Destination.TaskDetailDestination.createRoute(taskId))
                        },
                        prefs = prefs,
                        onRequestCamera = onRequestCamera,
                    )
                }

                // 目的地 2:任务详情(沿用实验二/三实现)
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
