from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional


class DocumentBlockCategory(str, Enum):
    TITLE = "title"
    HEADING = "heading"
    PARAGRAPH = "paragraph"
    TABLE = "table"
    FIGURE = "figure"
    CALLOUT = "callout"
    LIST_ITEM = "list_item"


@dataclass(frozen=True)
class DocumentBoundingBox:
    """Rappresentazione geometrica di un blocco di testo o elemento estratto."""
    column_identifier: int = 0
    vertical_position: float = 0.0
    horizontal_position: float = 0.0
    element_width: float = 0.0
    element_height: float = 0.0
    text_content: str = ""
    block_category: DocumentBlockCategory = DocumentBlockCategory.PARAGRAPH

    def __init__(
        self,
        column_identifier: Optional[int] = None,
        vertical_position: Optional[float] = None,
        horizontal_position: Optional[float] = None,
        element_width: Optional[float] = None,
        element_height: Optional[float] = None,
        text_content: str = "",
        block_category: DocumentBlockCategory = DocumentBlockCategory.PARAGRAPH,
        col_id: Optional[int] = None,
        y_pos: Optional[float] = None,
        x_pos: Optional[float] = None,
        width: Optional[float] = None,
        height: Optional[float] = None
    ) -> None:
        resolved_col = col_id if col_id is not None else (column_identifier if column_identifier is not None else 0)
        resolved_y = y_pos if y_pos is not None else (vertical_position if vertical_position is not None else 0.0)
        resolved_x = x_pos if x_pos is not None else (horizontal_position if horizontal_position is not None else 0.0)
        resolved_w = width if width is not None else (element_width if element_width is not None else 0.0)
        resolved_h = height if height is not None else (element_height if element_height is not None else 0.0)

        object.__setattr__(self, "column_identifier", int(resolved_col))
        object.__setattr__(self, "vertical_position", float(resolved_y))
        object.__setattr__(self, "horizontal_position", float(resolved_x))
        object.__setattr__(self, "element_width", float(resolved_w))
        object.__setattr__(self, "element_height", float(resolved_h))
        object.__setattr__(self, "text_content", str(text_content))
        object.__setattr__(self, "block_category", block_category)

    # Proprietà di compatibilità per il codice esistente
    @property
    def col_id(self) -> int:
        return self.column_identifier

    @property
    def y_pos(self) -> float:
        return self.vertical_position

    @property
    def x_pos(self) -> float:
        return self.horizontal_position

    @property
    def width(self) -> float:
        return self.element_width

    @property
    def height(self) -> float:
        return self.element_height


@dataclass(frozen=True)
class RawTableCell:
    """Definizione di una singola cella tabellare con coordinate di estensione."""
    content: str
    row_span: int = 1
    col_span: int = 1

    def __post_init__(self) -> None:
        if self.row_span < 1:
            raise ValueError(f"row_span deve essere >= 1, ricevuto {self.row_span}")
        if self.col_span < 1:
            raise ValueError(f"col_span deve essere >= 1, ricevuto {self.col_span}")


@dataclass(frozen=True)
class NormalizedTableMatrix:
    """Rappresentazione bidimensionale normalizzata di una tabella clinica."""
    column_headers: List[str]
    matrix_rows: List[List[str]]
    total_columns: int
    total_rows: int


@dataclass(frozen=True)
class ExtractedDocumentLayout:
    """Documento clinico estratto con metadati e sequenza ordinata di blocchi."""
    source_identifier: str
    total_pages: int
    ordered_bounding_boxes: List[DocumentBoundingBox]
    normalized_tables: List[NormalizedTableMatrix] = field(default_factory=list)
