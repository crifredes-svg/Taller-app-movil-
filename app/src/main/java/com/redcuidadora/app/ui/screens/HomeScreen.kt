package com.redcuidadora.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
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
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.Shield
import androidx.compose.material.icons.filled.Warning
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
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
    onNavigateToCheckIn: () -> Unit
) {
    var selectedMood by remember { mutableStateOf("Cansada") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Spacer(modifier = Modifier.height(16.dp))

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
                onClick = { /* SOS trigger */ },
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

        // Profile Greeting Card
        Card(
            modifier = Modifier.fillMaxWidth(),
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
                        text = "Hola, María 👋",
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
                    text = "Estudiante y cuidadora • Cuidando a Don Carlos (82 años)",
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
                        text = "Alerta preventiva de sobrecarga: Llevas días con alta exigencia académica y cuidado. Pide un relevo a tu red antes de que afecte tus certámenes.",
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
                        selectedMood = mood
                        onNavigateToCheckIn()
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
                    text = "Mañana 09:30 - Relevo para clases presenciales cubierto por Ana González (Tía)",
                    style = MaterialTheme.typography.bodyMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Medium
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Main SOS Button
        Button(
            onClick = { /* Activate SOS */ },
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
