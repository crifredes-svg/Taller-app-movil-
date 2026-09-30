package com.redcuidadora.app.ui.components

import androidx.compose.animation.animateColorAsState
import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Female
import androidx.compose.material.icons.filled.Male
import androidx.compose.material3.Icon
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant

enum class Gender {
    MALE, FEMALE
}

@Composable
fun GenderToggle(
    selectedGender: Gender,
    onGenderSelected: (Gender) -> Unit,
    modifier: Modifier = Modifier
) {
    val maleActiveColor = Color(0xFF2563EB) // Bright Male Blue
    val maleInactiveBg = Color(0xFF1E293B) // Dark Navy
    val femaleActiveColor = Color(0xFFEC4899) // Bright Female Pink
    val femaleInactiveBg = Color(0xFF311221) // Dark Pinkish Navy

    val mutedSymbolColor = Color(0xFF64748B)

    Row(
        modifier = modifier
            .fillMaxWidth()
            .height(54.dp)
            .clip(RoundedCornerShape(16.dp))
            .background(DarkSurfaceVariant)
            .padding(4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp)
    ) {
        // Male Side
        val isMale = selectedGender == Gender.MALE
        val maleBg by animateColorAsState(
            targetValue = if (isMale) maleActiveColor else maleInactiveBg,
            label = "maleBg"
        )
        val maleContentColor = if (isMale) Color.White else mutedSymbolColor

        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxHeight()
                .clip(RoundedCornerShape(12.dp))
                .background(maleBg)
                .clickable { onGenderSelected(Gender.MALE) },
            contentAlignment = Alignment.Center
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Male,
                    contentDescription = "Masculino ♂",
                    tint = maleContentColor,
                    modifier = Modifier.size(24.dp)
                )
                Text(
                    text = "Hombre",
                    color = maleContentColor,
                    fontWeight = if (isMale) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 15.sp
                )
            }
        }

        // Female Side
        val isFemale = selectedGender == Gender.FEMALE
        val femaleBg by animateColorAsState(
            targetValue = if (isFemale) femaleActiveColor else femaleInactiveBg,
            label = "femaleBg"
        )
        val femaleContentColor = if (isFemale) Color.White else mutedSymbolColor

        Box(
            modifier = Modifier
                .weight(1f)
                .fillMaxHeight()
                .clip(RoundedCornerShape(12.dp))
                .background(femaleBg)
                .clickable { onGenderSelected(Gender.FEMALE) },
            contentAlignment = Alignment.Center
        ) {
            Row(
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.spacedBy(8.dp)
            ) {
                Icon(
                    imageVector = Icons.Default.Female,
                    contentDescription = "Femenino ♀",
                    tint = femaleContentColor,
                    modifier = Modifier.size(24.dp)
                )
                Text(
                    text = "Mujer",
                    color = femaleContentColor,
                    fontWeight = if (isFemale) FontWeight.Bold else FontWeight.Normal,
                    fontSize = 15.sp
                )
            }
        }
    }
}
