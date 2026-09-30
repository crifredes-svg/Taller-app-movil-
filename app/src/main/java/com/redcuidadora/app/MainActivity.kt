package com.redcuidadora.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Scaffold
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import com.redcuidadora.app.ui.components.ActionChoiceBottomSheet
import com.redcuidadora.app.ui.navigation.RedCuidadoraBottomNavigation
import com.redcuidadora.app.ui.navigation.Screen
import com.redcuidadora.app.ui.screens.AnadirContactoScreen
import com.redcuidadora.app.ui.screens.CalendarioScreen
import com.redcuidadora.app.ui.screens.CheckInScreen
import com.redcuidadora.app.ui.screens.CrearSolicitudScreen
import com.redcuidadora.app.ui.screens.HomeScreen
import com.redcuidadora.app.ui.screens.PerfilScreen
import com.redcuidadora.app.ui.screens.RedScreen
import com.redcuidadora.app.ui.screens.SolicitudesScreen
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme

class MainActivity : ComponentActivity() {
    @OptIn(ExperimentalMaterial3Api::class)
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            RedCuidadoraTheme {
                val navController = rememberNavController()
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route

                var showActionChoiceSheet by remember { mutableStateOf(false) }

                // Hide bottom bar on detail/form screens
                val hideBottomBarRoutes = listOf(
                    Screen.Perfil.route,
                    Screen.AnadirContacto.route,
                    Screen.CrearSolicitud.route
                )
                val shouldShowBottomBar = currentRoute !in hideBottomBarRoutes

                Scaffold(
                    modifier = Modifier.fillMaxSize(),
                    bottomBar = {
                        if (shouldShowBottomBar) {
                            RedCuidadoraBottomNavigation(
                                currentRoute = currentRoute,
                                onNavigateToRoute = { route ->
                                    navController.navigate(route) {
                                        popUpTo(Screen.Home.route) {
                                            saveState = true
                                        }
                                        launchSingleTop = true
                                        restoreState = true
                                    }
                                }
                            )
                        }
                    },
                    containerColor = MaterialTheme.colorScheme.background
                ) { innerPadding ->
                    Box(
                        modifier = Modifier
                            .fillMaxSize()
                            .background(MaterialTheme.colorScheme.background)
                            .padding(if (shouldShowBottomBar) innerPadding else PaddingValues())
                    ) {
                        NavHost(
                            navController = navController,
                            startDestination = Screen.Home.route
                        ) {
                            composable(Screen.Home.route) {
                                HomeScreen(
                                    onNavigateToSolicitudes = {
                                        navController.navigate(Screen.Solicitudes.route)
                                    },
                                    onNavigateToCheckIn = {
                                        navController.navigate(Screen.MiCarga.route)
                                    },
                                    onNavigateToPerfil = {
                                        navController.navigate(Screen.Perfil.route)
                                    }
                                )
                            }
                            composable(Screen.MiCarga.route) {
                                CheckInScreen(
                                    onNavigateBack = {
                                        navController.popBackStack()
                                    }
                                )
                            }
                            composable(Screen.Solicitudes.route) {
                                SolicitudesScreen(
                                    onOpenActionChoice = {
                                        showActionChoiceSheet = true
                                    }
                                )
                            }
                            composable(Screen.MiRed.route) {
                                RedScreen()
                            }
                            composable(Screen.Calendario.route) {
                                CalendarioScreen(
                                    onNavigateToSolicitudes = {
                                        navController.navigate(Screen.Solicitudes.route)
                                    }
                                )
                            }
                            composable(Screen.Perfil.route) {
                                PerfilScreen(
                                    onNavigateBack = {
                                        navController.popBackStack()
                                    }
                                )
                            }
                            composable(Screen.AnadirContacto.route) {
                                AnadirContactoScreen(
                                    onNavigateBack = {
                                        navController.popBackStack()
                                    }
                                )
                            }
                            composable(Screen.CrearSolicitud.route) {
                                CrearSolicitudScreen(
                                    onNavigateBack = {
                                        navController.popBackStack()
                                    }
                                )
                            }
                        }

                        // Intermediate Choice Modal Sheet
                        if (showActionChoiceSheet) {
                            ActionChoiceBottomSheet(
                                onDismissRequest = { showActionChoiceSheet = false },
                                onSelectAddContact = {
                                    navController.navigate(Screen.AnadirContacto.route)
                                },
                                onSelectCreateRequest = {
                                    navController.navigate(Screen.CrearSolicitud.route)
                                }
                            )
                        }
                    }
                }
            }
        }
    }
}
