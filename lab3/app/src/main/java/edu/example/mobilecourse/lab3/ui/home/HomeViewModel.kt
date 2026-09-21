package edu.example.mobilecourse.lab3.ui.home

import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import edu.example.mobilecourse.lab3.data.repository.TaskRepository
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.asStateFlow
import kotlinx.coroutines.launch

/**
 * 首页 ViewModel(指导书 3.2 ViewModel 模板 + 实验三步骤 16/17)。
 *
 * 单向数据流 UDF 的"状态在哪里":**在这里**。本类持有 [HomeUiState],
 * 通过只读 [uiState] 对外暴露(验收点"ViewModel 公开只读 StateFlow")。
 *
 * 职责:
 * 1. 初始化时调 [refresh] 加载数据(步骤 16)。
 * 2. [onAction] 收事件:Refresh 重载;ItemClicked 不改 state,只回调 [onOpenTask] 让上层导航。
 * 3. 用 [viewModelScope] 协程调 repository(步骤 17),catch 异常转成 errorMessage,
 *    保证"失败后可重试且不会崩溃"(验收点)。
 *
 * 不持有 NavController —— 导航由 Route/App 层基于 [onOpenTask] 回调执行,
 * 满足"页面组件不持有导航控制器"的解耦约定(沿用实验二)。
 *
 * @param repository     数据源,默认 [FakeTaskRepository](实验四会换成网络实现)
 * @param onOpenTask     用户点某条任务时的导航回调,参数 taskId,由 Route 注入
 */
class HomeViewModel(
    private val repository: TaskRepository,
    private val onOpenTask: (Int) -> Unit,
) : ViewModel() {

    // 只读对外暴露;内部通过 _uiState.update {} 修改。
    private val _uiState = MutableStateFlow(HomeUiState())
    val uiState: StateFlow<HomeUiState> = _uiState.asStateFlow()

    init {
        // 步骤 16:初始化时调用 refresh。
        refresh()
    }

    /**
     * 步骤 17:用 viewModelScope.launch 加载数据。
     *
     * 进入时先把 isLoading 置 true(让 UI 立刻显示 LoadingContent,即使是重试);
     * 成功 -> 写入 tasks、清空 errorMessage;失败 -> 写入 errorMessage、保留旧 tasks。
     */
    fun refresh() {
        _uiState.value = _uiState.value.copy(isLoading = true, errorMessage = null)
        viewModelScope.launch {
            try {
                val tasks = repository.getTasks()
                _uiState.value = HomeUiState(isLoading = false, tasks = tasks, errorMessage = null)
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
     * 统一事件入口(指导书 onAction = viewModel::onAction 模板)。
     *
     * - [HomeAction.Refresh]     -> 重载
     * - [HomeAction.ItemClicked] -> 不改 state,只把 taskId 通过 onOpenTask 向上送出
     */
    fun onAction(action: HomeAction) {
        when (action) {
            is HomeAction.Refresh -> refresh()
            is HomeAction.ItemClicked -> onOpenTask(action.taskId)
        }
    }
}
