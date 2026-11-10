import sqlite3
import json
from pathlib import Path
from typing import List, Optional, Any
from medfactory.src.chunking.base.chunk_models import ParentChunk, ChildChunk
from medfactory.src.database.interfaces.database_interface import ISQLiteBuilder
from medfactory.src.database.base.database_schema import DDL_SCHEMA
from medfactory.src.database.base.sqlite_domain_inserter import SQLiteDomainInserterMixin


class SQLiteModuleBuilder(SQLiteDomainInserterMixin, ISQLiteBuilder):
    """
    Costruttore del database relazionale module_kb.sqlite conforme alla specifica SRS (ROA-20).
    Supporta STRICT mode, PRAGMA di performance, FTS5 per ricerca full-text e VACUUM INTO
    con chiusura deterministica della transazione e rilascio garantito del file handle su Windows.
    """

    def __init__(self, staging_database_path: Path):
        self.staging_database_path = Path(staging_database_path)
        self._is_closed = False
        self.staging_database_path.parent.mkdir(parents=True, exist_ok=True)
        if self.staging_database_path.exists():
            self.staging_database_path.unlink()

        self.conn = sqlite3.connect(str(self.staging_database_path))
        try:
            self.conn.execute("PRAGMA page_size = 4096;")
            self.conn.execute("PRAGMA auto_vacuum = NONE;")
            self.conn.execute("PRAGMA encoding = 'UTF-8';")
            self.conn.executescript(DDL_SCHEMA)
            self.conn.commit()
        except Exception:
            self.close()
            raise

    def __enter__(self) -> "SQLiteModuleBuilder":
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> None:
        self.close()

    def close(self) -> None:
        """Chiude in modo deterministico la connessione SQLite rilasciando il descrittore su Windows."""
        if not self._is_closed and getattr(self, "conn", None) is not None:
            try:
                self.conn.commit()
            except sqlite3.Error as commit_err:
                raise RuntimeError(f"Errore di commit durante la chiusura SQLite: {commit_err}") from commit_err
            finally:
                self.conn.close()
                self._is_closed = True

    def insert_source(
        self,
        source_id: str,
        academic_title: str,
        publication_year: int,
        authors: List[str],
        publisher: str,
        isbn: Optional[str] = None,
        doi: Optional[str] = None,
        pmid: Optional[str] = None,
        edition: Optional[int] = None,
        volume: Optional[int] = None
    ) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO bibliographic_sources (
                source_id, isbn, doi, pmid, academic_title, edition, volume,
                publication_year, authors_json, publisher
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                source_id, isbn, doi, pmid, academic_title, edition, volume,
                int(publication_year), json.dumps(authors), publisher
            )
        )
        self.conn.commit()

    def insert_parent_chunk(self, chunk: ParentChunk) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO parent_chunks (
                parent_id, source_id, chapter, section_path,
                page_start, page_end, raw_content, token_count
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chunk.parent_id, chunk.source_id, chunk.chapter, chunk.section_path,
                int(chunk.page_start), int(chunk.page_end), chunk.raw_content, int(chunk.token_count)
            )
        )
        self.conn.commit()

    def insert_child_chunk(self, chunk: ChildChunk) -> None:
        cursor = self.conn.cursor()
        cursor.execute(
            """
            INSERT OR REPLACE INTO child_chunks (
                child_id, parent_id, vector_id, breadcrumb_header,
                text_content, token_count, hpo_terms, atc_codes, icd10_codes
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                chunk.child_id, chunk.parent_id, int(chunk.vector_id), chunk.breadcrumb_header,
                chunk.text_content, int(chunk.token_count),
                json.dumps(chunk.hpo_terms), json.dumps(chunk.atc_codes), json.dumps(chunk.icd10_codes)
            )
        )
        cursor.execute(
            """
            INSERT INTO child_chunks_fts (child_id, breadcrumb_header, text_content)
            VALUES (?, ?, ?)
            """,
            (chunk.child_id, chunk.breadcrumb_header, chunk.text_content)
        )
        self.conn.commit()

    def vacuum_into(self, target_path: Path) -> None:
        """
        Chiude qualsiasi transazione aperta tramite commit() ed esegue VACUUM INTO
        su target_path, garantendo la chiusura deterministica del descrittore SQLite.
        """
        target_file = Path(target_path)
        try:
            self.conn.commit()
            if target_file != self.staging_database_path:
                if target_file.exists():
                    target_file.unlink()
                target_path_str = str(target_file).replace("\\", "/")
                self.conn.execute(f"VACUUM INTO '{target_path_str}';")
            else:
                self.conn.execute("VACUUM;")
            self.conn.commit()
        finally:
            self.close()

    def build(self, target_path: Optional[Path] = None) -> None:
        """Finalizza il database eseguendo vacuum_into o commit e chiusura garantita."""
        try:
            if target_path is not None and Path(target_path) != self.staging_database_path:
                self.vacuum_into(Path(target_path))
            else:
                self.conn.commit()
        finally:
            self.close()
