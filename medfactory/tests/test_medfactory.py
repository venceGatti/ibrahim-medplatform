import pytest
import tempfile
from pathlib import Path
import json

from medfactory.src.dla.layout_analyzer import DocumentLayoutAnalyzer, BoundingBox
from medfactory.src.dla.table_resolver import TableSpanResolver, TableCell
from medfactory.src.chunking.hierarchical_chunker import HierarchicalChunker, ParentChunk, ChildChunk
from medfactory.src.compression.zstd_compressor import ZstdDictionaryCompressor
from medfactory.src.database.sqlite_builder import SQLiteModuleBuilder
from medfactory.src.packager.medpack_assembler import MedPackAssembler


def test_dla_reading_order_and_ismp():
    analyzer = DocumentLayoutAnalyzer()
    boxes = [
        BoundingBox(col_id=1, y_pos=10.0, x_pos=100.0, width=50.0, height=20.0, text_content="Col 2 Line 1"),
        BoundingBox(col_id=0, y_pos=50.0, x_pos=10.0, width=50.0, height=20.0, text_content="Col 1 Line 2: Somministrare 50 µg"),
        BoundingBox(col_id=0, y_pos=10.0, x_pos=10.0, width=50.0, height=20.0, text_content="Col 1 Line 1: Digossina 25 ug/ml"),
    ]
    reconstructed = analyzer.reconstruct_text(boxes)
    assert "Col 1 Line 1: Digossina 25 mcg/ml" in reconstructed
    assert "Col 1 Line 2: Somministrare 50 mcg" in reconstructed
    assert reconstructed.index("Col 1 Line 1") < reconstructed.index("Col 1 Line 2")
    assert reconstructed.index("Col 1 Line 2") < reconstructed.index("Col 2 Line 1")


def test_table_span_resolver():
    resolver = TableSpanResolver()
    # Tabella 2x2 con rowspan e colspan
    raw_table = [
        [TableCell("Header 1", col_span=2)],
        [TableCell("Colonna A", row_span=2), TableCell("Colonna B1")],
        [TableCell("Colonna B2")]
    ]
    grid = resolver.resolve_grid(raw_table)
    assert len(grid) == 3
    assert grid[0] == ["Header 1", "Header 1"]
    assert grid[1] == ["Colonna A", "Colonna B1"]
    assert grid[2] == ["Colonna A", "Colonna B2"]


def test_hierarchical_chunking_and_breadcrumb():
    chunker = HierarchicalChunker(target_child_tokens=200, child_overlap=20)
    text = " ".join([f"token_{i}" for i in range(850)])
    parent = ParentChunk(
        parent_id="p_test_1",
        source_id="urn:isbn:9788821445678",
        chapter="Cardiologia",
        section_path="Scompenso > Terapia",
        page_start=12,
        page_end=14,
        raw_content=text,
        token_count=850
    )
    children = chunker.split_into_children(
        parent=parent,
        section_hierarchy=["Cardiologia", "Scompenso", "Terapia"],
        global_vector_start_id=0,
        icd10_codes=["I50.9"]
    )
    assert len(children) > 1
    assert children[0].breadcrumb_header == "[Cardiologia > Scompenso > Terapia]\n\n"
    assert children[0].vector_id == 0
    assert children[1].vector_id == 1


def test_zstd_dictionary_and_medpack_build():
    with tempfile.TemporaryDirectory() as staging_dir_context:
        staging_root_path = Path(staging_dir_context)
        staging_dir = staging_root_path / "staging"
        staging_dir.mkdir()
        (staging_dir / "assets_media").mkdir()
        (staging_dir / "vector_index").mkdir()

        # Addestramento dizionario con frammenti di corpus medico reale
        corpus_slices = [
            f"Corpus clinico medico ICD-10 I50.9 Scompenso Cardiaco ATC C09AA05 HPO HP:0001635 iterazione {i}".encode('utf-8')
            for i in range(150)
        ]
        compressor = ZstdDictionaryCompressor()
        dict_bytes = compressor.train_dictionary(corpus_slices, dict_size=32768)
        assert len(dict_bytes) > 0

        # Crea module_kb.sqlite con SQLiteModuleBuilder
        staging_sqlite_db_path = staging_root_path / "staging_module.sqlite"
        builder = SQLiteModuleBuilder(staging_sqlite_db_path)
        builder.insert_source(
            source_id="urn:isbn:9788821445678",
            academic_title="Manuale di Malattie Cardiovascolari",
            publication_year=2024,
            authors=["Rossi M", "Bianchi L"],
            publisher="Edizioni Mediche"
        )
        p_content = " ".join([f"termine_{i}" for i in range(850)])
        builder.insert_parent_chunk(
            ParentChunk(
                parent_id="p_test_1",
                source_id="urn:isbn:9788821445678",
                chapter="Capitolo 1",
                section_path="Scompenso",
                page_start=1,
                page_end=3,
                raw_content=p_content,
                token_count=850
            )
        )
        c_content = " ".join([f"micro_{i}" for i in range(180)])
        builder.insert_child_chunk(
            ChildChunk(
                child_id="c_test_1",
                parent_id="p_test_1",
                vector_id=0,
                breadcrumb_header="[Capitolo 1 > Scompenso]\n\n",
                text_content=c_content,
                token_count=180,
                hpo_terms=["HP:0001635"],
                atc_codes=["C09AA05"],
                icd10_codes=["I50.9"]
            )
        )
        sqlite_target = staging_dir / "module_kb.sqlite"
        builder.vacuum_into(sqlite_target)
        assert sqlite_target.exists()

        # File asset e indici binari minimi reali
        with open(staging_dir / "assets_media" / "blob.bin", "wb") as f:
            f.write(b"RIFF_ZERO_COPY_BLOB_FOR_TESTING_PURPOSES_EXACT_ALIGNMENT")
        with open(staging_dir / "assets_media" / "media_manifest.cbor", "wb") as f:
            f.write(b"\xa1\x64code\x64pack")
        with open(staging_dir / "vector_index" / "index.bin", "wb") as f:
            f.write(b"\x00" * 384 * 4)  # 1 vettore da 384 float
        with open(staging_dir / "vector_index" / "meta.bin", "wb") as f:
            f.write(json.dumps([{"vector_id": 0, "child_id": "c_test_1"}]).encode('utf-8'))

        assembler = MedPackAssembler()
        medpack_out = staging_root_path / "cardiology_test.medpack"
        manifest = assembler.build_medpack(
            staging_dir=staging_dir,
            output_medpack_path=medpack_out,
            dictionary_bytes=dict_bytes,
            manifest_meta={
                "pack_id": "cardiology_test",
                "display_title": "Cardiologia Clinica Modulo 1",
                "total_parent_chunks": 1,
                "total_child_chunks": 1,
                "total_vectors": 1
            }
        )
        assert medpack_out.exists()
        assert manifest.pack_id == "cardiology_test"
        assert len(manifest.checksums.module_kb_sqlite) == 64
