package edu.example.mobilecourse.lab1

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
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
import edu.example.mobilecourse.lab1.data.CourseTask
import edu.example.mobilecourse.lab1.data.displayOwner
import edu.example.mobilecourse.lab1.data.sampleTasks
import edu.example.mobilecourse.lab1.ui.TaskCard

/**
 * 实验一入口 Activity。
 *
 * 步骤对照(实验指导书 C 部分):
 * - 步骤 1 Hello Compose:本 Activity 即可运行的 Hello
 * - 步骤 5 在 MainActivity 中展示 3 个 TaskCard(用 LazyColumn)
 * - 步骤 6 owner=null 通过 [displayOwner] + Elvis 显示 "未分配"
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MaterialTheme {
                AppScreen(
                    tasks = sampleTasks,
                    onTaskClick = { id ->
                        // 实验一只关心 UI,点击事件先打日志,实验二会接导航
                        android.util.Log.d("Lab1", "Task clicked: $id")
                    },
                )
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun AppScreen(
    tasks: List<CourseTask>,
    onTaskClick: (Int) -> Unit,
) {
    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = { Text("实验一 · Compose 任务卡片") },
            )
        },
    ) { innerPadding ->
        LazyColumn(
            modifier = Modifier.fillMaxSize(),
            contentPadding = PaddingValues(
                top = innerPadding.calculateTopPadding(),
                bottom = innerPadding.calculateBottomPadding(),
            ),
            verticalArrangement = Arrangement.spacedBy(4.dp),
        ) {
            // 稳定 key 提示性能,实验二接 LazyColumn 时会再次强调
            items(tasks, key = { it.id }) { task ->
                TaskCard(
                    title = task.title,
                    owner = displayOwner(task),   // owner=null 时会显示 "未分配"
                    completed = task.completed,
                    priority = task.priority,
                    onClick = { onTaskClick(task.id) },
                )
            }
        }
    }
}

/**
 * MainActivity 整页 Preview,可直接在 Android Studio 看 3 个 TaskCard 排版。
 */
@Preview(showBackground = true, name = "MainActivity 整页")
@Composable
private fun PreviewAppScreen() {
    MaterialTheme {
        AppScreen(
            tasks = sampleTasks,
            onTaskClick = {},
        )
    }
}
