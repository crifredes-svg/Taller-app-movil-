from types import SimpleNamespace
from unittest.mock import Mock
import asyncio
import json
import re

import pytest
from fastapi import HTTPException
from fastapi import Request
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.api.routes import (
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
    router_notificaciones,
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
        router_notificaciones,
    )
    public_endpoints = {
        "crear_usuario",
        "verificar_registro",
        "reenviar_codigo_registro",
        "iniciar_sesion",
    }
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


def test_error_no_controlado_responde_json_generico_sin_filtrar_detalle(caplog):
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
    assert "secreto de conexion" not in caplog.text
    assert "RuntimeError" in caplog.text


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
    codigos_enviados = {}

    def capturar_codigo(correo, codigo, _minutos):
        codigos_enviados[correo] = codigo

    with patch("app.main._initialize_database"), patch(
        "app.models.usuarios.model.enviar_codigo_verificacion",
        side_effect=capturar_codigo,
    ):
        with TestClient(app) as client:
            client.codigos_enviados = codigos_enviados
            yield client
    app.dependency_overrides.clear()
    test_engine.dispose()


def _registrar_y_verificar(client, payload):
    solicitud = client.post("/api/v1/usuarios", json=payload)
    if solicitud.status_code != 202:
        return solicitud
    return client.post(
        "/api/v1/usuarios/verificar",
        json={
            "registro_id": solicitud.json()["registro_id"],
            "codigo": client.codigos_enviados[payload["correo"]],
        },
    )


