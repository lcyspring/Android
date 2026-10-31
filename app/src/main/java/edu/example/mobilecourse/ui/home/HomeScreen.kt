package edu.example.mobilecourse.ui.home

import android.Manifest
import android.content.pm.PackageManager
import android.widget.Toast
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.PhotoCamera
import androidx.compose.material3.Button
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.core.content.ContextCompat
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.lifecycle.viewmodel.compose.viewModel
import edu.example.mobilecourse.CourseTask
import edu.example.mobilecourse.TaskCard
import edu.example.mobilecourse.data.repository.SettingsRepository
import edu.example.mobilecourse.ui.theme.MyApplicationTheme

/**
 * HomeRoute：负责创建/订阅 ViewModel，并把状态与回调注入到 [HomeScreen]。
 *
 * 这是 UDF 的“粘合层”：StateFlow 在这里被 collect 成 Compose State，
 * 事件由 [onAction] 与 [onNavigate] 分别交给 ViewModel 与上层 NavController。
 * DataStore 的 SettingsRepository 也在此层注入，不进入 Composable。
 */
@Composable
fun HomeRoute(
    onNavigate: (Int) -> Unit,
) {
    val context = LocalContext.current.applicationContext
    val settingsRepository = remember { SettingsRepository(context) }
    val viewModel: HomeViewModel = viewModel(
        factory = HomeViewModel.Factory(settingsRepository = settingsRepository)
    )
    val uiState by viewModel.uiState.collectAsStateWithLifecycle()
    HomeScreen(
        uiState = uiState,
        onAction = viewModel::onAction,
        onNavigate = onNavigate,
    )
}

/**
 * HomeScreen：纯 UI，根据 [uiState] 渲染四态 + 筛选开关 + 相机权限按钮。
 * 不直接访问 Repository / DataStore，也不持有 NavController。
 */
