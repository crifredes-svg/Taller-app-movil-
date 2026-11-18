"""Profile routes and HTTP controller."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from ...database import get_db
from ...models.usuarios.model import Usuario
from ...security import get_current_user
from ...models.usuarios.model import actualizar_mi_perfil as ejecutar_actualizar_mi_perfil
from ...views.usuarios.view import PerfilUpdate, UsuarioOut

router_perfil = APIRouter(
    prefix="/api/v1/perfil",
    tags=["Perfil"],
)

@router_perfil.patch("/me", response_model=UsuarioOut)
def actualizar_mi_perfil(
    datos: PerfilUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ejecutar_actualizar_mi_perfil(datos, current_user, db)
