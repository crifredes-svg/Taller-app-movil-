package com.redcuidadora.app.data.network

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.GET
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path

// DTO Models matching FastAPI Schemas
data class UsuarioDto(
    val id: Int? = null,
    val nombre: String,
    val correo: String,
    val rol_general: String? = null,
    val persona_a_cargo: String? = null,
    val genero: String? = null,
    val codigo_unico: String? = null
)

data class CheckInDto(
    val id: Int? = null,
    val usuario_id: Int? = null,
    val nivel_sobrecarga: String,
    val factores: List<String>? = emptyList(),
    val notas: String? = null,
    val fecha: String? = null
)

data class ContactoPorCodigoDto(
    val codigo_unico: String,
    val relacion: String,
    val apoyos: List<String>? = emptyList(),
    val disponibilidad: String? = null
)

data class ContactoDto(
    val id: Int? = null,
    val usuario_id: Int? = null,
    val nombre: String,
    val relacion: String,
    val apoyos: List<String>? = emptyList(),
    val disponibilidad: String? = null,
    val contacto_usuario_id: Int? = null
)

data class SolicitudRelevoDto(
    val id: Int? = null,
    val solicitante_id: Int,
    val cuidador_id: Int? = null,
    val titulo: String,
    val fecha: String,
    val hora_inicio: String,
    val hora_fin: String,
    val detalles: String? = null,
    val estado: String? = "pendiente"
)

data class ActualizarEstadoRelevoDto(
    val estado: String,
    val cuidador_id: Int? = null
)

data class AlertaSOSDto(
    val id: Int? = null,
    val usuario_id: Int,
    val mensaje: String? = "Alerta SOS de emergencia activada",
    val ubicacion: String? = null,
    val estado: String? = "activa",
    val fecha: String? = null
)

interface ApiService {

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
