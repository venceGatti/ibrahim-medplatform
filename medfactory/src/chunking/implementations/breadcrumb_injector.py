from typing import List


class BreadcrumbInjector:
    """
    Iniettore di contesto tassonomico per i child chunks.
    Assicura che ogni passaggio atomico preservi l'inquadramento nosologico
    nel formato: '[Discipline > Subspecialty > Pathology > SectionHeading]\n\n'
    rispettando il limite di budget di token (<= 20% dei token child, <= 50 token).
    """

    MAX_BREADCRUMB_TOKENS: int = 50

    def generate_breadcrumb(self, section_hierarchy: List[str]) -> str:
        """
        Costruisce l'intestazione breadcrumb dalla lista ordinata dei nodi tassonomici.
        """
        if not section_hierarchy:
            return ""

        # Sanifica e rimuove elementi vuoti
        sanitized_hierarchy = [node.strip() for node in section_hierarchy if node.strip()]
        if not sanitized_hierarchy:
            return ""

        breadcrumb_content = " > ".join(sanitized_hierarchy)
        breadcrumb_tokens = breadcrumb_content.split()

        # Tronca se supera il limite massimo consentito di token per l'header
        if len(breadcrumb_tokens) > self.MAX_BREADCRUMB_TOKENS:
            truncated_content = " ".join(breadcrumb_tokens[:self.MAX_BREADCRUMB_TOKENS])
            return f"[{truncated_content}]\n\n"

        return f"[{breadcrumb_content}]\n\n"

    def inject(self, child_text: str, section_hierarchy: List[str]) -> str:
        """
        Inietta l'header breadcrumb all'inizio del testo del child chunk.
        """
        header = self.generate_breadcrumb(section_hierarchy)
        return f"{header}{child_text}"
