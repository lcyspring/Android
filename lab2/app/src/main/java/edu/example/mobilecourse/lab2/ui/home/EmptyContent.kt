package edu.example.mobilecourse.lab2.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Inbox
import androidx.compose.material3.Button
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp

/**
 * 列表为空时的占位界面(指导书步骤 8、验收点"列表为空时有明确空状态")。
 *
 * 实验二关键解耦点:EmptyContent 是**无状态**展示组件,只根据入参渲染;
 * "刷新"事件通过 [onRefresh] 回调向上传递,由 HomeScreen/上层处理(实验三会接到 ViewModel.refresh)。
 *
 * @param onRefresh "点这里重试"按钮回调,空 List 时的恢复路径
 */
@Composable
fun EmptyContent(onRefresh: () -> Unit = {}) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .padding(32.dp),
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.Center,
        ) {
            Icon(
                imageVector = Icons.Filled.Inbox,
                contentDescription = "没有任务",
                tint = MaterialTheme.colorScheme.outline,
                modifier = Modifier.size(56.dp),
            )
            Spacer(modifier = Modifier.size(12.dp))
            Text(
                text = "当前没有任务",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Spacer(modifier = Modifier.size(4.dp))
            Text(
                text = "下拉刷新或等待数据加载",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
            )
            Spacer(modifier = Modifier.size(16.dp))
            Button(onClick = onRefresh) {
                Text("点这里重试")
            }
        }
    }
}

@Preview(showBackground = true, name = "空状态")
@Composable
private fun PreviewEmptyContent() {
    MaterialTheme {
        EmptyContent(onRefresh = {})
    }
}
