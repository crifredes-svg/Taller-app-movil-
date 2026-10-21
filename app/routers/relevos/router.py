"""Relief-request routes and HTTP controller."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...models.relevos.model import actualizar_relevo as ejecutar_actualizar_relevo
from ...models.relevos.model import crear_solicitud_relevo as ejecutar_crear_solicitud_relevo
from ...models.relevos.model import listar_relevos_usuario as ejecutar_listar_relevos_usuario
from ...models.relevos.model import obtener_resumen_semana as ejecutar_obtener_resumen_semana
from ...views.relevos.view import (
    ResumenSemanaOut,
    SolicitudRelevoEstadoIn,
    SolicitudRelevoIn,
    SolicitudRelevoOut,
)

router_relevos = APIRouter(
    prefix="/api/v1/relevos",
    tags=["Solicitudes y calendario"],
)

@router_relevos.get("/resumen/semana", response_model=ResumenSemanaOut)
def obtener_resumen_semana(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_obtener_resumen_semana(current_user, db)

@router_relevos.post(
    "",
    response_model=SolicitudRelevoOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_solicitud_relevo(
    datos: SolicitudRelevoIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_crear_solicitud_relevo(datos, current_user, db)

@router_relevos.get(
    "/usuarios/{usuario_id}",
    response_model=list[SolicitudRelevoOut],
)
def listar_relevos_usuario(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_listar_relevos_usuario(usuario_id, limit, offset, current_user, db)

@router_relevos.patch("/{relevo_id}", response_model=SolicitudRelevoOut)
def actualizar_relevo(
    relevo_id: int,
    datos: SolicitudRelevoEstadoIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_actualizar_relevo(relevo_id, datos, current_user, db)
