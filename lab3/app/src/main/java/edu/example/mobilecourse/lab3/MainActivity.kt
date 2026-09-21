package edu.example.mobilecourse.lab3

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.MaterialTheme
import edu.example.mobilecourse.lab3.ui.App

/**
 * 实验三入口 Activity。
 *
 * 实验三关键重构:把首页状态从 Composable 移到 [edu.example.mobilecourse.lab3.ui.home.HomeViewModel],
 * 数据从顶层常量改为 [edu.example.mobilecourse.lab3.data.repository.TaskRepository] 统一提供,
 * Home 目的地由 [edu.example.mobilecourse.lab3.ui.home.HomeRoute] 用 `collectAsStateWithLifecycle`
 * 订阅 `StateFlow<HomeUiState>`,MainActivity 仍只负责挂载 Compose 树。
 *
 * 验收四态(改 setContent 内的 App 参数后重新运行):
 * - Content: `App()`(默认 FakeTaskRepository)
 * - Empty:  `App(overrideRepository = FakeTaskRepository(emptyMode = true))`
 * - Error:  `App(overrideRepository = FakeTaskRepository(errorMode = true))`
 * - Loading: 进入瞬间即见
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MaterialTheme {
                App()
            }
        }
    }
}
