package edu.example.mobilecourse.lab1.ui

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
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import edu.example.mobilecourse.lab1.data.CourseTask
import edu.example.mobilecourse.lab1.data.displayOwner

/**
 * 可复用的任务卡片。
 *
 * 实验一要求:至少 3 种基本组件 + 一个可复用 Composable。
 * 本 Composable 内用到的组件:
 * 1. [Card]           —— 外层卡片容器(Material3)
 * 2. [Row] / [Column] —— 线性布局
 * 3. [Text]           —— 文字
 * 4. [Icon]           —— 图标(已完成 ✓ / 进行中 ⊙ / 负责人 👤)
 *
 * 重要约定:卡片本身不持有任何业务状态,只根据入参渲染 UI;
 * 点击事件通过 [onClick] 回调由上层处理(为实验二的导航做准备)。
 *
 * @param title      任务标题
 * @param owner      负责人(可空),由调用方传 [displayOwner] 处理后的字符串
 * @param completed  是否完成
 * @param priority   优先级(拓展任务),决定标题颜色
 * @param onClick    整张卡片被点击的回调
 */
@Composable
fun TaskCard(
    title: String,
    owner: String,
    completed: Boolean,
    priority: Int = 2,
    onClick: () -> Unit = {},
) {
    Card(
        onClick = onClick,
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
 * 实验一要求:至少 1 个可独立 Preview。这里用 @Preview 注解,
 * Android Studio 直接渲染,不需要跑模拟器。
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
        )
    }
}
