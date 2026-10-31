"""
Definizione formale dello schema DDL del database relazionale module_kb.sqlite (ROA-20).
Include STRICT mode su tutte le tabelle relazionali, indici B-Tree saturi,
indice full-text FTS5 e tabelle farmacologiche, diagnostiche e docimologiche.
"""

DDL_SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE bibliographic_sources (
    source_id TEXT PRIMARY KEY NOT NULL,
    isbn TEXT,
    doi TEXT,
    pmid TEXT,
    academic_title TEXT NOT NULL,
    edition INTEGER,
    volume INTEGER,
    publication_year INTEGER NOT NULL,
    authors_json TEXT NOT NULL,
    publisher TEXT NOT NULL
) STRICT;

CREATE TABLE parent_chunks (
    parent_id TEXT PRIMARY KEY NOT NULL,
    source_id TEXT NOT NULL,
    chapter TEXT NOT NULL,
    section_path TEXT NOT NULL,
    page_start INTEGER NOT NULL,
    page_end INTEGER NOT NULL,
    raw_content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    FOREIGN KEY (source_id) REFERENCES bibliographic_sources(source_id) ON DELETE CASCADE,
    CHECK (token_count >= 1)
) STRICT;

CREATE TABLE child_chunks (
    child_id TEXT PRIMARY KEY NOT NULL,
    parent_id TEXT NOT NULL,
    vector_id INTEGER NOT NULL UNIQUE,
    breadcrumb_header TEXT NOT NULL,
    text_content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    hpo_terms TEXT,
    atc_codes TEXT,
    icd10_codes TEXT,
    FOREIGN KEY (parent_id) REFERENCES parent_chunks(parent_id) ON DELETE CASCADE,
    CHECK (token_count >= 1)
) STRICT;

CREATE TABLE clinical_icd10 (
    icd10_code TEXT PRIMARY KEY NOT NULL,
    description TEXT NOT NULL,
    chapter TEXT NOT NULL,
    block_range TEXT NOT NULL,
    is_leaf INTEGER NOT NULL DEFAULT 1,
    prior_probability REAL NOT NULL DEFAULT 0.01
) STRICT;

CREATE TABLE clinical_atc (
    atc_code TEXT PRIMARY KEY NOT NULL,
    substance_name TEXT NOT NULL,
    level1_anatomical TEXT NOT NULL,
    level2_therapeutic TEXT NOT NULL,
    level3_pharmacological TEXT NOT NULL,
    level4_chemical TEXT NOT NULL,
    is_prodrug INTEGER NOT NULL DEFAULT 0,
    primary_cyp_enzymes TEXT NOT NULL DEFAULT '[]',
    defined_daily_dose REAL,
    ddd_unit TEXT
) STRICT;

CREATE TABLE clinical_hpo (
    hpo_id TEXT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL,
    definition TEXT NOT NULL,
    ancestors_json TEXT NOT NULL,
    information_content REAL NOT NULL DEFAULT 0.0,
    cluster_id TEXT NOT NULL DEFAULT 'GENERAL',
    cluster_gamma REAL NOT NULL DEFAULT 0.50,
    cost_weight REAL NOT NULL DEFAULT 1.0
) STRICT;

CREATE TABLE rel_icd10_hpo (
    icd10_code TEXT NOT NULL,
    hpo_id TEXT NOT NULL,
    frequency_percentage REAL NOT NULL DEFAULT 100.0,
    is_mandatory INTEGER NOT NULL DEFAULT 0,
    is_pathognomonic INTEGER NOT NULL DEFAULT 0,
    lambda_multiplier REAL NOT NULL DEFAULT 1.0,
    weight_pos REAL NOT NULL DEFAULT 1.0,
    weight_neg REAL NOT NULL DEFAULT -0.5,
    PRIMARY KEY (icd10_code, hpo_id),
    FOREIGN KEY (icd10_code) REFERENCES clinical_icd10(icd10_code) ON DELETE CASCADE,
    FOREIGN KEY (hpo_id) REFERENCES clinical_hpo(hpo_id) ON DELETE CASCADE
) STRICT;

CREATE TABLE substances (
    substance_id TEXT PRIMARY KEY NOT NULL,
    substance_name TEXT NOT NULL,
    atc_code TEXT,
    is_prodrug INTEGER NOT NULL DEFAULT 0,
    active_metabolite TEXT,
    FOREIGN KEY (atc_code) REFERENCES clinical_atc(atc_code) ON DELETE SET NULL
) STRICT;

CREATE TABLE substance_cyp_profiles (
    atc_code TEXT NOT NULL,
    inn_name TEXT NOT NULL,
    is_prodrug INTEGER NOT NULL DEFAULT 0,
    isoenzyme TEXT NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('SUBSTRATE', 'INHIBITOR', 'INDUCER')),
    fm_fraction REAL NOT NULL DEFAULT 0.0,
    potency_tier TEXT NOT NULL DEFAULT 'NONE',
    PRIMARY KEY (atc_code, isoenzyme, role)
) STRICT;

