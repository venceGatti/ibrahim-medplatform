from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class PipelineBuildConfig:
    """Configurazione deterministica della pipeline MedFactory."""
    module_id: str
    display_title: str
    dla_alpha_weight: float = 10000.0
    dla_beta_weight: float = 1.0
    target_parent_tokens: int = 1000
    target_child_tokens: int = 200
    child_overlap_tokens: int = 30
    zstd_dict_target_size: int = 114688
    zstd_compression_level: int = 19
    hpo_release_version: str = "2024-04-13"
    icd10_release_version: str = "2019-v1"
    atc_index_year: int = 2024
    compiler_version: str = "medfactory-dla-v1.4.2"
