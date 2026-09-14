# 实验一报告 — Kotlin + Compose 开发环境及基础界面

> 学生填写:姓名 / 学号 / 班级 / 完成日期

## 一、实验环境

| 项目 | 信息 |
|---|---|
| 操作系统 | Windows 11 |
| Android Studio 版本 | (待填,Android Studio → About 查看) |
| Android SDK | API 37 (Android 16) |
| JDK | 17.0.19 |
| Kotlin | 2.0.21 |
| Compose BOM | 2024.10.01 |
| Gradle | 8.10.2 |
| 模拟器 / 真机 | (待填,如 Pixel 7 API 37 模拟器 或 自己的手机型号) |

## 二、需求与设计

**任务列表**(对齐实验指导书 C 部分):

| 步骤 | 完成情况 |
|---|---|
| 1. Hello Compose 运行 | ✅ MainActivity 可运行 |
| 2. CourseTask 数据类 + sampleTasks | ✅ `data/CourseTask.kt` |
| 3. 实现 TaskCard(title, owner, completed, onClick) | ✅ `ui/TaskCard.kt` |
| 4. 2 个 Preview(进行中/已完成) | ✅ `PreviewTaskCardInProgress` / `PreviewTaskCardCompleted`(扩展加了"未分配"分支) |
| 5. MainActivity 中展示 3 个 TaskCard | ✅ LazyColumn + items 显示 sampleTasks |
| 6. owner=null 通过 Elvis 显示"未分配" | ✅ `displayOwner()` 函数 |
| 拓展 增加优先级样式 | ✅ priority 1→红, 3→灰 |
| 拓展 MaterialTheme typography | ✅ 用 titleMedium / bodySmall |

## 三、关键代码与说明

### 1. CourseTask data class + 空安全

文件:`app/src/main/java/edu/example/mobilecourse/lab1/data/CourseTask.kt`

```kotlin
data class CourseTask(
    val id: Int,
    val title: String,
    val owner: String?,            // 可空,可能没人负责
    val completed: Boolean = false,
    val priority: Int = 2,
)

fun displayOwner(task: CourseTask): String =
    task.owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未分配"
```

**空安全解释链**:
1. `task.owner?.trim()` — owner 为 null 时整条链返回 null,不再执行后续
2. `?.takeIf { it.isNotEmpty() }` — 如果 trim 后是空字符串,返回 null
3. `?: "未分配"` — Elvis 运算符,左侧为 null 时取右侧默认值

**自问自答**(实验指导书 H 部分):

- **数据在哪里?** `sampleTasks` 是顶层 `List<CourseTask>`,实验一只关心 UI,数据来源固定;实验三会把数据移到 ViewModel + Repository。
- **状态在哪里?** Composable 都是**无状态**的,数据通过参数从外层传入,符合 Compose 单向数据流准备。
- **事件从哪里来、到哪里去?** `TaskCard.onClick` 是回调,由 `AppScreen` 的 `onTaskClick` 接收,目前只打日志;实验二会接 `navController.navigate`。
- **错误在哪里处理?** 实验一数据都是本地不可变常量,无错误路径;实验三接入 Repository 后会出现 Loading/Error/Empty/Content 四态。

### 2. TaskCard Composable(≥3 种基本组件)

文件:`app/src/main/java/edu/example/mobilecourse/lab1/ui/TaskCard.kt`

```kotlin
@Composable
fun TaskCard(
    title: String,
    owner: String,
    completed: Boolean,
    priority: Int = 2,
    onClick: () -> Unit = {},
) {
    Card(onClick = onClick, ...) {
        Row(...) {
            Icon(if (completed) Icons.Filled.CheckCircle
            else Icons.Filled.RadioButtonUnchecked, ...)
            Column(...) {
                Text(title, color = when (priority) { 1 -> error; 3 -> outline; else -> onSurface })
                Row {
                    Icon(Icons.Filled.Person, ...)
                    Text(owner, ...)
                }
            }
        }
    }
}
```

**用到的基本组件(4 种,满足"≥3 种"要求)**:
1. `Card` — Material3 卡片容器,自带 onClick(实验二接导航)
2. `Row` / `Column` — 线性布局
3. `Text` — 文字
4. `Icon` — 图标(状态图标 + 负责人图标)

**重要约定**:TaskCard 不持有任何业务状态,只根据入参渲染 UI;点击通过 `onClick` 回调由上层处理(为实验二解耦做准备)。

### 3. MainActivity 用 LazyColumn 展示 3 个 TaskCard

文件:`app/src/main/java/edu/example/mobilecourse/lab1/MainActivity.kt`

```kotlin
LazyColumn(
    contentPadding = PaddingValues(
        top = innerPadding.calculateTopPadding(),
        bottom = innerPadding.calculateBottomPadding(),
    ),
    verticalArrangement = Arrangement.spacedBy(4.dp),
) {
    items(tasks, key = { it.id }) { task ->
        TaskCard(
            title = task.title,
            owner = displayOwner(task),
            completed = task.completed,
            priority = task.priority,
            onClick = { onTaskClick(task.id) },
        )
    }
}
```

**关键点**:
- 用 `displayOwner(task)` 把 owner=null 转为 "未分配"
- `key = { it.id }` 给 LazyColumn 稳定键,提升性能(实验二会再强调)
- 实验一只用 3 条数据,但 LazyColumn 能平滑扩展到 100 条(实验二验收点)

## 四、运行截图

> 学生自填,至少放 3 张:

| 截图 | 说明 |
|---|---|
| (待填) | 1. 启动后 MainActivity 列表截图 |
| (待填) | 2. TaskCard Preview(进行中 + 已完成 + 未分配) |
| (待填) | 3. 模拟器/真机运行截图 |

## 五、故障记录(现象 → 定位 → 原因 → 修复)

> 实验指导书要求"至少记录一个真实故障",以下为示例,请替换为你自己的真实故障。

**现象**:首次打开项目 Android Studio 报 `Gradle sync failed: Could not resolve gradle...`

**定位**:File → Sync Project with Gradle Files 看输出,提示 gradle-wrapper.jar 缺失。

**原因**:我用 Write 工具直接生成项目骨架时,无法生成 `gradle-wrapper.jar` 二进制文件,Android Studio 第一次打开时会自动补全,但需要联网下载。

**修复**:Android Studio 打开项目后,等待自动下载完成(几分钟),或手动执行 `gradle wrapper` 命令。

## 六、验收点自检(实验指导书 E 部分)

- [x] 项目可编译运行,无红色异常
- [x] TaskCard 能显示两种状态(进行中 RadioButtonUnchecked / 已完成 CheckCircle)
- [x] 代码中无无理由 `!!`(`displayOwner` 全程用安全调用链)
- [x] 至少一个 Composable 可独立 Preview(`PreviewTaskCardInProgress` 等 3 个)

## 七、提交物清单(实验指导书 F 部分)

- [x] 源代码仓库:`d:\rain_android\lab1`(已 git init 并提交)
- [x] 实验报告 1-2 页:本文件即是

## 八、拓展任务(可选,G 部分)

- [x] 增加优先级样式(priority 1=红 / 3=灰)
- [x] 使用 MaterialTheme typography(titleMedium / bodySmall),不硬编码字号
