from types import SimpleNamespace
from unittest.mock import Mock
import asyncio
import json

import pytest
from fastapi import HTTPException
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.routes import (
    _commit_or_conflict,
    actualizar_estado_sos,
    actualizar_relevo,
    router_usuarios,
    router_auth,
    router_perfil,
    router_checkins,
    router_contactos,
    router_relevos,
    router_sos,
)
from app.schemas import (
    AlertaSOSEstadoIn,
    SolicitudRelevoEstadoIn,
)
from app.security import (
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from app.main import app, manejar_error_no_controlado
from app.database import Base, get_db


def test_no_expone_listado_de_usuarios():
    assert not any(
        "GET" in route.methods or "PATCH" in route.methods
        for route in router_usuarios.routes
    )


def test_solamente_registro_y_login_son_publicos():
    routers = (
        router_auth,
        router_perfil,
        router_usuarios,
        router_checkins,
        router_contactos,
        router_relevos,
        router_sos,
    )
    public_endpoints = {"crear_usuario", "iniciar_sesion"}
    for router in routers:
        for route in router.routes:
            dependency_calls = {
                dependency.call for dependency in route.dependant.dependencies
            }
            if route.endpoint.__name__ in public_endpoints:
                assert get_current_user not in dependency_calls
            else:
                assert get_current_user in dependency_calls, route.path


def test_health_is_public_but_docs_and_user_reads_are_disabled(api_client):
    assert api_client.get("/health").status_code == 200
    for path in ("/docs", "/redoc", "/openapi.json"):
        assert api_client.get(path).status_code == 404
    assert api_client.get("/api/v1/usuarios").status_code == 405
    assert api_client.get("/api/v1/usuarios/1").status_code == 404


def test_password_hash_is_not_plain_text_and_can_be_verified():
    stored_hash = hash_password("una-clave-larga-de-prueba")
    assert stored_hash != "una-clave-larga-de-prueba"
    assert verify_password("una-clave-larga-de-prueba", stored_hash)
    assert not verify_password("otra-clave", stored_hash)


def test_codigo_de_contacto_acepta_formato_android_y_codigo_legacy():
    from app.schemas import ContactoPorCodigoIn

    codigo_android = ContactoPorCodigoIn(
        codigo_unico=" RC-d35c82 ",
        relacion="Tía",
    )
    codigo_legacy = ContactoPorCodigoIn(
        codigo_unico="A1B2C3D4",
        relacion="Hermano",
    )

    assert codigo_android.codigo_unico == "D35C82"
    assert codigo_android.apoyos is None
    assert codigo_android.disponibilidad is None
    assert codigo_legacy.codigo_unico == "A1B2C3D4"


@pytest.mark.parametrize("token", [None, "not.a.valid.jwt"])
def test_missing_or_invalid_token_returns_401(token):
    credentials = (
        None
        if token is None
        else SimpleNamespace(scheme="Bearer", credentials=token)
    )
    with pytest.raises(HTTPException) as error:
        get_current_user(credentials=credentials, db=Mock())
    assert error.value.status_code == 401
    assert error.value.headers["WWW-Authenticate"] == "Bearer"


def test_access_token_contains_user_subject():
    from jose import jwt
    import os

    token = create_access_token(123)
    claims = jwt.decode(token, os.environ["JWT_SECRET"], algorithms=["HS256"])
    assert claims["sub"] == "123"


@pytest.mark.parametrize(
    ("estado_actual", "estado_solicitado"),
    [
        ("completada", "pendiente"),
        ("completada", "aceptada"),
    ],
)
def test_rechaza_transiciones_invalidas_de_relevo(
    estado_actual,
    estado_solicitado,
):
    relevo = SimpleNamespace(
        estado=estado_actual,
        cuidador_id=7,
        solicitante_id=1,
    )
    db = Mock()
    db.get.return_value = relevo
    db.query.return_value.filter.return_value.first.return_value = object()
    cuidador_id = 7 if estado_solicitado == "aceptada" else None

    with pytest.raises(HTTPException) as error:
        actualizar_relevo(
            1,
            SolicitudRelevoEstadoIn(
                estado=estado_solicitado,
                cuidador_id=cuidador_id,
            ),
            current_user=SimpleNamespace(id=7),
            db=db,
        )

    assert error.value.status_code == 400
    db.commit.assert_not_called()


@pytest.mark.parametrize("estado_solicitado", ["activa", "atendida"])
def test_rechaza_reapertura_de_alerta_sos(estado_solicitado):
    alerta = SimpleNamespace(estado="cerrada", usuario_id=2)
    db = Mock()
    db.get.return_value = alerta

    with pytest.raises(HTTPException) as error:
        actualizar_estado_sos(
            1,
            AlertaSOSEstadoIn(estado=estado_solicitado),
            current_user=SimpleNamespace(id=2),
            db=db,
        )

    assert error.value.status_code == 400
    db.commit.assert_not_called()


def test_integrity_error_rollback_y_respuesta_400():
    db = Mock()
    db.commit.side_effect = IntegrityError("insert", {}, Exception("duplicate"))

    with pytest.raises(HTTPException) as error:
        _commit_or_conflict(db, "Conflicto de datos")

    assert error.value.status_code == 400
    db.rollback.assert_called_once()


def test_error_no_controlado_responde_json_generico_sin_filtrar_detalle():
    request = Request(
        {"type": "http", "method": "GET", "path": "/", "headers": []}
    )
    response = asyncio.run(
        manejar_error_no_controlado(request, RuntimeError("secreto de conexion"))
    )
    payload = json.loads(response.body)

    assert response.status_code == 500
    assert payload == {
        "status": "error",
        "message": "Error interno del servidor",
        "detail": "Error interno del servidor",
    }


@pytest.fixture
def api_client():
    from unittest.mock import patch

    test_engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=test_engine)
    test_session = sessionmaker(bind=test_engine, autoflush=False)

    def override_get_db():
        db = test_session()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with patch("app.main._initialize_database"):
        with TestClient(app) as client:
            yield client
    app.dependency_overrides.clear()
    test_engine.dispose()


