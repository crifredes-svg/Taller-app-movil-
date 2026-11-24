package com.redcuidadora.app.data.network

import java.text.SimpleDateFormat
import java.util.Calendar
import java.util.Locale

fun todayIso(): String = SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).format(Calendar.getInstance().time)

fun currentWeekDates(): List<String> {
    val day = Calendar.getInstance()
    day.add(Calendar.DAY_OF_MONTH, -((day.get(Calendar.DAY_OF_WEEK) + 5) % 7))
    val format = SimpleDateFormat("yyyy-MM-dd", Locale.ROOT)
    return List(7) {
        format.format(day.time).also { day.add(Calendar.DAY_OF_MONTH, 1) }
    }
}

data class ReliefSchedule(val date: String, val start: String, val end: String)

fun parseReliefSchedule(value: String): ReliefSchedule {
    val match = Regex("""^(\d{4}-\d{2}-\d{2}) ([0-2]\d:[0-5]\d) - ([0-2]\d:[0-5]\d)$""")
        .matchEntire(value.trim())
        ?: error("Usa el horario YYYY-MM-DD HH:mm - HH:mm.")
    val (date, start, end) = match.destructured
    val format = SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).apply { isLenient = false }
    require(runCatching { format.parse(date)?.let(format::format) == date }.getOrDefault(false)) {
        "Ingresa una fecha válida."
    }
    require(date >= todayIso()) { "La fecha no puede estar en el pasado." }
    require(start < "24:00" && end < "24:00" && start < end) { "La hora final debe ser posterior al inicio, en el mismo día." }
    return ReliefSchedule(date, start, end)
}

fun SolicitudRelevoDto.hours(): Double {
    fun minutes(value: String): Int {
        val parts = value.split(":")
        return (parts.getOrNull(0)?.toIntOrNull() ?: 0) * 60 + (parts.getOrNull(1)?.toIntOrNull() ?: 0)
    }
    return (minutes(horaFin) - minutes(horaInicio)).coerceAtLeast(0) / 60.0
}

fun SolicitudRelevoDto.shareText(): String =
    "$titulo\n$fecha $horaInicio - $horaFin\n$descripcion\nEstado: $estado"
