import type {
  CanonicalBlockType,
  FsrsRatingGrade,
  SymptomPolarity,
} from './sduiContracts';

export type ActiveTabIdentifier =
  | 'clinical_sheet'
  | 'symptom_matcher'
  | 'drug_safety'
  | 'exam_simulator';

export type IpcCircuitState = 'CLOSED' | 'OPEN' | 'HALF_OPEN';

export interface SidecarHealthReport {
  readonly status: string;
  readonly rss_mb: number;
  readonly uptime_seconds: number;
}

export interface SidecarExecutionOutcome {
  readonly success: boolean;
  readonly execution_outcome: Readonly<Record<string, unknown>>;
  readonly error_message?: string;
}

export interface IIpcSidecarClient {
  checkHealth(): Promise<SidecarHealthReport>;
  executeAction(
    actionType: string,
    actionParameters: Readonly<Record<string, unknown>>
  ): Promise<SidecarExecutionOutcome>;
  currentCircuitState(): IpcCircuitState;
  consecutiveFailures(): number;
}

export interface IWebGLContextBroker {
  acquireContext(
    ownerIdentifier: string,
    canvasElement: HTMLCanvasElement,
    onContextPreempted: () => void
  ): WebGLRenderingContext | null;
  releaseContext(ownerIdentifier: string): void;
  activeOwner(): string | null;
  activeContextCount(): number;
}

export interface RenalPatientParameters {
  readonly ageYears: number;
  readonly isFemale: boolean;
  readonly serumCreatinineMgDl: number;
  readonly calculatedEgfr: number;
}

export interface IMedClientStoreState {
  readonly activeTab: ActiveTabIdentifier;
  readonly searchQuery: string;
  readonly selectedSymptoms: Readonly<Record<string, SymptomPolarity>>;
  readonly activeMedications: readonly string[];
  readonly renalParameters: RenalPatientParameters;
  readonly examAnswers: Readonly<Record<string, number | string>>;
  readonly fsrsReviewHistory: Readonly<Record<string, FsrsRatingGrade>>;
  readonly tabScrollOffsets: Readonly<Record<ActiveTabIdentifier, number>>;
  readonly ipcConnectionStatus: 'ONLINE' | 'OFFLINE_LOCAL' | 'RECONNECTING';
  readonly activeCanonicalView: CanonicalBlockType;

  setActiveTab: (targetTab: ActiveTabIdentifier) => void;
  setSearchQuery: (queryText: string) => void;
  toggleSymptomPolarity: (hpoId: string, polarity?: SymptomPolarity) => void;
  removeSymptom: (hpoId: string) => void;
  addMedication: (substanceCode: string) => void;
  removeMedication: (substanceCode: string) => void;
  updateRenalParameters: (ageYears: number, isFemale: boolean, serumCreatinineMgDl: number) => void;
  recordExamAnswer: (questionId: string, selectedAnswer: number | string) => void;
  recordFsrsRating: (cardId: string, grade: FsrsRatingGrade) => void;
  resetExamSessionOnly: () => void;
  setTabScrollOffset: (tabId: ActiveTabIdentifier, scrollTopPx: number) => void;
  setIpcConnectionStatus: (status: 'ONLINE' | 'OFFLINE_LOCAL' | 'RECONNECTING') => void;
}
