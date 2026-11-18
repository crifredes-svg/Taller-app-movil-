package com.redcuidadora.app.ui.screens

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import android.widget.Toast
import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.verticalScroll
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.automirrored.filled.ArrowBack
import androidx.compose.material.icons.filled.ContentCopy
import androidx.compose.material.icons.filled.Person
import androidx.compose.material.icons.filled.QrCode
import androidx.compose.material3.AlertDialog
import androidx.compose.material3.Button
import androidx.compose.material3.ButtonDefaults
import androidx.compose.material3.Card
import androidx.compose.material3.CardDefaults
import androidx.compose.material3.Icon
import androidx.compose.material3.IconButton
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.tooling.preview.Preview
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import com.redcuidadora.app.data.local.TokenManager
import com.redcuidadora.app.data.network.RetrofitClient
import com.redcuidadora.app.data.network.*
import com.redcuidadora.app.ui.components.Gender
import com.redcuidadora.app.ui.components.GenderToggle
import com.redcuidadora.app.ui.theme.DarkSurface
import com.redcuidadora.app.ui.theme.DarkSurfaceVariant
import com.redcuidadora.app.ui.theme.PrimaryEmerald
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import com.redcuidadora.app.ui.theme.StatusRed
import com.redcuidadora.app.ui.theme.TextPrimaryDark
import com.redcuidadora.app.ui.theme.TextSecondaryDark
import kotlinx.coroutines.launch

