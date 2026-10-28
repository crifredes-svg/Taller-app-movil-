"""Public collection of resource-specific MVC routers."""

from .autenticacion.router import iniciar_sesion, router_auth, cerrar_sesion
from .checkins.router import (
    consultar_tendencia_carga,
    crear_checkin,
    listar_checkins,
    router_checkins,
)
from .contactos.router import (
    crear_contacto,
    crear_contacto_por_codigo,
    listar_contactos,
    obtener_balance_red,
    router_contactos,
)
from .perfil.router import actualizar_mi_perfil, router_perfil
from .relevos.router import (
    actualizar_relevo,
    crear_solicitud_relevo,
    listar_relevos_usuario,
    obtener_resumen_semana,
    router_relevos,
)
from .sos.router import (
    activar_sos,
    actualizar_estado_sos,
    listar_alertas_sos,
    listar_sos_recibidas,
    router_sos,
)
from .usuarios.router import crear_usuario, router_usuarios

__all__ = [
    "actualizar_estado_sos",
    "actualizar_mi_perfil",
    "actualizar_relevo",
    "activar_sos",
    "cerrar_sesion",
    "consultar_tendencia_carga",
    "crear_checkin",
    "crear_contacto",
    "crear_contacto_por_codigo",
    "crear_solicitud_relevo",
    "crear_usuario",
    "iniciar_sesion",
    "listar_alertas_sos",
    "listar_checkins",
    "listar_contactos",
    "listar_relevos_usuario",
    "listar_sos_recibidas",
    "obtener_balance_red",
    "obtener_resumen_semana",
    "router_auth",
    "router_checkins",
    "router_contactos",
    "router_perfil",
    "router_relevos",
    "router_sos",
    "router_usuarios",
]
