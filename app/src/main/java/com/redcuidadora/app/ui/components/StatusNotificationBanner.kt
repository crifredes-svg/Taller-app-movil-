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
fun StatusNotificationBanner(
    message: String,
    isSuccess: Boolean,
    modifier: Modifier = Modifier
) {
    val borderColor = if (isSuccess) StatusGreen else StatusRed
    val icon = if (isSuccess) Icons.Default.CheckCircle else Icons.Default.Error
    val darkNavyBg = Color(0xFF1E293B) // Dark navy background

    Row(
        modifier = modifier
            .fillMaxWidth()
            .background(darkNavyBg, RoundedCornerShape(4.dp))
            .border(2.dp, borderColor, RoundedCornerShape(4.dp))
            .padding(horizontal = 14.dp, vertical = 12.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(10.dp)
    ) {
        Icon(
            imageVector = icon,
            contentDescription = if (isSuccess) "Éxito" else "Error",
            tint = borderColor
        )
        Text(
            text = message,
            color = TextPrimaryDark,
            fontSize = 13.sp,
            fontWeight = FontWeight.SemiBold
        )
    }
}

@Preview(name = "Demostración de Banners de Notificación", showBackground = true, backgroundColor = 0xFF121316)
@Composable
fun BannersDemoPreview() {
    RedCuidadoraTheme {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(DarkBackground)
                .padding(20.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp)
        ) {
            Text(
                text = "1. Positivo (Contacto)",
                color = Color.Gray,
                fontSize = 12.sp
            )
            StatusNotificationBanner(
                message = "Se añadió el contacto a tu red de confianza",
                isSuccess = true
            )

            Text(
                text = "2. Negativo (Contacto)",
                color = Color.Gray,
                fontSize = 12.sp
            )
            StatusNotificationBanner(
                message = "Error inesperado no se añadió el contacto",
                isSuccess = false
            )

            Text(
                text = "3. Positivo (Solicitud)",
                color = Color.Gray,
                fontSize = 12.sp
            )
            StatusNotificationBanner(
                message = "Se completó la solicitud correctamente",
                isSuccess = true
            )

            Text(
                text = "4. Negativo (Solicitud)",
                color = Color.Gray,
                fontSize = 12.sp
            )
            StatusNotificationBanner(
                message = "Hubo un error y no se mandó la solicitud",
                isSuccess = false
            )
        }
    }
}
