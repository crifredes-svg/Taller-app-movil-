from app.models.checkins.entity import CheckIn
from app.models.contactos.entity import ContactoConfianza
from app.models.relevos.entity import SolicitudRelevo
from app.models.sos.entity import AlertaSOS
from app.models.usuarios.entity import Usuario
from app.models.checkins import model as checkin_model
from app.routers.autenticacion.router import router_auth
from app.routers.checkins.router import router_checkins
from app.routers.contactos.router import router_contactos
from app.routers.perfil.router import router_perfil
from app.routers.relevos.router import router_relevos
from app.routers.sos.router import router_sos
from app.routers.usuarios.router import router_usuarios
from app.views.checkins.view import CheckInIn
from app.views.contactos.view import ContactoConfianzaIn
from app.views.relevos.view import SolicitudRelevoIn
from app.views.sos.view import AlertaSOSIn
from app.views.usuarios.view import UsuarioIn


def test_resource_models_and_views_are_separated():
    assert Usuario.__tablename__ == "usuarios"
    assert CheckIn.__tablename__ == "checkins"
    assert ContactoConfianza.__tablename__ == "contactos_confianza"
    assert SolicitudRelevo.__tablename__ == "solicitudes_relevo"
    assert AlertaSOS.__tablename__ == "alertas_sos"

    for view in (
        UsuarioIn,
        CheckInIn,
        ContactoConfianzaIn,
        SolicitudRelevoIn,
        AlertaSOSIn,
    ):
        assert view.model_fields


def test_each_http_router_has_its_own_resource_module():
    routers = (
        router_usuarios,
        router_auth,
        router_perfil,
        router_checkins,
        router_contactos,
        router_relevos,
        router_sos,
    )

    assert [len(router.routes) for router in routers] == [1, 2, 1, 3, 4, 5, 4]


def test_checkin_router_delegates_data_operations_to_its_model():
    assert callable(checkin_model.crear_checkin)
    assert callable(checkin_model.listar_checkins)
    assert all(
        route.endpoint.__module__ == "app.routers.checkins.router"
        for route in router_checkins.routes
    )
