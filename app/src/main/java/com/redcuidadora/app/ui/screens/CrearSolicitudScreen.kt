package com.redcuidadora.app.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.components.StatusNotificationBanner
import com.redcuidadora.app.data.local.TokenManager
import com.redcuidadora.app.data.network.*
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun CrearSolicitudScreen(
    onNavigateBack: () -> Unit,
    showPreviewErrorBanner: Boolean = false,
) {
    val context = LocalContext.current
    var titulo by remember { mutableStateOf("") }
    var horario by remember { mutableStateOf("") }
    var detalles by remember { mutableStateOf("") }
    var tipo by remember { mutableStateOf<String?>(null) }
    val action = rememberApiAction()

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top Navigation Header
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth(),
        ) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Volver",
                    tint = TextPrimaryDark,
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Hacer Solicitud de Relevo",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold,
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = "Motivo / Título de la solicitud",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = titulo,
            onValueChange = { titulo = it },
            placeholder = { Text("Ej. Relevo para clases presenciales y taller", color = TextSecondaryDark) },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = DarkSurface,
                unfocusedContainerColor = DarkSurface,
                focusedBorderColor = PrimaryEmerald,
                unfocusedBorderColor = DarkSurfaceVariant,
                focusedTextColor = TextPrimaryDark,
                unfocusedTextColor = TextPrimaryDark,
            ),
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Tipo de relevo",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            listOf("estudio" to "Estudio", "clases" to "Clases", "compras" to "Compras", "casa" to "Casa").forEach { (value, label) ->
                val selected = tipo == value
                FilterChip(
                    selected = selected,
                    onClick = { tipo = value },
                    label = { Text(label, fontSize = 12.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        containerColor = DarkSurfaceVariant,
                        selectedContainerColor = PrimaryEmerald,
                        selectedLabelColor = TextPrimaryDark,
                        labelColor = TextSecondaryDark,
                    ),
                    border = FilterChipDefaults.filterChipBorder(
                        enabled = true, selected = selected,
                        borderColor = DarkSurfaceVariant, selectedBorderColor = PrimaryEmerald,
                    ),
                )
            }
        }
        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Horario y fecha requerida",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = horario,
            onValueChange = { horario = it },
            placeholder = { Text("YYYY-MM-DD HH:mm - HH:mm", color = TextSecondaryDark) },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = DarkSurface,
                unfocusedContainerColor = DarkSurface,
                focusedBorderColor = PrimaryEmerald,
                unfocusedBorderColor = DarkSurfaceVariant,
                focusedTextColor = TextPrimaryDark,
                unfocusedTextColor = TextPrimaryDark,
            ),
        )

        Spacer(modifier = Modifier.height(16.dp))

        Text(
            text = "Detalles adicionales para tu red",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = detalles,
            onValueChange = { detalles = it },
            placeholder = { Text("Ej. Asistir a taller universitario. Dejar almuerzo servido.", color = TextSecondaryDark) },
            modifier = Modifier.fillMaxWidth(),
            minLines = 3,
            maxLines = 5,
            shape = RoundedCornerShape(12.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = DarkSurface,
                unfocusedContainerColor = DarkSurface,
                focusedBorderColor = PrimaryEmerald,
                unfocusedBorderColor = DarkSurfaceVariant,
                focusedTextColor = TextPrimaryDark,
                unfocusedTextColor = TextPrimaryDark,
            ),
        )

        Spacer(modifier = Modifier.height(28.dp))

        Button(
            onClick = {
                action.run("Solicitud de relevo publicada") {
                    val type = tipo ?: error("Selecciona el tipo de relevo.")
                    val title = titulo.trim()
                    require(title.length in 3..80) { "El título debe tener entre 3 y 80 caracteres." }
                    require(detalles.trim().length in 10..200) { "Los detalles deben tener entre 10 y 200 caracteres." }
                    val schedule = parseReliefSchedule(horario)
                    val id = TokenManager.getUserId(context) ?: error("Inicia sesión nuevamente.")
                    RetrofitClient.getApiService(context).crearSolicitudRelevo(
                        SolicitudRelevoDto(
                            solicitanteId = id, titulo = title, tipo = type,
                            descripcion = detalles.trim(), fecha = schedule.date,
                            horaInicio = schedule.start, horaFin = schedule.end,
                        ),
                    ).requireBody(201)
                }
            },
            enabled = !action.busy && !action.success,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
            shape = RoundedCornerShape(14.dp),
        ) {
            Text(
                text = "Publicar Solicitud de Relevo",
                style = MaterialTheme.typography.titleMedium,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold,
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Negative Status Notification Banner (Error)
        if (action.message != null || showPreviewErrorBanner) {
            StatusNotificationBanner(
                message = action.message ?: "Hubo un error y no se mandó la solicitud",
                isSuccess = action.success,
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Preview(name = "Teléfono - Crear Solicitud", showBackground = true, showSystemUi = true)
@Composable
fun CrearSolicitudScreenPreview() {
    RedCuidadoraTheme {
        CrearSolicitudScreen(onNavigateBack = {}, showPreviewErrorBanner = true)
    }
}

@Preview(name = "Tablet - Crear Solicitud", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun CrearSolicitudTabletPreview() {
    RedCuidadoraTheme {
        CrearSolicitudScreen(onNavigateBack = {}, showPreviewErrorBanner = true)
    }
}
