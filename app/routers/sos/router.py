"""SOS routes and HTTP controller."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...models.sos.model import activar_sos as ejecutar_activar_sos
from ...models.sos.model import actualizar_estado_sos as ejecutar_actualizar_estado_sos
from ...models.sos.model import listar_alertas_sos as ejecutar_listar_alertas_sos
from ...models.sos.model import listar_sos_recibidas as ejecutar_listar_sos_recibidas
from ...views.sos.view import AlertaSOSIn, AlertaSOSEstadoIn, AlertaSOSOut

router_sos = APIRouter(
    prefix="/api/v1/sos",
    tags=["SOS"],
)

@router_sos.post(
    "",
    response_model=AlertaSOSOut,
    status_code=status.HTTP_201_CREATED,
)
def activar_sos(
    datos: AlertaSOSIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_activar_sos(datos, current_user, db)

@router_sos.get("/recibidas", response_model=list[AlertaSOSOut])
def listar_sos_recibidas(
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_listar_sos_recibidas(limit, offset, current_user, db)

@router_sos.get(
    "/usuarios/{usuario_id}",
    response_model=list[AlertaSOSOut],
)
def listar_alertas_sos(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_listar_alertas_sos(usuario_id, limit, offset, current_user, db)

@router_sos.patch("/{alerta_id}", response_model=AlertaSOSOut)
def actualizar_estado_sos(
    alerta_id: int,
    datos: AlertaSOSEstadoIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_actualizar_estado_sos(alerta_id, datos, current_user, db)
