package edu.example.mobilecourse.lab3.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import edu.example.mobilecourse.lab3.data.model.CourseTask
import edu.example.mobilecourse.lab3.data.model.displayOwner
import edu.example.mobilecourse.lab3.data.model.emptyTasks
import edu.example.mobilecourse.lab3.data.model.sampleTasks
import edu.example.mobilecourse.lab3.ui.TaskCard

/**
 * 首页 Screen(指导书 3.2 Route/Screen 模板 + 实验三步骤 18)。
 *
 * **纯 UI**:只根据 [uiState] 渲染、把事件封装成 [HomeAction] 通过 [onAction] 向上发送。
 * 不持有 ViewModel、不调 repository、不持有 NavController(验收点"Screen 不直接调用 repository")。
 *
 * 四态分支(指导书"四态模板" + 实验三验收点"四种 UI 状态均可演示"):
 * - [HomeUiState.isLoading] = true           -> [LoadingContent]
 * - [HomeUiState.errorMessage] != null        -> [ErrorContent] + Retry
 * - [HomeUiState.tasks].isEmpty() 且非上述      -> [EmptyContent]
 * - 其他                                       -> LazyColumn(tasks)
 *
 * @param uiState  来自 HomeViewModel 的 StateFlow
 * @param onAction 事件入口,接 HomeViewModel::onAction
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    uiState: HomeUiState,
    onAction: (HomeAction) -> Unit,
) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text("实验三 · 任务列表(${uiState.tasks.size})") },
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

            // 分支 3:Empty —— repository 返回 emptyList(步骤 20)。
            uiState.tasks.isEmpty() -> Box(modifier = Modifier.fillMaxSize()) {
                EmptyContent(onRefresh = { onAction(HomeAction.Refresh) })
            }

            // 分支 4:Content —— 正常列表,沿用实验二的稳定 key + TaskCard。
            else -> LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(
                    top = innerPadding.calculateTopPadding(),
                    bottom = innerPadding.calculateBottomPadding(),
                ),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items(uiState.tasks, key = { it.id }) { task ->
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

@Preview(showBackground = true, name = "首页 · Content(100 条样本截前若干)")
@Composable
private fun PreviewHomeScreenContent() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = false, tasks = sampleTasks, errorMessage = null),
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "首页 · Loading")
@Composable
private fun PreviewHomeScreenLoading() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = true),
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "首页 · Error")
@Composable
private fun PreviewHomeScreenError() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(
                isLoading = false,
                errorMessage = "FakeTaskRepository 模拟网络异常",
            ),
            onAction = {},
        )
    }
}

@Preview(showBackground = true, name = "首页 · Empty")
@Composable
private fun PreviewHomeScreenEmpty() {
    MaterialTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = false, tasks = emptyTasks, errorMessage = null),
            onAction = {},
        )
    }
}
