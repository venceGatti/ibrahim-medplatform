from medfactory.src.compression.interfaces.compression_interface import IMarkdownSynthesizer
from medfactory.src.compression.base.compression_models import (
    ClinicalSheetSynthesisRequest,
    SynthesizedMarkdownSheet
)


class StaticMarkdownSynthesizer(IMarkdownSynthesizer):
    """
    Sintetizzatore deterministico per schede cliniche statiche (SSG).
    Genera documenti conformi a CommonMark con callout tipizzati per le allerte cliniche.
    """

    def synthesize_sheet(self, request: ClinicalSheetSynthesisRequest) -> SynthesizedMarkdownSheet:
        """
        Compila la monografia medica statica a partire dai dati strutturati della richiesta.
        """
        markdown_sections = []

        # Intestazione e Tassonomia
        breadcrumb = " > ".join(request.taxonomy_path) if request.taxonomy_path else "Medicina Generale"
        markdown_sections.append(f"# {request.disease_title} ({request.icd10_code})")
        markdown_sections.append(f"*Tassonomia: {breadcrumb}*\n")

        # Callouts primari di emergenza (RED_FLAG)
        red_flags = [c for c in request.callouts if c.severity_type.value == "RED_FLAG"]
        for rf in red_flags:
            markdown_sections.append(rf.format_markdown())
            markdown_sections.append("")

        # Sezione 1: Definizione ed Epidemiologia
        markdown_sections.append("## 1. Definizione ed Epidemiologia")
        markdown_sections.append(request.definition_text.strip())
        markdown_sections.append("")

        # Sezione 2: Eziologia e Fisiopatologia
        markdown_sections.append("## 2. Eziologia e Fisiopatologia")
        markdown_sections.append(request.etiology_text.strip())
        markdown_sections.append("")

        # Sezione 3: Quadro Clinico e Segni Obiettivi
        markdown_sections.append("## 3. Quadro Clinico e Sintomatologia")
        if request.clinical_signs:
            for sign in request.clinical_signs:
                markdown_sections.append(f"- {sign.strip()}")
        else:
            markdown_sections.append("- Asintomatico nelle fasi iniziali.")
        markdown_sections.append("")

        # Sezione 4: Iter Diagnostico
        markdown_sections.append("## 4. Iter Diagnostico e Criteri")
        if request.diagnostic_workup:
            for step in request.diagnostic_workup:
                markdown_sections.append(f"1. {step.strip()}")
        else:
            markdown_sections.append("1. Valutazione clinica e laboratoristica standard.")
        markdown_sections.append("")

        # Callouts di perle cliniche o esami
        tips = [c for c in request.callouts if c.severity_type.value in ("EXAM_TIP", "CLINICAL_PEARL")]
        for tip in tips:
            markdown_sections.append(tip.format_markdown())
            markdown_sections.append("")

        # Sezione 5: Terapia Farmacologica e Controindicazioni
        markdown_sections.append("## 5. Trattamento Farmacologico")
        if request.pharmacotherapy_atc:
            for atc in request.pharmacotherapy_atc:
                markdown_sections.append(f"- ATC: `{atc.strip()}`")
        else:
            markdown_sections.append("- Terapia di supporto personalizzata.")
        markdown_sections.append("")

        # Callouts di controindicazioni
        contraindications = [c for c in request.callouts if c.severity_type.value == "CONTRAINDICATION"]
        for contra in contraindications:
            markdown_sections.append(contra.format_markdown())
            markdown_sections.append("")

        full_markdown = "\n".join(markdown_sections).strip()

        return SynthesizedMarkdownSheet(
            sheet_identifier=request.sheet_identifier,
            icd10_code=request.icd10_code,
            document_title=request.disease_title,
            raw_markdown_content=full_markdown,
            character_count=len(full_markdown),
            callout_count=len(request.callouts)
        )
