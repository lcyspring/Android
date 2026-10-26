package edu.example.mobilecourse.lab4.ui.home

import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import edu.example.mobilecourse.lab4.data.preferences.UserPreferences
import edu.example.mobilecourse.lab4.data.repository.TaskRepository

/**
 * 首页 Route(实验四扩展:UserPreferences + 相机权限回调)。
 *
 * 职责:把 [HomeViewModel] 与 [HomeScreen] 连起来,额外注入:
 * - [prefs]  DataStore 偏好,ViewModel collect 两个 Flow
 * - [onRequestCamera]  相机权限回调,ViewModel 收到 RequestCameraPermission 事件时向上送出
 * - filteredTasks  从 uiState.tasks + showOnlyIncomplete 筛选,保持 Screen 纯 UI
 *
 * @param repository        数据源,由 App 注入(实验四默认 NetworkTaskRepository)
 * @param onNavigate        点某条任务时的导航回调
 * @param prefs             DataStore 偏好存储
 * @param onRequestCamera   点击相机按钮时的回调,由 App/MainActivity 层调用 ActivityResultLauncher
 */
@Composable
fun HomeRoute(
    repository: TaskRepository,
    onNavigate: (Int) -> Unit,
    prefs: UserPreferences,
    onRequestCamera: () -> Unit,
) {
    val viewModel: HomeViewModel = viewModel(
        factory = object : ViewModelProvider.Factory {
            @Suppress("UNCHECKED_CAST")
            override fun <T : ViewModel> create(modelClass: Class<T>): T =
                HomeViewModel(
                    repository = repository,
                    onOpenTask = onNavigate,
                    prefs = prefs,
                    onRequestCamera = onRequestCamera,
                ) as T
        }
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()

    // 筛选在 Route 层完成,Screen 保持纯 UI(验收点"不在 Composable 中直接读写 DataStore")
    val filteredTasks = if (uiState.showOnlyIncomplete) {
        uiState.tasks.filter { !it.completed }
    } else {
        uiState.tasks
    }

    HomeScreen(
        uiState = uiState,
        filteredTasks = filteredTasks,
        onAction = viewModel::onAction,
    )
}
