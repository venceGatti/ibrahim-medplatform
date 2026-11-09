export type CanonicalBlockType =
  | 'ClinicalSheetBlock'
  | 'SymptomMatcherBlock'
  | 'DrugSafetyBlock'
  | 'ExamSimulatorBlock';

export type LegacyAliasBlockType =
  | 'MarkdownBlock'
  | 'DifferentialDiagnosisBlock'
  | 'InteractiveFlowchartBlock'
  | 'ClinicalExamBlock'
  | 'AnatomicalHotspotBlock';

export type SupportedBlockType = CanonicalBlockType | LegacyAliasBlockType;

export type CalloutSeverity =
  | 'RED_FLAG'
  | 'BLACKBOX'
  | 'CONTRAINDICATION'
  | 'EXAM_TIP'
  | 'CLINICAL_PEARL'
  | 'INFO'
  | 'WARNING'
  | 'CRITICAL'
  | 'EXAM_TIP';

export interface ClinicalCallout {
  readonly severity: CalloutSeverity;
  readonly message?: string;
  readonly body_markdown?: string;
  readonly title?: string;
  readonly icd10_refs?: readonly string[];
  readonly hpo_refs?: readonly string[];
  readonly atc_refs?: readonly string[];
}

export interface ClinicalSheetBlock {
  readonly block_type: 'ClinicalSheetBlock' | 'MarkdownBlock';
  readonly sheet_id: string;
  readonly title: string;
  readonly content_markdown: string;
  readonly callouts: readonly ClinicalCallout[];
  readonly media_sha256_hashes?: readonly string[];
  readonly molecule_sha256_svg?: string;
  readonly molecule_sha256_pdb?: string;
}

export type SymptomPolarity = 'PRESENT' | 'ABSENT';

export interface DifferentialCandidate {
  readonly disease_id: string;
  readonly name: string;
  readonly probability: number;
  readonly icd10_code?: string;
  readonly severity?: 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
}

export interface NextBestQuestionSpec {
  readonly question_id?: string;
  readonly text?: string;
  readonly hpo_id?: string;
  readonly information_gain_bits?: number;
}

export interface EmergencyTriageTelemetry {
  readonly qsofa_score: number;
  readonly news2_score: number;
  readonly shock_index: number;
  readonly alert_level: 'NOMINAL' | 'YELLOW_ATTENTION' | 'RED_CRITICAL';
  readonly trigger_reason?: string;
}

export interface SymptomMatcherBlock {
  readonly block_type: 'SymptomMatcherBlock' | 'DifferentialDiagnosisBlock';
  readonly differential_candidates: readonly DifferentialCandidate[];
  readonly selected_symptoms: readonly string[];
  readonly pertinent_negatives?: readonly string[];
  readonly nbq: NextBestQuestionSpec;
  readonly triage_telemetry?: EmergencyTriageTelemetry;
}

export type CypEnzymeId = 'CYP3A4' | 'CYP2D6' | 'CYP2C9' | 'CYP2C19' | 'CYP1A2';

export interface DrugInteractionRecord {
  readonly drug_a: string;
  readonly drug_b: string;
  readonly level: 1 | 2 | 3 | 4;
  readonly mechanism: string;
  readonly is_prodrug_bioactivation_block?: boolean;
}

export interface PharmacotherapyAlert {
  readonly code: string;
  readonly severity: 1 | 2 | 3 | 4;
  readonly message?: string;
}

export interface FdcDecompositionRecord {
  readonly brand_or_combo_name: string;
  readonly active_principles: readonly string[];
}

export interface DrugSafetyBlock {
  readonly block_type: 'DrugSafetyBlock';
  readonly interactions: readonly DrugInteractionRecord[];
  readonly cyp_clearance: Readonly<Record<string, number>>;
  readonly alerts: readonly PharmacotherapyAlert[];
  readonly egfr: number;
  readonly qtc_tisdale_score?: number;
  readonly triple_whammy_detected?: boolean;
  readonly fdc_decompositions?: readonly FdcDecompositionRecord[];
}

