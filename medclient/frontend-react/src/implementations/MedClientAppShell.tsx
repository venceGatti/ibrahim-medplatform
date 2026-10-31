import React from 'react';
import { Globe, Power } from 'lucide-react';
import { resolveCanonicalBlockType } from '../base/sduiRegistry';
import { useMedClientStore } from '../base/useMedClientStore';
import type { ActiveTabIdentifier } from '../interfaces/engineContracts';
import type {
  ClinicalSheetBlock,
  DrugSafetyBlock,
  ExamSimulatorBlock,
  SymptomMatcherBlock,
} from '../interfaces/sduiContracts';
import { ClinicalSheetBlockView } from './ClinicalSheetBlockView';
import { DrugSafetyBlockView } from './DrugSafetyBlockView';
import { ExamSimulatorBlockView } from './ExamSimulatorBlockView';
import { SymptomMatcherBlockView } from './SymptomMatcherBlockView';

interface ErrorBoundaryProps {
  readonly children: React.ReactNode;
}

interface ErrorBoundaryState {
  readonly hasError: boolean;
  readonly errorMessage: string;
}

export class ClinicalViewErrorBoundary extends React.Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  public constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { hasError: false, errorMessage: '' };
  }

  public static getDerivedStateFromError(caughtError: Error): ErrorBoundaryState {
    return {
      hasError: true,
      errorMessage: caughtError.message,
    };
  }

  public render(): React.ReactNode {
    if (this.state.hasError) {
      return (
        <div
          className="rounded-lg border-2 border-red-600 bg-red-950 p-6 text-red-100"
          data-testid="sdui-error-boundary-fallback"
        >
          <h3 className="text-base font-bold">
            An unexpected error occurred in this view
          </h3>
          <p className="mt-2 font-mono text-xs text-red-200">{this.state.errorMessage}</p>
        </div>
      );
    }
    return this.props.children;
  }
}

interface SidecarStatusViewProps {
  readonly title: string;
  readonly isLoading: boolean;
  readonly errorMessage: string | null;
  readonly onRetry: () => void;
}

export const SidecarStatusView: React.FC<SidecarStatusViewProps> = ({
  title,
  isLoading,
  errorMessage,
  onRetry,
}) => {
  if (isLoading) {
    return (
      <div
        className="flex flex-col items-center justify-center rounded-xl border border-slate-800 bg-slate-900/60 p-12 text-center"
        data-testid="sdui-loading-indicator"
      >
        <div className="mb-4 h-8 w-8 animate-spin rounded-full border-2 border-blue-500 border-t-transparent" />
        <h3 className="text-sm font-bold text-white">Caricamento {title} in corso...</h3>
        <p className="mt-1 text-xs text-slate-400">
          Interrogazione del Sidecar clinico locale su{' '}
          <code className="rounded bg-slate-800 px-1 py-0.5 font-mono text-blue-300">
            http://127.0.0.1:8765
          </code>
        </p>
      </div>
    );
  }

  return (
    <div
      className="rounded-xl border border-amber-600/60 bg-amber-950/30 p-6 text-amber-100"
      data-testid="sdui-offline-indicator"
    >
      <div className="flex items-start gap-3">
        <div className="rounded-lg bg-amber-900/60 p-2 text-amber-400">
          <Power className="h-5 w-5" />
        </div>
        <div className="flex-1">
          <h3 className="text-sm font-bold text-amber-200">
            Sidecar Clinico Locale Non Raggiungibile
          </h3>
          <p className="mt-1 text-xs text-amber-300/80">
            Impossibile recuperare i dati per <span className="font-semibold text-white">{title}</span>.
            Verificare che il runtime FastAPI sia attivo su 127.0.0.1:8765 con l&apos;header X-Tauri-IPC-Secret.
          </p>
          {errorMessage && (
            <p className="mt-2 rounded bg-black/40 p-2 font-mono text-xs text-red-300">
              {errorMessage}
            </p>
          )}
          <button
            type="button"
            onClick={onRetry}
            className="mt-4 rounded bg-amber-600 px-3 py-1.5 text-xs font-semibold text-slate-950 hover:bg-amber-500 transition"
            data-testid="sdui-retry-connection-button"
          >
            Riprova Connessione
          </button>
        </div>
      </div>
    </div>
  );
};

const NAVIGATION_TABS: readonly {
  readonly id: ActiveTabIdentifier;
  readonly label: string;
  readonly blockType: string;
}[] = [
  { id: 'clinical_sheet', label: 'Monografia Clinica', blockType: 'ClinicalSheetBlock' },
  { id: 'symptom_matcher', label: 'Diagnosi Differenziale', blockType: 'SymptomMatcherBlock' },
  { id: 'drug_safety', label: 'Sicurezza CYP450 & eGFR', blockType: 'DrugSafetyBlock' },
  { id: 'exam_simulator', label: 'Simulatore Esami & FSRS', blockType: 'ExamSimulatorBlock' },
];

