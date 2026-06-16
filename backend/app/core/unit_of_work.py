from sqlmodel import Session


class UnitOfWork:
    """
    Patrón Unit of Work: agrupa las operaciones de una petición
    en una única transacción y hace commit o rollback según el resultado.
    """

    def __init__(self, session: Session) -> None:
        self._session = session

    def __enter__(self) -> "UnitOfWork":
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if exc_type is None:
            self._session.commit()
        else:
            self._session.rollback()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def flush(self) -> None:
        self._session.flush()
