import { create } from 'zustand';
import type { ActiveTabIdentifier, IMedClientStoreState } from '../interfaces/engineContracts';
import type {
  ClinicalSheetBlock,
  EmergencyTriageTelemetry,
  FsrsRatingGrade,
  SymptomMatcherBlock,
  SymptomMatcherOutput,
  SymptomPolarity,
} from '../interfaces/sduiContracts';

import { resolveSidecarIpcConfig, SidecarIpcClient } from './sidecarIpcClient';

import {
  SIDECAR_IPC_ENDPOINTS,
  STORAGE_KEY_MEDCLIENT,
  computeCkdEpi2021Egfr,
  mapTabToCanonicalBlock,
} from './storeHelpers';

import {
  loadPersistedMedClientState,
  savePersistedMedClientState,
} from './storePersistence';

export { SIDECAR_IPC_ENDPOINTS, STORAGE_KEY_MEDCLIENT, computeCkdEpi2021Egfr, mapTabToCanonicalBlock };

export const sidecarIpcClient = new SidecarIpcClient(resolveSidecarIpcConfig());

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
        differential_candidates: output.differential_diagnosis.map((candidateEntry) => {
          const anyCand = candidateEntry as unknown as Record<string, unknown>;
          const diseaseId = String(anyCand.icd10_code ?? anyCand.disease_id ?? anyCand.name ?? anyCand.disease_name ?? 'UNKNOWN');
          const name = String(anyCand.name ?? anyCand.disease_name ?? diseaseId);
          const rawProb = typeof anyCand.probability === 'number'
            ? anyCand.probability
            : typeof anyCand.posterior_probability === 'number'
              ? anyCand.posterior_probability
              : 0.5;
          const severity = (rawProb > 0.7 ? 'CRITICAL' : rawProb > 0.4 ? 'HIGH' : 'MODERATE') as 'LOW' | 'MODERATE' | 'HIGH' | 'CRITICAL';
          return {
            disease_id: diseaseId,
            name,
            probability: rawProb,
            icd10_code: anyCand.icd10_code ? String(anyCand.icd10_code) : undefined,
            severity,
          };
        }),
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
      const { requestPharmacologyEvaluation } = await import('./storeEvaluators');
      const block = await requestPharmacologyEvaluation(activeMedications, renal);
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
      const { requestExamEvaluation } = await import('./storeEvaluators');
      const examBlock = await requestExamEvaluation(itemType, userSelection);
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