def _register_test_user(client, email="persona@example.com"):
    return _registrar_y_verificar(
        client,
        {
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


def test_validacion_no_devuelve_contrasena_ni_cuerpo(api_client):
    response = api_client.post(
        "/api/v1/usuarios",
        json={"nombre": "Prueba", "correo": "prueba@correo.cl", "password": "corta"},
    )
    assert response.status_code == 422
    assert "corta" not in response.text
    assert all("input" not in error and "ctx" not in error for error in response.json()["detail"])


@pytest.mark.parametrize("codigo", [123456, None, [], {}])
def test_codigo_de_contacto_no_textual_devuelve_422(api_client, codigo):
    user = _register_test_user(api_client).json()
    token = _login_test_user(api_client).json()["access_token"]
    response = api_client.post(
        f"/api/v1/contactos/usuarios/{user['id']}/por-codigo",
        headers={"Authorization": f"Bearer {token}"},
        json={"codigo_unico": codigo, "relacion": "Amigo"},
    )
    assert response.status_code == 422


def test_disponibles_y_completar_sin_reasignar_cuidador(api_client):
    from datetime import date

    owner = _register_test_user(api_client, "owner@example.com").json()
    helper = _register_test_user(api_client, "helper@example.com").json()
    outsider = _register_test_user(api_client, "outsider@example.com").json()
    owner_headers = {"Authorization": f"Bearer {_login_test_user(api_client, 'owner@example.com').json()['access_token']}"}
    helper_headers = {"Authorization": f"Bearer {_login_test_user(api_client, 'helper@example.com').json()['access_token']}"}
    outsider_headers = {"Authorization": f"Bearer {_login_test_user(api_client, 'outsider@example.com').json()['access_token']}"}
    contact = api_client.post(
        f"/api/v1/contactos/usuarios/{owner['id']}/por-codigo",
        headers=owner_headers,
        json={"codigo_unico": helper["codigo_unico"], "relacion": "Amigo"},
    )
    assert contact.status_code == 201
    created = api_client.post(
        "/api/v1/relevos",
        headers=owner_headers,
        json={
            "titulo": "Apoyo en casa", "tipo": "casa",
            "descripcion": "Necesito ayuda en mi casa",
            "fecha": date.today().isoformat(),
            "hora_inicio": "10:00", "hora_fin": "11:00",
            "solicitante_id": owner["id"],
        },
    )
    assert created.status_code == 201
    relief_id = created.json()["id"]
    assert api_client.get("/api/v1/relevos/disponibles").status_code == 401
    available = api_client.get("/api/v1/relevos/disponibles", headers=helper_headers)
    assert available.status_code == 200
    assert [item["id"] for item in available.json()] == [relief_id]
    assert api_client.get("/api/v1/relevos/disponibles", headers=outsider_headers).json() == []
    assert api_client.get("/api/v1/relevos/disponibles", headers=owner_headers).json() == []
    assert api_client.patch(
        f"/api/v1/relevos/{relief_id}", headers=helper_headers,
        json={"estado": "aceptada", "cuidador_id": helper["id"]},
    ).status_code == 200
    assert api_client.get("/api/v1/relevos/disponibles", headers=helper_headers).json() == []
    invalid = api_client.patch(
        f"/api/v1/relevos/{relief_id}", headers=helper_headers,
        json={"estado": "completada", "cuidador_id": outsider["id"]},
    )
    assert invalid.status_code == 400
    completed = api_client.patch(
        f"/api/v1/relevos/{relief_id}", headers=helper_headers,
        json={"estado": "completada"},
    )
    assert completed.status_code == 200
    assert completed.json()["cuidador_id"] == helper["id"]


def test_solicitante_cancela_relevo_aceptado_y_notifica_al_cuidador(api_client):
    from datetime import date

    solicitante = _register_test_user(api_client, "cancela-owner@example.com").json()
    cuidador = _register_test_user(api_client, "cancela-helper@example.com").json()
    otro = _register_test_user(api_client, "cancela-otro@example.com").json()
    headers_solicitante = {
        "Authorization": f"Bearer {_login_test_user(api_client, 'cancela-owner@example.com').json()['access_token']}"
    }
    headers_cuidador = {
        "Authorization": f"Bearer {_login_test_user(api_client, 'cancela-helper@example.com').json()['access_token']}"
    }
    headers_otro = {
        "Authorization": f"Bearer {_login_test_user(api_client, 'cancela-otro@example.com').json()['access_token']}"
    }

    vinculo = api_client.post(
        f"/api/v1/contactos/usuarios/{solicitante['id']}/por-codigo",
        headers=headers_solicitante,
        json={"codigo_unico": cuidador["codigo_unico"], "relacion": "Amigo"},
    )
    assert vinculo.status_code == 201
    creado = api_client.post(
        "/api/v1/relevos",
        headers=headers_solicitante,
        json={
            "titulo": "Apoyo en casa",
            "tipo": "casa",
            "descripcion": "Necesito ayuda en mi casa",
            "fecha": date.today().isoformat(),
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "solicitante_id": solicitante["id"],
        },
    )
    relevo_id = creado.json()["id"]
    aceptado = api_client.patch(
        f"/api/v1/relevos/{relevo_id}",
        headers=headers_cuidador,
        json={"estado": "aceptada", "cuidador_id": cuidador["id"]},
    )
    assert aceptado.status_code == 200

    assert api_client.post(f"/api/v1/relevos/{relevo_id}/cancelar").status_code == 401
    ajeno = api_client.post(
        f"/api/v1/relevos/{relevo_id}/cancelar",
        headers=headers_otro,
    )
    assert ajeno.status_code == 404
    cancelado = api_client.post(
        f"/api/v1/relevos/{relevo_id}/cancelar",
        headers=headers_solicitante,
    )
    assert cancelado.status_code == 200
    assert cancelado.json()["resultado"] == "eliminada"
    assert api_client.get(
        f"/api/v1/relevos/usuarios/{solicitante['id']}",
        headers=headers_solicitante,
    ).json() == []
    notificacion = api_client.get(
        "/api/v1/notificaciones",
        headers=headers_cuidador,
    ).json()
    assert [item["mensaje"] for item in notificacion] == [
        "La persona que solicitó el relevo canceló la solicitud. "
        "Ya no necesitas cubrirla."
    ]


def test_cuidador_cancela_aceptacion_reabre_relevo_y_notifica(api_client):
    from datetime import date

    solicitante = _register_test_user(api_client, "reopen-owner@example.com").json()
    cuidador = _register_test_user(api_client, "reopen-helper@example.com").json()
    headers_solicitante = {
        "Authorization": f"Bearer {_login_test_user(api_client, 'reopen-owner@example.com').json()['access_token']}"
    }
    headers_cuidador = {
        "Authorization": f"Bearer {_login_test_user(api_client, 'reopen-helper@example.com').json()['access_token']}"
    }

    vinculo = api_client.post(
        f"/api/v1/contactos/usuarios/{solicitante['id']}/por-codigo",
        headers=headers_solicitante,
        json={"codigo_unico": cuidador["codigo_unico"], "relacion": "Amigo"},
    )
    assert vinculo.status_code == 201
    creado = api_client.post(
        "/api/v1/relevos",
        headers=headers_solicitante,
        json={
            "titulo": "Apoyo en casa",
            "tipo": "casa",
            "descripcion": "Necesito ayuda en mi casa",
            "fecha": date.today().isoformat(),
            "hora_inicio": "10:00",
            "hora_fin": "11:00",
            "solicitante_id": solicitante["id"],
        },
    )
    relevo_id = creado.json()["id"]
    aceptado = api_client.patch(
        f"/api/v1/relevos/{relevo_id}",
        headers=headers_cuidador,
        json={"estado": "aceptada", "cuidador_id": cuidador["id"]},
    )
    assert aceptado.status_code == 200

    cancelado = api_client.post(
        f"/api/v1/relevos/{relevo_id}/cancelar",
        headers=headers_cuidador,
    )
    assert cancelado.status_code == 200
    assert cancelado.json()["resultado"] == "pendiente"
    actualizado = api_client.get(
        f"/api/v1/relevos/usuarios/{solicitante['id']}",
        headers=headers_solicitante,
    ).json()
    assert len(actualizado) == 1
    assert actualizado[0]["id"] == relevo_id
    assert actualizado[0]["estado"] == "pendiente"
    assert actualizado[0]["cuidador_id"] is None
    notificacion = api_client.get(
        "/api/v1/notificaciones",
        headers=headers_solicitante,
    ).json()
    assert [item["mensaje"] for item in notificacion] == [
        "La persona que había aceptado cubrir tu relevo canceló. "
        "La solicitud volvió a estar pendiente para que otra "
        "persona pueda aceptarla."
    ]


def test_tendencia_no_pierde_dias_con_mas_de_cien_checkins(api_client):
    from datetime import datetime, timedelta, timezone
    from app.models import CheckIn

    user = _register_test_user(api_client).json()
    token = _login_test_user(api_client).json()["access_token"]
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        db.add_all(
            CheckIn(usuario_id=user["id"], nivel="sobrepasada", fecha=now - timedelta(days=i))
            for i in (0, 1, 2)
        )
        db.add_all(
            CheckIn(usuario_id=user["id"], nivel="bien", fecha=now)
            for _ in range(101)
        )
        db.commit()
    finally:
        gen.close()
    response = api_client.get(
        "/api/v1/checkins/tendencia", headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.json() == {
        "dias_evaluados": 5, "dias_alta_carga": 3, "sugerir_pedir_apoyo": True,
    }


def test_flujo_registro_duplicado_login_y_acceso_protegido(api_client):
    created = _register_test_user(api_client)
    assert created.status_code == 201
    assert created.json()["detail"] == "Cuenta creada correctamente"
    assert "password_hash" not in created.json()
    assert re.fullmatch(r"RC-[0-9A-F]{6}", created.json()["codigo_unico"])

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
    assert login.json()["detail"] == "Inicio de sesión correcto"
    token = login.json()["access_token"]
    assert login.json()["usuario"]["correo"] == "persona@example.com"
    authorized = api_client.get(
        "/api/v1/checkins/usuarios/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert authorized.status_code == 200
    assert authorized.json() == []


def test_registro_completo_con_campos_opcionales(api_client):
    response = _registrar_y_verificar(
        api_client,
        {
            "nombre": "María González",
            "correo": "maria.ejemplo@correo.cl",
            "password": "EjemploSeguro123",
            "genero": "femenino",
            "ocupacion": "Estudiante y cuidadora",
            "persona_cuidada_nombre": "Carlos",
            "persona_cuidada_edad": 82,
        },
    )
    assert response.status_code == 201
    body = response.json()
    assert re.fullmatch(r"RC-[0-9A-F]{6}", body["codigo_unico"])
    assert body["tipo"] == "estudiante"
    assert body["genero"] == "femenino"
    assert body["persona_cuidada_edad"] == 82
    assert "password" not in body and "password_hash" not in body


def test_registro_invalido_devuelve_422(api_client):
    base = {
        "nombre": "María González",
        "correo": "maria.ejemplo@correo.cl",
        "password": "EjemploSeguro123",
    }
    for cambio in (
        {"password": "corta"},
        {"genero": "otro"},
        {"correo": "no-es-correo"},
        {"correo": "maria@correo.zzzz"},
    ):
        response = api_client.post("/api/v1/usuarios", json={**base, **cambio})
        assert response.status_code == 422, cambio


@pytest.mark.parametrize("extension", ["com", "cl", "org", "es", "xyz"])
def test_registro_acepta_extensiones_de_correo_permitidas(api_client, extension):
    response = _registrar_y_verificar(
        api_client,
        {
            "nombre": "María González",
            "correo": f"maria@correo.{extension}",
            "password": "EjemploSeguro123",
        },
    )
    assert response.status_code == 201


def test_registro_con_genero_masculino_y_sin_genero(api_client):
    base = {
        "nombre": "Pedro Soto",
        "password": "EjemploSeguro123",
    }
    masculino = _registrar_y_verificar(
        api_client,
        {**base, "correo": "pedro@correo.cl", "genero": "masculino"},
    )
    assert masculino.status_code == 201
    assert masculino.json()["genero"] == "masculino"

    sin_genero = _registrar_y_verificar(
        api_client,
        {**base, "correo": "sin.genero@correo.cl"},
    )
    assert sin_genero.status_code == 201
    assert sin_genero.json()["genero"] is None
    assert sin_genero.json()["persona_cuidada_nombre"] is None


_REGISTRO_DEMO = {
    "nombre": "Persona Demo",
    "correo": "persona@example.com",
    "password": "una-clave-segura-de-prueba",
}


def _verificar(client, registro_id, codigo):
    return client.post(
        "/api/v1/usuarios/verificar",
        json={"registro_id": registro_id, "codigo": codigo},
    )


def _codigo_distinto(codigo):
    return "000000" if codigo != "000000" else "111111"


def _modificar_registro_pendiente(correo, **cambios):
    from app.models import RegistroPendiente

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        db.query(RegistroPendiente).filter(
            RegistroPendiente.correo == correo
        ).update(cambios, synchronize_session=False)
        db.commit()
    finally:
        gen.close()


def _hace(segundos):
    from datetime import datetime, timedelta, timezone

    return datetime.now(timezone.utc).replace(tzinfo=None) - timedelta(
        seconds=segundos
    )


def test_registro_no_crea_cuenta_hasta_verificar_codigo(api_client):
    solicitud = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO)
    assert solicitud.status_code == 202
    body = solicitud.json()
    assert body["correo"] == "persona@example.com"
    assert body["expira_en_minutos"] == 35
    assert body["reenviar_en_segundos"] == 60
    assert _login_test_user(api_client).status_code == 401

    codigo = api_client.codigos_enviados["persona@example.com"]
    assert re.fullmatch(r"\d{6}", codigo)
    assert _verificar(api_client, body["registro_id"], "12345").status_code == 422
    fallido = _verificar(api_client, body["registro_id"], _codigo_distinto(codigo))
    assert fallido.status_code == 400
    assert fallido.json()["detail"] == "Código incorrecto. Te quedan 3 intentos"

    verificado = _verificar(api_client, body["registro_id"], codigo)
    assert verificado.status_code == 201
    assert verificado.json()["correo"] == "persona@example.com"
    assert _login_test_user(api_client).status_code == 200
    assert _verificar(api_client, body["registro_id"], codigo).status_code == 404


def test_cuatro_intentos_fallidos_invalidan_codigo_hasta_reenviarlo(api_client):
    registro_id = api_client.post(
        "/api/v1/usuarios", json=_REGISTRO_DEMO
    ).json()["registro_id"]
    codigo = api_client.codigos_enviados["persona@example.com"]

    fallidos = [
        _verificar(api_client, registro_id, _codigo_distinto(codigo)).status_code
        for _ in range(4)
    ]
    assert fallidos == [400, 400, 400, 429]
    assert _verificar(api_client, registro_id, codigo).status_code == 429

    reenvio_temprano = api_client.post(
        "/api/v1/usuarios/reenviar-codigo",
        json={"registro_id": registro_id},
    )
    assert reenvio_temprano.status_code == 429
    assert "Retry-After" in reenvio_temprano.headers

    _modificar_registro_pendiente("persona@example.com", enviado_en=_hace(61))
    reenvio = api_client.post(
        "/api/v1/usuarios/reenviar-codigo",
        json={"registro_id": registro_id},
    )
    assert reenvio.status_code == 202
    nuevo_codigo = api_client.codigos_enviados["persona@example.com"]
    assert _verificar(api_client, registro_id, nuevo_codigo).status_code == 201


def test_codigo_vencido_no_crea_cuenta(api_client):
    registro_id = api_client.post(
        "/api/v1/usuarios", json=_REGISTRO_DEMO
    ).json()["registro_id"]
    codigo = api_client.codigos_enviados["persona@example.com"]
    _modificar_registro_pendiente("persona@example.com", expira_en=_hace(1))

    vencido = _verificar(api_client, registro_id, codigo)
    assert vencido.status_code == 410
    assert _login_test_user(api_client).status_code == 401


def test_codigo_expira_exactamente_a_los_35_minutos(api_client):
    from datetime import datetime, timedelta
    from unittest.mock import patch

    inicio = datetime(2026, 11, 22, 12)
    with patch("app.models.usuarios.model.utc_now_naive", return_value=inicio):
        solicitud = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO)
    codigo = api_client.codigos_enviados["persona@example.com"]
    with patch(
        "app.models.usuarios.model.utc_now_naive",
        return_value=inicio + timedelta(minutes=35),
    ):
        assert _verificar(api_client, solicitud.json()["registro_id"], codigo).status_code == 410


def test_verificacion_rechaza_digitos_no_ascii_sin_consumir_intentos(api_client):
    registro_id = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO).json()["registro_id"]
    for _ in range(4):
        assert _verificar(api_client, registro_id, "\uff11\uff12\uff13\uff14\uff15\uff16").status_code == 422
    assert _verificar(api_client, registro_id, api_client.codigos_enviados["persona@example.com"]).status_code == 201


def test_registro_envia_codigo_solo_al_destinatario_y_lo_verifica(api_client, monkeypatch):
    from unittest.mock import patch
    from app.correo import enviar_codigo_verificacion

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "remitente@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "clave-de-prueba")
    monkeypatch.delenv("SMTP_FROM", raising=False)
    with patch(
        "app.models.usuarios.model.enviar_codigo_verificacion",
        side_effect=enviar_codigo_verificacion,
    ), patch("app.correo.enviador.smtplib.SMTP") as smtp_class:
        solicitud = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO)
    assert solicitud.status_code == 202
    smtp = smtp_class.return_value.__enter__.return_value
    smtp.send_message.assert_called_once()
    mensaje = smtp.send_message.call_args.args[0]
    assert mensaje.get_all("To") == ["persona@example.com"]
    assert mensaje["Cc"] is None and mensaje["Bcc"] is None
    codigo = re.search(r"\b([0-9]{6})\b", mensaje.get_content()).group(1)
    assert "codigo" not in solicitud.json()
    assert _login_test_user(api_client).status_code == 401
    assert _verificar(api_client, solicitud.json()["registro_id"], codigo).status_code == 201
    assert _login_test_user(api_client).status_code == 200


