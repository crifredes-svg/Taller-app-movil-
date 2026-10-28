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
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.Send
import androidx.compose.material.icons.filled.CalendarToday
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Phone
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Surface
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import android.widget.Toast
import com.redcuidadora.app.data.local.TokenManager
import com.redcuidadora.app.data.network.*
import androidx.compose.ui.tooling.preview.Preview
import com.redcuidadora.app.ui.navigation.RedCuidadoraBottomNavigation
import com.redcuidadora.app.ui.navigation.Screen
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
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun RedScreen() {
    var selectedCategory by remember { mutableStateOf("Todos") }
    val context = LocalContext.current
    val userId = TokenManager.getUserId(context)
    val network = rememberRemoteData(userId) {
        allPages { RetrofitClient.getApiService(context).listarContactos(userId ?: error("Inicia sesión nuevamente."), it) }
    }
    val balance = rememberRemoteData(userId) {
        RetrofitClient.getApiService(context).obtenerBalance(userId ?: error("Inicia sesión nuevamente.")).requireBody()
    }

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
            text = "Mi Red de Confianza",
            style = MaterialTheme.typography.headlineLarge,
            color = TextPrimaryDark,
            fontWeight = FontWeight.Bold,
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

                balance.data?.contactos?.forEachIndexed { index, contact ->
                    val color = listOf(PrimaryEmerald, Color(0xFF3B82F6), StatusAmber)[index % 3]
                    Row(
                        modifier = Modifier.fillMaxWidth(),
                        horizontalArrangement = Arrangement.SpaceBetween
                    ) {
                        Text(text = "${contact.nombre} (${contact.relacion})", color = TextPrimaryDark, fontSize = 13.sp)
                        Text(text = "${contact.porcentaje}% (${contact.horasApoyo} hrs)", color = color, fontWeight = FontWeight.Bold, fontSize = 13.sp)
                    }
                    Spacer(modifier = Modifier.height(4.dp))
                    LinearProgressIndicator(
                        progress = { (contact.porcentaje / 100).toFloat().coerceIn(0f, 1f) },
                        modifier = Modifier.fillMaxWidth().height(8.dp),
                        color = color,
                        trackColor = DarkSurfaceVariant,
                    )
                    Spacer(modifier = Modifier.height(10.dp))
                }

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
                        text = balance.data?.let {
                            if (it.totalHoras == 0.0) "Sin horas de apoyo registradas."
                            else "${it.totalHoras} horas de apoyo del ${it.desde} al ${it.hasta}."
                        } ?: balance.message,
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
                        labelColor = TextSecondaryDark
                    ),
                    border = null
                )
            }
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Contact Cards List
        val contacts = network.data.orEmpty().filter {
            val role = java.text.Normalizer.normalize(it.relacion.lowercase(), java.text.Normalizer.Form.NFD)
                .replace(Regex("\\p{M}"), "")
            when (selectedCategory) {
                "Familia" -> listOf("tia", "tio", "madre", "padre", "hermana", "hermano", "abuela", "abuelo", "prima", "primo", "pareja", "hija", "hijo", "familia").any(role::contains)
                "Compañeros" -> role.contains("companer")
                "Vecinos" -> role.contains("vecin")
                else -> true
            }
        }.mapIndexed { index, contact ->
            ContactItem(
                contact.nombre, contact.relacion, contact.apoyos?.split(",")?.filter(String::isNotBlank).orEmpty(),
                contact.disponibilidad ?: "Sin disponibilidad informada", contact.nombre.take(1).uppercase(),
                listOf(PrimaryEmerald, Color(0xFF3B82F6), StatusAmber)[index % 3],
            )
        }
        if (contacts.isEmpty()) {
            Text(
                text = if (network.data == null) network.message else "No hay contactos en esta categoría.",
                color = TextSecondaryDark,
                style = MaterialTheme.typography.bodyMedium,
            )
        }

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
                            IconButton(onClick = { Toast.makeText(context, "Este contacto no tiene teléfono disponible en el servicio.", Toast.LENGTH_LONG).show() }) {
                                Icon(
                                    imageVector = Icons.Default.Phone,
                                    contentDescription = "Llamar",
                                    tint = TextSecondaryDark
                                )
                            }
                            IconButton(onClick = { Toast.makeText(context, "Este contacto no tiene un número de mensajería disponible en el servicio.", Toast.LENGTH_LONG).show() }) {
                                Icon(
                                    imageVector = Icons.AutoMirrored.Filled.Send,
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

@Preview(name = "Teléfono - Mi Red", showBackground = true, showSystemUi = true)
@Composable
fun RedScreenPreview() {
    RedCuidadoraTheme {
        Scaffold(
            bottomBar = {
                RedCuidadoraBottomNavigation(
                    currentRoute = Screen.MiRed.route,
                    onNavigateToRoute = {}
                )
            },
            containerColor = MaterialTheme.colorScheme.background
        ) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                RedScreen()
            }
        }
    }
}

@Preview(name = "Tablet - Mi Red", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun RedScreenTabletPreview() {
    RedCuidadoraTheme {
        Scaffold(
            bottomBar = {
                RedCuidadoraBottomNavigation(
                    currentRoute = Screen.MiRed.route,
                    onNavigateToRoute = {}
                )
            },
            containerColor = MaterialTheme.colorScheme.background
        ) { innerPadding ->
            Box(modifier = Modifier.padding(innerPadding)) {
                RedScreen()
            }
        }
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
