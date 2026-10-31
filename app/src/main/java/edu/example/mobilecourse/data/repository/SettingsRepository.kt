package edu.example.mobilecourse.data.repository

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/**
 * 用户偏好（DataStore Preferences）访问仓库。
 *
 * 职责：
 *   1. 定义偏好 key；
 *   2. 提供 Flow 形式的读取接口（响应式，UI 可自动收到变更）；
 *   3. 提供 suspend 形式的写入接口。
 *
 * 注意：Composable 不直接读写 DataStore，统一经过 ViewModel → Repository。
 */
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(
    name = "settings"
)

class SettingsRepository(private val context: Context) {

    companion object {
        /** “仅看未完成任务”开关 */
        private val KEY_SHOW_ONLY_INCOMPLETE = booleanPreferencesKey("show_only_incomplete")
    }

    /** 读取：Flow<Boolean>，true 表示仅看未完成 */
    val showOnlyIncompleteFlow: Flow<Boolean> =
        context.dataStore.data.map { prefs ->
            prefs[KEY_SHOW_ONLY_INCOMPLETE] ?: false
        }

    /** 写入：挂起函数 */
    suspend fun setShowOnlyIncomplete(value: Boolean) {
        context.dataStore.edit { prefs ->
            prefs[KEY_SHOW_ONLY_INCOMPLETE] = value
        }
    }
}
