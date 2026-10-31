import { create } from 'zustand';
import { SidecarIpcClient } from './sidecarIpcClient';
import type {
  ActiveTabIdentifier,
  IMedClientStoreState,
  RenalPatientParameters,
} from '../interfaces/engineContracts';
import type {
  CanonicalBlockType,
  ClinicalSheetBlock,
  DrugSafetyBlock,
  ExamSimulatorBlock,
  FsrsRatingGrade,
  SymptomMatcherBlock,
  SymptomMatcherOutput,
  SymptomPolarity,
} from '../interfaces/sduiContracts';

import { resolveSidecarIpcConfig, SidecarIpcClient } from './sidecarIpcClient';

export const SIDECAR_IPC_ENDPOINTS = {
  CLINICAL_SHEET: '/api/v3/sheets/{sheet_id}',
  ENGINE_EVALUATE: '/api/v3/engine/evaluate',
  PHARMA_EVALUATE: '/api/v3/pharma/evaluate',
  EXAM_EVALUATE: '/api/v3/exam/evaluate',
  AGENT_HEALTH: '/agent/health',
  AGENT_EXECUTE: '/agent/execute',
} as const;

export const sidecarIpcClient = new SidecarIpcClient(resolveSidecarIpcConfig());

const STORAGE_KEY_MEDCLIENT = 'medclient_persistent_state_v1';

export function computeCkdEpi2021Egfr(
  ageYears: number,
  isFemale: boolean,
  serumCreatinineMgDl: number
): number {
  const safeCreatinine = Math.max(0.1, serumCreatinineMgDl);
  const clampedAge = Math.max(18, Math.min(120, ageYears));
  const kappa = isFemale ? 0.7 : 0.9;
  const alpha = isFemale ? -0.241 : -0.302;
  const sexMultiplier = isFemale ? 1.012 : 1.0;

  const ratio = safeCreatinine / kappa;
  const minTerm = Math.pow(Math.min(ratio, 1.0), alpha);
  const maxTerm = Math.pow(Math.max(ratio, 1.0), -1.2);
  const ageTerm = Math.pow(0.9938, clampedAge);

  const rawEgfr = 142.0 * minTerm * maxTerm * ageTerm * sexMultiplier;
  return Math.round(rawEgfr * 100) / 100;
}

function mapTabToCanonicalBlock(tabId: ActiveTabIdentifier): CanonicalBlockType {
  if (tabId === 'symptom_matcher') {
    return 'SymptomMatcherBlock';
  }
  if (tabId === 'drug_safety') {
    return 'DrugSafetyBlock';
  }
  if (tabId === 'exam_simulator') {
    return 'ExamSimulatorBlock';
  }
  return 'ClinicalSheetBlock';
}

interface PersistedSlice {
  readonly activeTab: ActiveTabIdentifier;
  readonly searchQuery: string;
  readonly selectedSymptoms: Readonly<Record<string, SymptomPolarity>>;
  readonly activeMedications: readonly string[];
  readonly renalParameters: RenalPatientParameters;
  readonly tabScrollOffsets: Readonly<Record<ActiveTabIdentifier, number>>;
}

const DEFAULT_RENAL_PARAMETERS: RenalPatientParameters = {
  ageYears: 68,
  isFemale: false,
  serumCreatinineMgDl: 1.4,
  calculatedEgfr: computeCkdEpi2021Egfr(68, false, 1.4),
};

const DEFAULT_PERSISTED_SLICE: PersistedSlice = {
  activeTab: 'clinical_sheet',
  searchQuery: '',
  selectedSymptoms: {
    'HP:0001635': 'PRESENT',
    'HP:0002094': 'PRESENT',
  },
  activeMedications: ['B01AC04', 'A02BC01'],
  renalParameters: DEFAULT_RENAL_PARAMETERS,
  tabScrollOffsets: {
    clinical_sheet: 0,
    symptom_matcher: 0,
    drug_safety: 0,
    exam_simulator: 0,
  },
};

export function loadPersistedMedClientState(): PersistedSlice {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return DEFAULT_PERSISTED_SLICE;
    }
    const serializedJson = window.localStorage.getItem(STORAGE_KEY_MEDCLIENT);
    if (!serializedJson) {
      return DEFAULT_PERSISTED_SLICE;
    }
    const parsedState = JSON.parse(serializedJson) as Partial<PersistedSlice>;
    if (!parsedState || typeof parsedState !== 'object') {
      return DEFAULT_PERSISTED_SLICE;
    }
    return {
      activeTab: parsedState.activeTab ?? DEFAULT_PERSISTED_SLICE.activeTab,
      searchQuery:
        typeof parsedState.searchQuery === 'string'
          ? parsedState.searchQuery
          : DEFAULT_PERSISTED_SLICE.searchQuery,
      selectedSymptoms:
        parsedState.selectedSymptoms ?? DEFAULT_PERSISTED_SLICE.selectedSymptoms,
      activeMedications: Array.isArray(parsedState.activeMedications)
        ? parsedState.activeMedications
        : DEFAULT_PERSISTED_SLICE.activeMedications,
      renalParameters: parsedState.renalParameters ?? DEFAULT_PERSISTED_SLICE.renalParameters,
      tabScrollOffsets: parsedState.tabScrollOffsets ?? DEFAULT_PERSISTED_SLICE.tabScrollOffsets,
    };
  } catch (_storageReadError) {
    return DEFAULT_PERSISTED_SLICE;
  }
}

