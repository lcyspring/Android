package edu.example.mobilecourse.lab3.ui.taskdetail

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Inbox
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material3.Button
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import edu.example.mobilecourse.lab3.data.model.CourseTask
import edu.example.mobilecourse.lab3.data.model.displayOwner
import edu.example.mobilecourse.lab3.data.model.sampleTasks
import edu.example.mobilecourse.lab3.data.model.taskById

/**
 * 任务详情页(指导书步骤 9:TaskDetailScreen(taskId))。
 *
 * 实验二关键解耦约定:
 * - 本 Composable **不持有 NavController**,返回事件通过 [onBack] 回调向上传递,
 *   由 App 调用 `navController.popBackStack()`,便于独立 Preview 与测试。
 * - taskId 由 NavBackStackEntry 解析后传入,UI 只负责"根据 taskId 取数据 -> 渲染"。
 * - 找不到任务时显示明确"任务不存在"状态(对应验收点"边界/错误状态")。
 *
 * @param taskId 导航带入的任务 ID(来自 Home -> TaskDetailDestination 的参数)
 * @param onBack 返回按钮回调
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskDetailScreen(
    taskId: Int,
    onBack: () -> Unit,
) {
    val task: CourseTask? = taskById(taskId)

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text(task?.title ?: "任务不存在") },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回",
                        )
                    }
                },
            )
        },
    ) { innerPadding ->
        if (task == null) {
            // 边界状态:taskId 没对应任务(例如手敲路由 task_detail/99999)。
            Box(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding)
                    .padding(32.dp),
                contentAlignment = Alignment.Center,
            ) {
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                ) {
                    Icon(
                        imageVector = Icons.Filled.Inbox,
                        contentDescription = "任务不存在",
                        tint = MaterialTheme.colorScheme.outline,
                        modifier = Modifier.size(56.dp),
                    )
                    Spacer(modifier = Modifier.size(12.dp))
                    Text(
                        text = "找不到 taskId=$taskId 的任务",
                        style = MaterialTheme.typography.titleMedium,
                    )
                    Spacer(modifier = Modifier.size(16.dp))
                    Button(onClick = onBack) { Text("返回列表") }
                }
            }
        } else {
            // 正常状态:展示任务详情 + 关联任务列表(纵向滚动验证长内容)。
            LazyColumn(
                modifier = Modifier
                    .fillMaxSize()
                    .padding(innerPadding),
                contentPadding = PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                // 详情卡片区。
                item {
                    Column(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(12.dp),
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Icon(
                                imageVector = if (task.completed) Icons.Filled.CheckCircle
                                else Icons.Filled.RadioButtonUnchecked,
                                contentDescription = if (task.completed) "已完成" else "进行中",
                                tint = if (task.completed) MaterialTheme.colorScheme.primary
                                else MaterialTheme.colorScheme.outline,
                                modifier = Modifier.size(32.dp),
                            )
                            Spacer(modifier = Modifier.width(12.dp))
                            Text(
                                text = task.title,
                                style = MaterialTheme.typography.headlineSmall,
                            )
                        }
                        Spacer(modifier = Modifier.size(16.dp))
                        DetailRow(label = "任务 ID", value = task.id.toString())
                        DetailRow(label = "负责人", value = displayOwner(task))
                        DetailRow(label = "状态", value = if (task.completed) "已完成" else "进行中")
                        DetailRow(label = "优先级", value = "${task.priority} (1最高 / 3最低)")
                    }
                }

                // 关联任务:取相邻 5 条,验证详情页也能滚动。
                val related: List<CourseTask> = sampleTasks.filter { it.id != task.id }.take(5)
                item {
                    Text(
                        text = "关联任务",
                        style = MaterialTheme.typography.titleMedium,
                        modifier = Modifier.padding(top = 8.dp, bottom = 4.dp),
                    )
                }
                items(related, key = { it.id }) { r ->
                    Row(
                        modifier = Modifier
                            .fillMaxWidth()
                            .padding(vertical = 6.dp),
                        verticalAlignment = Alignment.CenterVertically,
                    ) {
                        Icon(
                            imageVector = if (r.completed) Icons.Filled.CheckCircle
                            else Icons.Filled.RadioButtonUnchecked,
                            contentDescription = null,
                            tint = if (r.completed) MaterialTheme.colorScheme.primary
                            else MaterialTheme.colorScheme.outline,
                            modifier = Modifier.size(20.dp),
                        )
                        Spacer(modifier = Modifier.width(12.dp))
                        Column {
                            Text(text = r.title, style = MaterialTheme.typography.bodyLarge)
                            Text(
                                text = "负责人:${displayOwner(r)}",
                                style = MaterialTheme.typography.bodySmall,
                                color = MaterialTheme.colorScheme.outline,
                            )
                        }
                    }
                }
            }
        }
    }
}

@Composable
private fun DetailRow(label: String, value: String) {
    Row(
        modifier = Modifier
            .fillMaxWidth()
            .padding(vertical = 4.dp),
        horizontalArrangement = Arrangement.SpaceBetween,
    ) {
        Text(
            text = label,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.outline,
        )
        Text(
            text = value,
            style = MaterialTheme.typography.bodyLarge,
        )
    }
}

@Preview(showBackground = true, name = "详情 · 正常任务")
@Composable
private fun PreviewTaskDetailFound() {
    MaterialTheme {
        TaskDetailScreen(taskId = 1, onBack = {})
    }
}

@Preview(showBackground = true, name = "详情 · owner=null 任务")
@Composable
private fun PreviewTaskDetailUnassigned() {
    MaterialTheme {
        TaskDetailScreen(taskId = 3, onBack = {})
    }
}

@Preview(showBackground = true, name = "详情 · 任务不存在")
@Composable
private fun PreviewTaskDetailMissing() {
    MaterialTheme {
        TaskDetailScreen(taskId = 99999, onBack = {})
    }
}
