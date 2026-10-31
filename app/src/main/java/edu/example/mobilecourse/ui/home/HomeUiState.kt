package edu.example.mobilecourse.ui.home

import edu.example.mobilecourse.CourseTask

/**
 * 首页 UI 状态：不可变数据类。
 *
 * 五态用四个字段的组合表达：
 *   - [isLoading] = true                → Loading
 *   - [errorMessage] != null             → Error（[tasks] 应为空）
 *   - [tasks].isEmpty() 且非加载/出错     → Empty
 *   - 其它                                → Content
 *   - [showOnlyIncomplete]               → 筛选标记（是否只看未完成）
 *
 * 该状态由 ViewModel 持有并通过 StateFlow 向下分发，Screen 端只读取不修改。
 */
data class HomeUiState(
    val isLoading: Boolean = false,
    val tasks: List<CourseTask> = emptyList(),
    val errorMessage: String? = null,
    val showOnlyIncomplete: Boolean = false,
)
