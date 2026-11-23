package com.redcuidadora.app.ui.screens

import android.os.SystemClock
import androidx.activity.compose.BackHandler
import kotlin.time.Duration.Companion.seconds
import androidx.compose.foundation.border
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.imePadding
import androidx.compose.foundation.layout.heightIn
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.BasicTextField
import androidx.compose.foundation.text.KeyboardActions
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Button
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.CompositionLocalProvider
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableLongStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.saveable.rememberSaveable
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.Alignment
import androidx.compose.ui.focus.FocusRequester
import androidx.compose.ui.focus.focusRequester
import androidx.compose.ui.focus.onFocusChanged
import androidx.compose.ui.graphics.SolidColor
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.input.key.KeyEventType
import androidx.compose.ui.input.key.isCtrlPressed
import androidx.compose.ui.input.key.isShiftPressed
import androidx.compose.ui.input.key.key
import androidx.compose.ui.input.key.onPreviewKeyEvent
import androidx.compose.ui.input.key.type
import androidx.compose.ui.platform.ClipboardManager
import androidx.compose.ui.platform.LocalClipboardManager
import androidx.compose.ui.platform.testTag
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.text.AnnotatedString
import androidx.compose.ui.text.TextRange
import androidx.compose.ui.text.input.ImeAction
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.text.input.TextFieldValue
import androidx.compose.ui.text.style.TextAlign
import androidx.compose.ui.unit.dp
import com.google.gson.JsonParseException
import com.redcuidadora.app.data.network.ApiErrorParser
import com.redcuidadora.app.data.network.ApiService
import com.redcuidadora.app.data.network.ReenvioCodigoDto
import com.redcuidadora.app.data.network.RegistroPendienteDto
import com.redcuidadora.app.data.network.UsuarioDto
import com.redcuidadora.app.data.network.VerificacionRegistroDto
import com.redcuidadora.app.ui.components.StatusNotificationBanner
import java.io.IOException
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.delay
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch

