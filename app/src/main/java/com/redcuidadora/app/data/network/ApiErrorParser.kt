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
                if ((detailElement != null) && (detailElement.isJsonPrimitive)) {
                    return detailElement.asString
                } else if ((detailElement != null) && (detailElement.isJsonArray)) {
                    val firstError = detailElement.asJsonArray.firstOrNull()?.asJsonObject
                    val msg = firstError?.get("msg")?.asString ?: "Datos inválidos"
                    val loc = firstError?.get("loc")?.asJsonArray?.lastOrNull()?.asString ?: ""
                    return translateErrorMsg(msg, loc)
                }
            }
            "Error inesperado (${response.code()})"
        } catch (_: Exception) {
            "Error inesperado (${response.code()})"
        }
    }

    private fun translateErrorMsg(msg: String, field: String): String {
        val fieldName = when (field) {
            "descripcion" -> "La descripción"
            "titulo" -> "El título"
            "fecha" -> "La fecha"
            "correo" -> "El correo"
            "password" -> "La contraseña"
            else -> field
        }
        return when {
            msg.contains("at most 200", ignoreCase = true) || msg.contains("max_length", ignoreCase = true) ->
                "La descripción no puede superar los 200 caracteres."
            msg.contains("at least", ignoreCase = true) ->
                "La descripción debe tener al menos 10 caracteres."
            msg.contains("value is not a valid email", ignoreCase = true) ->
                "Ingresa un correo electrónico válido."
            else -> if (fieldName.isNotEmpty()) "$fieldName: $msg" else msg
        }
    }
}