def test_nuevo_registro_con_el_mismo_correo_invalida_el_anterior(api_client):
    primero = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO)
    assert primero.status_code == 202
    assert api_client.post(
        "/api/v1/usuarios", json=_REGISTRO_DEMO
    ).status_code == 429

    _modificar_registro_pendiente("persona@example.com", enviado_en=_hace(61))
    segundo = api_client.post(
        "/api/v1/usuarios",
        json={**_REGISTRO_DEMO, "password": "otra-clave-segura-de-prueba"},
    )
    assert segundo.status_code == 202
    codigo = api_client.codigos_enviados["persona@example.com"]

    assert _verificar(
        api_client, primero.json()["registro_id"], codigo
    ).status_code == 404
    assert _verificar(
        api_client, segundo.json()["registro_id"], codigo
    ).status_code == 201


def test_registro_no_queda_pendiente_si_falla_el_envio_del_correo(api_client):
    from unittest.mock import patch
    from app.correo import CorreoNoEnviadoError

    with patch(
        "app.models.usuarios.model.enviar_codigo_verificacion",
        side_effect=CorreoNoEnviadoError("SMTP caído"),
    ):
        fallido = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO)
    assert fallido.status_code == 503

    reintento = api_client.post("/api/v1/usuarios", json=_REGISTRO_DEMO)
    assert reintento.status_code == 202


