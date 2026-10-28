package com.redcuidadora.app.data.network

import com.google.gson.annotations.SerializedName
import com.google.gson.JsonNull
import com.google.gson.JsonObject
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.RequestBody
import okhttp3.RequestBody.Companion.toRequestBody
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

// Auth DTOs
data class LoginInDto(
    val correo: String,
    val password: String,
)

data class TokenOutDto(
    @SerializedName("access_token") val accessToken: String,
    @SerializedName("token_type") val tokenType: String = "bearer",
    @SerializedName("expires_in") val expiresIn: Int = 1800,
    val usuario: UsuarioDto,
)

data class LogoutOutDto(
    val detail: String? = "Sesión cerrada correctamente",
)

fun UsuarioDto.profileUpdateBody(): RequestBody = JsonObject().apply {
    addProperty("nombre", nombre)
    tipo?.let { addProperty("tipo", it) }
    add("ocupacion", ocupacion?.let { com.google.gson.JsonPrimitive(it) } ?: JsonNull.INSTANCE)
    add("genero", genero?.let { com.google.gson.JsonPrimitive(it) } ?: JsonNull.INSTANCE)
    add("persona_cuidada_nombre", personaCuidadaNombre?.let { com.google.gson.JsonPrimitive(it) } ?: JsonNull.INSTANCE)
    add("persona_cuidada_edad", personaCuidadaEdad?.let { com.google.gson.JsonPrimitive(it) } ?: JsonNull.INSTANCE)
}.toString().toRequestBody("application/json; charset=utf-8".toMediaType())

// Usuario DTO
data class UsuarioDto(
    val id: Int? = null,
    val nombre: String,
    val correo: String,
    val password: String? = null,
    val ocupacion: String? = null,
    val tipo: String? = "estudiante",
    val genero: String? = null,
    @SerializedName("codigo_unico") val codigoUnico: String? = null,
    @SerializedName("persona_cuidada_nombre") val personaCuidadaNombre: String? = null,
    @SerializedName("persona_cuidada_edad") val personaCuidadaEdad: Int? = null,
)

// Check-in DTO
data class CheckInDto(
    val id: Int? = null,
    @SerializedName("usuario_id") val usuarioId: Int? = null,
    val nivel: String, // "bien" | "algo_cansada" | "necesito_apoyo" | "sobrepasada"
    val factores: String? = null,
    val nota: String? = null,
    val fecha: String? = null,
)

// Contacto DTOs
data class ContactoPorCodigoDto(
    @SerializedName("codigo_unico") val codigoUnico: String,
    val relacion: String,
    val apoyos: String? = "Apoyo general",
    val disponibilidad: String? = "Disponible",
)

data class ContactoDto(
    val id: Int? = null,
    @SerializedName("usuario_id") val usuarioId: Int? = null,
    val nombre: String,
    val relacion: String,
    val apoyos: String? = null,
    val disponibilidad: String? = null,
    @SerializedName("contacto_usuario_id") val contactoUsuarioId: Int? = null,
)

// Solicitud Relevo DTO
data class SolicitudRelevoDto(
    val id: Int? = null,
    @SerializedName("solicitante_id") val solicitanteId: Int,
    @SerializedName("cuidador_id") val cuidadorId: Int? = null,
    val titulo: String,
    val tipo: String, // "estudio" | "clases" | "compras" | "casa"
    val descripcion: String,
    val fecha: String, // YYYY-MM-DD
    @SerializedName("hora_inicio") val horaInicio: String, // HH:MM
    @SerializedName("hora_fin") val horaFin: String, // HH:MM
    val estado: String? = "pendiente",
)

data class ActualizarEstadoRelevoDto(
    val estado: String, // "pendiente" | "aceptada" | "completada"
    @SerializedName("cuidador_id") val cuidadorId: Int? = null,
)

// SOS DTO
data class AlertaSOSDto(
    val id: Int? = null,
    @SerializedName("usuario_id") val usuarioId: Int,
    val mensaje: String = "Alerta SOS de emergencia activada",
    val estado: String? = "activa",
    val fecha: String? = null,
)

data class TendenciaCargaDto(
    @SerializedName("dias_evaluados") val diasEvaluados: Int,
    @SerializedName("dias_alta_carga") val diasAltaCarga: Int,
    @SerializedName("sugerir_pedir_apoyo") val sugerirPedirApoyo: Boolean,
)

