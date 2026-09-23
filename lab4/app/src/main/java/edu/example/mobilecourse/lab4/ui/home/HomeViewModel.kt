package edu.example.mobilecourse.lab4.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import edu.example.mobilecourse.lab4.data.preferences.UserPreferences
import edu.example.mobilecourse.lab4.data.repository.TaskRepository
import kotlinx.coroutines.ExperimentalCoroutinesApi
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch

/**
 * 首页 ViewModel(实验四扩展:DataStore 偏好 + 相机权限事件)。
 *
 * 单向数据流 UDF 的"状态在哪里":**在这里**。
 *
 * 实验三已有:refresh / onAction(Refresh + ItemClicked) / _uiState 只读暴露。
 * 实验四新增:
 * - 接收 [UserPreferences],在 init 中 collect 两个 DataStore Flow 并写入 _uiState。
 * - onAction 处理三个新事件:ToggleIncompleteFilter / ToggleDarkMode(写 DataStore)、
 *   RequestCameraPermission(不改 state,只把事件通过 [onRequestCamera] 回调向上送出)。
 *
 * 验收点:
 * - 数据访问仍通过 Repository(NetworkTaskRepository 替换 FakeTaskRepository,接口不变)。
 * - DataStore 不在 Composable 中直接读写(Composable 只从 uiState 读偏好、通过 onAction 写)。
 *
 * @param repository      数据源,默认 NetworkTaskRepository(实验四网络实现)
 * @param onOpenTask      用户点某条任务时的导航回调
 * @param prefs           DataStore 偏好存储入口
 * @param onRequestCamera 点击相机按钮时的回调,由 Route/App 层调用 ActivityResultLauncher
 */
@OptIn(ExperimentalCoroutinesApi::class)
class HomeViewModel(
    private val repository: TaskRepository,
    private val onOpenTask: (Int) -> Unit,
    private val prefs: UserPreferences,
    private val onRequestCamera: () -> Unit,
) : ViewModel() {

    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        // 实验三:加载网络数据
        refresh()

        // 实验四:collect DataStore 偏好,变化自动反映到 uiState
        viewModelScope.launch {
            prefs.showOnlyIncompleteFlow.collect { enabled ->
                _uiState.value = _uiState.value.copy(showOnlyIncomplete = enabled)
            }
        }
        viewModelScope.launch {
            prefs.darkModeFlow.collect { enabled ->
                _uiState.value = _uiState.value.copy(darkMode = enabled)
            }
        }
    }

    /**
     * 加载数据(实验三步骤 17,实验四换成 NetworkTaskRepository)。
     */
    fun refresh() {
        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
        viewModelScope.launch {
            try {
                val tasks = repository.getTasks()
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    tasks = tasks,
                    errorMessage = null,
                )
            } catch (e: Throwable) {
                // 失败不崩溃:把异常转成可展示文案,Retry 按钮再触发 refresh。
                _uiState.value = _uiState.value.copy(
                    isLoading = false,
                    errorMessage = e.message ?: "加载失败",
                )
            }
        }
    }

    /**
     * 事件入口(实验四扩展:新增三个事件)。
     */
    fun onAction(action: HomeAction) {
        when (action) {
            is HomeAction.Refresh -> refresh()

            is HomeAction.ItemClicked -> onOpenTask(action.taskId)

            // 实验四:写 DataStore(不在 Composable 直写,验收点)
            is HomeAction.ToggleIncompleteFilter -> {
                viewModelScope.launch {
                    val newVal = !_uiState.value.showOnlyIncomplete
                    prefs.setShowOnlyIncomplete(newVal)
                    // DataStore flow collect 会自动更新 uiState,这里直接改也可以,双保险
                    _uiState.value = _uiState.value.copy(showOnlyIncomplete = newVal)
                }
            }

            is HomeAction.ToggleDarkMode -> {
                viewModelScope.launch {
                    val newVal = !_uiState.value.darkMode
                    prefs.setDarkMode(newVal)
                    _uiState.value = _uiState.value.copy(darkMode = newVal)
                }
            }

            // 实验四:相机权限请求不改 state,交给 Route/App 层 ActivityResultLauncher
            is HomeAction.RequestCameraPermission -> onRequestCamera()
        }
    }

    /**
     * 根据 showOnlyIncomplete 筛选后的任务列表(Content 态调用)。
     * 不存进 _uiState.tasks(保持原始数据),避免筛选状态和数据源混淆。
     */
    fun filteredTasks(): List<edu.example.mobilecourse.lab4.data.model.CourseTask> {
        return if (_uiState.value.showOnlyIncomplete) {
            _uiState.value.tasks.filter { !it.completed }
        } else {
            _uiState.value.tasks
        }
    }
}
