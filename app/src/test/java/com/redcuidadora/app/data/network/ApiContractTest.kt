package com.redcuidadora.app.data.network

import com.google.gson.JsonParser
import kotlinx.coroutines.runBlocking
import okhttp3.mockwebserver.MockResponse
import okhttp3.mockwebserver.MockWebServer
import org.junit.After
import org.junit.Assert.*
import org.junit.Before
import org.junit.Test
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory

class ApiContractTest {
    private lateinit var server: MockWebServer
    private lateinit var api: ApiService

    @Before
    fun setup() {
        server = MockWebServer()
        server.start()
        api = Retrofit.Builder()
            .baseUrl(server.url("/"))
            .addConverterFactory(GsonConverterFactory.create())
            .build().create(ApiService::class.java)
    }

    @After
    fun cleanup() = server.shutdown()

    private fun respond(code: Int, json: String) {
        server.enqueue(MockResponse().setResponseCode(code).setBody(json)
            .setHeader("Content-Type", "application/json"))
    }

    @Test
    fun registrationUsesBackendFieldsAndExact201() = runBlocking {
        respond(201, """{"id":1,"nombre":"Persona","correo":"persona@example.com","codigo_unico":"RC-A1B2C3"}""")
        val user = api.crearUsuario(UsuarioDto(
            nombre = "Persona", correo = "persona@example.com",
            password = "EjemploSeguro123", genero = "masculino",
        )).requireBody(201)
        assertEquals("RC-A1B2C3", user.codigoUnico)
        val request = server.takeRequest()
        assertEquals("/api/v1/usuarios", request.path)
        val body = JsonParser.parseString(request.body.readUtf8()).asJsonObject
        assertEquals("masculino", body["genero"].asString)
        assertEquals("persona@example.com", body["correo"].asString)
        assertFalse(body.has("persona_cuidada_edad"))
    }

    @Test
    fun logoutUsesPostWithoutBodyAndRejectsOtherSuccessCodes() = runBlocking {
        respond(200, """{"detail":"Sesión cerrada correctamente"}""")
        assertEquals("Sesión cerrada correctamente", api.cerrarSesion().requireBody().detail)
        val request = server.takeRequest()
        assertEquals("POST", request.method)
        assertEquals("/api/v1/auth/logout", request.path)
        assertEquals(0L, request.bodySize)
        respond(201, """{"detail":"No es el código esperado"}""")
        try {
            api.cerrarSesion().requireBody(200)
            fail("201 no debe aceptarse como logout exitoso")
        } catch (_: IllegalStateException) {
        }
    }

    @Test
    fun loginReadsTokenAndProfile() = runBlocking {
        respond(200, """{"access_token":"fake-test-token","token_type":"bearer","expires_in":1800,"usuario":{"id":7,"nombre":"Persona","correo":"persona@example.com"}}""")
        val result = api.iniciarSesion(LoginInDto("persona@example.com", "EjemploSeguro123")).requireBody()
        assertEquals(7, result.usuario.id)
        assertEquals(1800, result.expiresIn)
        assertEquals("/api/v1/auth/login", server.takeRequest().path)
    }

    @Test
    fun availableReliefsAndCompletionUseCorrectContracts() = runBlocking {
        respond(200, "[]")
        api.listarRelevosDisponibles(100).requireBody()
        assertEquals("/api/v1/relevos/disponibles?offset=100", server.takeRequest().path)
        respond(200, """{"id":3,"solicitante_id":1,"cuidador_id":2,"titulo":"Apoyo","tipo":"casa","descripcion":"Ayuda en casa","fecha":"2099-12-01","hora_inicio":"10:00","hora_fin":"11:00","estado":"completada"}""")
        api.actualizarRelevo(3, ActualizarEstadoRelevoDto("completada")).requireBody()
        val request = server.takeRequest()
        assertEquals("PATCH", request.method)
        assertEquals("/api/v1/relevos/3", request.path)
        val body = JsonParser.parseString(request.body.readUtf8()).asJsonObject
        assertEquals("completada", body["estado"].asString)
        assertFalse(body.has("cuidador_id"))
    }

    @Test
    fun profileClearsNullableFieldsWithoutSendingSecrets() = runBlocking {
        respond(200, """{"id":1,"nombre":"Persona","correo":"persona@example.com"}""")
        api.actualizarMiPerfil(UsuarioDto(
            id = 1, nombre = "Persona", correo = "persona@example.com",
            password = "never-send-this",
        ).profileUpdateBody()).requireBody()
        val request = server.takeRequest()
        val body = JsonParser.parseString(request.body.readUtf8()).asJsonObject
        assertTrue(body["ocupacion"].isJsonNull)
        assertTrue(body["persona_cuidada_nombre"].isJsonNull)
        assertTrue(body["persona_cuidada_edad"].isJsonNull)
        assertFalse(body.has("password"))
        assertFalse(body.has("correo"))
        assertFalse(body.has("id"))
    }

    @Test
    fun paginationFetchesFollowingPage() = runBlocking {
        val item = """{"id":1,"nombre":"Persona","relacion":"Familia"}"""
        respond(200, List(100) { item }.joinToString(",", "[", "]"))
        respond(200, "[]")
        assertEquals(100, allPages { api.listarContactos(1, it) }.size)
        assertEquals("/api/v1/contactos/usuarios/1?offset=0", server.takeRequest().path)
        assertEquals("/api/v1/contactos/usuarios/1?offset=100", server.takeRequest().path)
    }

    @Test
    fun validationErrorsKeepReadableMessage() = runBlocking {
        respond(422, """{"detail":[{"loc":["body","nombre"],"msg":"Nombre inválido","type":"value_error"}]}""")
        val response = api.crearUsuario(UsuarioDto(nombre = "", correo = "persona@example.com"))
        assertEquals("nombre: Nombre inválido", ApiErrorParser.parseError(response))
    }

    @Test
    fun scheduleParsesValidDateAndHours() {
        assertEquals(ReliefSchedule("2099-12-01", "09:00", "10:30"),
            parseReliefSchedule("2099-12-01 09:00 - 10:30"))
    }

    @Test(expected = IllegalArgumentException::class)
    fun scheduleRejectsImpossibleDate() {
        parseReliefSchedule("2099-02-30 09:00 - 10:00")
    }

    @Test(expected = IllegalArgumentException::class)
    fun scheduleRejectsReversedHours() {
        parseReliefSchedule("2099-12-01 12:00 - 10:00")
    }

    @Test(expected = IllegalArgumentException::class)
    fun scheduleRejectsOutOfRangeHour() {
        parseReliefSchedule("2099-12-01 25:00 - 26:00")
    }
}
