package edu.example.mobilecourse.ui.taskdetail

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import edu.example.mobilecourse.CourseTask
import edu.example.mobilecourse.data.repository.NetworkTaskRepository
import edu.example.mobilecourse.data.repository.TaskRepository
import edu.example.mobilecourse.ui.theme.MyApplicationTheme
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * TaskDetailRoute：在 Compose 入口处按 [taskId] 通过 [TaskRepository] 取单条数据。
 *
 * 这里为了实验 2 简单可演示，直接在 Composable 中通过 remember + LaunchedEffect 加载；
 * 真实工程中应当像 HomeScreen 一样接入 TaskDetailViewModel + StateFlow。
 */
@Composable
fun TaskDetailRoute(
    taskId: Int,
    onBack: () -> Unit,
    repository: TaskRepository = NetworkTaskRepository()
) {
    var loading by remember { mutableStateOf(true) }
    var task by remember { mutableStateOf<CourseTask?>(null) }
    var errorMsg by remember { mutableStateOf<String?>(null) }

    LaunchedEffect(taskId) {
        loading = true
        errorMsg = null
        runCatching {
            withContext(Dispatchers.IO) { repository.getTaskById(taskId) }
        }.onSuccess {
            task = it
        }.onFailure { throwable ->
            errorMsg = throwable.message ?: "未知错误"
        }
        loading = false
    }

    TaskDetailScreen(
        taskId = taskId,
        loading = loading,
        task = task,
        errorMessage = errorMsg,
        onBack = onBack
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskDetailScreen(
    taskId: Int,
    loading: Boolean,
    task: CourseTask?,
    errorMessage: String?,
    onBack: () -> Unit,
) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text(text = "任务详情 #$taskId", fontWeight = FontWeight.SemiBold) },
                navigationIcon = {
                    IconButton(onClick = onBack) {
                        Icon(
                            imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                            contentDescription = "返回"
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer,
                    navigationIconContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
                .padding(16.dp)
        ) {
            when {
                loading -> Text(
                    text = "加载中…",
                    style = MaterialTheme.typography.bodyLarge,
                    modifier = Modifier.align(Alignment.Center)
                )

                errorMessage != null -> Column(
                    modifier = Modifier.align(Alignment.Center),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(12.dp)
                ) {
                    Text(
                        text = "加载失败",
                        style = MaterialTheme.typography.titleMedium,
                        color = MaterialTheme.colorScheme.error
                    )
                    Text(text = errorMessage, style = MaterialTheme.typography.bodyMedium)
                    Button(onClick = onBack) { Text(text = "返回首页") }
                }

                task == null -> Text(
                    text = "未找到该任务",
                    style = MaterialTheme.typography.bodyLarge,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.align(Alignment.Center)
                )

                else -> DetailBody(task = task!!)
            }
        }
    }
}

@Composable
private fun DetailBody(task: CourseTask) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .clip(RoundedCornerShape(12.dp)),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.surfaceVariant.copy(alpha = 0.5f)
        ),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "任务标题",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Text(
                text = task.title,
                style = MaterialTheme.typography.titleLarge,
                fontWeight = FontWeight.SemiBold
            )

            Text(
                text = "负责人",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 8.dp)
            )
            Text(
                text = task.displayOwner(),
                style = MaterialTheme.typography.bodyLarge
            )

            Text(
                text = "状态",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier.padding(top = 8.dp)
            )
            Text(
                text = if (task.completed) "已完成" else "进行中",
                style = MaterialTheme.typography.bodyLarge,
                color = if (task.completed) MaterialTheme.colorScheme.primary
                else MaterialTheme.colorScheme.tertiary
            )
        }
    }
}

@Preview(showBackground = true, name = "TaskDetail 预览")
@Composable
private fun TaskDetailScreenPreview() {
    val sample = CourseTask(
        id = 7,
        title = "示例任务 #7 · 状态流与 ViewModel",
        owner = "学号-1006",
        completed = false
    )
    MyApplicationTheme {
        TaskDetailScreen(
            taskId = sample.id,
            loading = false,
            task = sample,
            errorMessage = null,
            onBack = {}
        )
    }
}