def test_enviador_smtp_usa_starttls_y_envia_el_codigo(monkeypatch):
    from unittest.mock import patch
    from app.correo import CorreoNoEnviadoError, enviar_codigo_verificacion

    monkeypatch.setenv("SMTP_HOST", "smtp.example.com")
    monkeypatch.setenv("SMTP_PORT", "587")
    monkeypatch.setenv("SMTP_USER", "remitente@example.com")
    monkeypatch.setenv("SMTP_PASSWORD", "clave-de-aplicacion")
    monkeypatch.delenv("SMTP_FROM", raising=False)
    with patch("app.correo.enviador.smtplib.SMTP") as smtp_class:
        enviar_codigo_verificacion("destino@example.com", "123456", 35)

    smtp = smtp_class.return_value.__enter__.return_value
    smtp.starttls.assert_called_once()
    smtp.login.assert_called_once_with(
        "remitente@example.com",
        "clave-de-aplicacion",
    )
    mensaje = smtp.send_message.call_args.args[0]
    assert mensaje["To"] == "destino@example.com"
    assert mensaje["From"] == "remitente@example.com"
    assert "123456" in mensaje.get_content()

    monkeypatch.delenv("SMTP_HOST")
    with pytest.raises(CorreoNoEnviadoError):
        enviar_codigo_verificacion("destino@example.com", "123456", 35)


