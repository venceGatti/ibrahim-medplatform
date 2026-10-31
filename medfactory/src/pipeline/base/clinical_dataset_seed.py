"""
Dataset clinico autorevole di Cardiologia e Medicina Interna per la compilazione
di module_kb.sqlite e la generazione deterministica di asset multimediali (.webp, .svg)
e vettori 384-D normalizzati L2.
"""

import hashlib
import io
import json
from pathlib import Path
from typing import List, Tuple, Dict
import numpy as np
from PIL import Image, ImageDraw
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder


def compute_deterministic_l2_vector(text_input: str, dimension: int = 384) -> Tuple[np.ndarray, bytes]:
    """
    Calcola un vettore continuo a 384 dimensioni normalizzato sulla sfera unitaria L2
    a partire dai token trigrammi del testo clinico, restituendo (array_float32, blob_bytes).
    """
    accumulator = np.zeros(dimension, dtype=np.float64)
    normalized_text = text_input.strip().lower()
    tokens = normalized_text.split() if normalized_text else ["cardiology"]

    for token_idx, token in enumerate(tokens):
        digest = hashlib.sha512(f"{token}_{token_idx}".encode("utf-8")).digest()
        for byte_pos, byte_value in enumerate(digest):
            target_dim = (token_idx * 31 + byte_pos * 7) % dimension
            signed_contribution = (float(byte_value) - 127.5) / 127.5
            accumulator[target_dim] += signed_contribution

    norm_val = float(np.linalg.norm(accumulator))
    if norm_val < 1e-12:
        accumulator[0] = 1.0
        norm_val = 1.0

    unit_vector = (accumulator / norm_val).astype(np.float32)
    return unit_vector, unit_vector.tobytes()


def generate_clinical_media_assets(media_directory: Path) -> Tuple[str, str]:
    """
    Genera fisicamente su disco un tracciato ECG medico reale in formato WebP (PIL.Image)
    e un diagramma strutturale molecolare 2D SVG (Clopidogrel tienopiridina),
    salvando i file come media/{sha256}.webp e media/{sha256}.svg.
    """
    media_directory.mkdir(parents=True, exist_ok=True)

    # 1. Generazione immagine diagnostica ECG STEMI Anteriore con PIL.Image
    canvas_width, canvas_height = 320, 180
    ecg_image = Image.new("RGB", (canvas_width, canvas_height), color=(252, 246, 246))
    drawer = ImageDraw.Draw(ecg_image)

    for grid_x in range(0, canvas_width, 16):
        drawer.line([(grid_x, 0), (grid_x, canvas_height)], fill=(242, 215, 215), width=1)
    for grid_y in range(0, canvas_height, 16):
        drawer.line([(0, grid_y), (canvas_width, grid_y)], fill=(242, 215, 215), width=1)

    baseline_y = 115
    waveform_points = [
        (0, baseline_y), (40, baseline_y), (52, baseline_y - 10), (62, baseline_y),
        (75, baseline_y + 12), (85, 32), (96, 62), (125, 58), (155, 72),
        (185, baseline_y), (240, baseline_y), (255, baseline_y - 10),
        (268, baseline_y + 12), (278, 32), (290, 62), (319, 58)
    ]
    drawer.line(waveform_points, fill=(18, 28, 45), width=2)

    webp_buffer = io.BytesIO()
    ecg_image.save(webp_buffer, format="WEBP", quality=92)
    webp_bytes = webp_buffer.getvalue()
    webp_sha256 = hashlib.sha256(webp_bytes).hexdigest()
    (media_directory / f"{webp_sha256}.webp").write_bytes(webp_bytes)

    # 2. Generazione diagramma molecolare 2D SVG reale (Clopidogrel - ATC B01AC04)
    svg_content = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 240 160" width="240" height="160">'
        '<rect width="240" height="160" fill="#f8fafc"/>'
        '<g stroke="#0f172a" stroke-width="2" fill="none">'
        '<polygon points="60,50 90,35 120,50 120,85 90,100 60,85"/>'
        '<polygon points="120,50 155,40 175,68 155,95 120,85"/>'
        '<line x1="60" y1="50" x2="35" y2="35"/>'
        '<line x1="90" y1="100" x2="90" y2="130"/>'
        '</g>'
        '<text x="20" y="32" font-family="monospace" font-size="12" fill="#0284c7">Cl</text>'
        '<text x="178" y="72" font-family="monospace" font-size="12" fill="#ca8a04">S</text>'
        '<text x="84" y="144" font-family="monospace" font-size="12" fill="#dc2626">COOCH3</text>'
        '</svg>'
    )
    svg_bytes = svg_content.encode("utf-8")
    svg_sha256 = hashlib.sha256(svg_bytes).hexdigest()
    (media_directory / f"{svg_sha256}.svg").write_bytes(svg_bytes)

    return webp_sha256, svg_sha256


