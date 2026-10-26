package edu.example.mobilecourse.lab3.ui.home

import edu.example.mobilecourse.lab3.data.model.CourseTask

/**
 * 首页 UI 状态(指导书 3.2 UiState 模板 + 实验三步骤 14)。
 *
 * 单一数据源,表达 Loading / Error / Empty / Content 四态(指导书"四态模板"):
 * - [isLoading] = true                -> LoadingContent
 * - [errorMessage] != null            -> ErrorContent(message, onRetry)
 * - [tasks].isEmpty() 且非 loading 且无 error -> EmptyContent
 * - 其他                               -> LazyColumn(tasks)
 *
 * 用 Boolean + nullable errorMessage 的组合(指导书起始代码即此形态),
 * 拓展任务可改成 sealed interface,比较优缺点见实验报告"思考"栏目。
 *
 * @param isLoading     是否正在加载
 * @param tasks         已加载的任务列表,空 List 表示无数据
 * @param errorMessage  非 null 表示加载失败,展示在 ErrorContent
 */
data class HomeUiState(
    val isLoading: Boolean = false,
    val tasks: List<CourseTask> = emptyList(),
    val errorMessage: String? = null,
)

/**
 * 首页用户事件(指导书 3.2 UiState / Action 模板)。
 *
 * 单向数据流 UDF 的"事件向上":Screen 不直接改 [HomeUiState],
 * 只把用户意图封装成 [HomeAction] 发给 [HomeViewModel.onAction],
 * 由 ViewModel 决定如何更新 StateFlow(再向下流向 Screen)。
 *
 * - [Refresh]      用户点"重试"/下拉刷新,让 ViewModel 重新调 repository.getTasks()
 * - [ItemClicked]  用户点某张卡片,参数 taskId,ViewModel 不改 state,只把事件继续向上传给 Route/导航
 */
sealed interface HomeAction {
    data object Refresh : HomeAction
    data class ItemClicked(val taskId: Int) : HomeAction
}