@pytest.mark.parametrize("edad", [-1, 131])
def test_registro_con_edad_fuera_de_rango_devuelve_422(api_client, edad):
    response = api_client.post(
        "/api/v1/usuarios",
        json={
            "nombre": "María González",
            "correo": "maria.ejemplo@correo.cl",
            "password": "EjemploSeguro123",
            "persona_cuidada_nombre": "Carlos",
            "persona_cuidada_edad": edad,
        },
    )
    assert response.status_code == 422


def test_login_posterior_al_logout_emite_token_que_funciona(api_client):
    created = _register_test_user(api_client)
    url = f"/api/v1/checkins/usuarios/{created.json()['id']}"
    viejo = _login_test_user(api_client).json()["access_token"]
    viejo_headers = {"Authorization": f"Bearer {viejo}"}

    assert api_client.post("/api/v1/auth/logout", headers=viejo_headers).status_code == 200

    nuevo = _login_test_user(api_client)
    assert nuevo.status_code == 200
    nuevo_headers = {"Authorization": f"Bearer {nuevo.json()['access_token']}"}
    assert api_client.get(url, headers=nuevo_headers).status_code == 200
    assert api_client.get(url, headers=viejo_headers).status_code == 401


def test_logout_incrementa_la_version_una_vez_por_cierre(api_client):
    from app.models import Usuario

    created = _register_test_user(api_client)
    user_id = created.json()["id"]
    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        for esperado in (1, 2):
            token = _login_test_user(api_client).json()["access_token"]
            headers = {"Authorization": f"Bearer {token}"}
            assert api_client.post("/api/v1/auth/logout", headers=headers).status_code == 200
            db.expire_all()
            assert db.get(Usuario, user_id).token_version == esperado
    finally:
        gen.close()


