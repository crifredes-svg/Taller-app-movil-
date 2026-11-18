package com.redcuidadora.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Error
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.theme.DarkBackground
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.StatusGreen
import com.redcuidadora.app.ui.theme.StatusRed
import com.redcuidadora.app.ui.theme.TextPrimaryDark

@Composable
fun StatusNotificationBanner2(
    message: String,
    isSuccess: Boolean,
    modifier: Modifier = Modifier,
) {
    val borderColor = if (isSuccess) StatusGreen else StatusRed
    val icon = if (isSuccess) Icons.Default.CheckCircle else Icons.Default.Error
    val darkNavyBg = Color(0xFF1E293B)

    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(darkNavyBg, RoundedCornerShape(4.dp))
            .border(2.dp, borderColor, RoundedCornerShape(4.dp))
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp),
    ) {
        Icon(
            imageVector = icon,
            contentDescription = if (isSuccess) "Éxito" else "Error",
            tint = borderColor,
        )
        Text(
            text = message,
            color = TextPrimaryDark,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold,
        )
    }
}

@Preview(name = "6 Estados Visuales Banners 2 (Login, Registro, Cierre)", showBackground = true, backgroundColor = 0xFF121316)
@Composable
fun AuthBanners2StatesPreview() {
    RedCuidadoraTheme {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(DarkBackground)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            // 1. Login Positivo
            Text(text = "1. Inicio de sesión - Positivo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner2(
                message = "¡Sesión iniciada con éxito! Bienvenido de nuevo a RedCuidadora.",
                isSuccess = true,
            )

            // 2. Login Negativo
            Text(text = "2. Inicio de sesión - Negativo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner2(
                message = "Correo o contraseña incorrectos. Verifica tus credenciales.",
                isSuccess = false,
            )

            // 3. Registro Positivo
            Text(text = "3. Registro - Positivo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner2(
                message = "¡Cuenta creada con éxito! Tu código único es RC-A1B2C3.",
                isSuccess = true,
            )

            // 4. Registro Negativo (Combinado)
            Text(text = "4. Registro - Negativo (Combinado)", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner2(
                message = "Correo ya registrado, datos incorrectos o fallo del sistema.",
                isSuccess = false,
            )

            // 5. Cierre de sesión Positivo
            Text(text = "5. Cierre de sesión - Positivo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner2(
                message = "Sesión cerrada exitosamente. Tus datos locales están seguros.",
                isSuccess = true,
            )

            // 6. Cierre de sesión Negativo
            Text(text = "6. Cierre de sesión - Negativo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner2(
                message = "Hubo un error al cerrar sesión.",
                isSuccess = false,
            )
        }
    }
}