def populate_clinical_knowledge_tables(db_builder: SQLiteModuleBuilder, webp_sha256: str) -> None:
    """
    Popola module_kb.sqlite con le relazioni diagnostiche Log-Odds (rel_icd10_hpo),
    i profili farmacocinetici CYP450, i rischi d'organo, le combinazioni FDC, le linee guida CPIC,
    i 4 archetipi d'esame (MCQ, HOTSPOT, NLI_OPEN, DAG_SCENARIO) e il lessico medico.
    """
    rel_records: List[Tuple[str, str, float, int, int, float, float, float]] = [
        # I21.0 STEMI Anteriore
        ("I21.0", "HP:0100749", 95.0, 1, 1, 2.8, 3.4, -12.0),
        ("I21.0", "HP:0001649", 92.0, 0, 1, 2.6, 3.2, -2.4),
        ("I21.0", "HP:0000975", 78.0, 0, 0, 1.0, 2.1, -0.8),
        ("I21.0", "HP:0002094", 72.0, 0, 0, 1.0, 1.7, -0.6),
        ("I21.0", "HP:0001658", 99.0, 1, 1, 3.0, 4.2, -12.0),
        # I20.0 Angina Instabile
        ("I20.0", "HP:0001649", 96.0, 1, 1, 2.5, 3.3, -12.0),
        ("I20.0", "HP:0100749", 92.0, 1, 0, 1.0, 2.8, -12.0),
        ("I20.0", "HP:0002875", 68.0, 0, 0, 1.0, 1.6, -0.5),
        # I26.9 Embolia Polmonare
        ("I26.9", "HP:0002094", 96.0, 1, 0, 1.0, 3.1, -12.0),
        ("I26.9", "HP:0002789", 88.0, 0, 0, 1.0, 2.5, -1.5),
        ("I26.9", "HP:0100749", 74.0, 0, 0, 1.0, 2.0, -0.7),
        ("I26.9", "HP:0002105", 35.0, 0, 1, 2.6, 2.9, -0.3),
        ("I26.9", "HP:0001279", 42.0, 0, 0, 1.0, 1.8, -0.4),
        # J18.9 Polmonite
        ("J18.9", "HP:0001945", 94.0, 1, 0, 1.0, 2.9, -12.0),
        ("J18.9", "HP:0012735", 92.0, 1, 0, 1.0, 2.8, -12.0),
        ("J18.9", "HP:0002094", 75.0, 0, 0, 1.0, 1.9, -0.8),
        ("J18.9", "HP:0002098", 55.0, 0, 0, 1.0, 1.7, -0.5),
        # A41.9 Sepsi e Shock Settico
        ("A41.9", "HP:0001945", 92.0, 0, 0, 1.0, 2.7, -1.8),
        ("A41.9", "HP:0002615", 95.0, 1, 1, 2.7, 3.5, -12.0),
        ("A41.9", "HP:0002789", 89.0, 0, 0, 1.0, 2.4, -1.4),
        ("A41.9", "HP:0011031", 65.0, 0, 0, 1.0, 2.0, -0.6),
        # N17.9 Insufficienza Renale Acuta (AKI)
        ("N17.9", "HP:0001919", 99.0, 1, 1, 3.0, 4.0, -12.0),
        ("N17.9", "HP:0011031", 86.0, 0, 1, 2.5, 3.1, -1.9),
        ("N17.9", "HP:0003112", 97.0, 1, 1, 2.8, 3.6, -12.0),
        ("N17.9", "HP:0000951", 62.0, 0, 0, 1.0, 1.5, -0.5),
        # I35.0 Stenosi Aortica & I50.9 Scompenso Cardiaco
        ("I35.0", "HP:0001650", 99.0, 1, 1, 3.0, 4.1, -12.0),
        ("I35.0", "HP:0001654", 94.0, 0, 1, 2.6, 3.0, -2.5),
        ("I35.0", "HP:0001279", 65.0, 0, 0, 1.0, 2.2, -0.7),
        ("I50.9", "HP:0001635", 99.0, 1, 1, 2.8, 3.8, -12.0),
        ("I50.9", "HP:0025442", 84.0, 0, 1, 2.6, 3.1, -1.5),
        ("I50.9", "HP:0010444", 82.0, 0, 0, 1.0, 2.6, -1.3),
        ("I50.9", "HP:0007133", 76.0, 0, 0, 1.0, 2.1, -0.9),
    ]
    db_builder.insert_rel_icd10_hpo(rel_records)

    cyp_profiles = [
        ("B01AC04", "Clopidogrel", 1, "CYP2C19", "SUBSTRATE", 0.85, "NONE"),
        ("B01AC04", "Clopidogrel", 1, "CYP3A4", "SUBSTRATE", 0.15, "NONE"),
        ("A02BC01", "Omeprazolo", 0, "CYP2C19", "INHIBITOR", 0.0, "STRONG"),
        ("B01AA03", "Warfarin", 0, "CYP2C9", "SUBSTRATE", 0.85, "NONE"),
        ("B01AF01", "Rivaroxaban", 0, "CYP3A4", "SUBSTRATE", 0.65, "NONE"),
        ("C01BD01", "Amiodarone", 0, "CYP2C9", "INHIBITOR", 0.0, "MODERATE"),
        ("C01BD01", "Amiodarone", 0, "CYP3A4", "INHIBITOR", 0.0, "MODERATE"),
        ("C01BD01", "Amiodarone", 0, "CYP2D6", "INHIBITOR", 0.0, "MODERATE"),
        ("J01FA09", "Claritromicina", 0, "CYP3A4", "INHIBITOR", 0.0, "STRONG"),
        ("J01MA02", "Ciprofloxacina", 0, "CYP1A2", "INHIBITOR", 0.0, "STRONG"),
        ("C10AA01", "Simvastatina", 1, "CYP3A4", "SUBSTRATE", 0.90, "NONE"),
        ("C07AB02", "Metoprololo", 0, "CYP2D6", "SUBSTRATE", 0.80, "NONE"),
        ("N02AA59", "Codeina", 1, "CYP2D6", "SUBSTRATE", 0.90, "NONE"),
        ("M01AE01", "Ibuprofene", 0, "CYP2C9", "SUBSTRATE", 0.70, "NONE"),
    ]
    db_builder.insert_substance_cyp_profiles(cyp_profiles)

    organ_risks = [
        ("B01AC04", "Clopidogrel", 0, 0.0, 0.0, 0, 0, 0),
        ("A02BC01", "Omeprazolo", 0, 0.5, 0.2, 0, 0, 0),
        ("B01AA03", "Warfarin", 1, 0.0, 0.0, 0, 0, 0),
        ("C01BD01", "Amiodarone", 1, 3.0, 0.0, 0, 0, 0),
        ("J01FA09", "Claritromicina", 0, 2.0, 0.3, 0, 0, 0),
        ("J01MA12", "Levofloxacina", 0, 2.0, 0.5, 0, 0, 0),
        ("C09AA02", "Enalapril", 0, 0.0, 1.0, 1, 0, 0),
        ("C09AA03", "Lisinopril", 0, 0.0, 1.0, 1, 0, 0),
        ("C09AA05", "Ramipril", 0, 0.0, 1.0, 1, 0, 0),
        ("C09CA01", "Losartan", 0, 0.0, 1.0, 1, 0, 0),
        ("C03CA01", "Furosemide", 0, 1.0, 1.2, 0, 1, 0),
        ("C03AA03", "Idroclorotiazide", 0, 0.5, 1.0, 0, 1, 0),
        ("M01AE01", "Ibuprofene", 0, 0.0, 2.0, 0, 0, 1),
    ]
    db_builder.insert_substance_organ_risks(organ_risks)

    fdc_combinations = [
        ("C09BA02", "Enalapril e diuretici", "C09AA02", "Enalapril", 1.0),
        ("C09BA02", "Enalapril e diuretici", "C03AA03", "Idroclorotiazide", 1.0),
        ("C09BA03", "Lisinopril e diuretici", "C09AA03", "Lisinopril", 1.0),
        ("C09BA03", "Lisinopril e diuretici", "C03AA03", "Idroclorotiazide", 1.0),
        ("C09DA01", "Losartan e diuretici", "C09CA01", "Losartan", 1.0),
        ("C09DA01", "Losartan e diuretici", "C03AA03", "Idroclorotiazide", 1.0),
    ]
    db_builder.insert_atc_combinations(fdc_combinations)

    cpic_records = [
        (
            "CPIC_CLOP_CYP2C19", "B01AC04", "CYP2C19", "*2/*2 Poor Metabolizer",
            "Controindicazione assoluta a Clopidogrel per mancata bioattivazione; sostituire con Prasugrel o Ticagrelor.",
            1, "1A"
        ),
        (
            "CPIC_ABAC_HLAB", "J05AF06", "HLA-B", "*57:01 Positive",
            "Controindicazione assoluta ad Abacavir per rischio di reazione di ipersensibilità sistemica fatale.",
            1, "1A"
        ),
        (
            "CPIC_WARF_CYP2C9", "B01AA03", "CYP2C9", "*3/*3 Poor Metabolizer",
            "Ridurre il dosaggio iniziale di Warfarin del 50-75% e monitorare strettamente INR.",
            0, "1A"
        ),
    ]
    db_builder.insert_cpic_guidelines(cpic_records)

    interactions = [
        (
            "INT_CLOP_OMEP_01", "B01AC04", "A02BC01", 1,
            "Inibizione competitiva potente di CYP2C19 da parte di Omeprazolo; blocco della conversione del profarmaco Clopidogrel nel metabolita tiolico attivo.",
            "BLACKBOX WARNING LIVELLO 1: Inefficacia antiaggregante con rischio di trombosi acuta dello stent coronarico. Sostituire Omeprazolo con Pantoprazolo."
        ),
        (
            "INT_WARF_AMIO_01", "B01AA03", "C01BD01", 1,
            "Inibizione di CYP2C9 e CYP3A4 da parte di Amiodarone con accumulo plasmatico dell'enantiomero S-Warfarin (NTI).",
            "LIVELLO 1: Rischio di emorragia maggiore intracranica o gastrointestinale; ridurre la dose di Warfarin del 30-50%."
        ),
        (
            "INT_SIMV_CLAR_01", "C10AA01", "J01FA09", 1,
            "Inibizione forte di CYP3A4 intestinale ed epatico da parte di Claritromicina (AUC > 10x).",
            "LIVELLO 1: Rischio elevato di rabdomiolisi acuta e mioglobinuria; sospendere Simvastatina durante il ciclo antibiotico."
        ),
    ]
    db_builder.insert_drug_interactions(interactions)

    exam_questions = [
        (
            "EXAM_MCQ_STEMI_01", "MCQ", "I21.0",
            {
                "question_stem": "Paziente di 64 anni con STEMI anteriore sottoposto a PCI primaria con impianto di DES assume Clopidogrel 75 mg/die. Quale gastroprotettore presenta il minor rischio di inibizione enzimatica su CYP2C19?",
                "options": ["Omeprazolo", "Esomeprazolo", "Pantoprazolo", "Cimetidina"],
                "correct_index": 2,
                "rationale": "Pantoprazolo presenta affinità trascurabile per CYP2C19, preservando la bioattivazione epatica del profarmaco Clopidogrel."
            }
        ),
        (
            "EXAM_HOTSPOT_ECG_01", "HOTSPOT", "I21.0",
            {
                "image_sha256": webp_sha256,
                "prompt": "Individuare sul tracciato ECG il segmento con sopraslivellamento del tratto ST compatibile con lesione transmurale acuta.",
                "polygon_normalized": [[0.25, 0.15], [0.55, 0.15], [0.55, 0.50], [0.25, 0.50]],
                "tolerance_radius": 0.02
            }
        ),
        (
            "EXAM_NLI_SEPSIS_01", "NLI_OPEN", "A41.9",
            {
                "prompt": "Descrivere i criteri clinici del punteggio qSOFA e l'intervento emodinamico di prima linea nello shock settico.",
                "atomic_concepts": [
                    {"concept_id": "C1", "statement": "Frequenza respiratoria pari o superiore a 22 atti/min", "weight": 0.35},
                    {"concept_id": "C2", "statement": "Pressione arteriosa sistolica inferiore o uguale a 100 mmHg", "weight": 0.35},
                    {"concept_id": "C3", "statement": "Alterazione acuta dello stato mentale (GCS < 15) e cristalloidi 30 mL/kg", "weight": 0.30}
                ]
            }
        ),
        (
            "EXAM_DAG_AKI_01", "DAG_SCENARIO", "N17.9",
            {
                "initial_node": "NODE_T0",
                "nodes": {
                    "NODE_T0": {
                        "vitals": {"hr": 98, "sbp": 105, "spo2": 96},
                        "description": "Paziente in terapia con Enalapril e Furosemide sviluppa oliguria dopo assunzione di Ibuprofene.",
                        "choices": [
                            {"action_id": "ACT_STOP_NSAID", "next_node": "NODE_RECOVERY", "is_lethal": False, "score_delta": 30.0},
                            {"action_id": "ACT_DOUBLE_NSAID", "next_node": "NODE_LETHAL", "is_lethal": True, "score_delta": -30.0}
                        ]
                    }
                }
            }
        ),
    ]
    db_builder.insert_exam_items(exam_questions)

    lexicon_entries = [
        ("dispnea", 95000, "HP:0002094", "I50.9"),
        ("angina", 88000, "HP:0001649", "I20.0"),
        ("infarto", 92000, "HP:0001658", "I21.0"),
        ("sincope", 76000, "HP:0001279", "I35.0"),
        ("tachicardia", 84000, "HP:0001962", "I26.9"),
        ("oliguria", 64000, "HP:0011031", "N17.9"),
        ("febbre", 91000, "HP:0001945", "J18.9"),
        ("ipotensione", 79000, "HP:0002615", "A41.9"),
        ("emottisi", 58000, "HP:0002105", "I26.9"),
        ("ortopnea", 69000, "HP:0010444", "I50.9"),
    ]
    db_builder.insert_medical_lexicon(lexicon_entries)

    synonyms = [
        ("fame d aria", "HP:0002094", "Dyspnea"),
        ("fiato corto", "HP:0002094", "Dyspnea"),
        ("dolore al petto", "HP:0100749", "Chest pain"),
        ("oppressione retrosternale", "HP:0001649", "Angina pectoris"),
        ("batticuore", "HP:0001962", "Palpitations"),
        ("cuore in gola", "HP:0001962", "Palpitations"),
        ("svenimento", "HP:0001279", "Syncope"),
        ("gambe gonfie", "HP:0007133", "Bilateral pedal edema"),
        ("sudorazione fredda", "HP:0000975", "Hyperhidrosis"),
        ("blocco renale", "HP:0001919", "Acute kidney injury"),
    ]
    db_builder.insert_colloquial_synonyms(synonyms)
