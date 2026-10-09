from datetime import date, datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db
from .security import (
    ACCESS_TOKEN_SECONDS,
    create_access_token,
    get_current_user,
    hash_password,
    verify_password,
)
from .state_transitions import TRANSICIONES_RELEVO, TRANSICIONES_SOS


router_usuarios = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"],
)

router_checkins = APIRouter(
    prefix="/api/v1/checkins",
    tags=["Mi carga / Check-in"],
)

router_contactos = APIRouter(
    prefix="/api/v1/contactos",
    tags=["Red de confianza"],
)

router_relevos = APIRouter(
    prefix="/api/v1/relevos",
    tags=["Solicitudes y calendario"],
)

router_sos = APIRouter(
    prefix="/api/v1/sos",
    tags=["SOS"],
)

router_auth = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"],
)

router_perfil = APIRouter(
    prefix="/api/v1/perfil",
    tags=["Perfil"],
)


def _commit_or_conflict(db: Session, detail: str) -> None:
    """Confirma la transacción y convierte conflictos de datos en HTTP 400."""
    try:
        db.commit()
    except IntegrityError as exc:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from exc


def _duracion_horas(solicitud: models.SolicitudRelevo) -> float:
    inicio_hora, inicio_minuto = map(int, solicitud.hora_inicio.split(":"))
    fin_hora, fin_minuto = map(int, solicitud.hora_fin.split(":"))
    minutos = (fin_hora * 60 + fin_minuto) - (inicio_hora * 60 + inicio_minuto)
    return max(minutos, 0) / 60


def _dias_de_alta_carga(checkins, hoy: date) -> int:
    inicio = hoy - timedelta(days=4)
    dias = {
        checkin.fecha.date()
        for checkin in checkins
        if checkin.nivel in {"necesito_apoyo", "sobrepasada"}
        and inicio <= checkin.fecha.date() <= hoy
    }
    return len(dias)


# ---------- Usuarios ----------

@router_usuarios.post(
    "",
    response_model=schemas.UsuarioOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_usuario(
    datos: schemas.UsuarioIn,
    db: Session = Depends(get_db),
):
    usuario_existente = (
        db.query(models.Usuario)
        .filter(models.Usuario.correo == datos.correo)
        .first()
    )

    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya está registrado",
        )

    valores = datos.model_dump(exclude={"password"})
    usuario = models.Usuario(
        **valores,
        password_hash=hash_password(datos.password),
    )

    db.add(usuario)
    _commit_or_conflict(db, "El correo o el código de usuario ya está en uso")
    db.refresh(usuario)

    return usuario


@router_auth.post(
    "/login",
    response_model=schemas.TokenOut,
)
def iniciar_sesion(
    datos: schemas.LoginIn,
    db: Session = Depends(get_db),
):
    usuario = (
        db.query(models.Usuario)
        .filter(models.Usuario.correo == datos.correo)
        .first()
    )
    password_hash = usuario.password_hash if usuario is not None else None
    password_valid = verify_password(datos.password, password_hash)
    if usuario is None or not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Correo o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return schemas.TokenOut(
        access_token=create_access_token(usuario.id),
        expires_in=ACCESS_TOKEN_SECONDS,
        usuario=usuario,
    )


@router_perfil.patch(
    "/me",
    response_model=schemas.UsuarioOut,
)
def actualizar_mi_perfil(
    datos: schemas.PerfilUpdate,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    cambios = datos.model_dump(exclude_unset=True)
    if not cambios:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debes enviar al menos un campo para actualizar",
        )

    for campo, valor in cambios.items():
        setattr(current_user, campo, valor)

    _commit_or_conflict(db, "No se pudo actualizar el perfil por un conflicto de datos")
    db.refresh(current_user)
    return current_user


# ---------- Mi carga / Check-in ----------

