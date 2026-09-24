from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db


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
            status_code=status.HTTP_409_CONFLICT,
            detail="El correo ya está registrado",
        )

    usuario = models.Usuario(**datos.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)

    return usuario


@router_usuarios.get(
    "",
    response_model=list[schemas.UsuarioOut],
)
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()


@router_usuarios.get(
    "/{usuario_id}",
    response_model=schemas.UsuarioOut,
)
def obtener_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return usuario


# ---------- Mi carga / Check-in ----------

@router_checkins.post(
    "/usuarios/{usuario_id}",
    response_model=schemas.CheckInOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_checkin(
    usuario_id: int,
    datos: schemas.CheckInIn,
    db: Session = Depends(get_db),
):
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
    db.commit()
    db.refresh(checkin)

    return checkin


@router_checkins.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.CheckInOut],
)
def listar_checkins(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.CheckIn)
        .filter(models.CheckIn.usuario_id == usuario_id)
        .order_by(models.CheckIn.fecha.desc())
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
    db: Session = Depends(get_db),
):
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
    db.commit()
    db.refresh(contacto)

    return contacto


@router_contactos.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.ContactoConfianzaOut],
)
def listar_contactos(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.ContactoConfianza)
        .filter(models.ContactoConfianza.usuario_id == usuario_id)
        .all()
    )


# ---------- Solicitudes y calendario de relevos ----------

@router_relevos.post(
    "",
    response_model=schemas.SolicitudRelevoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud_relevo(
    datos: schemas.SolicitudRelevoIn,
    db: Session = Depends(get_db),
):
    usuario = db.get(models.Usuario, datos.solicitante_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El solicitante no existe",
        )

    solicitud = models.SolicitudRelevo(**datos.model_dump())

    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)

    return solicitud


@router_relevos.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.SolicitudRelevoOut],
)
def listar_relevos_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
):
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
        .order_by(models.SolicitudRelevo.fecha.asc())
        .all()
    )


@router_relevos.patch(
    "/{relevo_id}",
    response_model=schemas.SolicitudRelevoOut,
)
def actualizar_relevo(
    relevo_id: int,
    datos: schemas.SolicitudRelevoEstadoIn,
    db: Session = Depends(get_db),
):
    relevo = db.get(models.SolicitudRelevo, relevo_id)

    if relevo is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Solicitud de relevo no encontrada",
        )

    if datos.cuidador_id is not None:
        cuidador = db.get(models.Usuario, datos.cuidador_id)

        if cuidador is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="El cuidador no existe",
            )

        relevo.cuidador_id = datos.cuidador_id

    relevo.estado = datos.estado

    db.commit()
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
    db: Session = Depends(get_db),
):
    usuario = db.get(models.Usuario, datos.usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    alerta = models.AlertaSOS(**datos.model_dump())

    db.add(alerta)
    db.commit()
    db.refresh(alerta)

    return alerta


@router_sos.get(
    "/usuarios/{usuario_id}",
    response_model=list[schemas.AlertaSOSOut],
)
def listar_alertas_sos(
    usuario_id: int,
    db: Session = Depends(get_db),
):
    usuario = db.get(models.Usuario, usuario_id)

    if usuario is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado",
        )

    return (
        db.query(models.AlertaSOS)
        .filter(models.AlertaSOS.usuario_id == usuario_id)
        .order_by(models.AlertaSOS.fecha.desc())
        .all()
    )


@router_sos.patch(
    "/{alerta_id}",
    response_model=schemas.AlertaSOSOut,
)
def actualizar_estado_sos(
    alerta_id: int,
    datos: schemas.AlertaSOSEstadoIn,
    db: Session = Depends(get_db),
):
    alerta = db.get(models.AlertaSOS, alerta_id)

    if alerta is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alerta SOS no encontrada",
        )

    alerta.estado = datos.estado

    db.commit()
    db.refresh(alerta)

    return alerta