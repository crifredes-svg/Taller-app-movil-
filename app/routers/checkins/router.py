"""Check-in routes and HTTP controller."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...models.checkins.model import consultar_tendencia_carga as ejecutar_consultar_tendencia_carga
from ...models.checkins.model import crear_checkin as ejecutar_crear_checkin
from ...models.checkins.model import listar_checkins as ejecutar_listar_checkins
from ...views.checkins.view import CheckInIn, CheckInOut, TendenciaCargaOut

router_checkins = APIRouter(
    prefix="/api/v1/checkins",
    tags=["Mi carga / Check-in"],
)

@router_checkins.get("/tendencia", response_model=TendenciaCargaOut)
def consultar_tendencia_carga(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_consultar_tendencia_carga(current_user, db)

@router_checkins.post(
    "/usuarios/{usuario_id}",
    response_model=CheckInOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_checkin(
    usuario_id: int,
    datos: CheckInIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_crear_checkin(usuario_id, datos, current_user, db)

@router_checkins.get("/usuarios/{usuario_id}", response_model=list[CheckInOut])
def listar_checkins(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_listar_checkins(usuario_id, limit, offset, current_user, db)
