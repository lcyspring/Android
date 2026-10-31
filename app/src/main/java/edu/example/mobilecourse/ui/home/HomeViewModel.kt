package edu.example.mobilecourse.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import edu.example.mobilecourse.CourseTask
import edu.example.mobilecourse.data.repository.NetworkTaskRepository
import edu.example.mobilecourse.data.repository.SettingsRepository
import edu.example.mobilecourse.data.repository.TaskRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch

/**
 * 首页 ViewModel：持有 [HomeUiState] 并通过只读 [StateFlow] 向下分发。
 *
 * 单向数据流（UDF）三件事都在这里完成：
 *  1. 持有状态：[_uiState] 为可变内部源，[uiState] 为对外暴露的只读流；
 *  2. 处理事件：[onAction] 收到 [HomeAction] 后决定调用 [refresh]、切换筛选或忽略；
 *  3. 访问数据：网络通过 [TaskRepository]，本地偏好通过 [SettingsRepository]；
 *     两者都在 ViewModel 层完成，Composable 不直接读写。
 */
class HomeViewModel(
    private val repository: TaskRepository,
    private val settingsRepository: SettingsRepository,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState(isLoading = true))
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    /** 最近一次网络返回的原始列表（未过滤），切换"仅看未完成"时用它立即重新过滤 */
    private var allTasks: List<CourseTask> = emptyList()

    init {
        // 1. 先读 DataStore 中的筛选偏好
        // 2. 然后拉取网络任务
        viewModelScope.launch {
            val savedFilter = settingsRepository.showOnlyIncompleteFlow.first()
            _uiState.value = _uiState.value.copy(showOnlyIncomplete = savedFilter)
            refresh()
        }
    }

    fun onAction(action: HomeAction) {
        when (action) {
            is HomeAction.Refresh -> refresh()

            is HomeAction.ItemClicked -> {
                // 委托给上层导航：ViewModel 不持有 NavController
            }

            is HomeAction.ToggleShowOnlyIncomplete -> {
                viewModelScope.launch {
                    // 1. 写入 DataStore
                    settingsRepository.setShowOnlyIncomplete(action.checked)
                    // 2. 更新开关状态，并对已加载的列表立即重新过滤（UI 立即响应）
                    _uiState.value = _uiState.value.copy(
                        showOnlyIncomplete = action.checked,
                        tasks = applyFilter(allTasks, action.checked),
                    )
                }
            }

            is HomeAction.CameraPermissionRequested -> {
                // 事件已收到；真正向系统申请由 Route 层完成。
                // 此处可做日志埋点或权限理由展示的前置逻辑。
            }
        }
    }

    fun refresh() {
        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)

        viewModelScope.launch {
            runCatching { repository.getTasks() }
                .onSuccess { tasks ->
                    allTasks = tasks
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        tasks = applyFilter(tasks, _uiState.value.showOnlyIncomplete),
                        errorMessage = null,
                    )
                }
                .onFailure { throwable ->
                    _uiState.value = _uiState.value.copy(
                        isLoading = false,
                        tasks = emptyList(),
                        errorMessage = throwable.message ?: "未知错误",
                    )
                }
        }
    }

    private fun applyFilter(tasks: List<CourseTask>, onlyIncomplete: Boolean): List<CourseTask> {
        return if (onlyIncomplete) tasks.filter { !it.completed } else tasks
    }

    /**
     * 工厂：默认使用网络实现 [NetworkTaskRepository]；
     * 如需离线演示 Error / Empty，可临时替换为 FakeTaskRepository。
     */
    class Factory(
        private val settingsRepository: SettingsRepository,
        private val repository: TaskRepository = NetworkTaskRepository(),
    ) : ViewModelProvider.Factory {
        @Suppress("UNCHECKED_CAST")
        override fun <T : ViewModel> create(modelClass: Class<T>): T {
            if (modelClass.isAssignableFrom(HomeViewModel::class.java)) {
                return HomeViewModel(repository, settingsRepository) as T
            }
            throw IllegalArgumentException("Unknown ViewModel class: ${modelClass.name}")
        }
    }
}
