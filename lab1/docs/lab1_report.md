# 《移动应用开发》实验报告

## 实验一  Kotlin + Compose 开发环境及基础界面

| 项目 | 内容 | 项目 | 内容 |
|---|---|---|---|
| 姓名 | 李春雨 | 学号 | 202305567128 |
| 班级 | 计科2班 | 完成日期 | 2026-09-14 |
| 专业 | 计算机科学与技术 | 课程 | 移动应用开发 |
| 实验编号 | 实验一 | 实验名称 | Kotlin + Compose 开发环境及基础界面 |

---

# 一、实验目标

1. 验证 Android Studio、Android SDK、模拟器的开发环境，确认 Compose 项目可正常编译运行。
2. 掌握 Kotlin data class 的定义与空安全处理，理解可空类型 String? 与 Elvis 运算符的配合。
3. 熟悉 Jetpack Compose 基本组件（Card、Row、Column、Text、Icon）的用法，能编写可复用的 TaskCard Composable。
4. 理解 Compose 单向数据流的思想：Composable 不持有业务状态，数据从外层参数传入，事件通过回调向上传递。

# 二、实验环境

| 项目 | 信息 |
|---|---|
| 操作系统 | Windows 11 |
| 开发工具 | Android Studio（Lab1Compose 工程，AGP 8.7.2） |
| Android SDK | API 37（Android 16），路径 D:\Android\Sdk |
| JDK | 17（Android Studio 自带 JBR 17） |
| Kotlin | 2.0.21 |
| Compose BOM | 2024.10.01 |
| Android Gradle Plugin | 8.7.2 |
| Gradle | 8.10.2 |
| 运行设备 | Android 模拟器 Pixel 7（系统镜像 API 37.1，Google Play x86_64） |
| 构建结果 | BUILD SUCCESSFUL in 26s，35 actionable tasks: 14 executed, 21 up-to-date |

# 三、设计

## 3.1 页面结构

实验一只有一个主页面（MainActivity），内部使用 Scaffold + TopAppBar + LazyColumn 布局。LazyColumn 中每个条目是一个 TaskCard，展示一条 CourseTask 任务的标题、负责人、完成状态与优先级。

页面结构简图：

    Scaffold
    +-- TopAppBar("实验一 · Compose 任务卡片")
    +-- LazyColumn(稳定 key = task.id)
        +-- TaskCard[0]  (完成实验报告 / 张三 / 进行中 / 高优先级-红)
        +-- TaskCard[1]  (提交代码到 Git / 李四 / 已完成 / 普通优先级)
        +-- TaskCard[2]  (复习 Kotlin 空安全 / 未分配 / 进行中 / 低优先级-灰)

## 3.2 数据流

实验一是纯静态 UI，数据从顶层 List<CourseTask>（sampleTasks）单向流向 Composable，没有反向状态更新：

    sampleTasks (List<CourseTask>, 顶层常量)
          |  传入
          v
    AppScreen(tasks, onTaskClick)
          |  items(tasks, key=id)
          v
    TaskCard(title, owner, completed, priority, onClick)
          |  点击时回调
          v
    onTaskClick(task.id) -> Log.d（实验二会接 navController.navigate）

自问自答（实验指导书 H 部分）：

- **数据在哪里？** sampleTasks 是顶层 List<CourseTask> 常量，实验一只关心 UI，数据固定；实验三会把数据移到 ViewModel + Repository。
- **状态在哪里？** Composable 都是无状态的，数据通过参数从外层传入，符合 Compose 单向数据流的准备要求。
- **事件从哪里来、到哪里去？** TaskCard.onClick 是回调，由 AppScreen 的 onTaskClick 接收，目前只打日志；实验二会接 navController.navigate。
- **错误在哪里处理？** 实验一数据都是本地不可变常量，无错误路径；实验三接入 Repository 后会出现 Loading/Error/Empty/Content 四态。

## 3.3 类关系

    CourseTask (data class)
        +-- id: Int
        +-- title: String
        +-- owner: String?        <- 可空，用 displayOwner() 安全转换
        +-- completed: Boolean
        +-- priority: Int

    displayOwner(task): String   <- 纯函数：owner?.trim()?.takeIf{...} ?: "未分配"

    TaskCard(@Composable)        <- 无状态展示组件
        +-- 入参：title, owner, completed, priority, onClick
        +-- 不持有状态，只根据入参渲染 UI

## 3.4 关键决策

1. owner 声明为 String? 而非 String，显式表达"可能无人负责"的业务语义，用 Kotlin 空安全链加 Elvis 运算符处理 null，全程不使用 !!。
2. TaskCard 不持有任何业务状态，数据通过参数传入，点击通过 onClick 回调向上传递，为实验二的导航解耦做准备。
3. 使用 LazyColumn 而非 Column，即使只有 3 条数据，也复用了实验二的列表结构，并使用稳定 key = task.id 提升重组性能。
4. 优先级用 MaterialTheme.colorScheme（红/默认/灰）而非硬编码颜色，字号用 titleMedium / bodySmall，符合拓展任务要求。

