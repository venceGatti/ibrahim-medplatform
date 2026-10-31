from typing import List, Optional
from medfactory.src.dla.interfaces.dla_interface import ITableResolver
from medfactory.src.dla.base.dla_models import RawTableCell, NormalizedTableMatrix


class ComplexTableNormalizer(ITableResolver):
    """
    Risolutore topologico di tabelle cliniche complesse (OTSL 2D grid matrix logic).
    Espande matricialmente le celle con rowspan e colspan denormalizzando i puntatori semantici,
    garantendo che non si verifichi disallineamento dosaggio/paziente per appiattimento arbitrario.
    """

    def resolve_grid(self, raw_matrix: List[List[RawTableCell]]) -> List[List[str]]:
        """
        Espande una lista di righe di celle con rowspan e colspan in una matrice
        bidimensionale densa di stringhe.
        """
        if not raw_matrix:
            return []

        # Determina il numero iniziale di righe e calcola le colonne massime stimate
        initial_rows = len(raw_matrix)
        maximum_columns = 0
        for single_row in raw_matrix:
            row_span_sum = sum(cell.col_span for cell in single_row)
            if row_span_sum > maximum_columns:
                maximum_columns = row_span_sum

        if maximum_columns == 0:
            return []

        # Inizializza griglia 2D con None
        dense_grid: List[List[Optional[str]]] = [
            [None for _ in range(maximum_columns)] for _ in range(initial_rows)
        ]

        for row_index, current_row in enumerate(raw_matrix):
            column_cursor = 0
            for current_cell in current_row:
                # Trova la prima colonna libera nella riga corrente
                while column_cursor < maximum_columns and dense_grid[row_index][column_cursor] is not None:
                    column_cursor += 1

                # Espandi per row_span e col_span
                for row_offset in range(current_cell.row_span):
                    target_row = row_index + row_offset
                    while target_row >= len(dense_grid):
                        dense_grid.append([None for _ in range(maximum_columns)])

                    for col_offset in range(current_cell.col_span):
                        target_col = column_cursor + col_offset
                        if target_col >= maximum_columns:
                            for grid_row in dense_grid:
                                grid_row.append(None)
                            maximum_columns += 1
                        dense_grid[target_row][target_col] = current_cell.content

                column_cursor += current_cell.col_span

        # Sostituisci eventuali None residui con stringa vuota (eliminando l'identificatore val)
        normalized_grid: List[List[str]] = []
        for dense_row in dense_grid:
            sanitized_row: List[str] = [
                cell_content if cell_content is not None else ""
                for cell_content in dense_row
            ]
            normalized_grid.append(sanitized_row)

        return normalized_grid

    def to_canonical_markdown(self, resolved_matrix: List[List[str]], has_header: bool = True) -> str:
        """
        Converte la matrice espansa in una tabella conforme a GitHub Flavored Markdown (GFM).
        Sanifica i caratteri pipe ('|') interni alle celle per non rompere il rendering.
        """
        if not resolved_matrix:
            return ""

        def _escape_pipes(text: str) -> str:
            return text.replace("|", "\\|").replace("\n", " ").strip()

        sanitized_matrix = [
            [_escape_pipes(cell_content) for cell_content in row]
            for row in resolved_matrix
        ]

        header_row = sanitized_matrix[0]
        markdown_lines = ["| " + " | ".join(header_row) + " |"]
        separator = "| " + " | ".join(["---"] * len(header_row)) + " |"
        markdown_lines.append(separator)

        for content_row in sanitized_matrix[1 if has_header else 0:]:
            markdown_lines.append("| " + " | ".join(content_row) + " |")

        return "\n".join(markdown_lines)

    def to_normalized_matrix(self, resolved_matrix: List[List[str]]) -> NormalizedTableMatrix:
        """Costruisce l'oggetto tipizzato NormalizedTableMatrix."""
        if not resolved_matrix:
            return NormalizedTableMatrix(
                column_headers=[],
                matrix_rows=[],
                total_columns=0,
                total_rows=0
            )

        headers = resolved_matrix[0]
        body_matrix_rows = resolved_matrix[1:]
        return NormalizedTableMatrix(
            column_headers=headers,
            matrix_rows=body_matrix_rows,
            total_columns=len(headers),
            total_rows=len(body_matrix_rows)
        )

