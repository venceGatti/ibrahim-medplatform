import React from 'react';
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

const DEFAULT_CLINICAL_SHEET: ClinicalSheetBlock = {
  block_type: 'ClinicalSheetBlock',
  sheet_id: 'SHEET_STEMI_01',
  title: 'Infarto Miocardico Acuto con Sopraslivellamento ST (STEMI)',
  content_markdown: [
    '# Presentazione Clinica',
    'Dolore toracico retrosternale oppressivo irradiato al braccio sinistro e giugulo.',
    '# Diagnostica ECG 12 Derivazioni',
    'Sopraslivellamento del tratto ST >= 2 mm nelle derivazioni precordiali contigue.',
    '# Riperfusione Meccanica Primaria (PCI)',
    'Attivazione immediata sala di emodinamica con tempo door-to-balloon <= 90 minuti.',
  ].join('\n'),
  callouts: [
    {
      severity: 'RED_FLAG',
      title: 'Attivazione Emodinamica',
      message: 'Eseguire ECG entro 10 minuti dal primo contatto medico.',
    },
    {
      severity: 'BLACKBOX',
      title: 'Antiaggregazione DAPT',
      message: 'Evitare co-somministrazione di Clopidogrel e inibitori CYP2C19 (Omeprazolo).',
    },
  ],
  molecule_sha256_svg: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
  molecule_sha256_pdb: '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef',
};

const DEFAULT_SYMPTOM_MATCHER: SymptomMatcherBlock = {
  block_type: 'SymptomMatcherBlock',
  differential_candidates: [
    { disease_id: 'I21.0', name: 'STEMI Parete Anteriore', probability: 0.84, severity: 'CRITICAL' },
    { disease_id: 'I26.9', name: 'Embolia Polmonare Acuta', probability: 0.11, severity: 'HIGH' },
    { disease_id: 'I30.0', name: 'Pericardite Acuta', probability: 0.05, severity: 'MODERATE' },
  ],
  selected_symptoms: ['HP:0001635', 'HP:0002094'],
  nbq: {
    question_id: 'Q_ST_ELEV',
    hpo_id: 'HP:0001658',
    text: 'Il tracciato ECG mostra sopraslivellamento ST convesso nelle derivazioni V1-V4?',
    information_gain_bits: 1.42,
  },
  triage_telemetry: {
    qsofa_score: 2,
    news2_score: 7,
    shock_index: 1.12,
    alert_level: 'RED_CRITICAL',
    trigger_reason: 'Shock Index > 1.0 e qSOFA >= 2: attivare percorso tempo-dipendente.',
  },
};

const DEFAULT_DRUG_SAFETY: DrugSafetyBlock = {
  block_type: 'DrugSafetyBlock',
  interactions: [
    {
      drug_a: 'Clopidogrel (B01AC04)',
      drug_b: 'Omeprazole (A02BC01)',
      level: 1,
      mechanism: 'Inibizione competitiva CYP2C19: blocco bioattivazione del profarmaco tiopiridinico.',
      is_prodrug_bioactivation_block: true,
    },
  ],
  cyp_clearance: {
    CYP3A4: 0.88,
    CYP2D6: 0.92,
    CYP2C9: 0.76,
    CYP2C19: 0.14,
    CYP1A2: 0.95,
  },
  alerts: [{ code: 'BLACKBOX_INEFFICACY', severity: 1 }],
  egfr: 64.5,
  triple_whammy_detected: true,
  fdc_decompositions: [
    {
      brand_or_combo_name: 'Co-Aprovel',
      active_principles: ['Irbesartan (C09CA04)', 'Hydrochlorothiazide (C03AA03)'],
    },
  ],
};

const DEFAULT_EXAM_BLOCK: ExamSimulatorBlock = {
  block_type: 'ExamSimulatorBlock',
  item_type: 'MCQ',
  question_spec: {
    question_id: 'Q_CARDIO_01',
    stem: 'Quale gastroprotettore e preferibile associare alla DAPT con Clopidogrel per preservare la funzione CYP2C19?',
    options: [
      'Omeprazolo 40 mg',
      'Pantoprazolo 20 mg',
      'Esomeprazolo 40 mg',
      'Fluconazolo 200 mg',
    ],
    correct_index: 1,
  },
  fsrs_card_state: { stability: 6.4, difficulty: 4.1, reps: 4 },
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
              block={DEFAULT_CLINICAL_SHEET}
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
            <SymptomMatcherBlockView block={DEFAULT_SYMPTOM_MATCHER} />
          </div>

          <div
            className={`transition-opacity duration-150 ease-in-out ${
              activeTab === 'drug_safety' ? 'block opacity-100' : 'hidden opacity-0'
            }`}
            data-testid="dom-retained-view-drug_safety"
          >
            <DrugSafetyBlockView block={DEFAULT_DRUG_SAFETY} />
          </div>

          <div
            className={`transition-opacity duration-150 ease-in-out ${
              activeTab === 'exam_simulator' ? 'block opacity-100' : 'hidden opacity-0'
            }`}
            data-testid="dom-retained-view-exam_simulator"
          >
            <ExamSimulatorBlockView block={DEFAULT_EXAM_BLOCK} />
          </div>
        </ClinicalViewErrorBoundary>
      </main>
    </div>
  );
};
