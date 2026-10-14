package com.redcuidadora.app.data.network

import com.google.gson.annotations.SerializedName
import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path

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
    val disponibilidad: String? = "Disponible"
)

data class ContactoDto(
    val id: Int? = null,
    @SerializedName("usuario_id") val usuarioId: Int? = null,
    val nombre: String,
    val relacion: String,
    val apoyos: String? = null,
    val disponibilidad: String? = null,
    @SerializedName("contacto_usuario_id") val contactoUsuarioId: Int? = null
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
    val estado: String? = "pendiente"
)

data class ActualizarEstadoRelevoDto(
    val estado: String, // "pendiente" | "aceptada" | "completada"
    @SerializedName("cuidador_id") val cuidadorId: Int? = null
)

// SOS DTO
data class AlertaSOSDto(
    val id: Int? = null,
    @SerializedName("usuario_id") val usuarioId: Int,
    val mensaje: String = "Alerta SOS de emergencia activada",
    val estado: String? = "activa",
    val fecha: String? = null
)

interface ApiService {

    // ---------- Autenticación ----------
    @POST("api/v1/auth/login")
    suspend fun iniciarSesion(@Body loginIn: LoginInDto): Response<TokenOutDto>

    @PATCH("api/v1/perfil/me")
    suspend fun actualizarMiPerfil(@Body perfilUpdate: UsuarioDto): Response<UsuarioDto>

    // ---------- Usuarios ----------
    @POST("api/v1/usuarios")
    suspend fun crearUsuario(@Body usuario: UsuarioDto): Response<UsuarioDto>

    @GET("api/v1/usuarios")
    suspend fun listarUsuarios(): Response<List<UsuarioDto>>

    @GET("api/v1/usuarios/{usuario_id}")
    suspend fun obtenerUsuario(@Path("usuario_id") usuarioId: Int): Response<UsuarioDto>

    // ---------- Mi carga / Check-in ----------
    @POST("api/v1/checkins/usuarios/{usuario_id}")
    suspend fun crearCheckIn(
        @Path("usuario_id") usuarioId: Int,
        @Body checkIn: CheckInDto
    ): Response<CheckInDto>

    @GET("api/v1/checkins/usuarios/{usuario_id}")
    suspend fun listarCheckIns(@Path("usuario_id") usuarioId: Int): Response<List<CheckInDto>>

    // ---------- Contactos / Red ----------
    @POST("api/v1/contactos/usuarios/{usuario_id}/por-codigo")
    suspend fun crearContactoPorCodigo(
        @Path("usuario_id") usuarioId: Int,
        @Body dto: ContactoPorCodigoDto
    ): Response<ContactoDto>

    @GET("api/v1/contactos/usuarios/{usuario_id}")
    suspend fun listarContactos(@Path("usuario_id") usuarioId: Int): Response<List<ContactoDto>>

    // ---------- Solicitudes y Calendario de Relevos ----------
    @POST("api/v1/relevos")
    suspend fun crearSolicitudRelevo(@Body solicitud: SolicitudRelevoDto): Response<SolicitudRelevoDto>

    @GET("api/v1/relevos/usuarios/{usuario_id}")
    suspend fun listarRelevosUsuario(@Path("usuario_id") usuarioId: Int): Response<List<SolicitudRelevoDto>>

    @PATCH("api/v1/relevos/{relevo_id}")
    suspend fun actualizarRelevo(
        @Path("relevo_id") relevoId: Int,
        @Body dto: ActualizarEstadoRelevoDto
    ): Response<SolicitudRelevoDto>

    // ---------- SOS ----------
    @POST("api/v1/sos")
    suspend fun activarSOS(@Body alerta: AlertaSOSDto): Response<AlertaSOSDto>

    @GET("api/v1/sos/usuarios/{usuario_id}")
    suspend fun listarAlertasSOS(@Path("usuario_id") usuarioId: Int): Response<List<AlertaSOSDto>>
}
