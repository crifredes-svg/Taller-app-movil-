package com.redcuidadora.app.data.network

import com.google.gson.Gson
import com.google.gson.JsonObject
import retrofit2.Response

object ApiErrorParser {

    fun parseError(response: Response<*>): String {
        return try {
            val errorBody = response.errorBody()?.string() ?: return "Error de red en el servidor"
            val jsonObject = Gson().fromJson(errorBody, JsonObject::class.java)

            if (jsonObject.has("detail")) {
                val detailElement = jsonObject["detail"]
                if (detailElement != null && detailElement.isJsonPrimitive) {
                    return detailElement.asString
                } else if (detailElement != null && detailElement.isJsonArray) {
                    val firstError = detailElement.asJsonArray.firstOrNull()?.asJsonObject
                    val msg = firstError?.get("msg")?.asString ?: "Datos inválidos"
                    val loc = firstError?.get("loc")?.asJsonArray?.lastOrNull()?.asString ?: ""
                    return if (loc.isNotEmpty()) "$loc: $msg" else msg
                }
            }
            "Error inesperado (${response.code()})"
        } catch (_: Exception) {
            "Error inesperado (${response.code()})"
        }
    }
}
