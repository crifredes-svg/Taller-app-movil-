"""Schema compatibility exports backed by resource-specific API views."""

from ..views.usuarios.view import (
    UsuarioIn,
    UsuarioOut,
    RegistroOut,
    LoginIn,
    TokenOut,
    LogoutOut,
    PerfilUpdate,
    HealthOut,
)

from ..views.checkins.view import (
    CheckInIn,
    CheckInOut,
    TendenciaCargaOut,
)

from ..views.contactos.view import (
    ContactoConfianzaIn,
    ContactoPorCodigoIn,
    ContactoConfianzaOut,
    BalanceContactoOut,
    BalanceRedOut,
)

from ..views.relevos.view import (
    SolicitudRelevoIn,
    SolicitudRelevoEstadoIn,
    SolicitudRelevoOut,
    ResumenSemanaOut,
)

from ..views.sos.view import (
    AlertaSOSIn,
    AlertaSOSEstadoIn,
    AlertaSOSOut,
)

__all__ = [
    "UsuarioIn",
    "UsuarioOut",
    "RegistroOut",
    "LoginIn",
    "TokenOut",
    "LogoutOut",
    "PerfilUpdate",
    "HealthOut",
    "CheckInIn",
    "CheckInOut",
    "TendenciaCargaOut",
    "ContactoConfianzaIn",
    "ContactoPorCodigoIn",
    "ContactoConfianzaOut",
    "BalanceContactoOut",
    "BalanceRedOut",
    "SolicitudRelevoIn",
    "SolicitudRelevoEstadoIn",
    "SolicitudRelevoOut",
    "ResumenSemanaOut",
    "AlertaSOSIn",
    "AlertaSOSEstadoIn",
    "AlertaSOSOut",
]
