package edu.example.mobilecourse.lab2.ui.home

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
import edu.example.mobilecourse.lab2.data.CourseTask
import edu.example.mobilecourse.lab2.data.displayOwner
import edu.example.mobilecourse.lab2.data.emptyTasks
import edu.example.mobilecourse.lab2.data.sampleTasks
import edu.example.mobilecourse.lab2.ui.TaskCard

/**
 * 首页 Route(实验二暂未引入 ViewModel,Route 与 Screen 合一;实验三会拆 Route/Screen)。
 *
 * 解耦约定:本 Composable 不持有 NavController,只通过 [onOpenTask] 回调把"用户点了 taskId"
 * 向上送到 App,由 App 调用 `navController.navigate(TaskDetailDestination.createRoute(id))`。
 * 满足验收点"不直接访问 TaskCard / Screen 的 NavController"。
 *
 * @param tasks       任务列表,空 List 时显示 [EmptyContent]
 * @param onOpenTask  点击某张卡片时触发,参数是 taskId
 * @param onRefresh   空状态"点这里重试"回调(实验二暂只切回 100 条样本)
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    tasks: List<CourseTask>,
    onOpenTask: (Int) -> Unit,
    onRefresh: () -> Unit = {},
) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text("实验二 · 任务列表(${tasks.size})") },
            )
        },
    ) { innerPadding ->
        if (tasks.isEmpty()) {
            // 步骤 8:列表为空时显示明确空状态。
            Box(modifier = Modifier.fillMaxSize()) {
                EmptyContent(onRefresh = onRefresh)
            }
        } else {
            // 步骤 7:首页改为 LazyColumn,使用稳定 key = task.id。
            LazyColumn(
                modifier = Modifier.fillMaxSize(),
                contentPadding = PaddingValues(
                    top = innerPadding.calculateTopPadding(),
                    bottom = innerPadding.calculateBottomPadding(),
                ),
                verticalArrangement = Arrangement.spacedBy(4.dp),
            ) {
                items(tasks, key = { it.id }) { task ->
                    TaskCard(
                        title = task.title,
                        owner = displayOwner(task),   // owner=null 时显示 "未分配"
                        completed = task.completed,
                        priority = task.priority,
                        onOpenTask = { onOpenTask(task.id) },  // 步骤 12:只传 taskId,导航由上层
                    )
                }
            }
        }
    }
}

@Preview(showBackground = true, name = "首页 · 100 条样本(截前若干)")
@Composable
private fun PreviewHomeScreenContent() {
    MaterialTheme {
        HomeScreen(
            tasks = sampleTasks,
            onOpenTask = {},
            onRefresh = {},
        )
    }
}

@Preview(showBackground = true, name = "首页 · 空状态")
@Composable
private fun PreviewHomeScreenEmpty() {
    MaterialTheme {
        HomeScreen(
            tasks = emptyTasks,
            onOpenTask = {},
            onRefresh = {},
        )
    }
}