CREATE TABLE substance_organ_risks (
    atc_code TEXT PRIMARY KEY,
    inn_name TEXT NOT NULL,
    is_nti INTEGER NOT NULL DEFAULT 0,
    qtc_risk_weight REAL NOT NULL DEFAULT 0.0,
    nephro_risk_weight REAL NOT NULL DEFAULT 0.0,
    is_ras_blocker INTEGER NOT NULL DEFAULT 0,
    is_diuretic INTEGER NOT NULL DEFAULT 0,
    is_nsaid INTEGER NOT NULL DEFAULT 0
) STRICT;

CREATE TABLE atc_combinations (
    combo_atc_code TEXT NOT NULL,
    combo_inn_name TEXT NOT NULL,
    component_atc_code TEXT NOT NULL,
    component_inn_name TEXT NOT NULL,
    stoichiometric_ratio REAL NOT NULL DEFAULT 1.0,
    PRIMARY KEY (combo_atc_code, component_atc_code)
) STRICT;

CREATE TABLE cpic_guidelines (
    guideline_id TEXT PRIMARY KEY,
    atc_code TEXT NOT NULL,
    gene_symbol TEXT NOT NULL,
    diplotype_phenotype TEXT NOT NULL,
    clinical_recommendation TEXT NOT NULL,
    is_absolute_contraindication INTEGER NOT NULL DEFAULT 0,
    evidence_level TEXT NOT NULL DEFAULT '1A'
) STRICT;

CREATE TABLE drug_interactions (
    interaction_id TEXT PRIMARY KEY NOT NULL,
    substance_a TEXT NOT NULL,
    substance_b TEXT NOT NULL,
    severity_level INTEGER NOT NULL,
    mechanism_description TEXT NOT NULL,
    clinical_alert_text TEXT NOT NULL,
    FOREIGN KEY (substance_a) REFERENCES substances(substance_id) ON DELETE CASCADE,
    FOREIGN KEY (substance_b) REFERENCES substances(substance_id) ON DELETE CASCADE
) STRICT;

CREATE TABLE clinical_sheets (
    sheet_id TEXT PRIMARY KEY NOT NULL,
    icd10_code TEXT NOT NULL,
    title TEXT NOT NULL,
    content_markdown TEXT NOT NULL,
    callouts_json TEXT NOT NULL DEFAULT '[]',
    FOREIGN KEY (icd10_code) REFERENCES clinical_icd10(icd10_code) ON DELETE CASCADE
) STRICT;

CREATE TABLE exam_items (
    item_id TEXT PRIMARY KEY,
    item_type TEXT NOT NULL CHECK(item_type IN ('MCQ', 'HOTSPOT', 'NLI_OPEN', 'DAG_SCENARIO')),
    domain_icd10 TEXT NOT NULL,
    payload_json TEXT NOT NULL
) STRICT;

CREATE TABLE medical_lexicon (
    term TEXT PRIMARY KEY,
    frequency INTEGER NOT NULL DEFAULT 100,
    hpo_id TEXT,
    icd10_code TEXT
) STRICT;

CREATE TABLE colloquial_synonyms (
    colloquial_phrase TEXT PRIMARY KEY,
    hpo_id TEXT NOT NULL,
    canonical_label TEXT NOT NULL
) STRICT;

CREATE TABLE vector_metadata (
    vector_id INTEGER PRIMARY KEY NOT NULL,
    child_id TEXT NOT NULL,
    embedding_dimension INTEGER NOT NULL DEFAULT 384,
    embedding_blob BLOB,
    FOREIGN KEY (child_id) REFERENCES child_chunks(child_id) ON DELETE CASCADE
) STRICT;

-- Indici B-Tree Saturi
CREATE INDEX idx_child_vector ON child_chunks(vector_id);
CREATE INDEX idx_parent_source ON parent_chunks(source_id);
CREATE INDEX idx_child_parent ON child_chunks(parent_id);
CREATE INDEX idx_hpo_ancestors ON clinical_hpo(hpo_id);
CREATE INDEX idx_rel_icd10_hpo_lookup ON rel_icd10_hpo(hpo_id, icd10_code);
CREATE INDEX idx_atc_prodrug ON clinical_atc(is_prodrug);
CREATE INDEX idx_substances_prodrug ON substances(is_prodrug);
CREATE INDEX idx_cyp_profiles_atc ON substance_cyp_profiles(atc_code);
CREATE INDEX idx_interactions_ab ON drug_interactions(substance_a, substance_b);
CREATE INDEX idx_sheets_icd ON clinical_sheets(icd10_code);
CREATE INDEX idx_exam_domain ON exam_items(domain_icd10, item_type);

-- Tabella Virtuale FTS5 per ricerca full-text istantanea (<5ms)
CREATE VIRTUAL TABLE child_chunks_fts USING fts5(
    child_id UNINDEXED,
    breadcrumb_header,
    text_content,
    tokenize = 'porter unicode61'
);
"""
