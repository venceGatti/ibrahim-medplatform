from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional


class CalloutSeverityType(str, Enum):
    """Tipologia formale di callout per le schede cliniche statiche."""
    RED_FLAG = "RED_FLAG"
    CONTRAINDICATION = "CONTRAINDICATION"
    EXAM_TIP = "EXAM_TIP"
    CLINICAL_PEARL = "CLINICAL_PEARL"


@dataclass(frozen=True)
class ClinicalCallout:
    """Callout di allerta clinica inserito nella monografia statica."""
    severity_type: CalloutSeverityType
    callout_title: str
    callout_body: str

    def format_markdown(self) -> str:
        """Formatta il callout secondo lo standard CommonMark GitHub style."""
        body_lines = self.callout_body.strip().split("\n")
        formatted_body = "\n".join(f"> {line}" for line in body_lines)
        return (
            f"> [!{self.severity_type.value}]\n"
            f"> **{self.callout_title}**\n"
            f"{formatted_body}"
        )


@dataclass(frozen=True)
class ClinicalSheetSynthesisRequest:
    """Richiesta per la generazione di una scheda clinica statica."""
    sheet_identifier: str
    icd10_code: str
    disease_title: str
    taxonomy_path: List[str]
    definition_text: str
    etiology_text: str
    clinical_signs: List[str]
    diagnostic_workup: List[str]
    pharmacotherapy_atc: List[str]
    callouts: List[ClinicalCallout] = field(default_factory=list)


@dataclass(frozen=True)
class SynthesizedMarkdownSheet:
    """Scheda clinica statica compilata pronta per l'indicizzazione."""
    sheet_identifier: str
    icd10_code: str
    document_title: str
    raw_markdown_content: str
    character_count: int
    callout_count: int


@dataclass(frozen=True)
class CompressionMetadata:
    """Metadati relativi all'addestramento e impiego del dizionario Zstandard."""
    dictionary_byte_length: int
    compression_ratio: float
    decompression_integrity_verified: bool
