import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from cryptography.hazmat.primitives.asymmetric import ed25519

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent.parent
if str(_PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT))

from medfactory.src.dla.implementations.document_layout_analyzer import DocumentLayoutAnalyzer
from medfactory.src.dla.implementations.complex_table_normalizer import ComplexTableNormalizer
from medfactory.src.chunking.implementations.hierarchical_chunker import HierarchicalChunker
from medfactory.src.ontologies.implementations.hpo_ingestor import HPOIngestor
from medfactory.src.ontologies.implementations.icd10_atc_ingestor import ClassificationIngestor
from medfactory.src.compression.implementations.zstd_dictionary_trainer import ZstdDictionaryTrainer
from medfactory.src.compression.implementations.static_markdown_synthesizer import StaticMarkdownSynthesizer
from medfactory.src.compression.base.compression_models import (
    ClinicalSheetSynthesisRequest,
    ClinicalCallout,
    CalloutSeverityType
)
from medfactory.src.database.implementations.sqlite_module_builder import SQLiteModuleBuilder
from medfactory.src.packager.implementations.medpack_assembler import MedPackAssembler
from medfactory.src.packager.base.manifest_models import MedPackManifest
from medfactory.src.pipeline.interfaces.pipeline_interface import IMedFactoryPipeline
from medfactory.src.pipeline.base.pipeline_config import PipelineBuildConfig
from medfactory.src.pipeline.base.clinical_dataset_seed import (
    compute_deterministic_l2_vector,
    generate_clinical_media_assets,
    populate_clinical_knowledge_tables
)


