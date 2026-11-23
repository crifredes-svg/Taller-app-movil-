package com.redcuidadora.app.ui.screens

import android.content.ClipData
import android.content.ClipboardManager
import android.content.Context
import androidx.compose.ui.input.key.Key
import androidx.compose.ui.test.*
import androidx.compose.ui.test.junit4.StateRestorationTester
import androidx.compose.ui.test.junit4.createComposeRule
import androidx.test.platform.app.InstrumentationRegistry
import com.google.gson.JsonParser
import com.redcuidadora.app.data.network.ApiService
import com.redcuidadora.app.data.network.RegistroPendienteDto
import com.redcuidadora.app.ui.theme.RedCuidadoraTheme
import java.util.concurrent.TimeUnit
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Rule
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class VerificationScreenTest {
    @get:Rule val compose = createComposeRule()
    private lateinit var server: MockWebServer
    private lateinit var api: ApiService
    private val registrationId = "pending-registration-token-for-ui-test"
    private val pendingJson = """{"registro_id":"$registrationId","correo":"persona@example.com","expira_en_minutos":35,"reenviar_en_segundos":60}"""
    private val userJson = """{"id":1,"nombre":"Persona","correo":"persona@example.com","codigo_unico":"RC-A1B2C3"}"""

    @Before
    fun setup() {
        server = MockWebServer()
        server.start()
        api = Retrofit.Builder().baseUrl(server.url("/"))
            .addConverterFactory(GsonConverterFactory.create()).build()
            .create(ApiService::class.java)
    }

    @After
    fun cleanup() = server.shutdown()

    private fun respond(code: Int, body: String) {
        server.enqueue(MockResponse().setResponseCode(code).setBody(body)
            .setHeader("Content-Type", "application/json"))
    }

    private fun enterCode(code: String) {
        code.forEachIndexed { index, digit ->
            compose.onNodeWithTag("code-digit-$index").performTextInput(digit.toString())
        }
    }

    private fun waitForText(text: String) {
        compose.waitUntil(10_000) {
            compose.onAllNodesWithText(text).fetchSemanticsNodes().isNotEmpty()
        }
    }

    @Test
    fun registrationRequiresCodeAndSurvivesScreenRestoration() {
        respond(202, pendingJson)
        respond(201, userJson)
        var loggedIn = false
        val restoration = StateRestorationTester(compose)
        restoration.setContent {
            RedCuidadoraTheme {
                LoginScreen(onLoginSuccess = { loggedIn = true }, initialTab = 1, apiService = api)
            }
        }
        compose.onNodeWithTag("register-name").performTextInput("Persona")
        compose.onNodeWithTag("register-email").performTextInput("persona@example.com")
        compose.onNodeWithTag("register-password").performTextInput("EjemploSeguro123")
        compose.onNodeWithText("Registrarme").performScrollTo().performClick()
        waitForText("Verifica tu correo")
        assertEquals("/api/v1/usuarios", server.takeRequest(5, TimeUnit.SECONDS)?.path)
        compose.onAllNodes(hasSetTextAction()).assertCountEquals(6)
        compose.onNodeWithTag("verify-code").assertIsNotEnabled()
        compose.onNodeWithTag("code-digit-0").performTextInput("0")

        restoration.emulateSavedInstanceStateRestore()
        compose.onNodeWithTag("code-digit-0").assertTextEquals("0")
        assertEquals(1, server.requestCount)
        "12345".forEachIndexed { index, digit ->
            compose.onNodeWithTag("code-digit-${index + 1}").performTextInput(digit.toString())
        }
        compose.onNodeWithTag("verify-code").performScrollTo().performClick()
        waitForText("¡Correo verificado y cuenta creada! Tu código único es: RC-A1B2C3. Ahora inicia sesión.")
        val verification = server.takeRequest(5, TimeUnit.SECONDS)!!
        assertEquals("/api/v1/usuarios/verificar", verification.path)
        val body = JsonParser.parseString(verification.body.readUtf8()).asJsonObject
        assertEquals(registrationId, body["registro_id"].asString)
        assertEquals("012345", body["codigo"].asString)
        assertFalse(loggedIn)
        assertEquals(2, server.requestCount)
    }

    @OptIn(ExperimentalTestApi::class)
    @Test
    fun sixBoxesRejectClipboardPasteAndMultipleCharacters() {
        compose.setContent {
            RedCuidadoraTheme {
                VerificationScreen(
                    RegistroPendienteDto(registrationId, "persona@example.com", 35, 0),
                    api, onVerified = { fail("No debe crear una cuenta") }, onBack = {},
                )
            }
        }
        compose.onAllNodes(hasSetTextAction()).assertCountEquals(6)
        val first = compose.onNodeWithTag("code-digit-0")
        first.performTextInput("012345")
        first.assertTextEquals("")
        first.performTextInput("A")
        first.assertTextEquals("")

        val context = InstrumentationRegistry.getInstrumentation().targetContext
        val clipboard = context.getSystemService(Context.CLIPBOARD_SERVICE) as ClipboardManager
        compose.runOnIdle { clipboard.setPrimaryClip(ClipData.newPlainText("code", "7")) }
        first.performClick().performKeyInput {
            keyDown(Key.CtrlLeft)
            pressKey(Key.V)
            keyUp(Key.CtrlLeft)
        }
        first.assertTextEquals("")
        compose.onNodeWithTag("verify-code").assertIsNotEnabled()
        assertEquals(0, server.requestCount)
    }

    @Test
    fun exhaustedAttemptsBlockVerificationUntilSuccessfulResend() {
        respond(429, """{"detail":"Superaste los intentos permitidos. Pide un código nuevo"}""")
        respond(202, pendingJson)
        respond(201, userJson)
        var created = false
        compose.setContent {
            RedCuidadoraTheme {
                VerificationScreen(
                    RegistroPendienteDto(registrationId, "persona@example.com", 35, 0),
                    api, onVerified = { created = true }, onBack = {},
                )
            }
        }
        enterCode("012345")
        compose.onNodeWithTag("verify-code").performScrollTo().performClick()
        waitForText("Superaste los intentos permitidos. Pide un código nuevo")
        compose.onNodeWithTag("verify-code").assertIsNotEnabled()
        assertFalse(created)
        compose.onNodeWithTag("resend-code").performScrollTo().performClick()
        waitForText("Te enviamos un código nuevo. Tienes 4 intentos.")
        compose.onNodeWithTag("resend-code").assertIsNotEnabled()
        compose.onNodeWithTag("verify-code").assertIsNotEnabled()
        compose.onNodeWithTag("code-digit-0").assertTextEquals("")
        enterCode("654321")
        compose.onNodeWithTag("verify-code").performScrollTo().performClick()
        compose.waitUntil(10_000) { created }
        assertEquals("/api/v1/usuarios/verificar", server.takeRequest(5, TimeUnit.SECONDS)?.path)
        val resend = server.takeRequest(5, TimeUnit.SECONDS)!!
        assertEquals("/api/v1/usuarios/reenviar-codigo", resend.path)
        assertEquals(registrationId, JsonParser.parseString(resend.body.readUtf8()).asJsonObject["registro_id"].asString)
    }
}
