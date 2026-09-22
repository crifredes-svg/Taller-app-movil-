from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from . import models, schemas
from .database import get_db

router_usuarios = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"])
router_solicitudes = APIRouter(prefix="/api/v1/solicitudes", tags=["Solicitudes"])


# ---------- Usuarios ----------

@router_usuarios.post("", response_model=schemas.UsuarioOut, status_code=status.HTTP_201_CREATED)
def crear_usuario(datos: schemas.UsuarioIn, db: Session = Depends(get_db)):
    """Registra un usuario. Devuelve 409 si el correo ya existe."""
    existe = db.query(models.Usuario).filter(models.Usuario.correo == datos.correo).first()
    if existe:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="El correo ya está registrado")
    usuario = models.Usuario(**datos.model_dump())
    db.add(usuario)
    db.commit()
    db.refresh(usuario)
    return usuario


@router_usuarios.get("", response_model=list[schemas.UsuarioOut])
def listar_usuarios(db: Session = Depends(get_db)):
    """Lista todos los usuarios. 200 OK."""
    return db.query(models.Usuario).all()


@router_usuarios.get("/{usuario_id}", response_model=schemas.UsuarioOut)
def obtener_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Obtiene un usuario por id. Devuelve 404 si no existe."""
    usuario = db.get(models.Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    return usuario


@router_usuarios.post("/{usuario_id}/estados", response_model=schemas.EstadoOut, status_code=status.HTTP_201_CREATED)
def registrar_estado(usuario_id: int, datos: schemas.EstadoIn, db: Session = Depends(get_db)):
    """Guarda el check-in de bienestar. 404 si el usuario no existe."""
    usuario = db.get(models.Usuario, usuario_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado")
    estado = models.EstadoBienestar(**datos.model_dump(), usuario_id=usuario_id)
    db.add(estado)
    db.commit()
    db.refresh(estado)
    return estado


# ---------- Solicitudes ----------

@router_solicitudes.post("", response_model=schemas.SolicitudOut, status_code=status.HTTP_201_CREATED)
def crear_solicitud(datos: schemas.SolicitudIn, db: Session = Depends(get_db)):
    """Crea una solicitud de apoyo. 404 si el solicitante no existe."""
    usuario = db.get(models.Usuario, datos.solicitante_id)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El solicitante no existe")
    solicitud = models.SolicitudApoyo(descripcion=datos.descripcion, solicitante_id=datos.solicitante_id)
    db.add(solicitud)
    db.commit()
    db.refresh(solicitud)
    return solicitud


@router_solicitudes.get("", response_model=list[schemas.SolicitudOut])
def listar_solicitudes(db: Session = Depends(get_db)):
    """Lista todas las solicitudes, las más nuevas primero."""
    return db.query(models.SolicitudApoyo).order_by(models.SolicitudApoyo.fecha_creacion.desc()).all()


@router_solicitudes.patch("/{solicitud_id}", response_model=schemas.SolicitudOut)
def actualizar_estado_solicitud(solicitud_id: int, datos: schemas.SolicitudEstadoIn, db: Session = Depends(get_db)):
    """Acepta, rechaza o completa una solicitud. 404 si no existe, 409 si ya está completada."""
    solicitud = db.get(models.SolicitudApoyo, solicitud_id)
    if solicitud is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitud no encontrada")
    if solicitud.estado == "completada":
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="La solicitud ya está completada")
    solicitud.estado = datos.estado
    db.commit()
    db.refresh(solicitud)
    return solicitud