export const MedClientAppShell: React.FC = () => {
  const activeTab = useMedClientStore((state) => state.activeTab);
  const setActiveTab = useMedClientStore((state) => state.setActiveTab);
  const searchQuery = useMedClientStore((state) => state.searchQuery);
  const setSearchQuery = useMedClientStore((state) => state.setSearchQuery);
  const ipcConnectionStatus = useMedClientStore((state) => state.ipcConnectionStatus);
  const tabScrollOffsets = useMedClientStore((state) => state.tabScrollOffsets);
  const setTabScrollOffset = useMedClientStore((state) => state.setTabScrollOffset);

  const liveClinicalSheet = useMedClientStore((state) => state.liveClinicalSheet);
  const liveSymptomMatcher = useMedClientStore((state) => state.liveSymptomMatcher);
  const liveDrugSafety = useMedClientStore((state) => state.liveDrugSafety);
  const liveExamBlock = useMedClientStore((state) => state.liveExamBlock);
  const isSidecarLoading = useMedClientStore((state) => state.isSidecarLoading);
  const sidecarErrorMessage = useMedClientStore((state) => state.sidecarErrorMessage);

  const fetchClinicalSheet = useMedClientStore((state) => state.fetchClinicalSheet);
  const evaluateDifferentialDiagnosis = useMedClientStore((state) => state.evaluateDifferentialDiagnosis);
  const evaluatePharmacologySafety = useMedClientStore((state) => state.evaluatePharmacologySafety);
  const submitExamEvaluation = useMedClientStore((state) => state.submitExamEvaluation);

  const selectedSymptoms = useMedClientStore((state) => state.selectedSymptoms);
  const activeMedications = useMedClientStore((state) => state.activeMedications);
  const renalParameters = useMedClientStore((state) => state.renalParameters);

  const [isShutDown, setIsShutDown] = React.useState(false);

  React.useEffect(() => {
    void fetchClinicalSheet('SHEET_STEMI_01');
    void evaluateDifferentialDiagnosis();
    void evaluatePharmacologySafety();
    void submitExamEvaluation('MCQ', 1);
  }, []);

  React.useEffect(() => {
    void evaluateDifferentialDiagnosis();
  }, [selectedSymptoms]);

  React.useEffect(() => {
    void evaluatePharmacologySafety();
  }, [activeMedications, renalParameters]);

  const handleShutdown = async () => {
    if (!window.confirm('Vuoi arrestare MedPlatform e terminare tutti i servizi?')) {
      return;
    }
    try {
      await fetch('http://127.0.0.1:8765/agent/execute', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-Tauri-IPC-Secret': 'medclient_local_session_secure_token',
        },
        body: JSON.stringify({
          action_type: 'SHUTDOWN_SERVER',
          action_parameters: {},
        }),
      });
    } catch {
      // Process exits quickly causing expected network abort
    }
    setIsShutDown(true);
    setTimeout(() => {
      window.close();
    }, 1200);
  };

  const handleOpenBrowser = () => {
    window.open('http://localhost:5173', '_blank');
  };

  if (isShutDown) {
    return (
      <div className="flex min-h-screen flex-col items-center justify-center bg-slate-950 p-6 text-center text-white">
        <div className="max-w-md rounded-xl border border-slate-800 bg-slate-900/90 p-8 shadow-2xl">
          <div className="mx-auto mb-4 flex h-14 w-14 items-center justify-center rounded-full border border-red-700/50 bg-red-950/60 text-red-400">
            <Power className="h-7 w-7" />
          </div>
          <h2 className="text-xl font-bold">MedPlatform Arrestata</h2>
          <p className="mt-2 text-sm text-slate-400">
            I servizi locali e i motori clinici sono stati arrestati con successo. Puoi chiudere questa scheda.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100" data-testid="medclient-app-shell">
      <header className="border-b border-slate-800 bg-slate-900 px-6 py-3 shadow-sm">
        <div className="mx-auto flex max-w-7xl flex-wrap items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <span className="rounded bg-blue-600 px-2.5 py-1 text-xs font-extrabold tracking-wider text-white">
              MEDCLIENT v5
            </span>
            <h1 className="text-base font-bold text-white">
              Workstation Clinica Offline-First &amp; Motore SDUI
            </h1>
          </div>

          <div className="flex items-center gap-3">
            <input
              type="search"
              value={searchQuery}
              onChange={(ev) => setSearchQuery(ev.target.value)}
              aria-label="Cerca ICD-10, ATC, HPO..."
              className="rounded border border-slate-700 bg-slate-950 px-3 py-1 text-xs text-white"
              data-testid="global-search-input"
            />
            <span
              className={`rounded-full px-2.5 py-0.5 text-xs font-semibold ${
                ipcConnectionStatus === 'ONLINE'
                  ? 'bg-emerald-950 text-emerald-300'
                  : 'bg-amber-950 text-amber-300'
              }`}
              data-testid="ipc-connection-badge"
            >
              {ipcConnectionStatus}
            </span>

            {isSidecarLoading && (
              <span
                className="flex items-center gap-1.5 text-xs text-blue-400 animate-pulse font-mono"
                data-testid="sidecar-sync-indicator"
              >
                <span className="inline-block h-2 w-2 rounded-full bg-blue-400"></span>
                SYNC
              </span>
            )}

            <div className="flex items-center gap-2 pl-2 border-l border-slate-800">
              <button
                type="button"
                onClick={handleOpenBrowser}
                title="Apri nuova visualizzazione nel Browser Web"
                className="flex items-center gap-1.5 rounded border border-slate-700 bg-slate-800/80 px-2.5 py-1 text-xs font-semibold text-slate-200 hover:border-slate-500 hover:bg-slate-700 hover:text-white transition"
                data-testid="header-open-browser-btn"
              >
                <Globe className="h-3.5 w-3.5 text-blue-400" />
                <span>Apri Web</span>
              </button>

              <button
                type="button"
                onClick={handleShutdown}
                title="Arresta tutti i servizi MedPlatform"
                className="flex items-center gap-1.5 rounded border border-red-900/60 bg-red-950/40 px-2.5 py-1 text-xs font-semibold text-red-300 hover:border-red-700 hover:bg-red-900/60 hover:text-white transition"
                data-testid="header-shutdown-btn"
              >
                <Power className="h-3.5 w-3.5 text-red-400" />
                <span>Spegni</span>
              </button>
            </div>
          </div>
        </div>

        <nav className="mx-auto mt-3 flex max-w-7xl gap-2" data-testid="main-tab-navigation">
          {NAVIGATION_TABS.map((tabEntry) => {
            const resolvedCanonical = resolveCanonicalBlockType(tabEntry.blockType);
            const isSelected = activeTab === tabEntry.id;
            return (
              <button
                key={tabEntry.id}
                type="button"
                onClick={() => setActiveTab(tabEntry.id)}
                data-canonical={resolvedCanonical}
                data-testid={`nav-tab-${tabEntry.id}`}
                className={`rounded-t-md px-4 py-2 text-xs font-semibold transition ${
                  isSelected
                    ? 'border-b-2 border-blue-500 bg-slate-800 text-white'
                    : 'bg-slate-900/50 text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
              >
                {tabEntry.label}
              </button>
            );
          })}
        </nav>
      </header>

      <main className="mx-auto max-w-7xl p-6">
        <ClinicalViewErrorBoundary>
          {/* Regola 8: Persistenza Assoluta nel DOM tramite visibilita CSS (hidden / block) a 60 FPS */}
          <div
            className={`transition-opacity duration-150 ease-in-out ${
              activeTab === 'clinical_sheet' ? 'block opacity-100' : 'hidden opacity-0'
            }`}
            data-testid="dom-retained-view-clinical_sheet"
          >
            <ClinicalSheetBlockView
              block={liveClinicalSheet ?? DEFAULT_CLINICAL_SHEET}
              scrollTopPx={tabScrollOffsets.clinical_sheet}
              onScrollOffsetChange={(offset) => setTabScrollOffset('clinical_sheet', offset)}
            />
          </div>

          <div
            className={`transition-opacity duration-150 ease-in-out ${
              activeTab === 'symptom_matcher' ? 'block opacity-100' : 'hidden opacity-0'
            }`}
            data-testid="dom-retained-view-symptom_matcher"
          >
            <SymptomMatcherBlockView block={liveSymptomMatcher ?? DEFAULT_SYMPTOM_MATCHER} />
          </div>

          <div
            className={`transition-opacity duration-150 ease-in-out ${
              activeTab === 'drug_safety' ? 'block opacity-100' : 'hidden opacity-0'
            }`}
            data-testid="dom-retained-view-drug_safety"
          >
            <DrugSafetyBlockView block={liveDrugSafety ?? DEFAULT_DRUG_SAFETY} />
          </div>

          <div
            className={`transition-opacity duration-150 ease-in-out ${
              activeTab === 'exam_simulator' ? 'block opacity-100' : 'hidden opacity-0'
            }`}
            data-testid="dom-retained-view-exam_simulator"
          >
            <ExamSimulatorBlockView block={liveExamBlock ?? DEFAULT_EXAM_BLOCK} />
          </div>
        </ClinicalViewErrorBoundary>
      </main>
    </div>
  );
};