def _register_test_user(client, email="persona@example.com"):
    return client.post(
        "/api/v1/usuarios",
        json={
            "nombre": "Persona Demo",
            "correo": email,
            "password": "una-clave-segura-de-prueba",
        },
    )


def _login_test_user(client, email="persona@example.com"):
    return client.post(
        "/api/v1/auth/login",
        json={
            "correo": email,
            "password": "una-clave-segura-de-prueba",
        },
    )


def test_flujo_registro_duplicado_login_y_acceso_protegido(api_client):
    created = _register_test_user(api_client)
    assert created.status_code == 201
    assert "password_hash" not in created.json()
    assert created.json()["codigo_unico"].startswith("RC-")

    duplicate = _register_test_user(api_client)
    assert duplicate.status_code == 400

    wrong_password = api_client.post(
        "/api/v1/auth/login",
        json={
            "correo": "persona@example.com",
            "password": "clave-incorrecta",
        },
    )
    unknown_email = api_client.post(
        "/api/v1/auth/login",
        json={
            "correo": "desconocida@example.com",
            "password": "clave-incorrecta",
        },
    )
    assert wrong_password.status_code == unknown_email.status_code == 401
    assert wrong_password.json() == unknown_email.json()

    unauthenticated = api_client.get("/api/v1/checkins/usuarios/1")
    assert unauthenticated.status_code == 401
    assert unauthenticated.headers["www-authenticate"] == "Bearer"

    login = _login_test_user(api_client)
    assert login.status_code == 200
    token = login.json()["access_token"]
    assert login.json()["usuario"]["correo"] == "persona@example.com"
    authorized = api_client.get(
        "/api/v1/checkins/usuarios/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert authorized.status_code == 200
    assert authorized.json() == []


def test_perfil_actualiza_solo_al_usuario_autenticado(api_client):
    created = _register_test_user(api_client)
    token = _login_test_user(api_client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    unauthenticated = api_client.patch(
        "/api/v1/perfil/me",
        json={"nombre": "Nuevo Nombre"},
    )
    assert unauthenticated.status_code == 401

    updated = api_client.patch(
        "/api/v1/perfil/me",
        headers=headers,
        json={
            "nombre": "María González",
            "ocupacion": "Estudiante y cuidadora",
            "genero": "femenino",
            "tipo": "estudiante",
            "persona_cuidada_nombre": "Don Carlos",
            "persona_cuidada_edad": 82,
        },
    )
    assert updated.status_code == 200
    assert updated.json()["nombre"] == "María González"
    assert updated.json()["ocupacion"] == "Estudiante y cuidadora"
    assert updated.json()["persona_cuidada_nombre"] == "Don Carlos"
    assert updated.json()["persona_cuidada_edad"] == 82
    assert updated.json()["id"] == created.json()["id"]

    invalid = api_client.patch(
        "/api/v1/perfil/me",
        headers=headers,
        json={"nombre": None},
    )
    assert invalid.status_code == 422


def test_agregar_contacto_por_codigo_usa_el_contrato_android(api_client):
    owner = _register_test_user(api_client, "cuidadora@example.com")
    contact = _register_test_user(api_client, "contacto@example.com")
    token = _login_test_user(api_client, "cuidadora@example.com").json()[
        "access_token"
    ]

    response = api_client.post(
        f"/api/v1/contactos/usuarios/{owner.json()['id']}/por-codigo",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "codigo_unico": contact.json()["codigo_unico"],
            "relacion": "Tía",
        },
    )

    assert response.status_code == 201
    assert response.json()["nombre"] == "Persona Demo"
    assert response.json()["apoyos"] == ""
    assert response.json()["disponibilidad"] == ""


def test_checkin_acepta_factores_multiseleccion_de_android(api_client):
    created = _register_test_user(api_client)
    token = _login_test_user(api_client).json()["access_token"]

    response = api_client.post(
        f"/api/v1/checkins/usuarios/{created.json()['id']}",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "nivel": "algo_cansada",
            "factores": ["dormir_mal", "clases"],
            "nota": "Necesito un rato de descanso",
        },
    )

    assert response.status_code == 201
    assert response.json()["factores"] == "dormir_mal,clases"


