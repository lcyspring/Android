package edu.example.mobilecourse.ui

import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.Surface
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.navigation.NavHostController
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.rememberNavController
import edu.example.mobilecourse.ui.navigation.HomeDestination
import edu.example.mobilecourse.ui.navigation.TaskDetailDestination
import edu.example.mobilecourse.ui.navigation.homeDestination
import edu.example.mobilecourse.ui.navigation.taskDetailDestination
import edu.example.mobilecourse.ui.theme.MyApplicationTheme

/**
 * App：整个应用的根 Composable。负责：
 *  1. 套上主题 [MyApplicationTheme]；
 *  2. 创建并持有 [NavHostController]；
 *  3. 在 [NavHost] 中按 route 注册各 [Destination]。
 *
 * 页面（HomeRoute / TaskDetailRoute）均不持有 NavController：
 * 点击列表后通过 `onNavigate(id)` 回调到这里，由本层调用 `navController.navigate(...)`。
 */
@Composable
fun App(
    navController: NavHostController = rememberNavController()
) {
    MyApplicationTheme {
        Surface(modifier = Modifier.fillMaxSize()) {
            NavHost(
                navController = navController,
                startDestination = HomeDestination.route
            ) {
                homeDestination(
                    onNavigateToDetail = { taskId ->
                        navController.navigate(TaskDetailDestination.buildRoute(taskId))
                    }
                )
                taskDetailDestination(
                    onBack = { navController.popBackStack() }
                )
            }
        }
    }
}
