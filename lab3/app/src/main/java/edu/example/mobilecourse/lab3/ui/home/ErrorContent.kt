package edu.example.mobilecourse.lab3.ui.home

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.ErrorOutline
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
 * 错误占位(指导书"四态模板" Error 分支,实验三步骤 19)。
 *
 * 无状态展示组件:只渲染"加载失败"提示 + 重试按钮。
 * 重试事件通过 [onRetry] 回调向上传递,由 HomeScreen 路由到 ViewModel.refresh()。
 *
 * @param message  来自 [HomeUiState.errorMessage] 的失败文案
 * @param onRetry  "重试"按钮回调,接 HomeAction.Refresh
 */
@Composable
fun ErrorContent(
    message: String,
    onRetry: () -> Unit,
) {
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
                imageVector = Icons.Filled.ErrorOutline,
                contentDescription = "加载失败",
                tint = MaterialTheme.colorScheme.error,
                modifier = Modifier.size(56.dp),
            )
            Spacer(modifier = Modifier.size(12.dp))
            Text(
                text = "加载失败",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.onSurface,
            )
            Spacer(modifier = Modifier.size(4.dp))
            Text(
                text = message,
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.outline,
            )
            Spacer(modifier = Modifier.size(16.dp))
            Button(onClick = onRetry) { Text("重试") }
        }
    }
}

@Preview(showBackground = true, name = "错误状态")
@Composable
private fun PreviewErrorContent() {
    MaterialTheme {
        ErrorContent(message = "FakeTaskRepository 模拟网络异常", onRetry = {})
    }
}