@router_checkins.get(
    "/tendencia",
    response_model=schemas.TendenciaCargaOut,
)
def consultar_tendencia_carga(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ahora = datetime.now(timezone.utc).replace(tzinfo=None)
    fecha_inicio = ahora.date() - timedelta(days=4)
    fecha_inicio_utc = datetime.combine(fecha_inicio, datetime.min.time())
    checkins = (
        db.query(models.CheckIn)
        .filter(
            models.CheckIn.usuario_id == current_user.id,
            models.CheckIn.fecha >= fecha_inicio_utc,
            models.CheckIn.fecha <= ahora,
        )
        .order_by(models.CheckIn.fecha.desc(), models.CheckIn.id.desc())
        .limit(100)
        .all()
    )
    dias_alta_carga = _dias_de_alta_carga(checkins, ahora.date())
    return {
        "dias_evaluados": 5,
        "dias_alta_carga": dias_alta_carga,
        "sugerir_pedir_apoyo": dias_alta_carga >= 3,
    }

@router_checkins.post(
    "/usuarios/{usuario_id}",
    response_model=schemas.CheckInOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_checkin(
    usuario_id: int,
    datos: schemas.CheckInIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    checkin = models.CheckIn(
        **datos.model_dump(),
        usuario_id=usuario_id,
    )

    db.add(checkin)
    _commit_or_conflict(db, "No se pudo guardar el check-in por un conflicto de datos")
    db.refresh(checkin)

    return checkin


@router_checkins.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.CheckInOut],
)
def listar_checkins(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.CheckIn)
        .filter(models.CheckIn.usuario_id == usuario_id)
        .order_by(models.CheckIn.fecha.desc(), models.CheckIn.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# ---------- Red de confianza ----------

@router_contactos.post(
    "/usuarios/{usuario_id}",
    response_model=schemas.ContactoConfianzaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_contacto(
    usuario_id: int,
    datos: schemas.ContactoConfianzaIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    contacto = models.ContactoConfianza(
        **datos.model_dump(),
        usuario_id=usuario_id,
    )

    db.add(contacto)
    _commit_or_conflict(db, "No se pudo guardar el contacto por un conflicto de datos")
    db.refresh(contacto)

    return contacto


@router_contactos.post(
    "/usuarios/{usuario_id}/por-codigo",
    response_model=schemas.ContactoConfianzaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_contacto_por_codigo(
    usuario_id: int,
    datos: schemas.ContactoPorCodigoIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    propietario = db.get(models.Usuario, usuario_id)

    if propietario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    usuario_contacto = (
        db.query(models.Usuario)
        .filter(models.Usuario.codigo_unico == datos.codigo_unico)
        .first()
    )

    if usuario_contacto is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No existe un usuario asociado a ese código",
        )

    if usuario_contacto.id == usuario_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes añadirte a tu propia red de confianza",
        )

    contacto_existente = (
        db.query(models.ContactoConfianza)
        .filter(
            models.ContactoConfianza.usuario_id == usuario_id,
            models.ContactoConfianza.contacto_usuario_id
            == usuario_contacto.id,
        )
        .first()
    )

    if contacto_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta persona ya pertenece a tu red de confianza",
        )

    contacto = models.ContactoConfianza(
        nombre=usuario_contacto.nombre,
        relacion=datos.relacion,
        apoyos=datos.apoyos or "",
        disponibilidad=datos.disponibilidad or "",
        usuario_id=usuario_id,
        contacto_usuario_id=usuario_contacto.id,
    )

    db.add(contacto)
    _commit_or_conflict(db, "El contacto ya existe o hay un conflicto de datos")
    db.refresh(contacto)

    return contacto


@router_contactos.get(
    "/usuarios/{usuario_id}/balance",
    response_model=schemas.BalanceRedOut,
)
def obtener_balance_red(
    usuario_id: int,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    hoy = date.today()
    desde = hoy.replace(day=1)
    contactos = (
        db.query(models.ContactoConfianza)
        .filter(models.ContactoConfianza.usuario_id == usuario_id)
        .order_by(models.ContactoConfianza.id.asc())
        .all()
    )
    ids_red = {
        contacto.contacto_usuario_id
        for contacto in contactos
        if contacto.contacto_usuario_id is not None
    }

    horas_por_usuario: dict[int, float] = {}
    if ids_red:
        solicitudes = (
            db.query(models.SolicitudRelevo)
            .filter(
                models.SolicitudRelevo.solicitante_id == usuario_id,
                models.SolicitudRelevo.cuidador_id.in_(ids_red),
                models.SolicitudRelevo.estado == "completada",
                models.SolicitudRelevo.fecha >= desde,
                models.SolicitudRelevo.fecha <= hoy,
            )
            .all()
        )
        for solicitud in solicitudes:
            cuidador_id = solicitud.cuidador_id
            if cuidador_id is not None:
                horas_por_usuario[cuidador_id] = (
                    horas_por_usuario.get(cuidador_id, 0.0)
                    + _duracion_horas(solicitud)
                )

    filas = []
    usuarios_agregados: set[int] = set()
    for contacto in contactos:
        contacto_usuario_id = contacto.contacto_usuario_id
        if contacto_usuario_id is not None and contacto_usuario_id in usuarios_agregados:
            continue
        if contacto_usuario_id is not None:
            usuarios_agregados.add(contacto_usuario_id)
        filas.append(
            {
                "contacto_id": contacto.id,
                "nombre": contacto.nombre,
                "relacion": contacto.relacion,
                "horas_apoyo": round(
                    horas_por_usuario.get(contacto_usuario_id, 0.0),
                    1,
                ),
            }
        )

    total_horas = round(sum(horas_por_usuario.values()), 1)
    for fila in filas:
        fila["porcentaje"] = (
            round(fila["horas_apoyo"] / total_horas * 100, 1)
            if total_horas
            else 0.0
        )

    return {
        "desde": desde,
        "hasta": hoy,
        "total_horas": total_horas,
        "contactos": filas,
    }


@router_contactos.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.ContactoConfianzaOut],
)
def listar_contactos(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.ContactoConfianza)
        .filter(models.ContactoConfianza.usuario_id == usuario_id)
        .order_by(models.ContactoConfianza.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )


# ---------- Solicitudes y calendario de relevos ----------

@router_relevos.get(
    "/resumen/semana",
    response_model=schemas.ResumenSemanaOut,
)
def obtener_resumen_semana(
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    hoy = date.today()
    desde = hoy - timedelta(days=hoy.weekday())
    hasta_exclusiva = desde + timedelta(days=7)
    solicitudes = (
        db.query(models.SolicitudRelevo)
        .filter(
            models.SolicitudRelevo.solicitante_id == current_user.id,
            models.SolicitudRelevo.fecha >= desde,
            models.SolicitudRelevo.fecha < hasta_exclusiva,
            models.SolicitudRelevo.estado.in_({"aceptada", "completada"}),
        )
        .all()
    )
    horas = round(sum(_duracion_horas(item) for item in solicitudes), 1)
    return {
        "desde": desde,
        "hasta": hasta_exclusiva - timedelta(days=1),
        "horas_protegidas": horas,
    }

@router_relevos.post(
    "",
    response_model=schemas.SolicitudRelevoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud_relevo(
    datos: schemas.SolicitudRelevoIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != datos.solicitante_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El solicitante no existe",
        )
    usuario = db.get(models.Usuario, datos.solicitante_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El solicitante no existe",
        )

    if datos.hora_fin <= datos.hora_inicio:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La hora de término debe ser posterior a la hora de inicio",
        )

    solicitud = models.SolicitudRelevo(**datos.model_dump())

    db.add(solicitud)
    _commit_or_conflict(db, "No se pudo guardar la solicitud por un conflicto de datos")
    db.refresh(solicitud)

    return solicitud


@router_relevos.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.SolicitudRelevoOut],
)
def listar_relevos_usuario(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.SolicitudRelevo)
        .filter(
            (models.SolicitudRelevo.solicitante_id == usuario_id)
            | (models.SolicitudRelevo.cuidador_id == usuario_id)
        )
        .order_by(
            models.SolicitudRelevo.fecha.asc(),
            models.SolicitudRelevo.hora_inicio.asc(),
            models.SolicitudRelevo.id.asc(),
        )
        .offset(offset)
        .limit(limit)
        .all()
    )


