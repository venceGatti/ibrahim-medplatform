"""
Backward-compatible adapter for SQLiteModuleBuilder.
Delegates directly to 3-tier implementation.
"""
from pathlib import Path
from typing import Optional
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder as ImplSQLiteBuilder
from medfactory.src.database.base.database_schema import DDL_SCHEMA


class SQLiteModuleBuilder(ImplSQLiteBuilder):
    """
    Adapter retrocompatibile per SQLiteModuleBuilder.
    Utilizza staging_database_path.
    """

    def __init__(self, staging_database_path: Optional[Path] = None, database_path: Optional[Path] = None):
        target_path = staging_database_path if staging_database_path is not None else database_path
        if target_path is None:
            raise ValueError("È necessario specificare un percorso valido per il database.")
        super().__init__(staging_database_path=target_path)


__all__ = ["SQLiteModuleBuilder", "DDL_SCHEMA"]
