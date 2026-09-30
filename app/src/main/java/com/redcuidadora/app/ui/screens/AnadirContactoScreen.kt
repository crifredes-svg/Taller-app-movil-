package com.redcuidadora.app.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
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
import androidx.compose.material.icons.filled.QrCodeScanner
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
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
import androidx.compose.ui.tooling.preview.Devices
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.components.StatusNotificationBanner
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun AnadirContactoScreen(
    onNavigateBack: () -> Unit,
    showPreviewSuccessBanner: Boolean = true
) {
    val context = LocalContext.current
    var codigoContacto by remember { mutableStateOf("RC-8F3A92") }
    var relacionContigo by remember { mutableStateOf("Tía") }
    var showSuccessBanner by remember { mutableStateOf(showPreviewSuccessBanner) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top Navigation Header
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth()
        ) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Volver",
                    tint = TextPrimaryDark
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Añadir Contacto a tu Red",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        Text(
            text = "Código único de la persona",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark
        )
        Text(
            text = "Ingresa el código alfanumérico que te compartió la otra persona (ej. RC-8F3A92)",
            fontSize = 12.sp,
            color = TextSecondaryDark
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = codigoContacto,
            onValueChange = { codigoContacto = it.uppercase() },
            placeholder = { Text("Ej. RC-9A8B3C", color = TextSecondaryDark) },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            trailingIcon = {
                Icon(
                    imageVector = Icons.Default.QrCodeScanner,
                    contentDescription = "Código",
                    tint = PrimaryEmerald
                )
            },
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = DarkSurface,
                unfocusedContainerColor = DarkSurface,
                focusedBorderColor = PrimaryEmerald,
                unfocusedBorderColor = DarkSurfaceVariant,
                focusedTextColor = TextPrimaryDark,
                unfocusedTextColor = TextPrimaryDark
            )
        )

        Spacer(modifier = Modifier.height(20.dp))

        Text(
            text = "Relación que tiene contigo",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark
        )
        Text(
            text = "Define qué es esta persona para ti (ej. Tía, Compañero de carrera, Vecina, Hermano)",
            fontSize = 12.sp,
            color = TextSecondaryDark
        )
        Spacer(modifier = Modifier.height(8.dp))
        OutlinedTextField(
            value = relacionContigo,
            onValueChange = { relacionContigo = it },
            placeholder = { Text("Ej. Tía, Compañero de universidad", color = TextSecondaryDark) },
            modifier = Modifier.fillMaxWidth(),
            shape = RoundedCornerShape(12.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = DarkSurface,
                unfocusedContainerColor = DarkSurface,
                focusedBorderColor = PrimaryEmerald,
                unfocusedBorderColor = DarkSurfaceVariant,
                focusedTextColor = TextPrimaryDark,
                unfocusedTextColor = TextPrimaryDark
            )
        )

        Spacer(modifier = Modifier.height(28.dp))

        Button(
            onClick = {
                if (codigoContacto.isBlank() || relacionContigo.isBlank()) {
                    Toast.makeText(context, "Por favor completa el código y la relación", Toast.LENGTH_SHORT).show()
                } else {
                    showSuccessBanner = true
                }
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
            shape = RoundedCornerShape(14.dp)
        ) {
            Text(
                text = "Vincular a mi Red de Confianza",
                style = MaterialTheme.typography.titleMedium,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Success Status Notification Banner
        if (showSuccessBanner) {
            StatusNotificationBanner(
                message = "Se añadió el contacto a tu red de confianza",
                isSuccess = true
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

@Preview(name = "Teléfono - Añadir Contacto", showBackground = true, showSystemUi = true)
@Composable
fun AnadirContactoScreenPreview() {
    RedCuidadoraTheme {
        AnadirContactoScreen(onNavigateBack = {}, showPreviewSuccessBanner = true)
    }
}

@Preview(name = "Tablet - Añadir Contacto", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun AnadirContactoTabletPreview() {
    RedCuidadoraTheme {
        AnadirContactoScreen(onNavigateBack = {}, showPreviewSuccessBanner = true)
    }
}