@router_relevos.patch(
    "/{relevo_id}",
    response_model=schemas.SolicitudRelevoOut,
)
def actualizar_relevo(
    relevo_id: int,
    datos: schemas.SolicitudRelevoEstadoIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    relevo = db.get(
        models.SolicitudRelevo,
        relevo_id,
        with_for_update=True,
    )

    if relevo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de relevo no encontrada",
        )

    if datos.estado == "aceptada":
        if datos.cuidador_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de relevo no encontrada",
            )
        pertenece_a_red = (
            db.query(models.ContactoConfianza.id)
            .filter(
                models.ContactoConfianza.usuario_id == relevo.solicitante_id,
                models.ContactoConfianza.contacto_usuario_id == current_user.id,
            )
            .first()
        )
        if pertenece_a_red is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Solicitud de relevo no encontrada",
            )
    elif relevo.cuidador_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de relevo no encontrada",
        )

    if datos.estado not in TRANSICIONES_RELEVO.get(relevo.estado, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición de relevo '{relevo.estado}' → '{datos.estado}' no permitida",
        )

    if datos.cuidador_id is not None:
        cuidador = db.get(models.Usuario, datos.cuidador_id)

        if cuidador is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El cuidador no existe",
            )

        if cuidador.id == relevo.solicitante_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="El solicitante no puede aceptar su propia solicitud",
            )

        relevo.cuidador_id = datos.cuidador_id

    if datos.estado == "aceptada" and relevo.cuidador_id is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Debe indicarse quién cubrirá el relevo",
        )

    relevo.estado = datos.estado

    _commit_or_conflict(db, "No se pudo actualizar la solicitud por un conflicto de datos")
    db.refresh(relevo)

    return relevo


