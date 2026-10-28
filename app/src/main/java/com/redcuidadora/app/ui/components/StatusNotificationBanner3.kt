package com.redcuidadora.app.ui.components

import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.theme.DarkBackground
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme

@Composable
fun StatusNotificationBanner3(
    message: String,
    isSuccess: Boolean,
    modifier: Modifier = Modifier,
) {
    StatusNotificationBanner(
        message = message,
        isSuccess = isSuccess,
        modifier = modifier,
    )
}

@Preview(name = "SOS - Resultado positivo y negativo", showBackground = true, backgroundColor = 0xFF121316)
@Composable
fun SosBanners3StatesPreview() {
    RedCuidadoraTheme {
        Column(
            modifier = Modifier
                .fillMaxWidth()
                .background(DarkBackground)
                .padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text(text = "1. SOS - Positivo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner3(
                message = "Alerta SOS registrada correctamente. Tu red puede verla al consultar la app.",
                isSuccess = true,
            )
            Text(text = "2. SOS - Negativo", color = Color.Gray, fontSize = 11.sp)
            StatusNotificationBanner3(
                message = "No se pudo confirmar el envío de la alerta SOS. Revisa tu conexión e inténtalo nuevamente.",
                isSuccess = false,
            )
        }
    }
}