def test_tendencia_carga_usa_dias_distintos_en_ventana_de_cinco_dias(api_client):
    from datetime import date, datetime, time, timedelta
    from types import SimpleNamespace

    from app.routes import _dias_de_alta_carga

    hoy = date.today()
    checkins = [
        SimpleNamespace(
            nivel=nivel,
            fecha=datetime.combine(hoy - timedelta(days=dias_atras), time(12)),
        )
        for dias_atras, nivel in (
            (0, "necesito_apoyo"),
            (1, "sobrepasada"),
            (2, "necesito_apoyo"),
            (2, "sobrepasada"),
            (6, "sobrepasada"),
            (3, "algo_cansada"),
        )
    ]

    assert _dias_de_alta_carga(checkins, hoy) == 3


def test_consultar_tendencia_de_carga_exige_bearer_y_no_diagnostica(api_client):
    created = _register_test_user(api_client)
    token = _login_test_user(api_client).json()["access_token"]
    path = "/api/v1/checkins/tendencia"

    assert api_client.get(path).status_code == 401
    response = api_client.get(
        path,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "dias_evaluados": 5,
        "dias_alta_carga": 0,
        "sugerir_pedir_apoyo": False,
    }


def test_hello_world_public(api_client):
    response = api_client.get("/hello")

    assert response.status_code == 200
    assert response.text == "Hello World"


def test_sos_activa_es_visible_solo_a_integrantes_de_la_red(api_client):
    caregiver = _register_test_user(api_client, "cuidadora@example.com")
    helper = _register_test_user(api_client, "contacto@example.com")
    unrelated = _register_test_user(api_client, "ajena@example.com")
    caregiver_id = caregiver.json()["id"]
    caregiver_token = _login_test_user(
        api_client,
        "cuidadora@example.com",
    ).json()["access_token"]
    helper_token = _login_test_user(
        api_client,
        "contacto@example.com",
    ).json()["access_token"]
    unrelated_token = _login_test_user(
        api_client,
        "ajena@example.com",
    ).json()["access_token"]

    linked = api_client.post(
        f"/api/v1/contactos/usuarios/{caregiver_id}/por-codigo",
        headers={"Authorization": f"Bearer {caregiver_token}"},
        json={
            "codigo_unico": helper.json()["codigo_unico"],
            "relacion": "Tía",
        },
    )
    assert linked.status_code == 201

    alert = api_client.post(
        "/api/v1/sos",
        headers={"Authorization": f"Bearer {caregiver_token}"},
        json={"mensaje": "Necesito apoyo urgente", "usuario_id": caregiver_id},
    )
    assert alert.status_code == 201

    helper_inbox = api_client.get(
        "/api/v1/sos/recibidas",
        headers={"Authorization": f"Bearer {helper_token}"},
    )
    assert helper_inbox.status_code == 200
    assert [item["id"] for item in helper_inbox.json()] == [alert.json()["id"]]

    unrelated_inbox = api_client.get(
        "/api/v1/sos/recibidas",
        headers={"Authorization": f"Bearer {unrelated_token}"},
    )
    assert unrelated_inbox.status_code == 200
    assert unrelated_inbox.json() == []

    unauthenticated = api_client.get("/api/v1/sos/recibidas")
    assert unauthenticated.status_code == 401


