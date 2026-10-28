package com.redcuidadora.app.data.network

import android.widget.Toast
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.rememberCoroutineScope
import androidx.compose.runtime.setValue
import androidx.compose.ui.platform.LocalContext
import androidx.lifecycle.Lifecycle
import androidx.lifecycle.LifecycleEventObserver
import androidx.lifecycle.compose.LocalLifecycleOwner
import kotlinx.coroutines.CancellationException
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.launch
import retrofit2.Response

fun <T> Response<T>.requireBody(expectedCode: Int = 200): T {
    if (code() != expectedCode) throw IllegalStateException(ApiErrorParser.parseError(this))
    return body() ?: throw IllegalStateException("El servidor devolvió una respuesta vacía.")
}

suspend fun <T> allPages(fetch: suspend (Int) -> Response<List<T>>): List<T> {
    val result = mutableListOf<T>()
    do {
        val page = fetch(result.size).requireBody()
        result.addAll(page)
    } while (page.size == 100)
    return result
}

class RemoteData<T> {
    var data by mutableStateOf<T?>(null)
        internal set
    var message by mutableStateOf("Cargando…")
        internal set
}

@Composable
fun <T> rememberRemoteData(key: Any? = Unit, load: suspend () -> T): RemoteData<T> {
    val state = remember { RemoteData<T>() }
    val owner = LocalLifecycleOwner.current
    var revision by remember { mutableStateOf(0) }
    DisposableEffect(owner) {
        val observer = LifecycleEventObserver { _, event ->
            if (event == Lifecycle.Event.ON_RESUME) revision += 1
        }
        owner.lifecycle.addObserver(observer)
        onDispose { owner.lifecycle.removeObserver(observer) }
    }
    LaunchedEffect(key, revision) {
        state.data = null
        state.message = "Cargando…"
        try {
            state.data = load()
            state.message = ""
        } catch (e: CancellationException) {
            throw e
        } catch (e: Exception) {
            state.message = e.message ?: "No se pudieron cargar los datos."
        }
    }
    return state
}

class ApiAction(
    private val scope: CoroutineScope,
    private val notify: (String) -> Unit,
) {
    var busy by mutableStateOf(false)
        private set
    var message by mutableStateOf<String?>(null)
        private set
    var success by mutableStateOf(false)
        private set

    fun run(successMessage: String, onSuccess: () -> Unit = {}, block: suspend () -> Unit) {
        if (busy) return
        busy = true
        message = null
        success = false
        scope.launch {
            try {
                block()
                success = true
                message = successMessage
                notify(successMessage)
                onSuccess()
            } catch (e: CancellationException) {
                throw e
            } catch (e: Exception) {
                message = e.message ?: "No se pudo completar la operación."
                notify(message!!)
            } finally {
                busy = false
            }
        }
    }
}

@Composable
fun rememberApiAction(): ApiAction {
    val context = LocalContext.current
    val scope = rememberCoroutineScope()
    return remember(scope, context) {
        ApiAction(scope) { Toast.makeText(context, it, Toast.LENGTH_LONG).show() }
    }
}
