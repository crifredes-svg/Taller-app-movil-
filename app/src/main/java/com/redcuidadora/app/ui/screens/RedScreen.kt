package com.redcuidadora.app.ui.screens

import androidx.compose.foundation.background
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
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material.icons.filled.Send
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
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
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun RedScreen() {
    var selectedCategory by remember { mutableStateOf("Todos") }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Spacer(modifier = Modifier.height(16.dp))

        // Title
        Text(
            text = "Mi Red de Confianza",
            style = MaterialTheme.typography.headlineLarge,
            color = TextPrimaryDark,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(16.dp))

        // Circle of Trust Balance Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp)
        ) {
            Column(modifier = Modifier.padding(16.dp)) {
                Text(
                    text = "BALANCE DEL CÍRCULO DE CONFIANZA",
                    style = MaterialTheme.typography.labelMedium,
                    color = TextSecondaryDark,
                    fontWeight = FontWeight.Bold
                )

                Spacer(modifier = Modifier.height(14.dp))

                // Person 1: Ana
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Ana González (Tía)", color = TextPrimaryDark, fontSize = 13.sp)
                    Text(text = "50% (6 hrs)", color = PrimaryEmerald, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
                Spacer(modifier = Modifier.height(4.dp))
                LinearProgressIndicator(
                    progress = { 0.5f },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp),
                    color = PrimaryEmerald,
                    trackColor = DarkSurfaceVariant,
                )

                Spacer(modifier = Modifier.height(10.dp))

                // Person 2: Matías
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Matías Paredes (Compañero)", color = TextPrimaryDark, fontSize = 13.sp)
                    Text(text = "25% (3 hrs)", color = Color(0xFF3B82F6), fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
                Spacer(modifier = Modifier.height(4.dp))
                LinearProgressIndicator(
                    progress = { 0.25f },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp),
                    color = Color(0xFF3B82F6),
                    trackColor = DarkSurfaceVariant,
                )

                Spacer(modifier = Modifier.height(10.dp))

                // Person 3: Carla
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.SpaceBetween
                ) {
                    Text(text = "Carla Morales (Vecina)", color = TextPrimaryDark, fontSize = 13.sp)
                    Text(text = "25% (3 hrs)", color = StatusAmber, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                }
                Spacer(modifier = Modifier.height(4.dp))
                LinearProgressIndicator(
                    progress = { 0.25f },
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(8.dp),
                    color = StatusAmber,
                    trackColor = DarkSurfaceVariant,
                )

                Spacer(modifier = Modifier.height(14.dp))

                Row(verticalAlignment = Alignment.CenterVertically) {
                    Icon(
                        imageVector = Icons.Default.CheckCircle,
                        contentDescription = "Saludable",
                        tint = StatusGreen,
                        modifier = Modifier.size(18.dp)
                    )
                    Spacer(modifier = Modifier.width(6.dp))
                    Text(
                        text = "Distribución saludable. Nadie está sobrecargado.",
                        color = StatusGreen,
                        fontSize = 12.sp,
                        fontWeight = FontWeight.Medium
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Category Filter Chips
        Row(
            modifier = Modifier.fillMaxWidth(),
            horizontalArrangement = Arrangement.spacedBy(8.dp)
        ) {
            val categories = listOf("Todos", "Familia", "Compañeros", "Vecinos")
            categories.forEach { category ->
                val isSelected = selectedCategory == category
                FilterChip(
                    selected = isSelected,
                    onClick = { selectedCategory = category },
                    label = { Text(text = category, fontSize = 13.sp) },
                    colors = FilterChipDefaults.filterChipColors(
                        containerColor = DarkSurfaceVariant,
                        selectedContainerColor = PrimaryEmerald,
                        selectedLabelColor = TextPrimaryDark,
                        unselectedLabelColor = TextSecondaryDark
                    ),
                    border = null
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Contact Cards List
        val contacts = listOf(
            ContactItem("Ana González", "Tía", listOf("Relevo en casa", "Compras"), "Martes y Jueves 17:00 - 20:00", "A", PrimaryEmerald),
            ContactItem("Matías Paredes", "Compañero de carrera", listOf("Apoyo académico y apuntes"), "Lunes a Viernes 15:00 - 18:00", "M", Color(0xFF3B82F6)),
            ContactItem("Carla Morales", "Vecina", listOf("Relevo en casa", "Compras"), "Sábados 10:00 - 14:00", "C", StatusAmber)
        )

        contacts.forEach { contact ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(bottom = 12.dp),
                colors = CardDefaults.cardColors(containerColor = DarkSurface),
                shape = RoundedCornerShape(16.dp)
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween,
                        verticalAlignment = Alignment.CenterVertically
                    ) {
                        Row(verticalAlignment = Alignment.CenterVertically) {
                            Box(
                                modifier = Modifier
                                    .size(36.dp)
                                    .background(contact.color.copy(alpha = 0.2f), CircleShape),
                                contentAlignment = Alignment.Center
                            ) {
                                Text(
                                    text = contact.initial,
                                    color = contact.color,
                                    fontWeight = FontWeight.Bold,
                                    fontSize = 16.sp
                                )
                            }
                            Spacer(modifier = Modifier.width(10.dp))
                            Column {
                                Text(
                                    text = contact.name,
                                    style = MaterialTheme.typography.titleMedium,
                                    color = TextPrimaryDark,
                                    fontWeight = FontWeight.Bold
                                )
                                Text(
                                    text = contact.role,
                                    fontSize = 12.sp,
                                    color = TextSecondaryDark
                                )
                            }
                        }

                        Row {
                            IconButton(onClick = { /* Call */ }) {
                                Icon(
                                    imageVector = Icons.Default.Phone,
                                    contentDescription = "Llamar",
                                    tint = TextSecondaryDark
                                )
                            }
                            IconButton(onClick = { /* WhatsApp */ }) {
                                Icon(
                                    imageVector = Icons.Default.Send,
                                    contentDescription = "Mensaje",
                                    tint = StatusGreen
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(horizontalArrangement = Arrangement.spacedBy(6.dp)) {
                        contact.tags.forEach { tag ->
                            Surface(
                                color = DarkSurfaceVariant,
                                shape = RoundedCornerShape(6.dp)
                            ) {
                                Text(
                                    text = tag,
                                    color = TextSecondaryDark,
                                    fontSize = 11.sp,
                                    modifier = Modifier.padding(horizontal = 8.dp, vertical = 4.dp)
                                )
                            }
                        }
                    }

                    Spacer(modifier = Modifier.height(10.dp))

                    Row(verticalAlignment = Alignment.CenterVertically) {
                        Icon(
                            imageVector = Icons.Default.CalendarToday,
                            contentDescription = "Disponibilidad",
                            tint = TextSecondaryDark,
                            modifier = Modifier.size(14.dp)
                        )
                        Spacer(modifier = Modifier.width(6.dp))
                        Text(
                            text = "Disponibilidad: ${contact.availability}",
                            fontSize = 12.sp,
                            color = TextPrimaryDark,
                            fontWeight = FontWeight.Medium
                        )
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}

private data class ContactItem(
    val name: String,
    val role: String,
    val tags: List<String>,
    val availability: String,
    val initial: String,
    val color: Color
)
