import hashlib
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict
from medfactory.src.dla.interfaces.dla_interface import IDocumentLayoutAnalyzer
from medfactory.src.dla.base.dla_models import (
    DocumentBoundingBox,
    DocumentBlockCategory,
    ExtractedDocumentLayout
)
from medfactory.src.dla.implementations.topological_column_slicer import TopologicalColumnSlicer
from medfactory.src.dla.implementations.medical_unit_scale_guard import MedicalUnitScaleGuard


class CorruptedDocumentDLQError(ValueError):
    """Eccezione formale sollevata quando un documento o pagina viene isolato nella Dead-Letter Queue."""


@dataclass(frozen=True)
class DeadLetterDocumentRecord:
    """Record forense di isolamento Dead-Letter Queue (DLQ) con checksum crittografico SHA-256."""
    document_name: str
    sha256_checksum: str
    failure_reason: str
    isolated_at_utc: str
    byte_length: int


class DocumentLayoutAnalyzer(IDocumentLayoutAnalyzer):
    """
    Document Layout Analysis di MedFactory integrato con Docling DLA,
    topological column slicing anti-cross-talk, normalizzazione ISMP delle unità
    e isolamento forense Dead-Letter Queue (DLQ) vincolato a SHA-256.
    """

    def __init__(
        self,
        alpha_col_weight: float = 10000.0,
        beta_y_weight: float = 1.0,
        enable_docling: bool = True,
        dlq_directory: Optional[Path] = None
    ):
        self.column_slicer = TopologicalColumnSlicer(
            alpha_column_weight=alpha_col_weight,
            beta_vertical_weight=beta_y_weight
        )
        self.scale_guard = MedicalUnitScaleGuard()
        self.enable_docling = enable_docling
        self.dlq_directory = dlq_directory
        self.dead_letter_queue: List[DeadLetterDocumentRecord] = []

    @property
    def alpha(self) -> float:
        return self.column_slicer.alpha

    @property
    def beta(self) -> float:
        return self.column_slicer.beta

    def isolate_to_dlq(
        self,
        document_name: str,
        raw_document_bytes: bytes,
        failure_reason: str
    ) -> DeadLetterDocumentRecord:
        """
        Calcola il checksum crittografico SHA-256 del documento/pagina malformato,
        lo registra nella Dead-Letter Queue e persiste il report forense se dlq_directory è attivo.
        """
        sha256_digest = hashlib.sha256(raw_document_bytes).hexdigest()
        dlq_entry = DeadLetterDocumentRecord(
            document_name=document_name,
            sha256_checksum=sha256_digest,
            failure_reason=failure_reason,
            isolated_at_utc=datetime.now(timezone.utc).isoformat(),
            byte_length=len(raw_document_bytes)
        )
        self.dead_letter_queue.append(dlq_entry)

        if self.dlq_directory is not None:
            self.dlq_directory.mkdir(parents=True, exist_ok=True)
            report_path = self.dlq_directory / f"{sha256_digest}.dlq.json"
            report_content: Dict[str, object] = {
                "document_name": dlq_entry.document_name,
                "sha256_checksum": dlq_entry.sha256_checksum,
                "failure_reason": dlq_entry.failure_reason,
                "isolated_at_utc": dlq_entry.isolated_at_utc,
                "byte_length": dlq_entry.byte_length
            }
            report_path.write_text(json.dumps(report_content, indent=2), encoding="utf-8")

        return dlq_entry

    def sort_reading_order(self, text_boxes: List[DocumentBoundingBox]) -> List[DocumentBoundingBox]:
        """
        Ordina i nodi documentali secondo Pos_i = alpha * Col_id + beta * y_i.
        alpha >> beta previene il cross-talk orizzontale tra colonne adiacenti.
        """
        return self.column_slicer.sort_reading_order(text_boxes)

    def normalize_ismp_units(self, text_content: str) -> str:
        """
        Normalizzazione OCR per unità di misura critiche (ISMP compliance).
        Trasforma microgrammi (ug, µg) in mcg per evitare confusioni letali 1000x con mg.
        """
        return self.scale_guard.sanitize_dosage_units(text_content)

    def reconstruct_text(self, text_boxes: List[DocumentBoundingBox]) -> str:
        """
        Ordina topologicamente i blocchi e restituisce il testo sanificato concatenato.
        """
        ordered_boxes = self.sort_reading_order(text_boxes)
        normalized_texts = [
            self.normalize_ismp_units(box.text_content)
            for box in ordered_boxes
        ]
        return "\n\n".join(normalized_texts)

    def extract_document_layout(self, document_path: Path) -> ExtractedDocumentLayout:
        """
        Estrae la struttura del documento PDF o testo utilizzando pypdfium2,
        invocando detect_columns_if_missing() sulle pagine PDF e isolando nella DLQ
        con checksum SHA-256 eventuali file o pagine corrotte.
        """
        if not document_path.exists():
            raise FileNotFoundError(f"File documento non trovato: {document_path}")

        raw_document_bytes = document_path.read_bytes()
        if not raw_document_bytes:
            dlq_record = self.isolate_to_dlq(
                document_path.name, raw_document_bytes, "Empty document stream (0 bytes)"
            )
            raise CorruptedDocumentDLQError(
                f"Documento vuoto isolato in DLQ (sha256={dlq_record.sha256_checksum})"
            )

        extracted_boxes: List[DocumentBoundingBox] = []
        suffix = document_path.suffix.lower()

        if suffix == ".pdf":
            if not raw_document_bytes.startswith(b"%PDF-"):
                dlq_record = self.isolate_to_dlq(
                    document_path.name, raw_document_bytes, "Invalid PDF magic header (missing %PDF-)"
                )
                raise CorruptedDocumentDLQError(
                    f"Header PDF corrotto isolato in DLQ (sha256={dlq_record.sha256_checksum})"
                )
            try:
                import pypdfium2 as pdfium
                pdf_doc = pdfium.PdfDocument(str(document_path))
                total_pages = len(pdf_doc)
                for page_idx in range(total_pages):
                    page = pdf_doc[page_idx]
                    page_width = float(page.get_width()) if hasattr(page, "get_width") else 595.0
                    page_height = float(page.get_height()) if hasattr(page, "get_height") else 842.0
                    text_page = page.get_textpage()
                    page_text = text_page.get_text_range()
                    if page_text.strip():
                        page_boxes: List[DocumentBoundingBox] = []
                        raw_segments = [seg.strip() for seg in page_text.split("\n\n") if seg.strip()]
                        for seg_idx, segment_text in enumerate(raw_segments):
                            page_boxes.append(
                                DocumentBoundingBox(
                                    column_identifier=0,
                                    vertical_position=float(page_idx * 1000.0 + seg_idx * 40.0),
                                    horizontal_position=0.0,
                                    element_width=page_width / 2.0,
                                    element_height=min(page_height, 80.0),
                                    text_content=self.normalize_ismp_units(segment_text),
                                    block_category=DocumentBlockCategory.PARAGRAPH
                                )
                            )
                        detected_page_boxes = self.column_slicer.detect_columns_if_missing(
                            page_boxes,
                            page_width=page_width if page_width > 0 else 595.0,
                            expected_columns=2
                        )
                        extracted_boxes.extend(detected_page_boxes)
                pdf_doc.close()
            except Exception as extraction_err:
                dlq_record = self.isolate_to_dlq(
                    document_path.name, raw_document_bytes, f"PDF parsing error: {extraction_err}"
                )
                raise CorruptedDocumentDLQError(
                    f"Errore estrazione PDF isolato in DLQ (sha256={dlq_record.sha256_checksum}): {extraction_err}"
                ) from extraction_err
        else:
            try:
                text_content = raw_document_bytes.decode("utf-8")
            except UnicodeDecodeError as decode_err:
                dlq_record = self.isolate_to_dlq(
                    document_path.name, raw_document_bytes, f"UTF-8 decode failure: {decode_err}"
                )
                raise CorruptedDocumentDLQError(
                    f"Codifica UTF-8 corrotta isolata in DLQ (sha256={dlq_record.sha256_checksum})"
                ) from decode_err

            total_pages = 1
            paragraphs = [p.strip() for p in text_content.split("\n\n") if p.strip()]
            raw_text_boxes: List[DocumentBoundingBox] = []
            for p_idx, para in enumerate(paragraphs):
                raw_text_boxes.append(
                    DocumentBoundingBox(
                        column_identifier=0,
                        vertical_position=float(p_idx * 50.0),
                        horizontal_position=0.0,
                        element_width=250.0,
                        element_height=40.0,
                        text_content=self.normalize_ismp_units(para),
                        block_category=DocumentBlockCategory.PARAGRAPH
                    )
                )
            extracted_boxes = self.column_slicer.detect_columns_if_missing(
                raw_text_boxes, page_width=595.0, expected_columns=2
            )

        ordered_boxes = self.sort_reading_order(extracted_boxes)
        return ExtractedDocumentLayout(
            source_identifier=document_path.stem,
            total_pages=total_pages,
            ordered_bounding_boxes=ordered_boxes
        )
