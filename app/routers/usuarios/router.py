"""User registration routes and HTTP controller."""

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...models.usuarios.model import crear_usuario as ejecutar_crear_usuario
from ...views.usuarios.view import RegistroOut, UsuarioIn

router_usuarios = APIRouter(
    prefix="/api/v1/usuarios",
    tags=["Usuarios"],
)

@router_usuarios.post(
    "",
    response_model=RegistroOut,
    status_code=status.HTTP_201_CREATED,
)
def crear_usuario(
    datos: UsuarioIn,
    db: Session = Depends(get_db),
):
    return ejecutar_crear_usuario(datos, db)
