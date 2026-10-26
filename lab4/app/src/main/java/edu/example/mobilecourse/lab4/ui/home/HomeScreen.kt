package edu.example.mobilecourse.lab4.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CameraAlt
import androidx.compose.material.icons.filled.DarkMode
import androidx.compose.material.icons.filled.LightMode
import androidx.compose.material.icons.filled.FilterAlt
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import edu.example.mobilecourse.lab4.data.model.CourseTask
import edu.example.mobilecourse.lab4.data.model.displayOwner
import edu.example.mobilecourse.lab4.data.model.emptyTasks
import edu.example.mobilecourse.lab4.data.model.sampleTasks
import edu.example.mobilecourse.lab4.ui.TaskCard

/**
 * 首页 Screen(实验四扩展:三个按钮 + 筛选逻辑)。
 *
 * **纯 UI**:只根据 [uiState] 渲染、把事件封装成 [HomeAction] 通过 [onAction] 向上发送。
 * 不持有 ViewModel、不调 repository、不直接读写 DataStore(验收点)。
 *
 * 实验四新增 TopAppBar 右侧三个 IconButton:
 * - 筛选:ToggleIncompleteFilter(仅看未完成)
 * - 深色/浅色:ToggleDarkMode
 * - 相机:RequestCameraPermission(运行时权限)
 *
 * 实验四 Content 态筛选:[filteredTasks] 参数由 HomeRoute 传入(或 HomeViewModel.filteredTasks()),
 * 本 Screen 不调 ViewModel 方法,保持纯函数。
 *
 * @param uiState      来自 HomeViewModel 的 StateFlow
 * @param filteredTasks 筛选后的任务列表(Content 态使用,Empty 态仍用 uiState.tasks)
 * @param onAction     事件入口,接 HomeViewModel::onAction
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    uiState: HomeUiState,
    filteredTasks: List<CourseTask>,
    onAction: (HomeAction) -> Unit,
) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = {
                    val count = if (uiState.showOnlyIncomplete) "未完成${filteredTasks.size}" else "${uiState.tasks.size}"
                    Text("实验四 · 任务列表($count)")
                },
                actions = {
                    // 实验四:筛选按钮
                    IconButton(onClick = { onAction(HomeAction.ToggleIncompleteFilter) }) {
                        Icon(
                            imageVector = Icons.Filled.FilterAlt,
                            contentDescription = if (uiState.showOnlyIncomplete) "显示全部" else "仅看未完成",
                            tint = if (uiState.showOnlyIncomplete) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.onSurface,
                        )
                    }
                    // 实验四:深色模式切换
                    IconButton(onClick = { onAction(HomeAction.ToggleDarkMode) }) {
                        Icon(
                            imageVector = if (uiState.darkMode) Icons.Filled.LightMode else Icons.Filled.DarkMode,
                            contentDescription = if (uiState.darkMode) "切换浅色模式" else "切换深色模式",
                        )
                    }
                    // 实验四:相机运行时权限按钮
                    IconButton(onClick = { onAction(HomeAction.RequestCameraPermission) }) {
                        Icon(
                            imageVector = Icons.Filled.CameraAlt,
                            contentDescription = "申请相机权限",
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        when {
            // 分支 1:Loading —— HomeViewModel.refresh() 进入时 isLoading=true。
            uiState.isLoading -> Box(modifier = Modifier.fillMaxSize()) { LoadingContent() }

            // 分支 2:Error —— repository.getTasks() 抛异常,errorMessage 非 null。
            uiState.errorMessage != null -> Box(modifier = Modifier.fillMaxSize()) {
                ErrorContent(
                    message = uiState.errorMessage ?: "加载失败",
                    onRetry = { onAction(HomeAction.Refresh) },
                )
            }

            // 分支 3:Empty —— 筛选后或 repository 返回 emptyList。
            uiState.tasks.isEmpty() || filteredTasks.isEmpty() -> Box(
                modifier = Modifier.fillMaxSize(),
                contentAlignment = Alignment.Center,
            ) {
                EmptyContent(onRefresh = { onAction(HomeAction.Refresh) })
            }

            // 分支 4:Content —— 用 filteredTasks(已应用筛选)。
            else -> LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(
                    top = innerPadding.calculateTopPadding(),
                    bottom = innerPadding.calculateBottomPadding(),
                ),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items(filteredTasks, key = { it.id }) { task ->
                    TaskCard(
                        title = task.title,
                        owner = displayOwner(task),
                        completed = task.completed,
                        priority = task.priority,
                        onOpenTask = { onAction(HomeAction.ItemClicked(task.id)) },
                    )
                }
            }
        }
    }
}

// --- Preview ---

@Preview(showBackground = true, name = "实验四 Content 态")
@Composable
private fun PreviewHomeScreenContent() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = false, tasks = sampleTasks, errorMessage = null),
            filteredTasks = sampleTasks,
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "实验四 Loading 态")
@Composable
private fun PreviewHomeScreenLoading() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = true),
            filteredTasks = emptyList(),
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "实验四 Error 态")
@Composable
private fun PreviewHomeScreenError() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(
                isLoading = false,
                errorMessage = "FakeTaskRepository 模拟网络异常",
            ),
            filteredTasks = emptyList(),
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "实验四 Empty 态")
@Composable
private fun PreviewHomeScreenEmpty() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = false, tasks = emptyTasks, errorMessage = null),
            filteredTasks = emptyTasks,
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "实验四 仅看未完成 + 深色模式")
@Composable
private fun PreviewHomeScreenFilterDark() {
    MaterialTheme(colorScheme = darkColorScheme()) {
        HomeScreen(
            uiState = HomeUiState(
                isLoading = false,
                tasks = sampleTasks,
                errorMessage = null,
                showOnlyIncomplete = true,
                darkMode = true,
            ),
            filteredTasks = sampleTasks.filter { !it.completed },
            onAction = {},
        )
    }
}
