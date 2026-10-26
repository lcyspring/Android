# 实验二 · 移动 UI 设计与页面导航

课程《移动应用开发》实验二，在实验一 Kotlin + Compose 基础界面之上引入 Navigation Compose，实现 **Home（任务列表）→ TaskDetail（任务详情）** 的多页面导航，并完成 EmptyContent 空状态、100 条长列表滚动等验收点。

- 指导书：`移动应用开发_实验指导书_学生版.pdf`（实验二：移动 UI 设计与页面导航，2 学时）
- 姓名：李春雨　学号：202305567128　班级：计科2班

## 项目结构

```
edu.example.mobilecourse.lab2/
├── MainActivity.kt                          // 只 setContent { App() }，入口 Activity
├── data/
│   └── CourseTask.kt                        // data class + displayOwner 空安全 + sampleTasks 100 条 + taskById
└── ui/
    ├── App.kt                               // 根 Composable：NavHost 连接两个目的地，持有 NavController
    ├── TaskCard.kt                          // 可复用卡片，onOpenTask() 回调解耦，无导航依赖
    ├── navigation/
    │   └── Lab2Destinations.kt              // sealed class Destination 集中表达路由模板
    ├── home/
    │   ├── HomeScreen.kt                    // 首页：LazyColumn + 稳定 key + 空/非空分支
    │   └── EmptyContent.kt                  // 空列表占位，onRefresh 回调
    └── taskdetail/
        └── TaskDetailScreen.kt              // 详情页：taskId 取数 + 边界状态（找不到任务）
```

## 技术栈

| 组件 | 版本 |
|---|---|
| AGP | 8.7.2 |
| Kotlin | 2.0.21 |
| Compose BOM | 2024.10.01 |
| Navigation Compose | 2.8.3 |
| Gradle | 8.10.2 |
| compileSdk | 37 |
| minSdk | 24 |
| JDK | 17 |

## 环境要求

- JDK 17（Android Studio 自带 JBR 17 或 Microsoft OpenJDK 17 均可）
- Android SDK API 37（路径 D:\Android\Sdk，自行修改 `local.properties` 的 `sdk.dir`）
- Gradle Wrapper 8.10.2（项目自带 `gradlew`，首次构建会自动下载）
- 运行设备：Android 模拟器或真机，API 37

## 构建与运行

```powershell
# Windows（PowerShell）
.\gradlew.bat assembleDebug        # 编译 debug APK
.\gradlew.bat installDebug         # 安装到已连接设备
.\gradlew.bat assembleRelease      # 编译 release APK

# macOS / Linux
./gradlew assembleDebug
```

APK 输出路径：`app/build/outputs/apk/debug/app-debug.apk`

用 Android Studio 打开项目后，点 Run 按钮即可安装到模拟器。

## 导航关系

```
NavController (App 层 rememberNavController 持有)
     |
     v
NavHost(startDestination = "home")
  ├── composable("home")              → HomeScreen(tasks, onOpenTask, onRefresh)
  │       onOpenTask = { id -> navigate(TaskDetailDestination.createRoute(id)) }
  └── composable("task_detail/{taskId}") → TaskDetailScreen(taskId, onBack)
          taskId 由 NavHost 解析路由占位符后传入
          onBack = { popBackStack() }
```

关键解耦约定：**NavController 只在 App 这一层持有**，HomeScreen、TaskCard、TaskDetailScreen 都不直接访问它，只通过回调把事件向上传递。这样页面可以独立 Preview、独立测试、未来可被其他 Tab 或搜索页复用。

## 验收点对照

| 验收点 | 状态 |
|---|---|
| 导航能带入正确 taskId | ✅ TaskDetailScreen(taskId=1) 显示"完成实验二报告" |
| 不直接访问 TaskCard NavController | ✅ TaskCard 只调 onOpenTask()，由 App 接 navigate |
| 列表为空时有明确空状态 | ✅ EmptyContent + "点这里重试"按钮（修复 onRefresh 空实现） |
| 100 条数据滚动正常 | ✅ LazyColumn + 稳定 key = task.id |

## 空状态测试钩子

App 函数的 `overrideTasks` 参数可以传入 `emptyTasks` 触发空状态：

```kotlin
// 临时修改 MainActivity 的 setContent 来演示空状态
MaterialTheme {
    App(overrideTasks = emptyTasks)
}
```

## 构建结果

```
BUILD SUCCESSFUL in 1m 16s
35 actionable tasks: 35 executed
```

## Git 提交节点

```
4d8da96  docs(lab2): 实验二报告 docx + 生成脚本
a51b7be  feat(lab2): 主要功能 - NavHost 多页面导航
1734f26  chore(lab2): 起始项目骨架
```

## 实验报告

`docs/实验二报告_移动UI设计与页面导航.docx`

报告按指导书"五、实验报告统一模板"7 栏目组织（目标/环境/设计/实现/结果/故障与调试/思考），真实故障为：Destination.route 缺 `{taskId}` 占位符导致 `navigate("task_detail/7")` 报"目的地未注册"。

## 自检清单

- [x] 项目可从干净环境按 README 启动
- [x] 没有真实密码、token、API Key、个人隐私数据进入仓库
- [x] 导航参数正确，返回行为正常
- [x] 至少测试一个失败场景（taskId 找不到任务的边界状态）
- [x] Git 历史体现开发过程（3 个有意义提交）
- [x] 答辩成员能解释核心代码（NavHost / Destination / NavController 解耦方式）
