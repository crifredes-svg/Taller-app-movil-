"""Persistence adapters used by application services."""

from .sqlalchemy_repository import SqlAlchemyRepository

__all__ = ["SqlAlchemyRepository"]