# ---------- SOS ----------

@router_sos.post(
    "",
    response_model=schemas.AlertaSOSOut,
    status_code=status.HTTP_201_CREATED,
)
def activar_sos(
    datos: schemas.AlertaSOSIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != datos.usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, datos.usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    alerta = models.AlertaSOS(**datos.model_dump())

    db.add(alerta)
    _commit_or_conflict(db, "No se pudo crear la alerta por un conflicto de datos")
    db.refresh(alerta)

    return alerta


@router_sos.get(
    "/recibidas",
    response_model=list[schemas.AlertaSOSOut],
)
def listar_sos_recibidas(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    usuarios_de_la_red = (
        db.query(models.ContactoConfianza.usuario_id)
        .filter(
            models.ContactoConfianza.contacto_usuario_id == current_user.id
        )
    )
    return (
        db.query(models.AlertaSOS)
        .filter(
            models.AlertaSOS.usuario_id.in_(usuarios_de_la_red),
            models.AlertaSOS.estado == "activa",
        )
        .order_by(models.AlertaSOS.fecha.desc(), models.AlertaSOS.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router_sos.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.AlertaSOSOut],
)
def listar_alertas_sos(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.id != usuario_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.AlertaSOS)
        .filter(models.AlertaSOS.usuario_id == usuario_id)
        .order_by(models.AlertaSOS.fecha.desc(), models.AlertaSOS.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )


@router_sos.patch(
    "/{alerta_id}",
    response_model=schemas.AlertaSOSOut,
)
def actualizar_estado_sos(
    alerta_id: int,
    datos: schemas.AlertaSOSEstadoIn,
    current_user: models.Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    alerta = db.get(
        models.AlertaSOS,
        alerta_id,
        with_for_update=True,
    )

    if alerta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta SOS no encontrada",
        )

    if datos.estado == "atendida":
        es_propietario = alerta.usuario_id == current_user.id
        pertenece_a_red = (
            db.query(models.ContactoConfianza.id)
            .filter(
                models.ContactoConfianza.usuario_id == alerta.usuario_id,
                models.ContactoConfianza.contacto_usuario_id == current_user.id,
            )
            .first()
        )
        if not es_propietario and pertenece_a_red is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Alerta SOS no encontrada",
            )
    elif alerta.usuario_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta SOS no encontrada",
        )

    if datos.estado not in TRANSICIONES_SOS.get(alerta.estado, set()):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transición SOS '{alerta.estado}' → '{datos.estado}' no permitida",
        )

    alerta.estado = datos.estado

    _commit_or_conflict(db, "No se pudo actualizar la alerta por un conflicto de datos")
    db.refresh(alerta)

    return alerta