@Composable
fun PerfilScreen(
    onNavigateBack: () -> Unit,
    onLogoutConfirmed: () -> Unit = {},
) {
    val context = LocalContext.current
    val coroutineScope = rememberCoroutineScope()

    val user = remember { TokenManager.getUser(context) }
    val action = rememberApiAction()
    var nombre by remember { mutableStateOf(user?.nombre.orEmpty()) }
    var rolGeneral by remember { mutableStateOf(user?.ocupacion.orEmpty()) }
    var personaACargo by remember {
        mutableStateOf(user?.personaCuidadaNombre.orEmpty() + (user?.personaCuidadaEdad?.let { " ($it años)" } ?: ""))
    }
    var genero by remember { mutableStateOf(if (user?.genero == "masculino") Gender.MALE else Gender.FEMALE) }
    var generoModificado by remember { mutableStateOf(false) }

    var showLogoutDialog by remember { mutableStateOf(value = false) }

    val userCode = user?.codigoUnico.orEmpty()

    if (showLogoutDialog) {
        AlertDialog(
            onDismissRequest = { showLogoutDialog = false },
            title = {
                Text(text = "Cerrar sesión", fontWeight = FontWeight.Bold)
            },
            text = {
                Text(text = "¿Estás segura de que deseas cerrar tu sesión en RedCuidadora?")
            },
            confirmButton = {
                Button(
                    onClick = {
                        action.run("Sesión cerrada", onSuccess = {
                            showLogoutDialog = false
                            TokenManager.clearSession(context)
                            onLogoutConfirmed()
                        }) {
                            RetrofitClient.getApiService(context).cerrarSesion().requireBody(200)
                        }
                    },
                    enabled = !action.busy,
                    colors = ButtonDefaults.buttonColors(containerColor = StatusRed),
                ) {
                    Text(text = "Cerrar sesión")
                }
            },
            dismissButton = {
                TextButton(
                    onClick = {
                        showLogoutDialog = false
                    },
                ) {
                    Text(text = "Cancelar", color = TextSecondaryDark)
                }
            },
            containerColor = DarkSurface,
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .background(MaterialTheme.colorScheme.background)
            .statusBarsPadding()
            .navigationBarsPadding()
            .padding(horizontal = 20.dp)
            .verticalScroll(rememberScrollState()),
    ) {
        Spacer(modifier = Modifier.height(12.dp))

        // Top Navigation Header
        Row(
            verticalAlignment = Alignment.CenterVertically,
            modifier = Modifier.fillMaxWidth(),
        ) {
            IconButton(onClick = onNavigateBack) {
                Icon(
                    imageVector = Icons.AutoMirrored.Filled.ArrowBack,
                    contentDescription = "Volver",
                    tint = TextPrimaryDark,
                )
            }
            Spacer(modifier = Modifier.width(8.dp))
            Text(
                text = "Mis Datos / Mi Perfil",
                style = MaterialTheme.typography.titleLarge,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold,
            )
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Profile Avatar Header
        Box(
            modifier = Modifier.fillMaxWidth(),
            contentAlignment = Alignment.Center,
        ) {
            Box(
                modifier = Modifier
                    .size(80.dp)
                    .background(DarkSurfaceVariant, CircleShape),
                contentAlignment = Alignment.Center,
            ) {
                Icon(
                    imageVector = Icons.Default.Person,
                    contentDescription = "Avatar",
                    tint = PrimaryEmerald,
                    modifier = Modifier.size(44.dp),
                )
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Unique Alphanumeric Code Card
        Card(
            modifier = Modifier.fillMaxWidth(),
            colors = CardDefaults.cardColors(containerColor = DarkSurface),
            shape = RoundedCornerShape(16.dp),
        ) {
            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(16.dp),
                verticalAlignment = Alignment.CenterVertically,
                horizontalArrangement = Arrangement.SpaceBetween,
            ) {
                Row(
                    verticalAlignment = Alignment.CenterVertically,
                    horizontalArrangement = Arrangement.spacedBy(12.dp),
                ) {
                    Icon(
                        imageVector = Icons.Default.QrCode,
                        contentDescription = "Código",
                        tint = PrimaryEmerald,
                        modifier = Modifier.size(28.dp),
                    )
                    Column {
                        Text(
                            text = "Mi Código Único de Red",
                            fontSize = 12.sp,
                            color = TextSecondaryDark,
                        )
                        Text(
                            text = userCode,
                            fontSize = 18.sp,
                            fontWeight = FontWeight.Bold,
                            color = TextPrimaryDark,
                        )
                    }
                }

                IconButton(
                    onClick = {
                        if (userCode.isBlank()) return@IconButton
                        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
                        val clip = ClipData.newPlainText("Código RedCuidadora", userCode)
                        clipboard.setPrimaryClip(clip)
                        Toast.makeText(context, "Código copiado: $userCode", Toast.LENGTH_SHORT).show()
                    },
                ) {
                    Icon(
                        imageVector = Icons.Default.ContentCopy,
                        contentDescription = "Copiar código",
                        tint = PrimaryEmerald,
                    )
                }
            }
        }

        Spacer(modifier = Modifier.height(20.dp))

        // Gender Selector
        Text(
            text = "Género",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(8.dp))
        GenderToggle(
            selectedGender = genero,
            onGenderSelected = {
                genero = it
                generoModificado = true
            },
        )

        Spacer(modifier = Modifier.height(20.dp))

        // Input Fields
        Text(
            text = "Tu nombre completo",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = nombre,
            onValueChange = { nombre = it },
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
            text = "Tu ocupación / rol principal",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = rolGeneral,
            onValueChange = { rolGeneral = it },
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
            text = "Persona que está a tu cuidado",
            fontSize = 14.sp,
            fontWeight = FontWeight.SemiBold,
            color = TextPrimaryDark,
        )
        Spacer(modifier = Modifier.height(6.dp))
        OutlinedTextField(
            value = personaACargo,
            onValueChange = { personaACargo = it },
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

        // Save Button
        Button(
            onClick = {
                action.run("Datos guardados", onSuccess = onNavigateBack) {
                    val current = user ?: error("Inicia sesión nuevamente.")
                    require(nombre.trim().length in 2..80) { "El nombre debe tener entre 2 y 80 caracteres." }
                    require(rolGeneral.isBlank() || rolGeneral.trim().length in 2..100) { "La ocupación debe tener entre 2 y 100 caracteres." }
                    val person = personaACargo.trim()
                    val match = Regex("""^([^()]+?)(?:\s+\((\d{1,3}) años?\))?$""").matchEntire(person)
                    require(person.isBlank() || match != null) { "Usa Nombre (82 años), o solo el nombre de la persona cuidada." }
                    val personName = match?.groupValues?.get(1)?.trim()?.ifBlank { null }
                    val personAge = match?.groupValues?.get(2)?.toIntOrNull()
                    require(personName == null || personName.length in 2..80) { "El nombre de la persona cuidada debe tener entre 2 y 80 caracteres." }
                    require(personAge == null || personAge in 0..130) { "La edad debe estar entre 0 y 130." }
                    val saved = RetrofitClient.getApiService(context).actualizarMiPerfil(
                        current.copy(
                            password = null, nombre = nombre.trim(), ocupacion = rolGeneral.trim().ifBlank { null },
                            genero = if (!generoModificado) current.genero else if (genero == Gender.FEMALE) "femenino" else "masculino",
                            personaCuidadaNombre = personName, personaCuidadaEdad = personAge,
                        ).profileUpdateBody(),
                    ).requireBody(200)
                    TokenManager.updateUser(context, saved)
                }
            },
            enabled = !action.busy,
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            colors = ButtonDefaults.buttonColors(containerColor = PrimaryEmerald),
            shape = RoundedCornerShape(14.dp),
        ) {
            Text(
                text = "Guardar mis datos",
                style = MaterialTheme.typography.titleMedium,
                color = TextPrimaryDark,
                fontWeight = FontWeight.Bold,
            )
        }

        Spacer(modifier = Modifier.height(16.dp))

        // Logout Button
        OutlinedButton(
            onClick = { showLogoutDialog = true },
            modifier = Modifier
                .fillMaxWidth()
                .height(52.dp),
            shape = RoundedCornerShape(14.dp),
            colors = ButtonDefaults.outlinedButtonColors(contentColor = StatusRed),
            border = BorderStroke(1.dp, StatusRed),
        ) {
            Text(
                text = "Cerrar sesión",
                style = MaterialTheme.typography.titleMedium,
                color = StatusRed,
                fontWeight = FontWeight.Bold,
            )
        }

        // Generous bottom spacer to prevent system gesture bar / clipping on phones and tablets
        Spacer(modifier = Modifier.height(96.dp))
    }
}

@Preview(name = "Teléfono - Mis Datos", showBackground = true, showSystemUi = true)
@Composable
fun PerfilScreenPreview() {
    RedCuidadoraTheme {
        PerfilScreen(onNavigateBack = {}, onLogoutConfirmed = {})
    }
}

@Preview(name = "Tablet - Mis Datos", device = "spec:width=1280dp,height=800dp,dpi=240", showBackground = true, showSystemUi = true)
@Composable
fun PerfilScreenTabletPreview() {
    RedCuidadoraTheme {
        PerfilScreen(onNavigateBack = {}, onLogoutConfirmed = {})
    }
}
