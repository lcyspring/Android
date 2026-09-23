package edu.example.mobilecourse.lab4.data.preferences

import android.content.Context
import androidx.datastore.core.DataStore
import androidx.datastore.preferences.core.Preferences
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

/**
 * 实验四:DataStore 偏好存储(指导书步骤 25)。
 *
 * 两个偏好:
 * - showOnlyIncomplete: Boolean,默认 false,筛选"仅看未完成任务"
 * - darkMode: Boolean,默认 false,深色模式开关
 *
 * 验收点"不在 Composable 中直接读写 DataStore":
 *   DataStore 只能在 Repository/ViewModel 层访问,Composable 只从 ViewModel 的 StateFlow 读值、
 *   通过 onAction 向上写值。本类是唯一访问 DataStore 的入口。
 */
private val Context.dataStore: DataStore<Preferences> by preferencesDataStore(name = "lab4_prefs")

class UserPreferences(private val context: Context) {

    // --- 读取 Flow(对外暴露,ViewModel collect) ---
    val showOnlyIncompleteFlow: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[KEY_SHOW_INCOMPLETE] ?: false
    }

    val darkModeFlow: Flow<Boolean> = context.dataStore.data.map { prefs ->
        prefs[KEY_DARK_MODE] ?: false
    }

    // --- 写入 suspend 函数(ViewModel 在 viewModelScope.launch 中调用) ---
    suspend fun setShowOnlyIncomplete(enabled: Boolean) {
        context.dataStore.edit { it[KEY_SHOW_INCOMPLETE] = enabled }
    }

    suspend fun setDarkMode(enabled: Boolean) {
        context.dataStore.edit { it[KEY_DARK_MODE] = enabled }
    }

    companion object {
        private val KEY_SHOW_INCOMPLETE = booleanPreferencesKey("show_only_incomplete")
        private val KEY_DARK_MODE = booleanPreferencesKey("dark_mode")

        // 单例:全局共享同一个 Context
        @Volatile private var instance: UserPreferences? = null
        fun getInstance(context: Context): UserPreferences =
            instance ?: synchronized(this) {
                instance ?: UserPreferences(context.applicationContext).also { instance = it }
            }
    }
}
