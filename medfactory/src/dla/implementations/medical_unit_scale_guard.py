import re
from typing import Dict
from medfactory.src.dla.interfaces.dla_interface import IMedicalUnitScaleGuard


class MedicalUnitScaleGuard(IMedicalUnitScaleGuard):
    """
    Guardia lexica per la prevenzione di errori di dosaggio critici (ISMP Compliance).
    Normalizza le unità di misura per scongiurare scambi catastrofici (mcg vs mg, dL vs L).
    """

    # Espressione per microgrammi: mu greco (\u03bc), segno micro (\u00b5), ug, mcg
    MICROGRAM_PATTERN = re.compile(
        r'(?i)(?:\b|(?<=\d))\s*(?:\u00b5g|\u03bcg|ug)(\s*/\s*(?:ml|l|dl))?\b'
    )

    # Espressione per trailing zeros vietati da ISMP (es: 5.0 mg -> 5 mg)
    TRAILING_ZERO_PATTERN = re.compile(
        r'\b(\d+)\.0+(\s*(?:mcg|mg|g|kg|ml|l|dl|mmol|meq|iu))\b',
        re.IGNORECASE
    )

    # Espressione per naked decimals vietati da ISMP (es: .5 mg -> 0.5 mg)
    NAKED_DECIMAL_PATTERN = re.compile(
        r'(^|\s)\.(\d+)(\s*(?:mcg|mg|g|kg|ml|l|dl|mmol|meq|iu))\b',
        re.IGNORECASE
    )

    # Fattori di conversione standard rispetto all'unità base
    CONVERSION_FACTORS: Dict[str, float] = {
        "mcg": 1e-6,
        "mg": 1e-3,
        "g": 1.0,
        "kg": 1e3,
        "ml": 1e-3,
        "dl": 1e-1,
        "l": 1.0,
        "mmol/l": 1.0,
        "meq/l": 1.0
    }

    def sanitize_dosage_units(self, raw_text: str) -> str:
        """
        Sanifica il testo documentale sostituendo varianti ambigue di microgrammi con 'mcg',
        eliminando zero superflui post-virgola e anteponendo lo zero ai decimali orfani.
        """
        if not raw_text:
            return ""

        # 1. Normalizza microgrammi
        def _replace_microgram(match: re.Match) -> str:
            fractional_volume = match.group(1)
            if fractional_volume:
                clean_vol = re.sub(r'\s+', '', fractional_volume).lower()
                if "ml" in clean_vol:
                    return " mcg/ml"
                elif "dl" in clean_vol:
                    return " mcg/dl"
                elif "l" in clean_vol:
                    return " mcg/l"
                return f" mcg{clean_vol}"
            return " mcg"

        processed_text = self.MICROGRAM_PATTERN.sub(_replace_microgram, raw_text)

        # 2. Correggi trailing zeros: '5.0 mg' -> '5 mg'
        processed_text = self.TRAILING_ZERO_PATTERN.sub(r'\1\2', processed_text)

        # 3. Correggi naked decimals: '.5 mg' -> '0.5 mg'
        processed_text = self.NAKED_DECIMAL_PATTERN.sub(r'\g<1>0.\2\3', processed_text)

        return processed_text

    def validate_concentration_scale(self, metric_value: float, source_unit: str, target_unit: str) -> float:
        """
        Converte una concentrazione o quantità tra unità diverse, verificando
        che la scala sia compatibile dimensionalmente.
        """
        source_key = source_unit.strip().lower()
        target_key = target_unit.strip().lower()

        if source_key not in self.CONVERSION_FACTORS:
            raise ValueError(f"Unità sorgente sconosciuta: {source_unit}")
        if target_key not in self.CONVERSION_FACTORS:
            raise ValueError(f"Unità target sconosciuta: {target_unit}")

        base_value = metric_value * self.CONVERSION_FACTORS[source_key]
        converted_value = base_value / self.CONVERSION_FACTORS[target_key]
        return converted_value
