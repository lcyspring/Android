package edu.example.mobilecourse.lab2

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.material3.MaterialTheme
import edu.example.mobilecourse.lab2.ui.App

/**
 * 实验二入口 Activity。
 *
 * 实验二关键重构:把首页 UI 从 MainActivity 抽到 [App] / [edu.example.mobilecourse.lab2.ui.home.HomeScreen],
 * MainActivity 只负责挂载 Compose 树,所有页面与导航都在 [App] 内的 NavHost 中组合。
 *
 * 步骤对照(实验指导书 C 部分):
 * - 步骤 11 在 App 中连接 NavHost 两个目的地 —— 由 [App] 完成
 * - 步骤 12 TaskCard.onOpenTask -> navController.navigate —— 由 HomeScreen 上层回调
 */
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            MaterialTheme {
                App()
            }
        }
    }
}
