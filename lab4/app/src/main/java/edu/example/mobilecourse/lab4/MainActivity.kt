package edu.example.mobilecourse.lab4

import android.Manifest
import android.os.Bundle
import android.util.Log
import android.widget.Toast
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.material3.MaterialTheme
import edu.example.mobilecourse.lab4.data.preferences.UserPreferences
import edu.example.mobilecourse.lab4.ui.App

/**
 * 实验四入口 Activity(扩展:相机运行时权限)。
 *
 * 实验四关键设计:
 * - 相机权限**不在启动时无理由申请**,而是用户点相机按钮后才申请(步骤 26)。
 * - 权限拒绝后 Toast 提示,**App 不崩溃**(验收点)。
 * - DataStore 偏好通过 UserPreferences.getInstance(this) 初始化,传给 App。
 * - 默认用 NetworkTaskRepository(JSONPlaceholder),验收断网时传 FakeTaskRepository(errorMode = true)。
 */
class MainActivity : ComponentActivity() {

    private lateinit var prefs: UserPreferences

    // 实验四:运行时权限请求 Launcher,只在用户点相机按钮时触发
    private val cameraPermissionLauncher = registerForActivityResult(
        ActivityResultContracts.RequestPermission()
    ) { granted ->
        if (granted) {
            Log.d(TAG, "相机权限已授予")
            Toast.makeText(this, "相机权限已授予", Toast.LENGTH_SHORT).show()
        } else {
            Log.w(TAG, "相机权限被拒绝")
            Toast.makeText(this, "相机权限被拒绝,无法使用相机功能", Toast.LENGTH_LONG).show()
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        prefs = UserPreferences.getInstance(this)

        setContent {
            MaterialTheme {
                App(
                    prefs = prefs,
                    // 实验四:点击相机按钮 -> 动态申请权限(不在启动时申请)
                    onRequestCamera = {
                        cameraPermissionLauncher.launch(Manifest.permission.CAMERA)
                    },
                )
            }
        }
    }

    companion object {
        private const val TAG = "Lab4.MainActivity"
    }
}
