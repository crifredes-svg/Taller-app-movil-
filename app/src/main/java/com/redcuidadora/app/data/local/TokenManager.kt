package com.redcuidadora.app.data.local

import android.content.Context
import android.content.SharedPreferences
import com.google.gson.Gson
import com.redcuidadora.app.data.network.UsuarioDto

object TokenManager {
    private const val PREF_NAME = "redcuidadora_session_prefs"
    private const val KEY_ACCESS_TOKEN = "access_token"
    private const val KEY_EXPIRES_AT = "expires_at_timestamp"
    private const val KEY_USER_DATA = "user_data_json"

    private fun getPrefs(context: Context): SharedPreferences {
        return context.getSharedPreferences(PREF_NAME, Context.MODE_PRIVATE)
    }

    fun saveSession(context: Context, token: String, expiresInSeconds: Long, user: UsuarioDto?) {
        val expiresAt = System.currentTimeMillis() + (expiresInSeconds * 1000)
        val userJson = if (user != null) Gson().toJson(user) else null

        getPrefs(context).edit()
            .putString(KEY_ACCESS_TOKEN, token)
            .putLong(KEY_EXPIRES_AT, expiresAt)
            .putString(KEY_USER_DATA, userJson)
            .apply()
    }

    fun getToken(context: Context): String? {
        val prefs = getPrefs(context)
        val token = prefs.getString(KEY_ACCESS_TOKEN, null)
        val expiresAt = prefs.getLong(KEY_EXPIRES_AT, 0L)

        if ((token.isNullOrEmpty()) || (System.currentTimeMillis() >= expiresAt)) {
            clearSession(context)
            return null
        }
        return token
    }

    fun getUser(context: Context): UsuarioDto? {
        val userJson = getPrefs(context).getString(KEY_USER_DATA, null) ?: return null
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
        getPrefs(context).edit().clear().apply()
    }
}
