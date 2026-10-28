package com.redcuidadora.app.ui.screens

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
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import com.redcuidadora.app.data.local.TokenManager
import com.redcuidadora.app.data.network.*
import androidx.compose.ui.tooling.preview.Preview
import com.redcuidadora.app.ui.navigation.RedCuidadoraBottomNavigation
import com.redcuidadora.app.ui.navigation.Screen
import com.redcuidadora.app.ui.components.StatusNotificationBanner3
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.StatusAmber
import com.redcuidadora.app.ui.theme.StatusGreen
import com.redcuidadora.app.ui.theme.StatusOrange
import com.redcuidadora.app.ui.theme.StatusRed
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun HomeScreen(
    onNavigateToSolicitudes: () -> Unit,
    onNavigateToCheckIn: (String) -> Unit,
    onNavigateToPerfil: () -> Unit = {},
) {
    val context = LocalContext.current
    val action = rememberApiAction()
    val userId = TokenManager.getUserId(context)
    val user = rememberRemoteData(userId) {
        TokenManager.getUser(context) ?: error("Inicia sesión nuevamente.")
    }
    val contacts = rememberRemoteData(userId) {
        allPages { RetrofitClient.getApiService(context).listarContactos(userId ?: error("Inicia sesión nuevamente."), it) }
    }
    val checkIns = rememberRemoteData(userId) {
        allPages { RetrofitClient.getApiService(context).listarCheckIns(userId ?: error("Inicia sesión nuevamente."), it) }
    }
    val trend = rememberRemoteData(userId) { RetrofitClient.getApiService(context).obtenerTendencia().requireBody() }
    val alerts = rememberRemoteData(userId) { allPages { RetrofitClient.getApiService(context).listarSOSRecibidas(it) } }
    val relief = rememberRemoteData(userId) {
        allPages { RetrofitClient.getApiService(context).listarRelevosUsuario(userId ?: error("Inicia sesión nuevamente."), it) }
    }
    val latest = checkIns.data?.maxByOrNull { it.fecha.orEmpty() }
    val selectedMood = when (latest?.nivel) {
        "bien" -> "Bien"
        "algo_cansada" -> "Cansada"
        "necesito_apoyo" -> "Apoyo"
        "sobrepasada" -> "Sobrepasada"
        else -> ""
    }
    val next = relief.data?.filter { it.estado == "aceptada" && it.fecha >= todayIso() }
        ?.sortedWith(compareBy<SolicitudRelevoDto> { it.fecha }.thenBy { it.horaInicio })?.firstOrNull()
    val activeAlert = alerts.data?.firstOrNull { it.estado == "activa" }
    val alertText = when {
        activeAlert != null -> {
            val name = contacts.data?.find { it.contactoUsuarioId == activeAlert.usuarioId }?.nombre
                ?: "Usuario #${activeAlert.usuarioId}"
            "SOS de $name: ${activeAlert.mensaje}"
        }
        alerts.data == null -> alerts.message
        trend.data == null -> trend.message
        trend.data?.sugerirPedirApoyo == true ->
            "Alerta preventiva de sobrecarga: ${trend.data?.diasAltaCarga} días con alta carga. Considera pedir apoyo a tu red."
        else -> "Sin alertas de sobrecarga ni SOS recibidas."
    }
    var showSosDialog by remember { mutableStateOf(value = false) }

    if (showSosDialog) {
        AlertDialog(
            onDismissRequest = { showSosDialog = false },
            title = {
                Text(
                    text = "🚨 Activar SOS de Confianza",
                    fontWeight = FontWeight.Bold,
                    color = TextPrimaryDark,
                )
            },
            text = {
                Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
                    Text(
                        text = "La alerta quedará disponible para tu Red de Confianza${contacts.data?.takeIf { it.isNotEmpty() }?.joinToString(prefix = " (", postfix = ")") { it.nombre }.orEmpty()} cuando consulten la app, indicando que necesitas un relevo urgente. No se envían notificaciones push.",
                        color = TextSecondaryDark,
                        fontSize = 14.sp,
                    )
                    action.message?.takeIf { !action.success }?.let { message ->
                        StatusNotificationBanner3(message = message, isSuccess = false)
                    }
                }
            },
            confirmButton = {
                Button(
                    onClick = {
                        action.run("Alerta SOS registrada correctamente. Tu red puede verla al consultar la app.", onSuccess = { showSosDialog = false }) {
                            RetrofitClient.getApiService(context).activarSOS(
                                AlertaSOSDto(usuarioId = userId ?: error("Inicia sesión nuevamente.")),
                            ).requireBody(201)
                        }
                    },
                    enabled = !action.busy,
                    colors = ButtonDefaults.buttonColors(containerColor = StatusRed),
                ) {
                    Text("Enviar Alerta Urgente", color = Color.White, fontWeight = FontWeight.Bold)
                }
            },
            dismissButton = {
                TextButton(onClick = { showSosDialog = false }) {
                    Text("Cancelar", color = TextSecondaryDark)
                }
            },
            containerColor = DarkSurface,
            shape = RoundedCornerShape(16.dp)
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Spacer(modifier = Modifier.height(16.dp))

        if (!showSosDialog) {
            action.message?.let { message ->
                StatusNotificationBanner3(message = message, isSuccess = action.success)
                Spacer(modifier = Modifier.height(16.dp))
            }
        }

        // Top Header
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.SpaceBetween,
            verticalAlignment = Alignment.CenterVertically
        ) {
            Text(
                text = "RedCuidadora",
                style = MaterialTheme.typography.headlineLarge,
                color = PrimaryEmerald,
                fontWeight = FontWeight.Bold
            )

            Button(
                onClick = { showSosDialog = true },
                colors = ButtonDefaults.buttonColors(containerColor = StatusRed),
                shape = CircleShape,
                modifier = Modifier.height(36.dp)
            ) {
                Text(
                    text = "SOS",
                    color = Color.White,
                    fontWeight = FontWeight.Bold,
                    fontSize = 14.sp
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Profile Greeting Card (Tapping opens Mis Datos / Perfil)
        Card(
            modifier = Modifier
                .fillMaxWidth()
                .clickable { onNavigateToPerfil() },
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween,
                    verticalAlignment = Alignment.CenterVertically
                ) {
                    Text(
                        text = user.data?.let { "Hola, ${it.nombre} 👋" } ?: user.message,
                        style = MaterialTheme.typography.headlineMedium,
                        color = TextPrimaryDark
                    )

                    Surface(
                        color = PrimaryEmerald.copy(alpha = 0.2f),
                        shape = RoundedCornerShape(8.dp)
                    ) {
                        Text(
                            text = "ACTIVA",
                            color = PrimaryEmerald,
                            fontWeight = FontWeight.Bold,
                            fontSize = 12.sp,
                            modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                        )
                    }
                }

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = user.data?.let {
                        listOfNotNull(
                            it.ocupacion?.takeIf(String::isNotBlank),
                            it.personaCuidadaNombre?.let { name -> "Cuidando a $name${it.personaCuidadaEdad?.let { age -> " ($age años)" }.orEmpty()}" },
                        ).joinToString(" • ").ifBlank { "Completa tus datos en Mi Perfil" }
                    } ?: "",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextSecondaryDark
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Preventative Alert Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = StatusAmber.copy(alpha = 0.12f)),
            shape = RoundedCornerShape(16.dp),
            border = androidx.compose.foundation.BorderStroke(1.dp, StatusAmber.copy(alpha = 0.4f))
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.Top) {
                    Icon(
                        imageVector = Icons.Default.Warning,
                        contentDescription = "Alerta",
                        tint = StatusAmber,
                        modifier = Modifier.size(24.dp)
                    )
                    Spacer(modifier = Modifier.width(10.dp))
                    Text(
                        text = alertText,
                        style = MaterialTheme.typography.bodyMedium,
                        color = TextPrimaryDark
                    )
                }

                Spacer(modifier = Modifier.height(12.dp))

                Button(
                    onClick = onNavigateToSolicitudes,
                    colors = ButtonDefaults.buttonColors(containerColor = StatusAmber),
                    shape = RoundedCornerShape(10.dp)
                ) {
                    Text(
                        text = "Pedir relevo",
                        color = Color.Black,
                        fontWeight = FontWeight.Bold
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Mood Check-in Selector
        Text(
            text = "¿Cómo te sientes hoy?",
            style = MaterialTheme.typography.titleMedium,
            color = TextPrimaryDark,
            fontWeight = FontWeight.SemiBold
        )

        Spacer(modifier = Modifier.height(10.dp))

        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val moods = listOf(
                "Bien" to StatusGreen,
                "Cansada" to StatusAmber,
                "Apoyo" to StatusOrange,
                "Sobrepasada" to StatusRed
            )

            moods.forEach { (mood, color) ->
                val isSelected = selectedMood == mood
                FilterChip(
                    selected = isSelected,
                    onClick = {
                        onNavigateToCheckIn(when (mood) {
                            "Bien" -> "Estoy bien"
                            "Cansada" -> "Algo cansada"
                            "Apoyo" -> "Necesito apoyo"
                            else -> "Sobrepasada"
                        })
                    },
                    label = {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(10.dp)
                                    .background(color, CircleShape)
                            )
                            Spacer(modifier = Modifier.width(6.dp))
                            Text(text = mood, color = TextPrimaryDark, fontSize = 13.sp)
                        }
                    },
                    colors = FilterChipDefaults.filterChipColors(
                        containerColor = DarkSurfaceVariant,
                        selectedContainerColor = color.copy(alpha = 0.3f)
                    ),
                    border = FilterChipDefaults.filterChipBorder(
                        enabled = true,
                        selected = isSelected,
                        borderColor = DarkSurfaceVariant,
                        selectedBorderColor = color
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Next Shift Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.CalendarToday,
                        contentDescription = "Calendario",
                        tint = PrimaryEmerald,
                        modifier = Modifier.size(20.dp)
                    )
                    Spacer(modifier = Modifier.width(8.dp))
                    Text(
                        text = "PRÓXIMO RELEVO",
                        style = MaterialTheme.typography.labelMedium,
                        color = PrimaryEmerald,
                        fontWeight = FontWeight.Bold
                    )
                }

                Spacer(modifier = Modifier.height(8.dp))

                Text(
                    text = next?.let { item ->
                        val caregiver = contacts.data?.find { it.contactoUsuarioId == item.cuidadorId }?.nombre
                            ?: if (item.cuidadorId == userId) "Ti" else "usuario #${item.cuidadorId}"
                        "${item.fecha} ${item.horaInicio} - ${item.titulo}, cubierto por $caregiver"
                    } ?: if (relief.data == null) relief.message else "No tienes próximos relevos confirmados.",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Main SOS Button
        Button(
            onClick = { showSosDialog = true },
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
            shape = RoundedCornerShape(14.dp)
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Icon(
                    imageVector = Icons.Default.Shield,
                    contentDescription = "SOS",
                    tint = TextPrimaryDark
                )
                Spacer(modifier = Modifier.width(10.dp))
                Text(
                    text = "Activar SOS de Confianza",
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Bold
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Preview(name = "Teléfono - Inicio", showBackground = true, showSystemUi = true)
@Composable
fun HomeScreenPreview() {
    RedCuidadoraTheme {
        Scaffold(
            bottomBar = {
                RedCuidadoraBottomNavigation(
                    currentRoute = Screen.Home.route,
                    onNavigateToRoute = {},
                )
            },
            containerColor = MaterialTheme.colorScheme.background,
        ) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                HomeScreen(
                    onNavigateToSolicitudes = {},
                    onNavigateToCheckIn = {},
                )
            }
        }
    }
}

@Preview(name = "Tablet - Inicio", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun HomeScreenTabletPreview() {
    RedCuidadoraTheme {
        Scaffold(
            bottomBar = {
                RedCuidadoraBottomNavigation(
                    currentRoute = Screen.Home.route,
                    onNavigateToRoute = {},
                )
            },
            containerColor = MaterialTheme.colorScheme.background
        ) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                HomeScreen(
                    onNavigateToSolicitudes = {},
                    onNavigateToCheckIn = {}
                )
            }
        }
    }
}
