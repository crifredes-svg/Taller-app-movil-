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
    val clean = value.trim()
    val matchYmd = Regex("""^(\d{4}[-/]\d{2}[-/]\d{2}) ([0-2]?\d:[0-5]\d) - ([0-2]?\d:[0-5]\d)$""").matchEntire(clean)
    val matchDmy = Regex("""^(\d{2}[-/]\d{2}[-/]\d{4}) ([0-2]?\d:[0-5]\d) - ([0-2]?\d:[0-5]\d)$""").matchEntire(clean)

    val (dateRaw, startRaw, endRaw) = when {
        matchYmd != null -> matchYmd.destructured
        matchDmy != null -> matchDmy.destructured
        else -> error("Usa el horario DD-MM-YYYY HH:mm - HH:mm (ej. 15-05-2027 09:30 - 13:00).")
    }

    fun formatHour(h: String): String = if (h.length == 4) "0$h" else h

    val start = formatHour(startRaw)
    val end = formatHour(endRaw)

    val isoDate = if (matchDmy != null) {
        val parts = dateRaw.replace('/', '-').split("-")
        "${parts[2]}-${parts[1]}-${parts[0]}"
    } else {
        dateRaw.replace('/', '-')
    }

    val format = SimpleDateFormat("yyyy-MM-dd", Locale.ROOT).apply { isLenient = false }
    require(runCatching { format.parse(isoDate)?.let(format::format) == isoDate }.getOrDefault(false)) {
        "Ingresa una fecha válida."
    }
    require(isoDate >= todayIso()) { "La fecha no puede estar en el pasado." }
    require(start < "24:00" && end < "24:00" && start < end) { "La hora final debe ser posterior al inicio." }
    return ReliefSchedule(isoDate, start, end)
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
