from pathlib import Path
from typing import Any, Sequence

from sqlalchemy import URL, Engine, select
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlmodel import SQLModel, create_engine

from fd_viewer.core.database.models import FixedDeposit


class FDDataBase:
    def __init__(self, db_path: Path) -> None:
        self.__db_path = db_path
        self._engine = create_engine(
            URL.create(drivername="sqlite", database=str(self.__db_path.absolute()))
        )
        self._session_maker = sessionmaker(self.engine, expire_on_commit=True)

    #
    ### core thingies
    #
    def init(self):
        """Initiates the tables, only if they dont exists, and also creates the database path if it doesnt already exists"""
        if not self.db_path.exists():
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.db_path.touch()

        SQLModel.metadata.create_all(bind=self.engine)

    @property
    def session(self) -> Session:
        return self._session_maker()  # type: ignore

    @property
    def engine(self) -> Engine:
        return self._engine

    @property
    def db_path(self) -> Path:
        """The Database location"""
        return self.__db_path

    #
    ## CRUD ops in the FD viewer
    #
    def add_new_fd(self, fd: FixedDeposit) -> FixedDeposit | None:
        """Add new entry to the database"""
        with self.session as session:
            try:
                session.add(fd)
                session.commit()
                return fd
            except Exception:
                session.rollback()
                return None
            finally:
                session.close()

    def select_fd(
        self, condition: dict[str, Any] | None = None, count: int | None = None
    ) -> FixedDeposit | None | Sequence[Row[Any]]:
        """Retrieves the FD from the database"""
        with self.session as session:
            try:
                if condition is not None:
                    return session.get(FixedDeposit, condition)
                if count is not None:
                    return session.execute(select(FixedDeposit)).fetchmany(count)

                if condition and count is not None:
                    raise ValueError(
                        "Error: condition and count cannot be stated at a time"
                    )

                else:
                    return session.execute(select(FixedDeposit)).all()

            except Exception:
                return None
