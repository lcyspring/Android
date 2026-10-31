package edu.example.mobilecourse.ui.home

/**
 * 首页事件（UI → ViewModel）统一收口。
 *
 * 单向数据流约定：事件向上传递到 ViewModel，由 ViewModel 决定如何更新 [HomeUiState]。
 * 屏幕不直接调用 Repository，也不直接修改状态字段。
 */
sealed interface HomeAction {
    /** 重新拉取数据：用于初次进入、下拉刷新、错误后重试。 */
    data object Refresh : HomeAction

    /** 列表项被点击：交由上层导航跳转到 TaskDetail。 */
    data class ItemClicked(val id: Int) : HomeAction

    /** 切换“仅看未完成任务”筛选开关。 */
    data class ToggleShowOnlyIncomplete(val checked: Boolean) : HomeAction

    /** 用户点击了相机图标：ViewModel 负责记录事件并转交 Route 层申请权限。 */
    data object CameraPermissionRequested : HomeAction
}
