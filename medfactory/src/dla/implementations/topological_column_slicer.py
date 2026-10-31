from typing import List, Tuple
from medfactory.src.dla.base.dla_models import DocumentBoundingBox


class TopologicalColumnSlicer:
    """
    Algoritmo di slicing topologico multi-colonna anti-cross-talk.
    Ordina i blocchi documentali secondo la formulazione matematica:
    Pos_i = alpha * Col_id + beta * y_i con alpha >> beta (default alpha=10000.0, beta=1.0).
    Previene l'interleaving orizzontale errato tra colonne contigue di testo medico.
    """

    def __init__(self, alpha_column_weight: float = 10000.0, beta_vertical_weight: float = 1.0):
        self.alpha = alpha_column_weight
        self.beta = beta_vertical_weight

    def detect_columns_if_missing(
        self,
        bounding_boxes: List[DocumentBoundingBox],
        page_width: float = 595.0,
        expected_columns: int = 2
    ) -> List[DocumentBoundingBox]:
        """
        Se i blocchi non hanno un column_identifier valido (o sono tutti 0),
        esegue il clustering geometrico orizzontale deterministico per assegnare Col_id.
        """
        if not bounding_boxes:
            return []

        # Se sono già presenti identificatori di colonna distinti, mantienili
        distinct_columns = {box.column_identifier for box in bounding_boxes}
        if len(distinct_columns) > 1:
            return bounding_boxes

        column_boundary = page_width / expected_columns
        updated_boxes: List[DocumentBoundingBox] = []

        for box in bounding_boxes:
            # Calcola il baricentro orizzontale del blocco
            box_center_x = box.horizontal_position + (box.element_width / 2.0)
            assigned_col = int(box_center_x // column_boundary)
            if assigned_col >= expected_columns:
                assigned_col = expected_columns - 1

            new_box = DocumentBoundingBox(
                column_identifier=assigned_col,
                vertical_position=box.vertical_position,
                horizontal_position=box.horizontal_position,
                element_width=box.element_width,
                element_height=box.element_height,
                text_content=box.text_content,
                block_category=box.block_category
            )
            updated_boxes.append(new_box)

        return updated_boxes

    def sort_reading_order(self, bounding_boxes: List[DocumentBoundingBox]) -> List[DocumentBoundingBox]:
        """
        Ordina i nodi documentali secondo Pos_i = alpha * Col_id + beta * y_i.
        """
        if not bounding_boxes:
            return []

        return sorted(
            bounding_boxes,
            key=lambda box: self.alpha * box.column_identifier + self.beta * box.vertical_position
        )