def test_token_de_usuario_eliminado_devuelve_401(api_client):
    from app.models import Usuario

    created = _register_test_user(api_client)
    user_id = created.json()["id"]
    token = _login_test_user(api_client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        db.delete(db.get(Usuario, user_id))
        db.commit()
    finally:
        gen.close()

    protected = api_client.get(f"/api/v1/checkins/usuarios/{user_id}", headers=headers)
    assert protected.status_code == 401
    assert api_client.post("/api/v1/auth/logout", headers=headers).status_code == 401


def test_borrado_cuenta_notifica_relevo_y_limpia_solo_datos_relacionados(api_client):
    from datetime import date

    from app.models import (
        AlertaSOS,
        CheckIn,
        ContactoConfianza,
        Notificacion,
        SolicitudRelevo,
        Usuario,
    )

    solicitante = _register_test_user(api_client, "solicitante@example.com").json()["id"]
    cuidador = _register_test_user(api_client, "cuidador@example.com").json()["id"]
    otro = _register_test_user(api_client, "otro@example.com").json()["id"]
    token_cuidador = _login_test_user(api_client, "cuidador@example.com").json()["access_token"]
    token_solicitante = _login_test_user(api_client, "solicitante@example.com").json()["access_token"]
    token_otro = _login_test_user(api_client, "otro@example.com").json()["access_token"]

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        db.add_all(
            [
                CheckIn(usuario_id=solicitante, nivel="bien"),
                CheckIn(usuario_id=cuidador, nivel="bien"),
                CheckIn(usuario_id=otro, nivel="bien"),
                AlertaSOS(usuario_id=solicitante, mensaje="Prueba"),
                ContactoConfianza(
                    usuario_id=solicitante,
                    contacto_usuario_id=cuidador,
                    nombre="Cuidador",
                    relacion="Amigo",
                    apoyos="",
                    disponibilidad="",
                ),
                ContactoConfianza(
                    usuario_id=otro,
                    contacto_usuario_id=None,
                    nombre="Contacto ajeno",
                    relacion="Amigo",
                    apoyos="",
                    disponibilidad="",
                ),
                SolicitudRelevo(
                    titulo="Relevo aceptado",
                    tipo="casa",
                    descripcion="Apoyo",
                    fecha=date.today(),
                    hora_inicio="10:00",
                    hora_fin="11:00",
                    estado="aceptada",
                    solicitante_id=solicitante,
                    cuidador_id=cuidador,
                ),
                SolicitudRelevo(
                    titulo="Solicitud ajena",
                    tipo="casa",
                    descripcion="Apoyo",
                    fecha=date.today(),
                    hora_inicio="12:00",
                    hora_fin="13:00",
                    estado="pendiente",
                    solicitante_id=otro,
                ),
            ]
        )
        db.commit()
    finally:
        gen.close()

    sin_token = api_client.get("/api/v1/notificaciones")
    assert sin_token.status_code == 401
    headers_cuidador = {"Authorization": f"Bearer {token_cuidador}"}
    borrado = api_client.delete("/api/v1/perfil/me", headers=headers_cuidador)
    assert borrado.status_code == 204

    headers_solicitante = {"Authorization": f"Bearer {token_solicitante}"}
    pendientes = api_client.get("/api/v1/notificaciones", headers=headers_solicitante)
    assert pendientes.status_code == 200
    assert pendientes.json()[0]["mensaje"] == (
        "La persona que iba a cubrir tu relevo eliminó su cuenta. "
        "El relevo ya no está disponible."
    )
    notificacion_id = pendientes.json()[0]["id"]

    headers_otro = {"Authorization": f"Bearer {token_otro}"}
    assert api_client.patch(
        f"/api/v1/notificaciones/{notificacion_id}/leida",
        headers=headers_otro,
    ).status_code == 404
    marcada = api_client.patch(
        f"/api/v1/notificaciones/{notificacion_id}/leida",
        headers=headers_solicitante,
    )
    assert marcada.status_code == 200
    assert marcada.json()["leida"] is True
    assert api_client.get("/api/v1/notificaciones", headers=headers_solicitante).json() == []

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        assert db.query(Usuario).count() == 2
        assert db.query(CheckIn).filter(CheckIn.usuario_id == cuidador).count() == 0
        assert db.query(CheckIn).filter(CheckIn.usuario_id == solicitante).count() == 1
        assert db.query(CheckIn).filter(CheckIn.usuario_id == otro).count() == 1
        assert db.query(AlertaSOS).filter(AlertaSOS.usuario_id == solicitante).count() == 1
        assert db.query(ContactoConfianza).count() == 1
        assert db.query(SolicitudRelevo).count() == 1
        assert db.query(Notificacion).filter(Notificacion.usuario_id == solicitante).one().leida
    finally:
        gen.close()


def test_borrado_solicitante_avisa_a_quien_habia_aceptado(api_client):
    from datetime import date

    from app.models import SolicitudRelevo, Usuario

    solicitante = _register_test_user(api_client, "solicitante2@example.com").json()["id"]
    cuidador = _register_test_user(api_client, "cuidador2@example.com").json()["id"]
    token_solicitante = _login_test_user(
        api_client,
        "solicitante2@example.com",
    ).json()["access_token"]
    token_cuidador = _login_test_user(
        api_client,
        "cuidador2@example.com",
    ).json()["access_token"]

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        db.add(
            SolicitudRelevo(
                titulo="Relevo aceptado",
                tipo="casa",
                descripcion="Apoyo",
                fecha=date.today(),
                hora_inicio="10:00",
                hora_fin="11:00",
                estado="aceptada",
                solicitante_id=solicitante,
                cuidador_id=cuidador,
            )
        )
        db.commit()
    finally:
        gen.close()

    respuesta = api_client.delete(
        "/api/v1/perfil/me",
        headers={"Authorization": f"Bearer {token_solicitante}"},
    )
    assert respuesta.status_code == 204
    assert api_client.get(
        "/api/v1/notificaciones",
        headers={"Authorization": f"Bearer {token_cuidador}"},
    ).json()[0]["mensaje"] == (
        "La persona que solicitó el relevo eliminó su cuenta. "
        "El relevo que habías aceptado ya no está disponible."
    )

    gen = app.dependency_overrides[get_db]()
    db = next(gen)
    try:
        assert db.query(Usuario).filter(Usuario.id == solicitante).one_or_none() is None
        assert db.query(SolicitudRelevo).count() == 0
    finally:
        gen.close()


def test_token_sin_claim_ver_se_trata_como_version_cero(api_client):
    import os
    from datetime import datetime, timedelta, timezone

    from jose import jwt

    created = _register_test_user(api_client)
    user_id = created.json()["id"]
    token = jwt.encode(
        {
            "sub": str(user_id),
            "exp": datetime.now(timezone.utc) + timedelta(minutes=5),
        },
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )
    headers = {"Authorization": f"Bearer {token}"}
    url = f"/api/v1/checkins/usuarios/{user_id}"
    assert api_client.get(url, headers=headers).status_code == 200

    assert api_client.post("/api/v1/auth/logout", headers=headers).status_code == 200
    assert api_client.get(url, headers=headers).status_code == 401


def test_logout_revoca_el_token_y_devuelve_confirmacion(api_client):
    created = _register_test_user(api_client)
    token = _login_test_user(api_client).json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    protected_url = f"/api/v1/checkins/usuarios/{created.json()['id']}"

    assert api_client.get(protected_url, headers=headers).status_code == 200

    logout = api_client.post("/api/v1/auth/logout", headers=headers)
    assert logout.status_code == 200
    assert logout.json() == {"detail": "Sesión cerrada correctamente"}

    assert api_client.get(protected_url, headers=headers).status_code == 401
    assert api_client.post("/api/v1/auth/logout", headers=headers).status_code == 401


def test_logout_sin_token_devuelve_401(api_client):
    response = api_client.post("/api/v1/auth/logout")
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_token_vencido_devuelve_401(api_client):
    from datetime import datetime, timedelta, timezone
    import os

    from jose import jwt

    token = jwt.encode(
        {
            "sub": "1",
            "ver": 0,
            "exp": datetime.now(timezone.utc) - timedelta(seconds=1),
        },
        os.environ["JWT_SECRET"],
        algorithm="HS256",
    )
    response = api_client.get(
        "/api/v1/checkins/usuarios/1",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 401


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

    from app.api.routes import _dias_de_alta_carga

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