@Composable
fun VerificationScreen(
    registration: RegistroPendienteDto,
    api: ApiService,
    onVerified: (UsuarioDto) -> Unit,
    onBack: () -> Unit,
) {
    val scope = rememberCoroutineScope()
    var digits by rememberSaveable(registration.registroId) { mutableStateOf(List(6) { "" }) }
    var expiresAt by rememberSaveable(registration.registroId) {
        mutableLongStateOf(SystemClock.elapsedRealtime() + registration.expiraEnMinutos * 60_000L)
    }
    var resendAt by rememberSaveable(registration.registroId) {
        mutableLongStateOf(SystemClock.elapsedRealtime() + registration.reenviarEnSegundos * 1_000L)
    }
    var now by remember { mutableLongStateOf(SystemClock.elapsedRealtime()) }
    var verifying by remember { mutableStateOf(false) }
    var resending by remember { mutableStateOf(false) }
    var codeBlocked by rememberSaveable { mutableStateOf(false) }
    var registrationExpired by rememberSaveable { mutableStateOf(false) }
    var error by rememberSaveable { mutableStateOf<String?>(null) }
    var success by rememberSaveable { mutableStateOf<String?>(null) }
    val busy = verifying || resending
    val secondsLeft = ((expiresAt - now + 999) / 1_000).coerceAtLeast(0)
    val resendWait = ((resendAt - now + 999) / 1_000).coerceAtLeast(0)
    val canVerify = !busy && !codeBlocked && !registrationExpired &&
        secondsLeft > 0 && digits.all { it.length == 1 }

    LaunchedEffect(Unit) {
        while (isActive) {
            now = SystemClock.elapsedRealtime()
            delay(1.seconds)
        }
    }
    BackHandler { if (!busy) onBack() }

    val verify: () -> Unit = {
        if (canVerify) {
            verifying = true
            error = null
            success = null
            scope.launch {
                try {
                    val response = api.verificarRegistro(
                        VerificacionRegistroDto(registration.registroId, digits.joinToString("")),
                    )
                    val user = response.body()
                    if (response.code() == 201 && user?.id != null &&
                        user.correo.isNotBlank()
                    ) {
                        onVerified(user)
                    } else if (response.isSuccessful) {
                        error = "El servidor no confirmó la creación de la cuenta."
                    } else {
                        error = ApiErrorParser.parseError(response)
                        when (response.code()) {
                            429 -> codeBlocked = true
                            410 -> expiresAt = SystemClock.elapsedRealtime()
                            404 -> registrationExpired = true
                        }
                    }
                } catch (e: CancellationException) {
                    throw e
                } catch (_: IOException) {
                    error = "No se pudo conectar. Revisa tu conexión e intenta nuevamente."
                } catch (_: JsonParseException) {
                    error = "El servidor devolvió una respuesta inválida."
                } finally {
                    verifying = false
                }
            }
        }
    }

    Column(
        modifier = Modifier.fillMaxSize().statusBarsPadding().imePadding()
            .verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.spacedBy(20.dp),
    ) {
        Text("Verifica tu correo", style = MaterialTheme.typography.headlineMedium)
        Text("Enviamos un código a ${registration.correo}. La cuenta aún no está creada.")
        Text("Escribe los 6 dígitos, uno por casilla. No se permite pegar.")
        VerificationCodeFields(
            digits = digits,
            enabled = !busy && !registrationExpired,
            onDigitsChanged = { digits = it },
            onInvalidInput = { error = "Escribe un solo dígito por casilla, sin pegar." },
            onDone = verify,
        )
        Text(
            if (secondsLeft > 0) {
                "El código vence en ${secondsLeft / 60}:${(secondsLeft % 60).toString().padStart(2, '0')}. Máximo 4 intentos."
            } else {
                "El código venció. Solicita uno nuevo."
            },
        )
        error?.let { StatusNotificationBanner(it, isSuccess = false) }
        success?.let { StatusNotificationBanner(it, isSuccess = true) }
        Button(
            onClick = verify,
            enabled = canVerify,
            modifier = Modifier.fillMaxWidth().testTag("verify-code"),
        ) {
            Text(if (verifying) "Verificando..." else "Verificar y crear cuenta")
        }
        TextButton(
            enabled = !busy && !registrationExpired && resendWait == 0L,
            modifier = Modifier.fillMaxWidth().testTag("resend-code"),
            onClick = {
                resending = true
                error = null
                success = null
                scope.launch {
                    try {
                        val response = api.reenviarCodigo(ReenvioCodigoDto(registration.registroId))
                        val pending = response.body()
                        if (response.code() == 202 && pending != null &&
                            pending.registroId == registration.registroId &&
                            pending.expiraEnMinutos > 0 && pending.reenviarEnSegundos >= 0
                        ) {
                            now = SystemClock.elapsedRealtime()
                            expiresAt = now + pending.expiraEnMinutos * 60_000L
                            resendAt = now + pending.reenviarEnSegundos * 1_000L
                            digits = List(6) { "" }
                            codeBlocked = false
                            success = "Te enviamos un código nuevo. Tienes 4 intentos."
                        } else if (response.isSuccessful) {
                            error = "El servidor no confirmó el reenvío."
                        } else {
                            error = ApiErrorParser.parseError(response)
                            if (response.code() == 404) registrationExpired = true
                            response.headers()["Retry-After"]?.toLongOrNull()?.takeIf { it > 0 }?.let {
                                resendAt = SystemClock.elapsedRealtime() + it * 1_000L
                            }
                        }
                    } catch (e: CancellationException) {
                        throw e
                    } catch (_: IOException) {
                        error = "No se pudo reenviar. Revisa tu conexión e intenta nuevamente."
                    } catch (_: JsonParseException) {
                        error = "El servidor devolvió una respuesta inválida."
                    } finally {
                        resending = false
                    }
                }
            },
        ) {
            Text(
                when {
                    resending -> "Enviando..."
                    resendWait > 0 -> "Reenviar en ${resendWait}s"
                    else -> "Reenviar código"
                },
            )
        }
        TextButton(onClick = onBack, enabled = !busy, modifier = Modifier.fillMaxWidth()) {
            Text("Corregir correo o volver al registro")
        }
    }
}

