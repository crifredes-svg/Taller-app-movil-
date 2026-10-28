"""Trusted-contact routes and HTTP controller."""

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...models.contactos.model import crear_contacto as ejecutar_crear_contacto
from ...models.contactos.model import crear_contacto_por_codigo as ejecutar_crear_contacto_por_codigo
from ...models.contactos.model import listar_contactos as ejecutar_listar_contactos
from ...models.contactos.model import obtener_balance_red as ejecutar_obtener_balance_red
from ...views.contactos.view import (
    BalanceRedOut,
    ContactoConfianzaIn,
    ContactoConfianzaOut,
    ContactoPorCodigoIn,
)

router_contactos = APIRouter(
    prefix="/api/v1/contactos",
    tags=["Red de confianza"],
)

@router_contactos.post(
    "/usuarios/{usuario_id}",
    response_model=ContactoConfianzaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_contacto(
    usuario_id: int,
    datos: ContactoConfianzaIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_crear_contacto(usuario_id, datos, current_user, db)

@router_contactos.post(
    "/usuarios/{usuario_id}/por-codigo",
    response_model=ContactoConfianzaOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_contacto_por_codigo(
    usuario_id: int,
    datos: ContactoPorCodigoIn,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_crear_contacto_por_codigo(usuario_id, datos, current_user, db)

@router_contactos.get(
    "/usuarios/{usuario_id}/balance",
    response_model=BalanceRedOut,
)
def obtener_balance_red(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_obtener_balance_red(usuario_id, current_user, db)

@router_contactos.get(
    "/usuarios/{usuario_id}",
    response_model=list[ContactoConfianzaOut],
)
def listar_contactos(
    usuario_id: int,
    limit: int = Query(default=100, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_listar_contactos(usuario_id, limit, offset, current_user, db)
