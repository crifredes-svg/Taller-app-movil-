"""Shared persistence and calculation helpers for resource models."""

from datetime import date, timedelta

from fastapi import HTTPException, status
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from ..repositories import SqlAlchemyRepository
from .relevos.entity import SolicitudRelevo


def _commit_or_conflict(db: Session, detail: str) -> None:
    """Commit a write and translate integrity conflicts into HTTP 400."""
    repository = SqlAlchemyRepository(db)
    try:
        repository.commit()
    except IntegrityError as exc:
        repository.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
        ) from exc


def _duracion_horas(solicitud: SolicitudRelevo) -> float:
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
