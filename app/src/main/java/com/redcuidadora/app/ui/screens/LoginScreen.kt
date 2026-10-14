package com.redcuidadora.app.ui.screens

import android.widget.Toast
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Tab
import androidx.compose.material3.TabRow
import androidx.compose.material3.TabRowDefaults
import androidx.compose.material3.TabRowDefaults.tabIndicatorOffset
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.data.local.TokenManager
import com.redcuidadora.app.data.network.ApiErrorParser
import com.redcuidadora.app.data.network.LoginInDto
import com.redcuidadora.app.data.network.RetrofitClient
import com.redcuidadora.app.data.network.UsuarioDto
import com.redcuidadora.app.ui.components.Gender
import com.redcuidadora.app.ui.components.GenderToggle
import com.redcuidadora.app.ui.components.StatusNotificationBanner
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark
import kotlinx.coroutines.launch

@Composable
fun LoginScreen(
    onLoginSuccess: () -> Unit,
    initialTab: Int = 0,
    previewState: String? = null,
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    var selectedTabIndex by remember { mutableIntStateOf(initialTab) } // 0: Login, 1: Registro

    // Login fields
    var loginCorreo by remember { mutableStateOf("") }
    var loginPassword by remember { mutableStateOf("") }

    // Register fields
    var regNombre by remember { mutableStateOf("") }
    var regCorreo by remember { mutableStateOf("") }
    var regPassword by remember { mutableStateOf("") }
    var regOcupacion by remember { mutableStateOf("Estudiante y cuidadora") }
    var regGenero by remember { mutableStateOf(Gender.FEMALE) }
    var regPersonaNombre by remember { mutableStateOf("") }
    var regPersonaEdadText by remember { mutableStateOf("") }

    var errorMessage by remember {
        mutableStateOf(
            when (previewState) {
                "login_error" -> "Correo o contraseña incorrectos. Verifica tus credenciales."
                "register_error" -> "El correo electrónico ya se encuentra registrado en el sistema."
                else -> null
            },
        )
    }
    var successMessage by remember {
        mutableStateOf(
            when (previewState) {
                "login_success" -> "¡Sesión iniciada con éxito! Bienvenido de nuevo a RedCuidadora."
                "register_success" -> "¡Cuenta creada con éxito! Tu código único es RC-A1B2C3."
                else -> null
            },
        )
    }
    var isSubmitting by remember { mutableStateOf(value = false) }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .padding(horizontal = 24.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(modifier = Modifier.height(24.dp))

        // App Brand Header
        Column(
            horizontalAlignment = Alignment.CenterHorizontally,
            modifier = Modifier.fillMaxWidth(),
        ) {
            Text(
                text = "RedCuidadora",
                style = MaterialTheme.typography.headlineLarge,
                color = PrimaryEmerald,
                fontWeight = FontWeight.Bold,
            )
            Spacer(modifier = Modifier.height(6.dp))
            Text(
                text = "Red de apoyo y protección para cuidadoras",
                fontSize = 13.sp,
                color = TextSecondaryDark,
            )
        }

        Spacer(modifier = Modifier.height(28.dp))

        // Mode Tab Selector (Login / Registro)
        TabRow(
            selectedTabIndex = selectedTabIndex,
            containerColor = DarkSurface,
            contentColor = PrimaryEmerald,
            indicator = { tabPositions ->
                TabRowDefaults.SecondaryIndicator(
                    modifier = Modifier.tabIndicatorOffset(tabPositions[selectedTabIndex]),
                    color = PrimaryEmerald,
                )
            },
        ) {
            Tab(
                selected = selectedTabIndex == 0,
                onClick = {
                    selectedTabIndex = 0
                    errorMessage = null
                    successMessage = null
                },
                text = {
                    Text(
                        text = "Iniciar Sesión",
                        color = if (selectedTabIndex == 0) PrimaryEmerald else TextSecondaryDark,
                        fontWeight = FontWeight.Bold,
                    )
                },
            )
            Tab(
                selected = selectedTabIndex == 1,
                onClick = {
                    selectedTabIndex = 1
                    errorMessage = null
                    successMessage = null
                },
                text = {
                    Text(
                        text = "Registrarse",
                        color = if (selectedTabIndex == 1) PrimaryEmerald else TextSecondaryDark,
                        fontWeight = FontWeight.Bold,
                    )
                },
            )
        }

        Spacer(modifier = Modifier.height(24.dp))

        if (selectedTabIndex == 0) {
            // LOGIN FORM
            Text(
                text = "Correo electrónico",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = loginCorreo,
                onValueChange = { loginCorreo = it },
                placeholder = { Text("ejemplo@redcuidadora.dev", color = TextSecondaryDark) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(16.dp))

            Text(
                text = "Contraseña",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = loginPassword,
                onValueChange = { loginPassword = it },
                placeholder = { Text("Mínimo 12 caracteres", color = TextSecondaryDark) },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(28.dp))

            Button(
                onClick = {
                    if (loginCorreo.isBlank() || loginPassword.isBlank()) {
                        errorMessage = "Por favor ingresa tu correo y contraseña"
                        return@Button
                    }
                    isSubmitting = true
                    errorMessage = null
                    successMessage = null

                    coroutineScope.launch {
                        try {
                            val api = RetrofitClient.getApiService(context)
                            val response = api.iniciarSesion(LoginInDto(loginCorreo.trim(), loginPassword))

                            val body = response.body()
                            if ((response.isSuccessful) && (body != null)) {
                                TokenManager.saveSession(
                                    context = context,
                                    token = body.accessToken,
                                    expiresInSeconds = body.expiresIn.toLong(),
                                    user = body.usuario,
                                )
                                Toast.makeText(context, "¡Sesión iniciada con éxito!", Toast.LENGTH_SHORT).show()
                                onLoginSuccess()
                            } else {
                                errorMessage = ApiErrorParser.parseError(response)
                            }
                        } catch (_: Exception) {
                            errorMessage = "Error de conexión con el servidor (puerto 9000)"
                        } finally {
                            isSubmitting = false
                        }
                    }
                },
                enabled = !isSubmitting,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = if (isSubmitting) "Iniciando sesión..." else "Iniciar Sesión",
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Bold,
                )
            }

        } else {
            // REGISTRO FORM
            Text(
                text = "Nombre completo*",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = regNombre,
                onValueChange = { regNombre = it },
                placeholder = { Text("María González", color = TextSecondaryDark) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "Correo electrónico*",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = regCorreo,
                onValueChange = { regCorreo = it },
                placeholder = { Text("tu_correo@ejemplo.com", color = TextSecondaryDark) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "Contraseña* (Mínimo 12 caracteres)",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = regPassword,
                onValueChange = { regPassword = it },
                placeholder = { Text("Mínimo 12 caracteres", color = TextSecondaryDark) },
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "Género",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            GenderToggle(
                selectedGender = regGenero,
                onGenderSelected = { regGenero = it },
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "Ocupación / Rol (Opcional)",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = regOcupacion,
                onValueChange = { regOcupacion = it },
                placeholder = { Text("Estudiante y cuidadora", color = TextSecondaryDark) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "Persona cuidada - Nombre (Opcional)",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = regPersonaNombre,
                onValueChange = { regPersonaNombre = it },
                placeholder = { Text("Ej. Don Carlos", color = TextSecondaryDark) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(14.dp))

            Text(
                text = "Persona cuidada - Edad (Opcional)",
                fontSize = 13.sp,
                fontWeight = FontWeight.SemiBold,
                color = TextPrimaryDark,
            )
            Spacer(modifier = Modifier.height(6.dp))
            OutlinedTextField(
                value = regPersonaEdadText,
                onValueChange = { regPersonaEdadText = it },
                placeholder = { Text("Ej. 82", color = TextSecondaryDark) },
                modifier = Modifier.fillMaxWidth(),
                shape = RoundedCornerShape(12.dp),
                colors = OutlinedTextFieldDefaults.colors(
                    focusedContainerColor = DarkSurface,
                    unfocusedContainerColor = DarkSurface,
                    focusedBorderColor = PrimaryEmerald,
                    unfocusedBorderColor = DarkSurfaceVariant,
                    focusedTextColor = TextPrimaryDark,
                    unfocusedTextColor = TextPrimaryDark,
                ),
            )

            Spacer(modifier = Modifier.height(28.dp))

            Button(
                onClick = {
                    if ((regNombre.isBlank()) || (regCorreo.isBlank()) || (regPassword.length < 12)) {
                        errorMessage = "Ingresa nombre, correo y contraseña de al menos 12 caracteres"
                        return@Button
                    }
                    isSubmitting = true
                    errorMessage = null
                    successMessage = null

                    val generoStr = if (regGenero == Gender.FEMALE) "femenino" else "masculino"
                    val edadInt = regPersonaEdadText.toIntOrNull()

                    val usuarioIn = UsuarioDto(
                        nombre = regNombre.trim(),
                        correo = regCorreo.trim(),
                        password = regPassword,
                        ocupacion = regOcupacion.ifBlank { null },
                        tipo = "estudiante",
                        genero = generoStr,
                        personaCuidadaNombre = regPersonaNombre.ifBlank { null },
                        personaCuidadaEdad = edadInt,
                    )

                    coroutineScope.launch {
                        try {
                            val api = RetrofitClient.getApiService(context)
                            val response = api.crearUsuario(usuarioIn)

                            val userCreated = response.body()
                            if ((response.isSuccessful) && (userCreated != null)) {
                                val codigo = userCreated.codigoUnico ?: "RC-REGISTRO"
                                successMessage = "¡Cuenta creada! Tu código único es: $codigo. Ahora inicia sesión."
                                loginCorreo = regCorreo
                                selectedTabIndex = 0
                            } else {
                                errorMessage = ApiErrorParser.parseError(response)
                            }
                        } catch (_: Exception) {
                            errorMessage = "Error de conexión con el servidor (puerto 9000)"
                        } finally {
                            isSubmitting = false
                        }
                    }
                },
                enabled = !isSubmitting,
                modifier = Modifier
                    .fillMaxWidth()
                    .height(52.dp),
                colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
                shape = RoundedCornerShape(14.dp),
            ) {
                Text(
                    text = if (isSubmitting) "Creando cuenta..." else "Registrarme",
                    style = MaterialTheme.typography.titleMedium,
                    color = TextPrimaryDark,
                    fontWeight = FontWeight.Bold,
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Status Banners
        if (errorMessage != null) {
            StatusNotificationBanner(
                message = errorMessage!!,
                isSuccess = false,
            )
        }

        if (successMessage != null) {
            StatusNotificationBanner(
                message = successMessage!!,
                isSuccess = true,
            )
        }

        Spacer(modifier = Modifier.height(28.dp))
    }
}

@Preview(name = "Teléfono - Login", showBackground = true, showSystemUi = true)
@Composable
fun LoginScreenPreview() {
    RedCuidadoraTheme {
        LoginScreen(onLoginSuccess = {})
    }
}

@Preview(name = "Tablet - Login", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun LoginScreenTabletPreview() {
    RedCuidadoraTheme {
        LoginScreen(onLoginSuccess = {})
    }
}
