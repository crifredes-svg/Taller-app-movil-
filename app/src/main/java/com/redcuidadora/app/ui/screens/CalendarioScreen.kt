package com.redcuidadora.app.ui.screens

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.KeyboardArrowRight
import androidx.compose.material.icons.filled.Add
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.Schedule
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.redcuidadora.app.data.local.TokenManager
import com.redcuidadora.app.data.network.*
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.navigation.RedCuidadoraBottomNavigation
import com.redcuidadora.app.ui.navigation.Screen
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.StatusAmber
import com.redcuidadora.app.ui.theme.StatusGreen
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun CalendarioScreen(
    onNavigateToSolicitudes: () -> Unit,
) {
    val context = LocalContext.current
    val userId = TokenManager.getUserId(context)
    val weekDates = remember { currentWeekDates() }
    var selectedDayIndex by remember { mutableIntStateOf(weekDates.indexOf(todayIso()).coerceAtLeast(0)) }
    val summary = rememberRemoteData(userId) { RetrofitClient.getApiService(context).obtenerResumenSemana().requireBody() }
    val requests = rememberRemoteData(userId) {
        allPages { RetrofitClient.getApiService(context).listarRelevosUsuario(userId ?: error("Inicia sesión nuevamente."), it) }
    }
    val contacts = rememberRemoteData(userId) {
        allPages { RetrofitClient.getApiService(context).listarContactos(userId ?: error("Inicia sesión nuevamente."), it) }
    }
    val shifts = requests.data.orEmpty().filter { it.fecha == weekDates[selectedDayIndex] }.sortedBy { it.horaInicio }
    fun caregiverName(id: Int?): String = when (id) {
        userId -> "${TokenManager.getUser(context)?.nombre.orEmpty()} (Tú)"
        null -> "Buscando apoyo..."
        else -> contacts.data?.find { it.contactoUsuarioId == id }?.let { "${it.nombre} (${it.relacion})" } ?: "Usuario #$id"
    }

    val days = listOf(
        "Lun" to "L",
        "Mar" to "M",
        "Mié" to "X",
        "Jue" to "J",
        "Vie" to "V",
        "Sáb" to "S",
        "Dom" to "D",
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(modifier = Modifier.height(16.dp))

        // Title
        Text(
            text = "Calendario de Relevos",
            style = MaterialTheme.typography.headlineLarge,
            color = TextPrimaryDark,
            fontWeight = FontWeight.Bold,
        )
        Text(
            text = "Horas de estudio y turnos protegidos",
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondaryDark,
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Hours Counter Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp),
            border = BorderStroke(1.dp, PrimaryEmerald.copy(alpha = 0.5f)),
        ) {
            Row(
                modifier = Modifier.padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
            ) {
                Box(
                    modifier = Modifier
                        .size(40.dp)
                        .background(PrimaryEmerald.copy(alpha = 0.15f), CircleShape),
                    contentAlignment = Alignment.Center,
                ) {
                    Icon(
                        imageVector = Icons.Default.Schedule,
                        contentDescription = "Reloj",
                        tint = PrimaryEmerald,
                    )
                }
                Spacer(modifier = Modifier.width(12.dp))
                Text(
                    text = summary.data?.let { "${it.horasProtegidas} horas de estudio y clases protegidas esta semana" } ?: summary.message,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Week Days Selector
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
        ) {
            days.forEachIndexed { index, (label, initial) ->
                val isSelected = index == selectedDayIndex
                Column(
                    horizontalAlignment = Alignment.CenterHorizontally,
                    modifier = Modifier.clickable { selectedDayIndex = index },
                ) {
                    Text(
                        text = label,
                        fontSize = 12.sp,
                        color = TextSecondaryDark,
                        fontWeight = FontWeight.Medium,
                    )
                    Spacer(modifier = Modifier.height(6.dp))
                    Box(
                        modifier = Modifier
                            .size(40.dp)
                            .background(
                                color = if (isSelected) PrimaryEmerald else DarkSurfaceVariant,
                                shape = CircleShape,
                            ),
                        contentAlignment = Alignment.Center,
                    ) {
                        Text(
                            text = initial,
                            color = TextPrimaryDark,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp,
                        )
                    }
                    if (isSelected) {
                        Spacer(modifier = Modifier.height(4.dp))
                        Box(
                            modifier = Modifier
                                .size(4.dp)
                                .background(PrimaryEmerald, CircleShape),
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Header for Turnos
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically,
        ) {
            Text(
                text = "Turnos del ${weekDates[selectedDayIndex]}",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold,
            )

            Row(
                verticalAlignment = Alignment.CenterVertically,
                modifier = Modifier.clickable { onNavigateToSolicitudes() },
            ) {
                Icon(
                    imageVector = Icons.Default.Add,
                    contentDescription = "Solicitar",
                    tint = PrimaryEmerald,
                    modifier = Modifier.size(16.dp),
                )
                Spacer(modifier = Modifier.width(4.dp))
                Text(
                    text = "Solicitar Relevo",
                    color = PrimaryEmerald,
                    fontSize = 13.sp,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        if (shifts.isEmpty()) {
            Text(
                text = if (requests.data == null) requests.message else "No hay turnos para este día.",
                color = TextSecondaryDark,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

        shifts.filter { it.estado != "pendiente" }.forEach { shift ->
        Card(
            modifier = Modifier.fillMaxWidth().clickable { onNavigateToSolicitudes() },
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp),
            border = BorderStroke(1.dp, PrimaryEmerald),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Schedule,
                            contentDescription = "Horario",
                            tint = PrimaryEmerald,
                            modifier = Modifier.size(18.dp),
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "${shift.horaInicio} – ${shift.horaFin}",
                            color = TextPrimaryDark,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp,
                        )
                    }

                    Surface(
                        color = StatusGreen.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(8.dp),
                    ) {
                        Text(
                            text = if (shift.estado == "completada") "Completado" else "Confirmado",
                            color = StatusGreen,
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = shift.titulo,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Bold,
                )

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .background(PrimaryEmerald, CircleShape),
                            contentAlignment = Alignment.Center,
                        ) {
                            Text(text = caregiverName(shift.cuidadorId).take(1), color = TextPrimaryDark, fontWeight = FontWeight.Bold)
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(text = "Cuidador asignado", fontSize = 11.sp, color = TextSecondaryDark)
                            Text(
                                text = caregiverName(shift.cuidadorId),
                                fontSize = 13.sp,
                                color = TextPrimaryDark,
                                fontWeight = FontWeight.SemiBold,
                            )
                        }
                    }

                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = "Detalle",
                        tint = TextSecondaryDark,
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(12.dp))
        }

        shifts.filter { it.estado == "pendiente" }.forEach { shift ->
        Card(
            modifier = Modifier.fillMaxWidth().clickable { onNavigateToSolicitudes() },
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp),
            border = BorderStroke(1.dp, StatusAmber),
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.Schedule,
                            contentDescription = "Horario",
                            tint = StatusAmber,
                            modifier = Modifier.size(18.dp),
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "${shift.horaInicio} – ${shift.horaFin}",
                            color = TextPrimaryDark,
                            fontWeight = FontWeight.Bold,
                            fontSize = 14.sp,
                        )
                    }

                    Surface(
                        color = StatusAmber.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(8.dp),
                    ) {
                        Text(
                            text = "Buscando apoyo",
                            color = StatusAmber,
                            fontWeight = FontWeight.Bold,
                            fontSize = 11.sp,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp),
                        )
                    }
                }

                Spacer(modifier = Modifier.height(10.dp))

                Text(
                    text = shift.titulo,
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Bold,
                )

                Spacer(modifier = Modifier.height(12.dp))

                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically,
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Box(
                            modifier = Modifier
                                .size(32.dp)
                                .background(DarkSurfaceVariant, CircleShape),
                            contentAlignment = Alignment.Center,
                        ) {
                            Icon(
                                imageVector = Icons.Default.Person,
                                contentDescription = "Cuidador",
                                tint = TextSecondaryDark,
                                modifier = Modifier.size(18.dp),
                            )
                        }
                        Spacer(modifier = Modifier.width(8.dp))
                        Column {
                            Text(text = "Cuidador asignado", fontSize = 11.sp, color = TextSecondaryDark)
                            Text(
                                text = "Buscando apoyo...",
                                fontSize = 13.sp,
                                color = TextSecondaryDark,
                                fontWeight = FontWeight.Medium,
                            )
                        }
                    }

                    Icon(
                        imageVector = Icons.AutoMirrored.Filled.KeyboardArrowRight,
                        contentDescription = "Detalle",
                        tint = TextSecondaryDark,
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
        }
    }
}

@Preview(name = "Teléfono - Calendario", showBackground = true, showSystemUi = true)
@Composable
fun CalendarioScreenPreview() {
    RedCuidadoraTheme {
        Scaffold(
            bottomBar = {
                RedCuidadoraBottomNavigation(
                    currentRoute = Screen.Calendario.route,
                    onNavigateToRoute = {},
                )
            },
            containerColor = MaterialTheme.colorScheme.background,
        ) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                CalendarioScreen(onNavigateToSolicitudes = {})
            }
        }
    }
}

@Preview(name = "Tablet - Calendario", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun CalendarioScreenTabletPreview() {
    RedCuidadoraTheme {
        Scaffold(
            bottomBar = {
                RedCuidadoraBottomNavigation(
                    currentRoute = Screen.Calendario.route,
                    onNavigateToRoute = {},
                )
            },
            containerColor = MaterialTheme.colorScheme.background,
        ) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                CalendarioScreen(onNavigateToSolicitudes = {})
            }
        }
    }
}