def test_balance_red_y_resumen_semanal_usan_relevos_reales(api_client):
    from datetime import date

    caregiver = _register_test_user(api_client, "cuidadora@example.com")
    helper = _register_test_user(api_client, "contacto@example.com")
    caregiver_id = caregiver.json()["id"]
    caregiver_token = _login_test_user(
        api_client,
        "cuidadora@example.com",
    ).json()["access_token"]
    helper_token = _login_test_user(
        api_client,
        "contacto@example.com",
    ).json()["access_token"]
    caregiver_headers = {"Authorization": f"Bearer {caregiver_token}"}
    helper_headers = {"Authorization": f"Bearer {helper_token}"}

    link = api_client.post(
        f"/api/v1/contactos/usuarios/{caregiver_id}/por-codigo",
        headers=caregiver_headers,
        json={"codigo_unico": helper.json()["codigo_unico"], "relacion": "Tía"},
    )
    assert link.status_code == 201

    request = api_client.post(
        "/api/v1/relevos",
        headers=caregiver_headers,
        json={
            "titulo": "Relevo de prueba",
            "tipo": "clases",
            "descripcion": "Apoyo durante tres horas",
            "fecha": date.today().isoformat(),
            "hora_inicio": "09:00",
            "hora_fin": "12:00",
            "solicitante_id": caregiver_id,
        },
    )
    assert request.status_code == 201
    relevo_id = request.json()["id"]

    accepted = api_client.patch(
        f"/api/v1/relevos/{relevo_id}",
        headers=helper_headers,
        json={"estado": "aceptada", "cuidador_id": helper.json()["id"]},
    )
    assert accepted.status_code == 200
    completed = api_client.patch(
        f"/api/v1/relevos/{relevo_id}",
        headers=helper_headers,
        json={"estado": "completada"},
    )
    assert completed.status_code == 200

    balance = api_client.get(
        f"/api/v1/contactos/usuarios/{caregiver_id}/balance",
        headers=caregiver_headers,
    )
    assert balance.status_code == 200
    assert balance.json()["total_horas"] == 3.0
    assert balance.json()["contactos"][0]["horas_apoyo"] == 3.0
    assert balance.json()["contactos"][0]["porcentaje"] == 100.0

    week = api_client.get(
        "/api/v1/relevos/resumen/semana",
        headers=caregiver_headers,
    )
    assert week.status_code == 200
    assert week.json()["horas_protegidas"] == 3.0

    unauthorized = api_client.get(
        f"/api/v1/contactos/usuarios/{caregiver_id}/balance"
    )
    assert unauthorized.status_code == 401

    foreign = api_client.get(
        f"/api/v1/contactos/usuarios/{caregiver_id}/balance",
        headers=helper_headers,
    )
    assert foreign.status_code == 404


def test_handler_global_500_devuelve_json_sin_filtrar(api_client):
    assert api_client is not None

    def provocar_error_no_controlado():
        raise RuntimeError("secreto de conexion")

    app.add_api_route(
        "/_test/error-no-controlado",
        provocar_error_no_controlado,
        methods=["GET"],
        include_in_schema=False,
    )
    try:
        from fastapi.testclient import TestClient

        with TestClient(app, raise_server_exceptions=False) as client:
            response = client.get("/_test/error-no-controlado")
    finally:
        app.router.routes[:] = [
            route
            for route in app.router.routes
            if getattr(route, "path", None) != "/_test/error-no-controlado"
        ]

    assert response.status_code == 500
    assert response.json() == {
        "status": "error",
        "message": "Error interno del servidor",
        "detail": "Error interno del servidor",
    }
    assert "secreto de conexion" not in response.text


def test_token_invalido_y_acceso_a_datos_ajenos_se_rechazan(api_client):
    first = _register_test_user(api_client)
    assert first.status_code == 201
    second = _register_test_user(api_client, "otra@example.com")
    assert second.status_code == 201
    token = _login_test_user(api_client).json()["access_token"]

    invalid = api_client.get(
        "/api/v1/checkins/usuarios/1",
        headers={"Authorization": "Bearer token-invalido"},
    )
    assert invalid.status_code == 401

    foreign_user = api_client.get(
        "/api/v1/checkins/usuarios/2",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert foreign_user.status_code == 404

    unauthenticated_checkins = api_client.get(
        "/api/v1/checkins/usuarios/1"
    )
    assert unauthenticated_checkins.status_code == 401


def test_initialize_database_applies_migrations_then_create_all():
    from unittest.mock import patch

    with (
        patch("app.main.command.upgrade") as upgrade,
        patch("app.main.models.Base.metadata.create_all") as create_all,
    ):
        from app.main import _initialize_database

        _initialize_database()

    assert upgrade.call_args.args[1] == "head"
    create_all.assert_called_once()