data class BalanceContactoDto(
    @SerializedName("contacto_id") val contactoId: Int,
    val nombre: String,
    val relacion: String,
    @SerializedName("horas_apoyo") val horasApoyo: Double,
    val porcentaje: Double,
)

data class BalanceRedDto(
    val desde: String,
    val hasta: String,
    @SerializedName("total_horas") val totalHoras: Double,
    val contactos: List<BalanceContactoDto>,
)

data class ResumenSemanaDto(
    val desde: String,
    val hasta: String,
    @SerializedName("horas_protegidas") val horasProtegidas: Double,
)

@Suppress("unused")
interface ApiService {

    // ---------- Autenticación ----------
    @POST("api/v1/auth/login")
    suspend fun iniciarSesion(@Body loginIn: LoginInDto): Response<TokenOutDto>

    @POST("api/v1/auth/logout")
    suspend fun cerrarSesion(): Response<LogoutOutDto>

    @PATCH("api/v1/perfil/me")
    suspend fun actualizarMiPerfil(@Body perfilUpdate: RequestBody): Response<UsuarioDto>

    // ---------- Usuarios ----------
    @POST("api/v1/usuarios")
    suspend fun crearUsuario(@Body usuario: UsuarioDto): Response<UsuarioDto>

    // ---------- Mi carga / Check-in ----------
    @POST("api/v1/checkins/usuarios/{usuario_id}")
    suspend fun crearCheckIn(
        @Path("usuario_id") usuarioId: Int,
        @Body checkIn: CheckInDto,
    ): Response<CheckInDto>

    @GET("api/v1/checkins/usuarios/{usuario_id}")
    suspend fun listarCheckIns(@Path("usuario_id") usuarioId: Int, @Query("offset") offset: Int = 0): Response<List<CheckInDto>>

    @GET("api/v1/checkins/tendencia")
    suspend fun obtenerTendencia(): Response<TendenciaCargaDto>

    // ---------- Contactos / Red ----------
    @POST("api/v1/contactos/usuarios/{usuario_id}/por-codigo")
    suspend fun crearContactoPorCodigo(
        @Path("usuario_id") usuarioId: Int,
        @Body dto: ContactoPorCodigoDto,
    ): Response<ContactoDto>

    @GET("api/v1/contactos/usuarios/{usuario_id}")
    suspend fun listarContactos(@Path("usuario_id") usuarioId: Int, @Query("offset") offset: Int = 0): Response<List<ContactoDto>>

    @GET("api/v1/contactos/usuarios/{usuario_id}/balance")
    suspend fun obtenerBalance(@Path("usuario_id") usuarioId: Int): Response<BalanceRedDto>

    // ---------- Solicitudes y Calendario de Relevos ----------
    @POST("api/v1/relevos")
    suspend fun crearSolicitudRelevo(@Body solicitud: SolicitudRelevoDto): Response<SolicitudRelevoDto>

    @GET("api/v1/relevos/usuarios/{usuario_id}")
    suspend fun listarRelevosUsuario(@Path("usuario_id") usuarioId: Int, @Query("offset") offset: Int = 0): Response<List<SolicitudRelevoDto>>

    @GET("api/v1/relevos/disponibles")
    suspend fun listarRelevosDisponibles(@Query("offset") offset: Int = 0): Response<List<SolicitudRelevoDto>>

    @GET("api/v1/relevos/resumen/semana")
    suspend fun obtenerResumenSemana(): Response<ResumenSemanaDto>

    @PATCH("api/v1/relevos/{relevo_id}")
    suspend fun actualizarRelevo(
        @Path("relevo_id") relevoId: Int,
        @Body dto: ActualizarEstadoRelevoDto,
    ): Response<SolicitudRelevoDto>

    // ---------- SOS ----------
    @POST("api/v1/sos")
    suspend fun activarSOS(@Body alerta: AlertaSOSDto): Response<AlertaSOSDto>

    @GET("api/v1/sos/usuarios/{usuario_id}")
    suspend fun listarAlertasSOS(@Path("usuario_id") usuarioId: Int): Response<List<AlertaSOSDto>>

    @GET("api/v1/sos/recibidas")
    suspend fun listarSOSRecibidas(@Query("offset") offset: Int = 0): Response<List<AlertaSOSDto>>
}
