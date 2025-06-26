from pathlib import Path
from typing import Any, Sequence

from sqlalchemy import URL, Engine, select
from sqlalchemy.engine.row import Row
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm.session import Session
from sqlmodel import SQLModel, create_engine, col

from fd_viewer.core.database.models import FixedDeposit


class FDDataBase:
    def __init__(self, db_path: Path) -> None:
        self.__db_path = db_path
        self._engine = create_engine(
            URL.create(drivername="sqlite", database=str(self.__db_path.absolute())),
            echo=False,  # Set True for debugging SQL
        )
        self._session_maker = sessionmaker(self.engine, expire_on_commit=True)

    def init(self) -> None:
        """
        Initializes the database and creates the necessary tables.
        """
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
        """Returns the path to the SQLite database file."""
        return self.__db_path

    #
    ## CRUD: Add
    #
    def add_new_fd(self, fd: FixedDeposit) -> FixedDeposit | None:
        """Adds a new FixedDeposit entry to the database."""
        with self.session as session:
            try:
                session.add(fd)
                session.commit()
                session.refresh(fd)
                return fd
            except Exception as e:
                session.rollback()
                print(f"[DB ERROR] Failed to add FD: {e}")
                return None

    #
    ## CRUD: Read
    #
    def select_fd(
        self, condition: dict[str, Any] | None = None, count: int | None = None
    ) -> Sequence[FixedDeposit] | None:
        """
        Fetches FD records from the database.

        - If `condition` is provided: Filters using key=value mapping.
        - If `count` is provided: Limits the number of results.
        - If both are provided: Raises an error.
        """
        if condition and count:
            raise ValueError(
                "You cannot pass both 'condition' and 'count' at the same time."
            )

        with self.session as session:
            try:
                stmt = select(FixedDeposit)

                if condition:
                    for key, value in condition.items():
                        stmt = stmt.where(col(getattr(FixedDeposit, key)) == value)

                result = session.execute(stmt)

                if count:
                    return result.scalars().fetchmany(count)
                return result.scalars().all()

            except Exception as e:
                print(f"[DB ERROR] Failed to select FDs: {e}")
                return None

    #
    ## CRUD: Update
    #
    def update_fd(self, fd_id: int, updates: dict[str, Any]) -> bool:
        """Updates an existing FD entry given its ID and a dict of fields to update."""
        with self.session as session:
            try:
                fd = session.get(FixedDeposit, fd_id)
                if not fd:
                    print(f"[WARN] FD with ID {fd_id} not found.")
                    return False

                for key, value in updates.items():
                    setattr(fd, key, value)

                session.add(fd)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(f"[DB ERROR] Failed to update FD: {e}")
                return False

    #
    ## CRUD: Delete
    #
    def delete_fd(self, fd_id: int) -> bool:
        """Deletes an FD entry by ID."""
        with self.session as session:
            try:
                fd = session.get(FixedDeposit, fd_id)
                if not fd:
                    print(f"[WARN] FD with ID {fd_id} not found.")
                    return False

                session.delete(fd)
                session.commit()
                return True

            except Exception as e:
                session.rollback()
                print(f"[DB ERROR] Failed to delete FD: {e}")
                return False

    #
    ## Utility
    #
    def get_all_fds(self) -> Sequence[FixedDeposit]:
        """Returns all FD entries."""
        with self.session as session:
            try:
                result = session.execute(select(FixedDeposit))
                return result.scalars().all()
            except Exception as e:
                print(f"[DB ERROR] Failed to fetch all FDs: {e}")
                return []
