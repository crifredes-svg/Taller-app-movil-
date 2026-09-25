package com.redcuidadora.app.ui.navigation

import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.CalendarMonth
import androidx.compose.material.icons.filled.CheckCircle
import androidx.compose.material.icons.filled.Home
import androidx.compose.material.icons.filled.Mail
import androidx.compose.material.icons.filled.People
import androidx.compose.material.icons.outlined.CalendarMonth
import androidx.compose.material.icons.outlined.CheckCircle
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Mail
import androidx.compose.material.icons.outlined.People
import androidx.compose.ui.graphics.vector.ImageVector

sealed class Screen(
    val route: String,
    val title: String,
    val selectedIcon: ImageVector,
    val unselectedIcon: ImageVector
) {
    object Home : Screen(
        route = "home",
        title = "Inicio",
        selectedIcon = Icons.Filled.Home,
        unselectedIcon = Icons.Outlined.Home
    )

    object MiCarga : Screen(
        route = "mi_carga",
        title = "Mi Carga",
        selectedIcon = Icons.Filled.CheckCircle,
        unselectedIcon = Icons.Outlined.CheckCircle
    )

    object Solicitudes : Screen(
        route = "solicitudes",
        title = "Solicitudes",
        selectedIcon = Icons.Filled.Mail,
        unselectedIcon = Icons.Outlined.Mail
    )

    object MiRed : Screen(
        route = "mi_red",
        title = "Mi Red",
        selectedIcon = Icons.Filled.People,
        unselectedIcon = Icons.Outlined.People
    )

    object Calendario : Screen(
        route = "calendario",
        title = "Calendario",
        selectedIcon = Icons.Filled.CalendarMonth,
        unselectedIcon = Icons.Outlined.CalendarMonth
    )
}

val bottomNavScreens = listOf(
    Screen.Home,
    Screen.MiCarga,
    Screen.Solicitudes,
    Screen.MiRed,
    Screen.Calendario
)
