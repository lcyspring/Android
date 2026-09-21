package edu.example.mobilecourse.lab3.ui.home

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import edu.example.mobilecourse.lab3.data.repository.TaskRepository

/**
 * 首页 Route(指导书 3.2 Route/Screen 模板 + 实验三步骤 18)。
 *
 * 职责:把 [HomeViewModel] 与 [HomeScreen] 连起来 ——
 * 1. 用 [viewModel] 创建/取回 ViewModel(绑定到当前 NavBackStackEntry,配置变化时存活);
 * 2. [collectAsStateWithLifecycle] 把 [HomeViewModel.uiState] 这个 StateFlow 订阅成 Compose State,
 *    并在生命周期低于 STARTED 时停止收集,避免后台浪费;
 * 3. 把事件入口接成 `viewModel::onAction`,把导航回调 [onNavigate] 注入 ViewModel。
 *
 * 单向数据流 UDF 的方向(指导书 A 实验目标):
 * - State 向下:uiState 从 ViewModel 流向 HomeScreen;
 * - Event 向上:HomeScreen 把 Refresh / ItemClicked 封装成 [HomeAction] 通过 onAction 送回 ViewModel,
 *   ItemClicked 经 ViewModel.onOpenTask 回调到本层的 [onNavigate],最终由 App 接成 navigate(...)。
 *
 * @param repository 数据源,由 App 注入(默认 FakeTaskRepository,验收时切换 emptyMode/errorMode)
 * @param onNavigate 点某条任务时的导航回调,参数 taskId,App 接成 navigate(TaskDetailDestination.createRoute(id))
 */
@Composable
fun HomeRoute(
    repository: TaskRepository,
    onNavigate: (Int) -> Unit,
) {
    // viewModel() 绑定当前 NavBackStackEntry;factory 在第一次创建时执行,之后复用同一 ViewModel。
    // 用经典 ViewModelProvider.Factory(而非 viewModelFactory DSL),API 覆盖面更广、兼容性更稳。
    val viewModel: HomeViewModel = viewModel(
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                HomeViewModel(repository = repository, onOpenTask = onNavigate) as T
        }
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeScreen(
        uiState = uiState,
        onAction = viewModel::onAction,
    )
}
