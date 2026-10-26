package edu.example.mobilecourse.lab3.ui

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.RadioButtonUnchecked
import androidx.compose.material.icons.filled.Person
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import edu.example.mobilecourse.lab3.data.model.CourseTask
import edu.example.mobilecourse.lab3.data.model.displayOwner

/**
 * 可复用的任务卡片(实验二沿用实验一,只把点击回调从 onClick 改名为 [onOpenTask])。
 *
 * 实验二关键解耦约定(指导书步骤 12、验收点):
 * - TaskCard **不直接持有 NavController**,只通过 [onOpenTask] 回调向上传递"用户想打开这个 taskId"。
 * - 由上层 HomeScreen / App 把回调接到 `navController.navigate(TaskDetailDestination.createRoute(id))`。
 * 这样卡片可以脱离导航独立 Preview、独立测试、独立复用到搜索页或底部导航的其他 Tab。
 *
 * @param title      任务标题
 * @param owner      负责人展示文字(由调用方先用 [displayOwner] 处理过的字符串)
 * @param completed  是否完成
 * @param priority   优先级(拓展),决定标题颜色
 * @param onOpenTask 整张卡片被点击的回调,参数是 taskId,由上层据此导航
 */
@Composable
fun TaskCard(
    title: String,
    owner: String,
    completed: Boolean,
    priority: Int = 2,
    onOpenTask: () -> Unit = {},
) {
    Card(
        onClick = onOpenTask,
        modifier = Modifier
            .fillMaxWidth()
            .padding(horizontal = 16.dp, vertical = 6.dp),
        elevation = CardDefaults.cardElevation(defaultElevation = 2.dp),
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .padding(16.dp),
            verticalAlignment = Alignment.CenterVertically,
        ) {
            // 完成状态图标(进行中 ⊙ / 已完成 ✓)
            Icon(
                imageVector = if (completed) Icons.Filled.CheckCircle
                else Icons.Filled.RadioButtonUnchecked,
                contentDescription = if (completed) "已完成" else "进行中",
                tint = if (completed) MaterialTheme.colorScheme.primary
                else MaterialTheme.colorScheme.outline,
                modifier = Modifier.size(28.dp),
            )

            Spacer(modifier = Modifier.width(16.dp))

            // 标题 + 负责人(垂直排列)
            Column(modifier = Modifier.weight(1f)) {
                Text(
                    text = title,
                    style = MaterialTheme.typography.titleMedium,
                    color = when (priority) {
                        1 -> MaterialTheme.colorScheme.error   // 高优先级红
                        3 -> MaterialTheme.colorScheme.outline // 低优先级灰
                        else -> MaterialTheme.colorScheme.onSurface
                    },
                )
                Spacer(modifier = Modifier.size(4.dp))
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Filled.Person,
                        contentDescription = "负责人",
                        modifier = Modifier.size(16.dp),
                        tint = MaterialTheme.colorScheme.outline,
                    )
                    Spacer(modifier = Modifier.width(4.dp))
                    Text(
                        text = owner,
                        style = MaterialTheme.typography.bodySmall,
                        color = MaterialTheme.colorScheme.outline,
                    )
                }
            }
        }
    }
}

/**
 * Preview 1:进行中任务。
 *
 * 实验二关键点:TaskCard 不依赖 NavController,可直接 Preview,体现解耦价值。
 */
@Preview(showBackground = true, name = "进行中任务")
@Composable
private fun PreviewTaskCardInProgress() {
    MaterialTheme {
        TaskCard(
            title = "完成实验报告",
            owner = "张三",
            completed = false,
            priority = 1,
            onOpenTask = {},
        )
    }
}

/**
 * Preview 2:已完成任务。
 */
@Preview(showBackground = true, name = "已完成任务")
@Composable
private fun PreviewTaskCardCompleted() {
    MaterialTheme {
        TaskCard(
            title = "提交代码到 Git",
            owner = "李四",
            completed = true,
            priority = 2,
            onOpenTask = {},
        )
    }
}

/**
 * Preview 3(拓展):owner 为 null 的"未分配"分支。
 */
@Preview(showBackground = true, name = "未分配负责人")
@Composable
private fun PreviewTaskCardUnassigned() {
    MaterialTheme {
        val task = CourseTask(
            id = 99,
            title = "待认领任务",
            owner = null,
            completed = false,
            priority = 3,
        )
        TaskCard(
            title = task.title,
            owner = displayOwner(task),  // 这里会显示 "未分配"
            completed = task.completed,
            priority = task.priority,
            onOpenTask = {},
        )
    }
}
