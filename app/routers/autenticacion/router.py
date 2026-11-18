"""Authentication routes and HTTP controller."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...models.usuarios.model import cerrar_sesion as ejecutar_cerrar_sesion
from ...models.usuarios.model import iniciar_sesion as ejecutar_iniciar_sesion
from ...views.usuarios.view import LoginIn, LogoutOut, TokenOut

router_auth = APIRouter(
    prefix="/api/v1/auth",
    tags=["Autenticación"],
)

@router_auth.post("/login", response_model=TokenOut)
def iniciar_sesion(
    datos: LoginIn,
    db: Session = Depends(get_db),
):
    return ejecutar_iniciar_sesion(datos, db)

@router_auth.post("/logout", response_model=LogoutOut)
def cerrar_sesion(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # El incremento se resuelve en SQL para que logouts concurrentes no pierdan versiones.
    return ejecutar_cerrar_sesion(current_user, db)