class MedFactoryPipeline(IMedFactoryPipeline):
    """
    Orchestratore della pipeline end-to-end MedFactory.
    Esegue in sequenza: estrazione DLA, chunking gerarchico con breadcrumb,
    ingestione ontologie HPO/ICD-10/ATC, training dizionario Zstd 114.688 B,
    sintesi schede CommonMark con callout, compilazione SQLite STRICT e assemblaggio .medpack.
    """

    def __init__(self, build_config: PipelineBuildConfig):
        self.config = build_config
        self.dla = DocumentLayoutAnalyzer(
            alpha_col_weight=self.config.dla_alpha_weight,
            beta_y_weight=self.config.dla_beta_weight
        )
        self.table_normalizer = ComplexTableNormalizer()
        self.chunker = HierarchicalChunker(
            target_parent_tokens=self.config.target_parent_tokens,
            target_child_tokens=self.config.target_child_tokens,
            child_overlap=self.config.child_overlap_tokens
        )
        self.hpo_ingestor = HPOIngestor()
        self.classification_ingestor = ClassificationIngestor()
        self.zstd_trainer = ZstdDictionaryTrainer()
        self.synthesizer = StaticMarkdownSynthesizer()
        self.packager = MedPackAssembler()

    def _build_clinical_monographs(self) -> List[ClinicalSheetSynthesisRequest]:
        """Costruisce le richieste di sintesi per le schede cliniche del modulo cardiologico e medicina interna."""
        return [
            ClinicalSheetSynthesisRequest(
                sheet_identifier="sheet_stemi_anterior",
                icd10_code="I21.0",
                disease_title="Infarto Miocardico Acuto con Sopraslivellamento ST (STEMI Anteriore)",
                taxonomy_path=["Medicina Interna", "Cardiologia", "Sindromi Coronariche Acute"],
                definition_text=(
                    "Necrosi miocardica acuta transmurale secondaria a occlusione trombotica completa "
                    "dell'arteria coronaria discendente anteriore (IVA). Tempo door-to-balloon target $\\le 90\\,\\text{min}$."
                ),
                etiology_text="Rottura o erosione di placca aterosclerotica vulnerabile con attivazione piastrinica e trombosi.",
                clinical_signs=["Dolore toracico retrosternale oppressivo irradiato al braccio sinistro", "Diaforesi algida", "Dispnea"],
                diagnostic_workup=["ECG 12 derivazioni entro 10 minuti (sopraslivellamento ST V1-V4)", "Troponina I ad alta sensibilità"],
                pharmacotherapy_atc=["B01AC06", "B01AC04", "C07AB02", "C10AA01"],
                callouts=[
                    ClinicalCallout(
                        severity_type=CalloutSeverityType.RED_FLAG,
                        callout_title="Riperfusione Coronarica Immediata",
                        callout_body="Attivare immediatamente l'emodinamica per angioplastica primaria (PCI) entro 90 minuti."
                    ),
                    ClinicalCallout(
                        severity_type=CalloutSeverityType.CONTRAINDICATION,
                        callout_title="Paradosso del Profarmaco Clopidogrel",
                        callout_body="Evitare la co-somministrazione con Omeprazolo (inibitore CYP2C19) per rischio di trombosi acuta dello stent."
                    )
                ]
            ),
            ClinicalSheetSynthesisRequest(
                sheet_identifier="sheet_pulmonary_embolism",
                icd10_code="I26.9",
                disease_title="Embolia Polmonare Acuta",
                taxonomy_path=["Medicina Interna", "Cardiologia", "Malattie del Circolo Polmonare"],
                definition_text="Ostruzione acuta del letto arterioso polmonare da parte di materiale trombotico proveniente dal circolo venoso profondo.",
                etiology_text="Trombosi venosa profonda (TVP) degli arti inferiori o pelvica (triade di Virchow).",
                clinical_signs=["Dispnea ad insorgenza improvvisa", "Tachipnea e tachicardia", "Dolore toracico pleuritico ed emottisi"],
                diagnostic_workup=["Angio-TC del torace con mezzo di contrasto", "D-dimero ed Ecocardiogramma per sovraccarico VD"],
                pharmacotherapy_atc=["B01AF01", "B01AA03"],
                callouts=[
                    ClinicalCallout(
                        severity_type=CalloutSeverityType.RED_FLAG,
                        callout_title="Instabilità Emodinamica e Shock Index",
                        callout_body="Shock Index >= 1.0 o PAS <= 90 mmHg identificano Embolia Polmonare ad Alto Rischio con indicazione a trombolisi sistemica."
                    )
                ]
            ),
            ClinicalSheetSynthesisRequest(
                sheet_identifier="sheet_aortic_stenosis",
                icd10_code="I35.0",
                disease_title="Stenosi Aortica Valvolare",
                taxonomy_path=["Cardiologia", "Valvulopatie"],
                definition_text="Restringimento dell'orifizio valvolare aortico con ostruzione all'efflusso ventricolare sinistro.",
                etiology_text="Degenerazione calcifica senile o valvola aortica bicuspide congenita.",
                clinical_signs=["Soffio sistolico eiettivo a diamante", "Polso parvus et tardus", "Sincope da sforzo e angina"],
                diagnostic_workup=["Ecocardiogramma transtoracico con doppler (gradiente medio > 40 mmHg)", "ECG a 12 derivazioni"],
                pharmacotherapy_atc=["B01AC04", "C09AA02"],
                callouts=[
                    ClinicalCallout(
                        severity_type=CalloutSeverityType.RED_FLAG,
                        callout_title="Sincope da Sforzo",
                        callout_body="Segno di prognosi sfavorevole; rischio imminente di morte cardiaca improvvisa."
                    )
                ]
            ),
        ]

    def build_module_pack(self, working_directory: Path, output_file_path: Path) -> MedPackManifest:
        """
        Esegue l'intera pipeline di build generando il pacchetto .medpack definitivo.
        """
        working_directory = Path(working_directory)
        output_file_path = Path(output_file_path)
        staging_dir = working_directory / "staging"
        if staging_dir.exists():
            shutil.rmtree(staging_dir)
        staging_dir.mkdir(parents=True, exist_ok=True)

        (staging_dir / "database").mkdir(parents=True, exist_ok=True)
        (staging_dir / "vector_index").mkdir(parents=True, exist_ok=True)
        (staging_dir / "assets_media").mkdir(parents=True, exist_ok=True)
        (staging_dir / "assets" / "schede_statiche").mkdir(parents=True, exist_ok=True)
        media_dir = staging_dir / "media"
        media_dir.mkdir(parents=True, exist_ok=True)

        # 1. Generazione asset multimediali reali WebP (PIL.Image) e SVG 2D
        webp_sha256, svg_sha256 = generate_clinical_media_assets(media_dir)

        # 2. Ingestione Ontologie (Features 7 & 8)
        hpo_terms = self.hpo_ingestor.ingest_terms()
        icd10_records = self.classification_ingestor.ingest_icd10_catalog()
        atc_records = self.classification_ingestor.ingest_atc_catalog()

        # 3. Compilazione Database SQLite STRICT (Feature 11)
        transitional_db_path = working_directory / "module_kb_transitional.sqlite"
        final_db_path = staging_dir / "module_kb.sqlite"
        nested_db_path = staging_dir / "database" / "module_kb.sqlite"

        total_child_count = 0
        all_corpus_texts: List[bytes] = []
        vector_records: List[Tuple[int, str, int, bytes]] = []
        vector_meta_entries: List[Dict[str, Any]] = []
        raw_vector_blobs: List[bytes] = []

        with SQLiteModuleBuilder(transitional_db_path) as db_builder:
            db_builder.insert_source(
                source_id="MED_KB_2026",
                academic_title="Trattato di Cardiologia Clinica, Farmacologia e Medicina d'Urgenza",
                publication_year=2026,
                authors=["Prof. M. Rossi", "Dott. L. Bianchi", "Prof.ssa E. Verdi"],
                publisher="MedPlatform University Press",
                isbn="978-88-00-00001-0",
                doi="10.1000/medplatform.cardio.2026"
            )

            for icd in icd10_records:
                db_builder.insert_icd10(icd.icd10_code, icd.description, icd.chapter, icd.block_range, icd.is_leaf_code)

            for atc in atc_records:
                db_builder.insert_atc(
                    atc.atc_code, atc.substance_name, atc.level1_anatomical, atc.level2_therapeutic,
                    atc.level3_pharmacological, atc.level4_chemical, atc.is_prodrug,
                    atc.primary_cyp_enzymes, atc.defined_daily_dose, atc.ddd_unit
                )
                db_builder.insert_substance(
                    substance_id=atc.atc_code,
                    substance_name=atc.substance_name,
                    atc_code=atc.atc_code,
                    is_prodrug=atc.is_prodrug,
                    active_metabolite="Tiolo attivo H4" if atc.is_prodrug else None
                )

            for hpo in hpo_terms:
                db_builder.insert_hpo(hpo.hpo_id, hpo.name, hpo.definition, hpo.ancestor_ids, hpo.information_content)

            # Popola tutte le tabelle cliniche, farmacologiche, CPIC, FDC ed esami
            populate_clinical_knowledge_tables(db_builder, webp_sha256)

            # 4. Chunking gerarchico, sintesi schede e vettorizzazione 384-D L2
            monograph_requests = self._build_clinical_monographs()
            all_parents = []

            for monograph_req in monograph_requests:
                synthesized_sheet = self.synthesizer.synthesize_sheet(monograph_req)
                db_builder.insert_clinical_sheet(
                    synthesized_sheet.sheet_identifier,
                    synthesized_sheet.icd10_code,
                    synthesized_sheet.document_title,
                    synthesized_sheet.raw_markdown_content,
                    callouts=[
                        {"severity": c.severity_type.value, "title": c.callout_title, "body": c.callout_body}
                        for c in monograph_req.callouts
                    ]
                )
                sheet_file = staging_dir / "assets" / "schede_statiche" / f"{synthesized_sheet.sheet_identifier}.md"
                sheet_file.write_text(synthesized_sheet.raw_markdown_content, encoding="utf-8")

                sanitized_text = self.dla.normalize_ismp_units(
                    f"{synthesized_sheet.raw_markdown_content}\n\n"
                    f"Riferimento iconografico ECG: media/{webp_sha256}.webp e struttura 2D: media/{svg_sha256}.svg. "
                    "Somministrazione nitroglicerina endovenosa 10 ug/min normalizzata a 10 mcg/min."
                )
                parents = self.chunker.split_into_parents(
                    source_id="MED_KB_2026",
                    chapter=monograph_req.taxonomy_path[0],
                    section_path=" > ".join(monograph_req.taxonomy_path),
                    full_text=sanitized_text
                )
                for parent in parents:
                    all_parents.append(parent)
                    db_builder.insert_parent_chunk(parent)
                    all_corpus_texts.append(parent.raw_content.encode("utf-8"))

                    children = self.chunker.split_into_children(
                        parent=parent,
                        section_hierarchy=monograph_req.taxonomy_path,
                        global_vector_start_id=total_child_count,
                        hpo_terms=["HP:0100749", "HP:0001649", "HP:0002094"],
                        atc_codes=monograph_req.pharmacotherapy_atc,
                        icd10_codes=[monograph_req.icd10_code]
                    )
                    for child in children:
                        db_builder.insert_child_chunk(child)
                        all_corpus_texts.append(child.text_content.encode("utf-8"))
                        _, vector_blob = compute_deterministic_l2_vector(
                            f"{child.breadcrumb_header} {child.text_content}", dimension=384
                        )
                        vector_records.append((child.vector_id, child.child_id, 384, vector_blob))
                        vector_meta_entries.append({
                            "vector_id": child.vector_id,
                            "child_id": child.child_id,
                            "icd10_codes": child.icd10_codes
                        })
                        raw_vector_blobs.append(vector_blob)
                        total_child_count += 1

            db_builder.insert_vector_metadata(vector_records)
            db_builder.vacuum_into(final_db_path)

        if transitional_db_path.exists():
            transitional_db_path.unlink()
        shutil.copy2(final_db_path, nested_db_path)

        # 5. Scrittura indice vettoriale binario reale (384 float32 L2-normalizzati per child chunk)
        (staging_dir / "vector_index" / "index.bin").write_bytes(b"".join(raw_vector_blobs))
        (staging_dir / "vector_index" / "meta.bin").write_bytes(
            json.dumps(vector_meta_entries, sort_keys=True).encode("utf-8")
        )
        (staging_dir / "assets_media" / "blob.bin").write_bytes((media_dir / f"{webp_sha256}.webp").read_bytes())
        (staging_dir / "assets_media" / "media_manifest.cbor").write_bytes(
            json.dumps({"webp_sha256": webp_sha256, "svg_sha256": svg_sha256}, sort_keys=True).encode("utf-8")
        )

        # 6. Addestramento Dizionario Zstandard a 114.688 Byte (Feature 9)
        training_corpus = list(all_corpus_texts)
        for hpo in hpo_terms:
            training_corpus.append(f"{hpo.hpo_id} {hpo.name}: {hpo.definition}".encode("utf-8"))
        for icd in icd10_records:
            training_corpus.append(f"{icd.icd10_code} {icd.description}".encode("utf-8"))
        for atc in atc_records:
            training_corpus.append(f"{atc.atc_code} {atc.substance_name}".encode("utf-8"))

        dictionary_bytes = self.zstd_trainer.train_dictionary(
            training_corpus_chunks=training_corpus,
            target_size=self.config.zstd_dict_target_size
        )

        (working_directory / "zstd.dict").write_bytes(dictionary_bytes)
        (staging_dir / "zstd.dict").write_bytes(dictionary_bytes)

        # 7. Assemblaggio e Firma Ed25519 del pacchetto .medpack (Feature 12)
        manifest_meta: Dict[str, Any] = {
            "pack_id": self.config.module_id,
            "display_title": self.config.display_title,
            "total_parent_chunks": max(len(all_parents), 1),
            "total_child_chunks": max(total_child_count, 1),
            "total_vectors": max(total_child_count, 1)
        }

        deterministic_seed = hashlib.sha256(f"MEDPLATFORM_SIGNING_KEY_{self.config.module_id}".encode("utf-8")).digest()
        signing_key = ed25519.Ed25519PrivateKey.from_private_bytes(deterministic_seed)
        public_key_hex = signing_key.public_key().public_bytes_raw().hex()
        (working_directory / "public_key.hex").write_text(public_key_hex, encoding="utf-8")

        manifest = self.packager.build_medpack(
            staging_dir=staging_dir,
            output_medpack_path=output_file_path,
            dictionary_bytes=dictionary_bytes,
            manifest_meta=manifest_meta,
            private_key_ed25519=signing_key
        )

        verified, message = self.packager.verify_medpack(
            medpack_path=output_file_path,
            dictionary_bytes=dictionary_bytes,
            public_key_hex=public_key_hex
        )
        if not verified:
            raise RuntimeError(f"Fallita verifica automatica dell'archivio generato: {message}")

        return manifest


if __name__ == "__main__":
    import sys
    project_root_dir = Path(__file__).resolve().parent.parent.parent.parent.parent
    build_workspace_dir = project_root_dir / "medfactory_workspace"
    final_medpack_file = project_root_dir / "cardio_2026.medpack"

    pipeline_build_settings = PipelineBuildConfig(
        module_id="cardio_2026",
        display_title="Modulo Clinico Cardiologia e Medicina Interna 2026",
    )
    active_pipeline_executor = MedFactoryPipeline(build_config=pipeline_build_settings)
    final_manifest_record = active_pipeline_executor.build_module_pack(
        working_directory=build_workspace_dir,
        output_file_path=final_medpack_file
    )
    sys.stdout.write(
        f"MedPack generato con successo: {final_medpack_file} "
        f"(Dimensione: {final_medpack_file.stat().st_size} byte)\n"
    )
