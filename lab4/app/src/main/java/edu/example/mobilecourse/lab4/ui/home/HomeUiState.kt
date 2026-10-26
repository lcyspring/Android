package edu.example.mobilecourse.lab4.ui.home

import edu.example.mobilecourse.lab4.data.model.CourseTask

/**
 * 首页 UI 状态(实验四扩展:增加 DataStore 偏好字段)。
 *
 * 实验三已有字段:isLoading / tasks / errorMessage(四态)。
 * 实验四新增字段:
 * - [showOnlyIncomplete]  "仅看未完成任务"筛选,来自 DataStore
 * - [darkMode]            深色模式开关,来自 DataStore
 *
 * 四态判定顺序不变(Loading → Error → Empty → Content),
 * 新增的两个字段在 Content 态影响列表展示,在 Empty 态可能触发额外筛选。
 */
data class HomeUiState(
    val isLoading: Boolean = false,
    val tasks: List<CourseTask> = emptyList(),
    val errorMessage: String? = null,
    val showOnlyIncomplete: Boolean = false,   // 实验四新增:DataStore 偏好
    val darkMode: Boolean = false,             // 实验四新增:DataStore 偏好
)

/**
 * 首页用户事件(实验四扩展:增加偏好切换 + 相机权限)。
 *
 * 实验三已有:Refresh / ItemClicked。
 * 实验四新增:
 * - ToggleIncompleteFilter  切换"仅看未完成"筛选(写 DataStore)
 * - ToggleDarkMode          切换深色模式(写 DataStore)
 * - RequestCameraPermission 点击相机按钮,由 Route/App 层调用 ActivityResultLauncher
 */
sealed interface HomeAction {
    data object Refresh : HomeAction
    data class ItemClicked(val taskId: Int) : HomeAction
    data object ToggleIncompleteFilter : HomeAction       // 实验四新增
    data object ToggleDarkMode : HomeAction               // 实验四新增
    data object RequestCameraPermission : HomeAction      // 实验四新增
}
