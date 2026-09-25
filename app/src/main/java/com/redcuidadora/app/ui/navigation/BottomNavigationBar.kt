package com.redcuidadora.app.ui.navigation

import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.NavigationBarItemDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceHighlight
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark

@Composable
fun RedCuidadoraBottomNavigation(
    currentRoute: String?,
    onNavigateToRoute: (String) -> Unit
) {
    NavigationBar(
        containerColor = DarkSurface,
        contentColor = TextPrimaryDark
    ) {
        bottomNavScreens.forEach { screen ->
            val isSelected = currentRoute == screen.route
            NavigationBarItem(
                selected = isSelected,
                onClick = {
                    if (currentRoute != screen.route) {
                        onNavigateToRoute(screen.route)
                    }
                },
                icon = {
                    Icon(
                        imageVector = if (isSelected) screen.selectedIcon else screen.unselectedIcon,
                        contentDescription = screen.title
                    )
                },
                label = {
                    Text(
                        text = screen.title,
                        fontSize = 11.sp,
                        fontWeight = if (isSelected) FontWeight.SemiBold else FontWeight.Normal
                    )
                },
                colors = NavigationBarItemDefaults.colors(
                    selectedIconColor = PrimaryEmerald,
                    unselectedIconColor = TextSecondaryDark,
                    selectedTextColor = PrimaryEmerald,
                    unselectedTextColor = TextSecondaryDark,
                    indicatorColor = DarkSurfaceHighlight
                )
            )
        }
    }
}
