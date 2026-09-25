package com.redcuidadora.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ExperimentalLayoutApi
import androidx.compose.foundation.layout.FlowRow
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
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FilterChipDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateListOf
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

@OptIn(ExperimentalLayoutApi::class)
@Composable
fun CheckInScreen(
    onNavigateBack: () -> Unit
) {
    var selectedLevel by remember { mutableStateOf("Algo cansada") }
    val selectedFactors = remember {
        mutableStateListOf(
            "Semana de certámenes",
            "Clases / talleres presenciales",
            "Dormí mal estudiando y cuidando"
        )
    }
    var notesText by remember { mutableStateOf("") }

    val levels = listOf(
        Triple("Estoy bien", "Tranquila y organizada", StatusGreen),
        Triple("Algo cansada", "Batería baja pero rindiendo", StatusAmber),
        Triple("Necesito apoyo", "Al límite de mis fuerzas", StatusOrange),
        Triple("Sobrepasada", "Emergencia, necesito relevo", StatusRed)
    )

    val factors = listOf(
        "Semana de certámenes",
        "Clases / talleres presenciales",
        "Entrega de proyectos",
        "Dormí mal estudiando y cuidando",
        "Relevo para no faltar a clases",
        "Momento de respiro"
    )

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState())
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top Navigation Title
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
                text = "Mi Carga (Check-in)",
                style = MaterialTheme.typography.headlineMedium,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Overload Question
        Text(
            text = "¿Cuál es tu nivel de sobrecarga hoy?",
            style = MaterialTheme.typography.titleLarge,
            color = TextPrimaryDark,
            fontWeight = FontWeight.Bold
        )
        Text(
            text = "Tu red de apoyo recibirá alertas según tu estado.",
            style = MaterialTheme.typography.bodyMedium,
            color = TextSecondaryDark
        )

        Spacer(modifier = Modifier.height(16.dp))

        // 2x2 Grid for Overload Level Cards
        Column(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            levels.chunked(2).forEach { rowLevels ->
                Row(
                    modifier = Modifier.fillMaxWidth(),
                    horizontalArrangement = Arrangement.spacedBy(10.dp)
                ) {
                    rowLevels.forEach { (title, subtitle, color) ->
                        val isSelected = selectedLevel == title
                        Card(
                            modifier = Modifier
                                .weight(1f)
                                .clickable { selectedLevel = title }
                                .then(
                                    if (isSelected) Modifier.border(
                                        1.5.dp,
                                        color,
                                        RoundedCornerShape(14.dp)
                                    ) else Modifier
                                ),
                            colors = CardDefaults.cardColors(
                                containerColor = if (isSelected) color.copy(alpha = 0.15f) else DarkSurface
                            ),
                            shape = RoundedCornerShape(14.dp)
                        ) {
                            Column(modifier = Modifier.padding(14.dp)) {
                                Row(verticalAlignment = Alignment.CenterVertically) {
                                    Box(
                                        modifier = Modifier
                                            .size(12.dp)
                                            .background(color, CircleShape)
                                    )
                                    Spacer(modifier = Modifier.width(6.dp))
                                    Text(
                                        text = title,
                                        fontWeight = FontWeight.Bold,
                                        color = TextPrimaryDark,
                                        fontSize = 14.sp
                                    )
                                }
                                Spacer(modifier = Modifier.height(4.dp))
                                Text(
                                    text = subtitle,
                                    fontSize = 11.sp,
                                    color = TextSecondaryDark
                                )
                            }
                        }
                    }
                }
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Factors Section
        Text(
            text = "¿Qué factores influyen hoy? (Multi-select)",
            style = MaterialTheme.typography.titleMedium,
            color = TextPrimaryDark,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(10.dp))

        FlowRow(
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            modifier = Modifier.fillMaxWidth()
        ) {
            factors.forEach { factor ->
                val isSelected = selectedFactors.contains(factor)
                FilterChip(
                    selected = isSelected,
                    onClick = {
                        if (isSelected) selectedFactors.remove(factor)
                        else selectedFactors.add(factor)
                    },
                    label = {
                        Text(
                            text = factor,
                            color = if (isSelected) PrimaryEmerald else TextPrimaryDark,
                            fontSize = 13.sp
                        )
                    },
                    colors = FilterChipDefaults.filterChipColors(
                        containerColor = DarkSurfaceVariant,
                        selectedContainerColor = PrimaryEmerald.copy(alpha = 0.2f)
                    ),
                    border = FilterChipDefaults.filterChipBorder(
                        enabled = true,
                        selected = isSelected,
                        borderColor = DarkSurfaceVariant,
                        selectedBorderColor = PrimaryEmerald
                    )
                )
            }
        }

        Spacer(modifier = Modifier.height(24.dp))

        // Personal Notes
        Text(
            text = "Desahogo / Notas personales",
            style = MaterialTheme.typography.titleMedium,
            color = TextPrimaryDark,
            fontWeight = FontWeight.Bold
        )

        Spacer(modifier = Modifier.height(8.dp))

        OutlinedTextField(
            value = notesText,
            onValueChange = { notesText = it },
            placeholder = {
                Text(
                    text = "Escribe cómo te sientes... (Sólo visible para ti y coordinadores que elijas)",
                    color = TextSecondaryDark,
                    fontSize = 13.sp
                )
            },
            modifier = Modifier
                .fillMaxWidth()
                .height(120.dp),
            shape = RoundedCornerShape(14.dp),
            colors = OutlinedTextFieldDefaults.colors(
                focusedContainerColor = DarkSurface,
                unfocusedContainerColor = DarkSurface,
                focusedBorderColor = PrimaryEmerald,
                unfocusedBorderColor = DarkSurfaceVariant
            )
        )

        Spacer(modifier = Modifier.height(24.dp))

        // Save Button
        Button(
            onClick = onNavigateBack,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
            shape = RoundedCornerShape(14.dp)
        ) {
            Text(
                text = "Guardar estado",
                style = MaterialTheme.typography.titleMedium,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold
            )
        }

        Spacer(modifier = Modifier.height(24.dp))
    }
}