function savePersistedMedClientState(currentState: IMedClientStoreState): void {
  try {
    if (typeof window === 'undefined' || !window.localStorage) {
      return;
    }
    const sliceToPersist: PersistedSlice = {
      activeTab: currentState.activeTab,
      searchQuery: currentState.searchQuery,
      selectedSymptoms: currentState.selectedSymptoms,
      activeMedications: currentState.activeMedications,
      renalParameters: currentState.renalParameters,
      tabScrollOffsets: currentState.tabScrollOffsets,
    };
    window.localStorage.setItem(STORAGE_KEY_MEDCLIENT, JSON.stringify(sliceToPersist));
  } catch (_quotaOrSecurityError) {
    // Fallback in-memory attivo se LocalStorage ha raggiunto la quota massima
    return;
  }
}

const initialSlice = loadPersistedMedClientState();

export const useMedClientStore = create<IMedClientStoreState>((set, get) => ({
  activeTab: initialSlice.activeTab,
  searchQuery: initialSlice.searchQuery,
  selectedSymptoms: initialSlice.selectedSymptoms,
  activeMedications: initialSlice.activeMedications,
  renalParameters: initialSlice.renalParameters,
  examAnswers: { Q_INIT: 0 },
  fsrsReviewHistory: { CARD_INIT: 3 },
  tabScrollOffsets: initialSlice.tabScrollOffsets,
  ipcConnectionStatus: 'ONLINE',
  activeCanonicalView: mapTabToCanonicalBlock(initialSlice.activeTab),
  liveClinicalSheet: null,
  liveSymptomMatcher: null,
  liveDrugSafety: null,
  liveExamBlock: null,
  isSidecarLoading: false,
  sidecarErrorMessage: null,

  fetchClinicalSheet: async (sheetId = 'SHEET_STEMI_01') => {
    set({ isSidecarLoading: true, sidecarErrorMessage: null });
    try {
      const sheet = await sidecarIpcClient.getClinicalSheet<ClinicalSheetBlock>(sheetId);
      set({ liveClinicalSheet: sheet, isSidecarLoading: false, ipcConnectionStatus: 'ONLINE' });
    } catch (err) {
      set({
        liveClinicalSheet: null,
        sidecarErrorMessage: err instanceof Error ? err.message : String(err),
        isSidecarLoading: false,
        ipcConnectionStatus: 'OFFLINE_LOCAL',
      });
    }
  },

  evaluateDifferentialDiagnosis: async () => {
    const rawSymptoms = get().selectedSymptoms;
    const findings = Object.entries(rawSymptoms).map(([hpoId, state]) => ({
      hpo_id: hpoId,
      state,
      is_pathognomonic: false,
    }));
    if (findings.length === 0) {
      set({ liveSymptomMatcher: null, isSidecarLoading: false });
      return;
    }

    set({ isSidecarLoading: true, sidecarErrorMessage: null });
    try {
      const payload = {
        session_id: `session_${Date.now()}`,
        vitals: {
          heart_rate_bpm: 80.0,
          systolic_bp_mmhg: 120.0,
          respiratory_rate_bpm: 16.0,
          spo2_percent: 98.0,
          temperature_celsius: 36.6,
          avpu_scale: 'A',
          gcs_score: 15,
          supplemental_o2: false,
          hypercapnic_risk: false,
        },
        findings,
      };
      const output = await sidecarIpcClient.evaluateDiagnostic<SymptomMatcherOutput>(payload);
      const rawRedFlags = (output.red_flags ?? {}) as Record<string, unknown>;
      const triageTelemetry: EmergencyTriageTelemetry = {
        alert_level: (rawRedFlags.alert_level as 'NOMINAL' | 'YELLOW_ATTENTION' | 'RED_CRITICAL') ?? 'NOMINAL',
        shock_index: typeof rawRedFlags.shock_index === 'number' ? rawRedFlags.shock_index : 0.0,
        qsofa_score: typeof rawRedFlags.qsofa_score === 'number' ? rawRedFlags.qsofa_score : 0,
        news2_score: typeof rawRedFlags.news2_score === 'number' ? rawRedFlags.news2_score : 0,
        trigger_reason: Array.isArray(rawRedFlags.critical_triggers)
          ? rawRedFlags.critical_triggers.join('; ')
          : undefined,
      };

      const updatedBlock: SymptomMatcherBlock = {
        block_type: 'SymptomMatcherBlock',
        differential_candidates: output.differential_diagnosis.map((candidateEntry) => ({
          disease_id: candidateEntry.icd10_code ?? candidateEntry.name,
          name: candidateEntry.name,
          probability: candidateEntry.probability ?? 0.5,
          icd10_code: candidateEntry.icd10_code,
          severity: (candidateEntry.probability ?? 0) > 0.7 ? 'CRITICAL' : 'HIGH',
        })),
        selected_symptoms: Object.keys(rawSymptoms),
        nbq: output.nbq ?? {
          question_id: 'NBQ_01',
          text: 'Presenza di dispnea ingravescente a riposo?',
          hpo_id: 'HP:0002094',
        },
        triage_telemetry: triageTelemetry,
      };
      set({ liveSymptomMatcher: updatedBlock, isSidecarLoading: false, ipcConnectionStatus: 'ONLINE' });
    } catch (err) {
      set({
        liveSymptomMatcher: null,
        sidecarErrorMessage: err instanceof Error ? err.message : String(err),
        isSidecarLoading: false,
        ipcConnectionStatus: 'OFFLINE_LOCAL',
      });
    }
  },

  evaluatePharmacologySafety: async () => {
    const activeMedications = get().activeMedications;
    if (activeMedications.length === 0) {
      set({ liveDrugSafety: null, isSidecarLoading: false });
      return;
    }

    set({ isSidecarLoading: true, sidecarErrorMessage: null });
    try {
      const renal = get().renalParameters;
      const drugCatalog: Record<
        string,
        {
          inn: string;
          single: number;
          daily: number;
          prodrug: boolean;
          fm?: Record<string, number>;
        }
      > = {
        B01AC04: {
          inn: 'Clopidogrel',
          single: 75.0,
          daily: 75.0,
          prodrug: true,
          fm: { CYP2C19: 0.85 },
        },
        A02BC01: {
          inn: 'Omeprazole',
          single: 20.0,
          daily: 20.0,
          prodrug: false,
          fm: { CYP2C19: 0.7 },
        },
        C09CA04: { inn: 'Irbesartan', single: 150.0, daily: 150.0, prodrug: false },
        C03AA03: { inn: 'Hydrochlorothiazide', single: 12.5, daily: 12.5, prodrug: false },
        M01AE01: { inn: 'Ibuprofen', single: 400.0, daily: 1200.0, prodrug: false },
      };

      const prescribedDrugs = activeMedications.map((atc) => {
        const info = drugCatalog[atc] ?? { inn: atc, single: 50.0, daily: 100.0, prodrug: false };
        return {
          atc_code: atc,
          inn_name: info.inn,
          single_dose_mg: info.single,
          daily_dose_mg: info.daily,
          route: 'oral',
          is_prodrug: info.prodrug,
          is_narrow_therapeutic_index: false,
          qtc_base_risk: 0.0,
          is_ras_blocker: atc === 'C09CA04',
          is_diuretic: atc === 'C03AA03',
          is_nsaid: atc === 'M01AE01',
          fm_cyp: info.fm ?? {},
        };
      });

      const queryParams = {
        patient_id: 'PATIENT_LOCAL_01',
        age: renal.ageYears,
        is_female: renal.isFemale,
        serum_creatinine_mg_dl: renal.serumCreatinineMgDl,
        serum_potassium_meq_l: 4.2,
      };

      const block = await sidecarIpcClient.evaluatePharmacology<DrugSafetyBlock>(
        { prescribed_drugs: prescribedDrugs },
        queryParams
      );
      set({ liveDrugSafety: block, isSidecarLoading: false, ipcConnectionStatus: 'ONLINE' });
    } catch (err) {
      set({
        liveDrugSafety: null,
        sidecarErrorMessage: err instanceof Error ? err.message : String(err),
        isSidecarLoading: false,
        ipcConnectionStatus: 'OFFLINE_LOCAL',
      });
    }
  },

  submitExamEvaluation: async (itemType: string, userSelection: unknown) => {
    set({ isSidecarLoading: true, sidecarErrorMessage: null });
    try {
      const payload = {
        item_type: itemType,
        item_data: {
          question_id: 'Q_CARDIO_01',
          stem: 'Quale gastroprotettore e preferibile associare alla DAPT con Clopidogrel per preservare la funzione CYP2C19?',
          options: [
            'Omeprazolo 40 mg',
            'Pantoprazolo 20 mg',
            'Esomeprazolo 40 mg',
            'Fluconazolo 200 mg',
          ],
          correct_index: 1,
          allowed_transitions: { ACT_FLUIDS: 'STEP_02' },
          target_polygons: [
            [
              [0.1, 0.1],
              [0.9, 0.1],
              [0.5, 0.9],
            ],
          ],
        },
        user_selection: userSelection,
        fsrs_card_state: { stability: 6.4, difficulty: 4.1, elapsed_days: 1.0, reps: 4, lapses: 0 },
      };
      const examBlock = await sidecarIpcClient.evaluateExam<ExamSimulatorBlock>(payload);
      set({ liveExamBlock: examBlock, isSidecarLoading: false, ipcConnectionStatus: 'ONLINE' });
    } catch (err) {
      set({
        liveExamBlock: null,
        sidecarErrorMessage: err instanceof Error ? err.message : String(err),
        isSidecarLoading: false,
        ipcConnectionStatus: 'OFFLINE_LOCAL',
      });
    }
  },

  setActiveTab: (targetTab: ActiveTabIdentifier) => {
    set({
      activeTab: targetTab,
      activeCanonicalView: mapTabToCanonicalBlock(targetTab),
    });
    savePersistedMedClientState(get());
  },

  setSearchQuery: (queryText: string) => {
    set({ searchQuery: queryText });
    savePersistedMedClientState(get());
  },

  toggleSymptomPolarity: (hpoId: string, explicitPolarity?: SymptomPolarity) => {
    const currentMap = Object.assign(Object.create(null) as Record<string, SymptomPolarity>, get().selectedSymptoms);
    const existing = currentMap[hpoId];
    if (explicitPolarity) {
      currentMap[hpoId] = explicitPolarity;
    } else if (!existing) {
      currentMap[hpoId] = 'PRESENT';
    } else if (existing === 'PRESENT') {
      currentMap[hpoId] = 'ABSENT';
    } else {
      delete currentMap[hpoId];
    }
    set({ selectedSymptoms: currentMap });
    savePersistedMedClientState(get());
  },

  removeSymptom: (hpoId: string) => {
    const currentMap = Object.assign(Object.create(null) as Record<string, SymptomPolarity>, get().selectedSymptoms);
    delete currentMap[hpoId];
    set({ selectedSymptoms: currentMap });
    savePersistedMedClientState(get());
  },

  addMedication: (substanceCode: string) => {
    const existingList = get().activeMedications;
    if (!existingList.includes(substanceCode)) {
      set({ activeMedications: existingList.concat([substanceCode]) });
      savePersistedMedClientState(get());
    }
  },

  removeMedication: (substanceCode: string) => {
    const filteredList = get().activeMedications.filter((code) => code !== substanceCode);
    set({ activeMedications: filteredList });
    savePersistedMedClientState(get());
  },

  updateRenalParameters: (ageYears: number, isFemale: boolean, serumCreatinineMgDl: number) => {
    const calculatedEgfr = computeCkdEpi2021Egfr(ageYears, isFemale, serumCreatinineMgDl);
    set({
      renalParameters: {
        ageYears,
        isFemale,
        serumCreatinineMgDl,
        calculatedEgfr,
      },
    });
    savePersistedMedClientState(get());
  },

  recordExamAnswer: (questionId: string, selectedAnswer: number | string) => {
    const updatedAnswers = Object.assign(
      Object.create(null) as Record<string, number | string>,
      get().examAnswers
    );
    updatedAnswers[questionId] = selectedAnswer;
    set({ examAnswers: updatedAnswers });
  },

  recordFsrsRating: (cardId: string, grade: FsrsRatingGrade) => {
    const updatedRatings = Object.assign(
      Object.create(null) as Record<string, FsrsRatingGrade>,
      get().fsrsReviewHistory
    );
    updatedRatings[cardId] = grade;
    set({ fsrsReviewHistory: updatedRatings });
  },

  resetExamSessionOnly: () => {
    const clearedMap = Object.create(null) as Record<string, number | string>;
    set({ examAnswers: clearedMap });
  },

  setTabScrollOffset: (tabId: ActiveTabIdentifier, scrollTopPx: number) => {
    const clampedOffset = Math.max(0, scrollTopPx);
    const updatedOffsets = Object.assign(
      Object.create(null) as Record<ActiveTabIdentifier, number>,
      get().tabScrollOffsets
    );
    updatedOffsets[tabId] = clampedOffset;
    set({ tabScrollOffsets: updatedOffsets });
    savePersistedMedClientState(get());
  },

  setIpcConnectionStatus: (status: 'ONLINE' | 'OFFLINE_LOCAL' | 'RECONNECTING') => {
    set({ ipcConnectionStatus: status });
  },
}));
