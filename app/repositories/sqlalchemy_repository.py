"""SQLAlchemy session adapter for persistence operations."""

from typing import Any, TypeVar

from sqlalchemy.orm import Query, Session

Model = TypeVar("Model")


class SqlAlchemyRepository:
    """Keeps SQLAlchemy session operations behind the persistence boundary."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def query(self, model: type[Model]) -> Query[Model]:
        return self._session.query(model)

    def get(
        self,
        model: type[Model],
        identity: Any,
        **options: Any,
    ) -> Model | None:
        return self._session.get(model, identity, **options)

    def add(self, entity: object) -> None:
        self._session.add(entity)

    def refresh(self, entity: object) -> None:
        self._session.refresh(entity)

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()