@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HomeScreen(
    uiState: HomeUiState,
    onAction: (HomeAction) -> Unit,
    onNavigate: (Int) -> Unit,
) {
    val context = LocalContext.current

    // 相机权限申请：点击后才发起，不在启动时申请
    var cameraPermissionDenied by remember { mutableStateOf(false) }

    val cameraPermissionLauncher = rememberLauncherForActivityResult(
        contract = ActivityResultContracts.RequestPermission()
    ) { isGranted ->
        cameraPermissionDenied = !isGranted
    }

    Scaffold(
        modifier = Modifier.fillMaxSize(),
        topBar = {
            TopAppBar(
                title = {
                    Text(
                        text = "实验四 · 课程任务列表",
                        fontWeight = FontWeight.SemiBold
                    )
                },
                actions = {
                    // 仅看未完成 Switch
                    Row(
                        verticalAlignment = Alignment.CenterVertically,
                        horizontalArrangement = Arrangement.spacedBy(4.dp)
                    ) {
                        Text(
                            text = "仅看未完成",
                            style = MaterialTheme.typography.labelSmall,
                            color = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                        Switch(
                            checked = uiState.showOnlyIncomplete,
                            onCheckedChange = { checked ->
                                onAction(HomeAction.ToggleShowOnlyIncomplete(checked))
                            }
                        )
                    }

                    // 相机权限按钮：点击后再申请
                    IconButton(
                        onClick = {
                            when {
                                ContextCompat.checkSelfPermission(
                                    context,
                                    Manifest.permission.CAMERA
                                ) == PackageManager.PERMISSION_GRANTED -> {
                                    // 已授权：给出可见反馈（真实项目可在此启动相机 Intent 拍照）
                                    cameraPermissionDenied = false
                                    Toast.makeText(context, "相机权限已授权，可以开始拍照", Toast.LENGTH_SHORT).show()
                                }
                                else -> {
                                    // 未授权：发起申请
                                    cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                                }
                            }
                        }
                    ) {
                        Icon(
                            imageVector = Icons.Filled.PhotoCamera,
                            contentDescription = "相机",
                            tint = MaterialTheme.colorScheme.onPrimaryContainer
                        )
                    }
                },
                colors = TopAppBarDefaults.topAppBarColors(
                    containerColor = MaterialTheme.colorScheme.primaryContainer,
                    titleContentColor = MaterialTheme.colorScheme.onPrimaryContainer
                )
            )
        }
    ) { innerPadding ->
        Box(
            modifier = Modifier
                .fillMaxSize()
                .padding(innerPadding)
        ) {
            when {
                uiState.isLoading -> LoadingContent()

                uiState.errorMessage != null -> ErrorContent(
                    message = uiState.errorMessage!!,
                    onRetry = { onAction(HomeAction.Refresh) }
                )

                uiState.tasks.isEmpty() -> EmptyContent()

                else -> TaskListContent(
                    tasks = uiState.tasks,
                    onTaskClick = { id ->
                        onAction(HomeAction.ItemClicked(id))
                        onNavigate(id)
                    }
                )
            }

            // 相机权限被拒绝时的提示横幅：放在 when 之后，确保浮在最上层
            if (cameraPermissionDenied) {
                CameraPermissionDeniedBanner(
                    modifier = Modifier.align(Alignment.TopCenter),
                    onDismiss = { cameraPermissionDenied = false }
                )
            }
        }
    }
}

/** 相机权限被拒绝后的顶部横幅，用户可手动关闭 */
@Composable
private fun CameraPermissionDeniedBanner(
    modifier: Modifier = Modifier,
    onDismiss: () -> Unit,
) {
    Box(
        modifier = modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Row(
            modifier = Modifier
                .fillMaxWidth()
                .background(MaterialTheme.colorScheme.errorContainer)
                .padding(horizontal = 12.dp, vertical = 8.dp),
            verticalAlignment = Alignment.CenterVertically,
            horizontalArrangement = Arrangement.SpaceBetween
        ) {
            Text(
                text = "相机权限被拒绝，无法使用拍照功能",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onErrorContainer
            )
            Button(onClick = onDismiss) {
                Text("知道了", style = MaterialTheme.typography.labelSmall)
            }
        }
    }
}

@Composable
private fun LoadingContent() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            CircularProgressIndicator()
            Text(
                text = "正在加载任务…",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun ErrorContent(
    message: String,
    onRetry: () -> Unit,
) {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .padding(24.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(12.dp)
        ) {
            Text(
                text = "加载失败",
                style = MaterialTheme.typography.titleMedium,
                color = MaterialTheme.colorScheme.error,
                fontWeight = FontWeight.SemiBold
            )
            Text(
                text = message,
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
            Button(onClick = onRetry) {
                Text(text = "重试")
            }
        }
    }
}

@Composable
private fun EmptyContent() {
    Box(
        modifier = Modifier.fillMaxSize(),
        contentAlignment = Alignment.Center
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            Text(
                text = "暂无任务",
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.SemiBold
            )
            Text(
                text = "下拉刷新或稍后再试",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant
            )
        }
    }
}

@Composable
private fun TaskListContent(
    tasks: List<CourseTask>,
    onTaskClick: (Int) -> Unit,
) {
    LazyColumn(
        modifier = Modifier.fillMaxSize(),
        contentPadding = androidx.compose.foundation.layout.PaddingValues(
            horizontal = 16.dp,
            vertical = 12.dp
        ),
        verticalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        item {
            Text(
                text = "共 ${tasks.size} 条任务",
                style = MaterialTheme.typography.labelMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 4.dp)
            )
        }
        // 实验 2 验收点：LazyColumn 使用稳定 key
        items(items = tasks, key = { it.id }) { task ->
            TaskCard(
                title = task.title,
                owner = task.displayOwner(),
                completed = task.completed,
                onClick = { onTaskClick(task.id) }
            )
        }
    }
}

/* ---------- Previews：四态演示 ---------- */

@Preview(showBackground = true, name = "Loading 状态预览")
@Composable
private fun HomeScreenLoadingPreview() {
    MyApplicationTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = true),
            onAction = {},
            onNavigate = {}
        )
    }
}

@Preview(showBackground = true, name = "Error 状态预览")
@Composable
private fun HomeScreenErrorPreview() {
    MyApplicationTheme {
        HomeScreen(
            uiState = HomeUiState(
                isLoading = false,
                errorMessage = "NetworkTaskRepository 网络请求失败：Unable to resolve host"
            ),
            onAction = {},
            onNavigate = {}
        )
    }
}

@Preview(showBackground = true, name = "Empty 状态预览")
@Composable
private fun HomeScreenEmptyPreview() {
    MyApplicationTheme {
        HomeScreen(
            uiState = HomeUiState(isLoading = false, tasks = emptyList()),
            onAction = {},
            onNavigate = {}
        )
    }
}

@Preview(showBackground = true, showSystemUi = true, name = "Content + 仅看未完成 预览")
@Composable
private fun HomeScreenContentPreview() {
    val sample = List(8) { index ->
        CourseTask(
            id = index + 1,
            title = "示例任务 #${index + 1} · 网络请求与 DataStore",
            owner = if (index % 3 == 0) null else "学号-${1000 + index}",
            completed = index % 2 == 0
        )
    }
    MyApplicationTheme {
        HomeScreen(
            uiState = HomeUiState(
                isLoading = false,
                tasks = sample,
                showOnlyIncomplete = true
            ),
            onAction = {},
            onNavigate = {}
        )
    }
}