# 四、实现

## 4.1 CourseTask data class 与 displayOwner 空安全处理

文件：app/src/main/java/edu/example/mobilecourse/lab1/data/CourseTask.kt

    data class CourseTask(
        val id: Int,
        val title: String,
        val owner: String?,            // 可空，可能没人负责
        val completed: Boolean = false,
        val priority: Int = 2,
    )

    fun displayOwner(task: CourseTask): String =
        task.owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未分配"

空安全解释链：

1. task.owner?.trim() —— owner 为 null 时整条链返回 null，后面不再执行；
2. ?.takeIf { it.isNotEmpty() } —— trim 后如果是空字符串，返回 null；
3. ?: "未分配" —— Elvis 运算符，左侧为 null 时取右侧默认值。

## 4.2 TaskCard 可复用 Composable（使用 4 种基本组件）

文件：app/src/main/java/edu/example/mobilecourse/lab1/ui/TaskCard.kt

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
            modifier = Modifier.fillMaxWidth(),
        ) {
            Row(
                modifier = Modifier.padding(12.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Icon(
                    imageVector = if (completed) Icons.Filled.CheckCircle
                                  else Icons.Filled.RadioButtonUnchecked,
                    contentDescription = null,
                    tint = if (completed) MaterialTheme.colorScheme.primary
                           else MaterialTheme.colorScheme.outline,
                )
                Spacer(Modifier.width(12.dp))
                Column {
                    Text(
                        text = title,
                        style = MaterialTheme.typography.titleMedium,
                        color = when (priority) {
                            1 -> MaterialTheme.colorScheme.error      // 高优先级-红
                            3 -> MaterialTheme.colorScheme.outline    // 低优先级-灰
                            else -> MaterialTheme.colorScheme.onSurface
                        },
                    )
                    Spacer(Modifier.height(4.dp))
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Filled.Person,
                            contentDescription = null,
                            modifier = Modifier.size(14.dp),
                            tint = MaterialTheme.colorScheme.outline,
                        )
                        Spacer(Modifier.width(4.dp))
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

用到的基本组件（4 种，满足"至少 3 种"要求）：

1. Card —— Material3 卡片容器，自带 onClick（实验二接导航）；
2. Row / Column —— 线性布局；
3. Text —— 文字；
4. Icon —— 图标（完成状态图标 + 负责人图标）。

## 4.3 MainActivity 用 LazyColumn 展示 3 个 TaskCard

文件：app/src/main/java/edu/example/mobilecourse/lab1/MainActivity.kt

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

关键点：

- 用 displayOwner(task) 把 owner=null 转为"未分配"；
- key = { it.id } 给 LazyColumn 稳定键，提升重组性能（实验二会再强调）；
- 实验一只有 3 条数据，但 LazyColumn 能平滑扩展到上百条（实验二验收点）。

## 4.4 Preview（3 个，可独立预览）

文件：app/src/main/java/edu/example/mobilecourse/lab1/ui/TaskCard.kt

- PreviewTaskCardInProgress：进行中状态（张三、未完成、普通优先级）；
- PreviewTaskCardCompleted：已完成状态（李四、completed=true）；
- PreviewTaskCardUnassigned：未分配状态（owner=null，显示"未分配"，低优先级灰色标题）。

# 五、结果

## 5.1 成功截图

（在此插入截图 1：MainActivity 运行截图——3 张 TaskCard 列表，含进行中/已完成/未分配三种状态）

图 1  MainActivity 运行截图

（在此插入截图 2：TaskCard Preview 截图——进行中 + 已完成 + 未分配三个 Preview 并列）

图 2  TaskCard Preview 截图

（在此插入截图 3：模拟器整体运行截图，可看到桌面绿色应用图标）

图 3  模拟器实际运行截图

## 5.2 边界与错误状态

| 边界/错误状态 | 表现 |
|---|---|
| owner = null | displayOwner 返回"未分配"，不会崩溃 |
| owner = "   "（全空格） | trim() 后 isNotEmpty() 为 false，返回"未分配" |
| 优先级 priority = 1 | 标题显示为 MaterialTheme.colorScheme.error（红色） |
| 优先级 priority = 3 | 标题显示为 MaterialTheme.colorScheme.outline（灰色） |
| completed = true | 左侧图标为 CheckCircle，颜色为主色 |
| completed = false | 左侧图标为 RadioButtonUnchecked，颜色为 outline |

# 六、故障与调试

本次实验过程中遇到三个真实故障，均已解决。

## 故障一：模拟器系统镜像下载超时（Read timed out）

**现象**：在 Device Manager 中创建 Pixel 7 模拟器时，SDK Component Installer 下载 16 KB Page Size Google Play Intel x86_64 Atom System Image（API 37.1，共 2.0 GB）到 2% 后失败，日志报 "An error occurred while preparing SDK package ... Read timed out."，安装失败。

**定位**：查看下载地址为 https://dl.google.com/.../x86_64-playstore-ps16k-37.1_r09.zip。用 Test-NetConnection 测试 dl.google.com 的 443 端口可达，但大文件传输中途断流；尝试清华、阿里云等国内镜像，均无该 API 37.1 小版本镜像（返回 404）。

**原因**：国内直连 Google 官方下载服务器不稳定，长连接传输 2GB 大文件时被中途重置；而该 37.1 小版本镜像较新，国内镜像尚未同步。

**修复**：连接 Cisco AnyConnect VPN（日本专线，全局模式）后重新下载，SDK 安装器支持断点续传，下载从 2% 继续，最终 100% 完成并解压，模拟器成功开机。

## 故障二：Failed to find Platform SDK with path: platforms;android-37

**现象**：模拟器已开机，点 Run 后 Build 失败，Build Output 报错 "Failed to find Platform SDK with path: platforms;android-37"，构建停在 :app 阶段。

**定位**：查看 D:\Android\Sdk\platforms 目录，发现平台包实际安装在 android-37.0 目录，而不是 AGP 期望的 android-37；进一步查看该目录下 source.properties 与 package.xml，发现 AndroidVersion.ApiLevel=37.0、<api-level>37.0</api-level>、localPackage path="platforms;android-37.0"，即该平台以"Minor API Level 37.0"的新格式安装。

**原因**：Android 16 引入 Minor API Level 机制，新版 SDK 安装器把平台目录命名为 android-37.0 并把 api-level 记为 37.0；而项目使用的 AGP 8.7.2 仍按传统整数 API 级别查找名为 android-37、api-level 为整数 37 的平台包，两者命名与元数据不匹配，导致即使文件已下载仍判定平台缺失。

**修复**：将 platforms\android-37.0 整目录复制为 platforms\android-37，并在副本中修改三处元数据——package.xml 的 localPackage path 改为 platforms;android-37、<api-level> 改为 37，source.properties 的 AndroidVersion.ApiLevel 改为 37（保留原 android-37.0 目录不动）；再执行 gradlew --stop 结束缓存了旧扫描结果的 Gradle Daemon，重新 Run 后平台被正确识别，Build 通过。

## 故障三：AAPT error: resource mipmap/ic_launcher 找不到

**现象**：平台问题解决后，Build 又报 4 个 AAPT 错误，均指向 AndroidManifest.xml 第 6、8 行的 @mipmap/ic_launcher 与 @mipmap/ic_launcher_round 资源找不到。

**定位**：检查 app/src/main/res 目录，只有 values 文件夹（colors.xml、strings.xml、themes.xml），没有任何 mipmap 或图标资源。

**原因**：工程骨架生成时只创建了文本资源，缺少启动图标 PNG/XML；Manifest 引用了不存在的资源，AAPT 链接阶段直接失败。

**修复**：在 res 下新增 mipmap-anydpi-v26 自适应图标（ic_launcher.xml、ic_launcher_round.xml，引用 adaptive-icon），在 drawable 下新增前后景矢量图（ic_launcher_background.xml 绿色底、ic_launcher_foreground.xml 白色任务卡加对勾），并在 mipmap 目录放 API 24-25 的回退矢量图标。全部用 XML 矢量图实现，无需二进制 PNG。重新 Run 后 BUILD SUCCESSFUL。

# 七、思考

## 7.1 Kotlin 空安全的作用

在 Android 开发中，空指针异常（NPE）是最常见的崩溃原因之一。Kotlin 在类型系统层面区分 String（非空）与 String?（可空），强制开发者在编译期处理 null 情况。本实验中 owner 声明为 String?，调用时必须用 ?. 安全调用或显式非空断言 !!。displayOwner 函数使用 owner?.trim()?.takeIf { it.isNotEmpty() } ?: "未分配" 的安全调用链，既处理了 null 又处理了空白字符串，全程避免了 !! 带来的运行时崩溃风险。

## 7.2 Composable 无状态与有状态的区别

Compose 推荐将状态提升（State Hoisting）到上层 Composable。本实验的 TaskCard 完全无状态：title、owner、completed 等全部由参数传入，onClick 是回调。这样做的好处是 TaskCard 可复用、可独立 Preview、易于测试。实验三会进一步把状态从 Composable 提升到 ViewModel，通过 StateFlow 向下传递，形成完整的单向数据流（UDF）。

## 7.3 data class 与普通 class 的区别

Kotlin 的 data class 自动生成 equals()、hashCode()、toString()、componentN() 和 copy() 方法，适合用作数据载体。CourseTask 作为 UI 数据模型，用 data class 可以方便地比较两个任务是否相等（Compose 重组时依赖 equals 判断状态是否变化），也可以用 copy() 生成只修改了部分字段的新实例，这在实验二的不可变状态更新中会用到。

# 附录：提交物清单

| 提交物 | 状态 |
|---|---|
| 源代码 | 已提交至 https://github.com/lcyspring/Android 仓库 lcy 分支的 lab1/ 目录 |
| Git 提交节点 | 起始提交已完成；主要功能、最终修复两个节点待补充 |
| 实验报告 | 本报告 |
| 运行截图 | 3 张，待插入第五章 |
