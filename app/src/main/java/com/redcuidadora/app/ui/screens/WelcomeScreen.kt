package com.redcuidadora.app.ui.screens

import androidx.compose.foundation.background
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Favorite
import androidx.compose.material3.Icon
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.theme.DarkBackground
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun WelcomeScreen(
    onNavigateToLogin: () -> Unit = {},
) {
    Box(
        modifier = Modifier
            .fillMaxSize()
            .background(DarkBackground)
            .clickable { onNavigateToLogin() },
        contentAlignment = Alignment.Center,
    ) {
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.padding(24.dp),
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .background(PrimaryEmerald.copy(alpha = 0.2f), CircleShape),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = Icons.Default.Favorite,
                    contentDescription = "Logo",
                    tint = PrimaryEmerald,
                    modifier = Modifier.size(40.dp),
                )
            }
            Spacer(modifier = Modifier.height(24.dp))
            Text(
                text = "RedCuidadora",
                style = MaterialTheme.typography.headlineLarge,
                color = PrimaryEmerald,
                fontWeight = FontWeight.Bold,
                fontSize = 32.sp,
            )
            Spacer(modifier = Modifier.height(8.dp))
            Text(
                text = "Red de apoyo y protección para cuidadoras",
                style = MaterialTheme.typography.bodyMedium,
                color = TextSecondaryDark,
                fontSize = 14.sp,
            )
        }
    }
}

@Preview(name = "Teléfono - Bienvenida", showBackground = true, showSystemUi = true)
@Composable
fun WelcomeScreenPreview() {
    RedCuidadoraTheme {
        WelcomeScreen()
    }
}

@Preview(name = "Tablet - Bienvenida", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun WelcomeScreenTabletPreview() {
    RedCuidadoraTheme {
        WelcomeScreen()
    }
}
