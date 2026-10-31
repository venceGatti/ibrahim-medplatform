import { create } from 'zustand';
import type {
  ActiveTabIdentifier,
  IMedClientStoreState,
  RenalPatientParameters,
} from '../interfaces/engineContracts';
import type {
  CanonicalBlockType,
  FsrsRatingGrade,
  SymptomPolarity,
} from '../interfaces/sduiContracts';

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