@Composable
private fun VerificationCodeFields(
    digits: List<String>,
    enabled: Boolean,
    onDigitsChanged: (List<String>) -> Unit,
    onInvalidInput: () -> Unit,
    onDone: () -> Unit,
) {
    val focus = remember { List(6) { FocusRequester() } }
    // Bloquea el portapapeles solo en estas casillas, no en el resto de la app.
    val noClipboard = remember {
        object : ClipboardManager {
            override fun getText(): AnnotatedString? = null
            override fun setText(annotatedString: AnnotatedString) = Unit
        }
    }
    LaunchedEffect(Unit) { focus.first().requestFocus() }
    CompositionLocalProvider(LocalClipboardManager provides noClipboard) {
        Row(horizontalArrangement = Arrangement.spacedBy(6.dp), modifier = Modifier.fillMaxWidth()) {
            digits.forEachIndexed { index, digit ->
                var focused by remember { mutableStateOf(false) }
                BasicTextField(
                    value = TextFieldValue(digit, selection = TextRange(0, digit.length)),
                    onValueChange = { value ->
                        if (value.text.length > 1 || value.text.any { it !in '0'..'9' }) {
                            onInvalidInput()
                        } else {
                            onDigitsChanged(digits.toMutableList().also { it[index] = value.text })
                            if (value.text.isNotEmpty() && index < 5) focus[index + 1].requestFocus()
                        }
                    },
                    enabled = enabled,
                    singleLine = true,
                    textStyle = MaterialTheme.typography.titleLarge.copy(
                        textAlign = TextAlign.Center,
                        color = MaterialTheme.colorScheme.onSurface,
                    ),
                    cursorBrush = SolidColor(MaterialTheme.colorScheme.primary),
                    decorationBox = { innerTextField ->
                        Box(
                            contentAlignment = Alignment.Center,
                            modifier = Modifier.heightIn(min = 56.dp).padding(horizontal = 4.dp),
                        ) { innerTextField() }
                    },
                    keyboardOptions = KeyboardOptions(
                        keyboardType = KeyboardType.NumberPassword,
                        imeAction = if (index == 5) ImeAction.Done else ImeAction.Next,
                        autoCorrectEnabled = false,
                    ),
                    keyboardActions = KeyboardActions(
                        onNext = { if (index < 5) focus[index + 1].requestFocus() },
                        onDone = { onDone() },
                    ),
                    modifier = Modifier.weight(1f).onFocusChanged { focused = it.isFocused }
                        .focusRequester(focus[index])
                        .border(
                            1.dp,
                            if (focused) MaterialTheme.colorScheme.primary else MaterialTheme.colorScheme.outline,
                            RoundedCornerShape(8.dp),
                        )
                        .testTag("code-digit-$index")
                        .semantics { contentDescription = "Dígito ${index + 1} de 6" }
                        .onPreviewKeyEvent {
                            when {
                                (it.isCtrlPressed && it.key == Key.V) ||
                                    (it.isShiftPressed && it.key == Key.Insert) -> {
                                    if (it.type == KeyEventType.KeyDown) onInvalidInput()
                                    true
                                }
                                it.key == Key.Backspace && it.type == KeyEventType.KeyDown &&
                                    digit.isEmpty() && index > 0 -> {
                                    onDigitsChanged(digits.toMutableList().also { values -> values[index - 1] = "" })
                                    focus[index - 1].requestFocus()
                                    true
                                }
                                else -> false
                            }
                        },
                )
            }
        }
    }
}
