import type { ActiveTabIdentifier, IMedClientStoreState, RenalPatientParameters } from '../interfaces/engineContracts';
import type { SymptomPolarity } from '../interfaces/sduiContracts';
import { STORAGE_KEY_MEDCLIENT, computeCkdEpi2021Egfr } from './storeHelpers';

export interface PersistedSlice {
  readonly activeTab: ActiveTabIdentifier;
  readonly searchQuery: string;
  readonly selectedSymptoms: Readonly<Record<string, SymptomPolarity>>;
  readonly activeMedications: readonly string[];
  readonly renalParameters: RenalPatientParameters;
  readonly tabScrollOffsets: Readonly<Record<ActiveTabIdentifier, number>>;
}

export const DEFAULT_RENAL_PARAMETERS: RenalPatientParameters = {
  ageYears: 68,
  isFemale: false,
  serumCreatinineMgDl: 1.4,
  calculatedEgfr: computeCkdEpi2021Egfr(68, false, 1.4),
};

export const DEFAULT_PERSISTED_SLICE: PersistedSlice = {
  activeTab: 'clinical_sheet',
  searchQuery: '',
  selectedSymptoms: { 'HP:0001635': 'PRESENT', 'HP:0002094': 'PRESENT' },
  activeMedications: ['B01AC04', 'A02BC01'],
  renalParameters: DEFAULT_RENAL_PARAMETERS,
  tabScrollOffsets: { clinical_sheet: 0, symptom_matcher: 0, drug_safety: 0, exam_simulator: 0 },
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

export function savePersistedMedClientState(currentState: IMedClientStoreState): void {
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
    return;
  }
}
