package com.redcuidadora.app.data.local

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.redcuidadora.app.data.network.UsuarioDto
import kotlinx.coroutines.flow.MutableSharedFlow
import kotlinx.coroutines.flow.SharedFlow

@Suppress("unused")
object TokenManager {
    private const val PREF_NAME = "redcuidadora_session_prefs"
    private const val KEY_ACCESS_TOKEN = "access_token"
    private const val KEY_EXPIRES_AT = "expires_at_timestamp"
    private const val KEY_USER_DATA = "user_data_json"

    private val _changes = MutableSharedFlow<Unit>(replay = 1)
    val changes: SharedFlow<Unit> = _changes

    private fun getPrefs(context: Context?): SharedPreferences? {
        return try {
            context?.applicationContext?.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
        } catch (_: Exception) {
            null
        }
    }

    fun saveSession(context: Context, token: String, expiresInSeconds: Long, user: UsuarioDto?) {
        val expiresAt = System.currentTimeMillis() + (expiresInSeconds * 1000)
        val userJson = if (user != null) Gson().toJson(user) else null

        val prefs = getPrefs(context)
        val editor = prefs?.edit()
        editor?.putString(KEY_ACCESS_TOKEN, token)
        editor?.putLong(KEY_EXPIRES_AT, expiresAt)
        editor?.putString(KEY_USER_DATA, userJson)
        editor?.apply()

        _changes.tryEmit(Unit)
    }

    fun updateUser(context: Context, user: UsuarioDto) {
        val userJson = Gson().toJson(user)
        val prefs = getPrefs(context)
        val editor = prefs?.edit()
        editor?.putString(KEY_USER_DATA, userJson)
        editor?.apply()

        _changes.tryEmit(Unit)
    }

    fun getToken(context: Context): String? {
        val prefs = getPrefs(context) ?: return null
        val token = prefs.getString(KEY_ACCESS_TOKEN, null)
        val expiresAt = prefs.getLong(KEY_EXPIRES_AT, 0L)

        if ((token.isNullOrEmpty()) || (System.currentTimeMillis() >= expiresAt)) {
            clearSession(context)
            return null
        }
        return token
    }

    fun getUser(context: Context): UsuarioDto? {
        val userJson = getPrefs(context)?.getString(KEY_USER_DATA, null) ?: return null
        return try {
            Gson().fromJson(userJson, UsuarioDto::class.java)
        } catch (_: Exception) {
            null
        }
    }

    fun getUserId(context: Context): Int? {
        return getUser(context)?.id
    }

    fun isLoggedIn(context: Context): Boolean {
        return getToken(context) != null
    }

    fun clearSession(context: Context) {
        try {
            val prefs = getPrefs(context)
            val editor = prefs?.edit()
            editor?.clear()
            editor?.apply()
        } catch (_: Exception) {}
        _changes.tryEmit(Unit)
    }
}