export type ExamModeType =
  | 'MCQ'
  | 'HOTSPOT'
  | 'IMAGE_HOTSPOT'
  | 'NLI_OPEN'
  | 'DAG_SCENARIO';

export type NormalizedVertex2D = readonly [number, number];

export interface DagTransitionOption {
  readonly action_id: string;
  readonly label: string;
  readonly target_node_id: string;
  readonly delta_score: number;
}

export interface DagScenarioNode {
  readonly node_id: string;
  readonly clinical_vignette: string;
  readonly heart_rate_bpm: number;
  readonly systolic_bp_mmhg: number;
  readonly spo2_percent: number;
  readonly is_terminal: boolean;
  readonly transitions: readonly DagTransitionOption[];
}

export interface ExamQuestionSpec {
  readonly question_id?: string;
  readonly stem?: string;
  readonly options?: readonly string[];
  readonly correct_index?: number;
  readonly image_uri?: string;
  readonly target_polygons?: readonly (readonly NormalizedVertex2D[])[];
  readonly reference_premise?: string;
  readonly entailment_threshold?: number;
  readonly scenario_id?: string;
  readonly current_step?: string;
  readonly dag_nodes?: Readonly<Record<string, DagScenarioNode>>;
}

export interface FsrsCardState {
  readonly stability?: number;
  readonly difficulty?: number;
  readonly reps?: number;
  readonly elapsed_days?: number;
}

export type FsrsRatingGrade = 1 | 2 | 3 | 4;

export interface ExamSimulatorBlock {
  readonly block_type:
    | 'ExamSimulatorBlock'
    | 'InteractiveFlowchartBlock'
    | 'ClinicalExamBlock'
    | 'AnatomicalHotspotBlock';
  readonly item_type: ExamModeType | string;
  readonly question_spec?: ExamQuestionSpec;
  readonly item_data?: Readonly<Record<string, unknown>>;
  readonly fsrs_card_state: FsrsCardState;
}

export type SDUIAnyBlock =
  | ClinicalSheetBlock
  | SymptomMatcherBlock
  | DrugSafetyBlock
  | ExamSimulatorBlock;

export interface SDUIPayloadEnvelope {
  readonly schema_version: string;
  readonly active_slot: 'blue' | 'green';
  readonly system_alert_level: 'NOMINAL' | 'YELLOW_ATTENTION' | 'RED_CRITICAL';
  readonly blocks: readonly SDUIAnyBlock[];
}

export interface SearchMatchEntry {
  readonly concept_id: string;
  readonly title: string;
  readonly match_score: number;
  readonly source: string;
}

export interface HybridSearchResponse {
  readonly query: string;
  readonly matches: readonly SearchMatchEntry[];
}

export interface FSRSReviewOutput {
  readonly stability: number;
  readonly difficulty: number;
  readonly scheduled_days: number;
  readonly due_timestamp_utc: string;
  readonly reps: number;
  readonly lapses: number;
}

export interface SymptomMatcherOutput {
  readonly session_id: string;
  readonly execution_time_ms: number;
  readonly red_flags: Readonly<Record<string, unknown>>;
  readonly differential_diagnosis: readonly DifferentialCandidate[];
  readonly nbq?: NextBestQuestionSpec | null;
}

export interface AgentHealthResponse {
  readonly status: string;
  readonly rss_mb: number;
  readonly db_active: string;
  readonly uptime_seconds: number;
}

export interface AgentStateResponse {
  readonly active_slot: string;
  readonly active_db_path: string;
  readonly pool_stats: Readonly<Record<string, unknown>>;
  readonly session_count: number;
  readonly system_alert_level: string;
}

export interface AgentExecuteResponse {
  readonly action_type: string;
  readonly success: boolean;
  readonly execution_time_ms: number;
  readonly result_payload: Readonly<Record<string, unknown>>;
  readonly error_message?: string;
}
