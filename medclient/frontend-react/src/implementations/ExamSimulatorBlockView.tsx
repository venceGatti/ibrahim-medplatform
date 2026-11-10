import React, { useEffect, useState } from 'react';
import {
  evaluateHotspotHitWithTolerance,
  normalizeClickCoordinates,
} from '../base/hotspotGeometry';
import { sidecarIpcClient, useMedClientStore } from '../base/useMedClientStore';
import { HotspotCanvas } from './HotspotCanvas';
import type {
  ExamSimulatorBlock,
  FsrsRatingGrade,
  NormalizedVertex2D,
} from '../interfaces/sduiContracts';

export interface ExamSimulatorBlockViewProps {
  readonly block: ExamSimulatorBlock;
}

const FSRS_BUTTONS: readonly { readonly grade: FsrsRatingGrade; readonly label: string; readonly color: string }[] = [
  { grade: 1, label: 'Again (1)', color: 'bg-rose-700 hover:bg-rose-600' },
  { grade: 2, label: 'Hard (2)', color: 'bg-amber-700 hover:bg-amber-600' },
  { grade: 3, label: 'Good (3)', color: 'bg-emerald-700 hover:bg-emerald-600' },
  { grade: 4, label: 'Easy (4)', color: 'bg-blue-700 hover:bg-blue-600' },
];

export const ExamSimulatorBlockView: React.FC<ExamSimulatorBlockViewProps> = ({ block }) => {
  const questionSpec = block.question_spec ?? {
    question_id: 'Q_DEFAULT',
    stem: 'Valutare il quadro clinico presentato.',
    options: ['Opzione A', 'Opzione B', 'Opzione C', 'Opzione D'],
    correct_index: 0,
  };
  const questionId = questionSpec.question_id ?? 'Q_ACTIVE';

  const examAnswers = useMedClientStore((state) => state.examAnswers);
  const recordExamAnswer = useMedClientStore((state) => state.recordExamAnswer);
  const recordFsrsRating = useMedClientStore((state) => state.recordFsrsRating);
  const fsrsReviewHistory = useMedClientStore((state) => state.fsrsReviewHistory);

  const [hotspotHitStatus, setHotspotHitStatus] = useState<'IDLE' | 'HIT' | 'MISS'>('IDLE');
  const [lastClickCoords, setLastClickCoords] = useState<NormalizedVertex2D | null>(null);
  const [openResponseText, setOpenResponseText] = useState<string>('');
  const [nliPassed, setNliPassed] = useState<boolean | null>(null);
  const [activeDagNodeId, setActiveDagNodeId] = useState<string>(
    questionSpec.current_step ?? 'STEP_01'
  );
  const [activeMode, setActiveMode] = useState<string>(block.item_type ?? 'MCQ');

  useEffect(() => {
    const existingAnswer = examAnswers[questionId];
    if (existingAnswer === 'HOTSPOT_HIT') {
      setHotspotHitStatus('HIT');
    } else if (existingAnswer === 'HOTSPOT_MISS') {
      setHotspotHitStatus('MISS');
    } else if (!existingAnswer) {
      setHotspotHitStatus('IDLE');
      setLastClickCoords(null);
    }
  }, [questionId, examAnswers]);

  const handleHotspotCanvasClick = (mouseEv: React.MouseEvent<HTMLDivElement>): void => {
    const rect = mouseEv.currentTarget.getBoundingClientRect();
    const effectiveRect =
      rect.width > 0 && rect.height > 0
        ? rect
        : { left: 0, top: 0, width: 400, height: 300 };

    const [rawU, rawV] = normalizeClickCoordinates(
      mouseEv.clientX,
      mouseEv.clientY,
      effectiveRect
    );
    const clampedU = Math.max(0.0, Math.min(1.0, rawU));
    const clampedV = Math.max(0.0, Math.min(1.0, rawV));
    setLastClickCoords([clampedU, clampedV]);

    const polygons = questionSpec.target_polygons ?? [
      [
        [0.2, 0.2],
        [0.6, 0.2],
        [0.4, 0.6],
      ],
    ];
    const hitAny = polygons.some((poly) => evaluateHotspotHitWithTolerance(clampedU, clampedV, poly));
    setHotspotHitStatus(hitAny ? 'HIT' : 'MISS');
    recordExamAnswer(questionId, hitAny ? 'HOTSPOT_HIT' : 'HOTSPOT_MISS');
  };

  const handleEvaluateNliOpen = async (): Promise<void> => {
    const trimmedHypothesis = openResponseText.trim();
    if (trimmedHypothesis.length === 0) {
      return;
    }
    try {
      const evaluationResult = await sidecarIpcClient.executeAction('EVALUATE_NLI', {
        premise: questionSpec.reference_premise ?? '',
        hypothesis: trimmedHypothesis,
      });

      const outcomeData = (evaluationResult as any).execution_outcome as
        | { is_correct?: boolean; feedback?: string }
        | undefined;

      const isEntailed = Boolean(outcomeData?.is_correct);
      setNliPassed(isEntailed);
      recordExamAnswer(questionId, trimmedHypothesis);
    } catch {
      setNliPassed(false);
      recordExamAnswer(questionId, trimmedHypothesis);
    }
  };

  const dagNodes = questionSpec.dag_nodes ?? {
    STEP_01: {
      node_id: 'STEP_01', clinical_vignette: 'Paziente ipoteso con lattati 4.8 mmol/L.',
      heart_rate_bpm: 118, systolic_bp_mmhg: 82, spo2_percent: 91, is_terminal: false,
      transitions: [{ action_id: 'ACT_FLUIDS', label: 'Cristalloidi 30 mL/kg + Noradrenalina', target_node_id: 'STEP_02', delta_score: 50 }],
    },
    STEP_02: {
      node_id: 'STEP_02', clinical_vignette: 'Stabilizzazione PAM > 65 mmHg ottenuta.',
      heart_rate_bpm: 88, systolic_bp_mmhg: 112, spo2_percent: 97, is_terminal: true, transitions: [],
    },
  };

  const currentDagNode = dagNodes[activeDagNodeId] ?? Object.values(dagNodes)[0];

  return (
    <section
      className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-md"
      data-testid="exam-simulator-block"
    >
      <header className="flex flex-wrap items-center justify-between gap-3 border-b border-slate-800 pb-3">
        <div>
          <div className="flex items-center gap-2">
            <span className="text-xs font-semibold text-slate-400">Modalita Esame:</span>
            <div className="flex gap-1 rounded bg-slate-950 p-0.5 border border-slate-800" data-testid="exam-mode-selector">
              {(['MCQ', 'HOTSPOT', 'NLI_OPEN', 'DAG_SCENARIO'] as const).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setActiveMode(mode)}
                  className={`rounded px-2.5 py-0.5 text-xs font-semibold transition ${
                    activeMode === mode
                      ? 'bg-indigo-600 text-white shadow'
                      : 'text-slate-400 hover:text-slate-200'
                  }`}
                  data-testid={`exam-mode-btn-${mode}`}
                >
                  {mode}
                </button>
              ))}
            </div>
          </div>
          <h2 className="mt-2 text-base font-bold text-white">
            {questionSpec.stem ?? 'Valutazione Clinica Interattiva'}
          </h2>
        </div>
        <div className="text-right text-xs text-slate-400" data-testid="fsrs-stability-badge">
          <div>FSRS Stability: {block.fsrs_card_state.stability ?? 1.0}d</div>
          <div>Difficulty: {block.fsrs_card_state.difficulty ?? 5.0}</div>
        </div>
      </header>

      {activeMode === 'MCQ' && (
        <div className="space-y-3" data-testid="exam-mode-mcq">
          <div className="space-y-2">
            {(questionSpec.options ?? ['A', 'B', 'C', 'D']).map((optionText, idx) => {
              const selectedAnswerIdx = examAnswers[questionId];
              const isAnswered = selectedAnswerIdx !== undefined;
              const isSelected = selectedAnswerIdx === idx;
              const isCorrect = idx === questionSpec.correct_index;
              const isWrongSelection = isSelected && !isCorrect;

              let buttonStyleClass =
                'border-slate-800 bg-slate-950 text-slate-200 hover:border-slate-700';
              if (isAnswered) {
                if (isCorrect) {
                  buttonStyleClass =
                    'border-emerald-500 bg-emerald-950/70 text-emerald-100 font-semibold ring-1 ring-emerald-500';
                } else if (isWrongSelection) {
                  buttonStyleClass =
                    'border-rose-600 bg-rose-950/80 text-rose-200 font-semibold ring-1 ring-rose-500';
                } else {
                  buttonStyleClass =
                    'border-slate-800 bg-slate-950/40 text-slate-400 opacity-60';
                }
              }

              return (
                <button
                  key={`mcq-opt-${idx}`}
                  type="button"
                  onClick={() => recordExamAnswer(questionId, idx)}
                  className={`flex w-full items-center justify-between rounded-lg border px-4 py-2.5 text-left text-sm transition ${buttonStyleClass}`}
                  data-testid={`mcq-option-${idx}`}
                >
                  <span>
                    {idx + 1}. {optionText}
                  </span>
                  {isAnswered && isCorrect && (
                    <span className="text-xs font-bold text-emerald-400">✓ Corretto</span>
                  )}
                  {isAnswered && isWrongSelection && (
                    <span className="text-xs font-bold text-rose-400">✕ Errato</span>
                  )}
                </button>
              );
            })}
          </div>

          {examAnswers[questionId] !== undefined && (
            <div
              className="rounded-lg border border-slate-700 bg-slate-950/90 p-3.5 text-xs text-slate-300 shadow-sm"
              data-testid="mcq-clinical-rationale"
            >
              <div className="font-bold text-blue-400">Razionale Clinico (Linee Guida ESC / CPIC):</div>
              <p className="mt-1 leading-relaxed">
                {questionSpec.correct_index === 1
                  ? 'Il Pantoprazolo preserva la bioattivazione del Clopidogrel perché non inibisce in modo significativo il citocromo CYP2C19, riducendo il rischio di eventi ischemici acuti e trombosi dello stent.'
                  : 'Risposta clinica registrata. Valutare il profilo di interazione farmacocinetica e la clearance epatica.'}
              </p>
            </div>
          )}
        </div>
      )}

      {(activeMode === 'HOTSPOT' || activeMode === 'IMAGE_HOTSPOT') && (
        <HotspotCanvas
          imageUri={questionSpec.image_uri}
          targetPolygons={questionSpec.target_polygons}
          lastClickCoords={lastClickCoords}
          hotspotHitStatus={hotspotHitStatus}
          onCanvasClick={handleHotspotCanvasClick}
        />
      )}

      {activeMode === 'NLI_OPEN' && (
        <div className="space-y-3" data-testid="exam-mode-nli-open">
          <textarea
            rows={3}
            value={openResponseText}
            onChange={(ev) => setOpenResponseText(ev.target.value)}
            aria-label="Descrivi il trattamento d'emergenza di prima linea..."
            className="w-full rounded border border-slate-700 bg-slate-950 p-3 text-sm text-white"
            data-testid="nli-open-textarea"
          />
          <button
            type="button"
            onClick={handleEvaluateNliOpen}
            className="rounded bg-blue-600 px-4 py-1.5 text-xs font-semibold text-white hover:bg-blue-500"
            data-testid="nli-submit-button"
          >
            Verifica Entailment NLI
          </button>
          {nliPassed !== null && (
            <p className="text-xs font-bold text-emerald-300" data-testid="nli-evaluation-outcome">
              Esito NLI: {nliPassed ? 'ENTAILMENT CONFERMATO (>= 0.75)' : 'CONTRADDIZIONE / INCOMPLETO'}
            </p>
          )}
        </div>
      )}

      {activeMode === 'DAG_SCENARIO' && currentDagNode && (
        <div className="space-y-3 rounded-lg border border-slate-800 bg-slate-950 p-4" data-testid="exam-mode-dag">
          <div className="flex flex-wrap gap-3 text-xs font-mono">
            <span className="rounded bg-slate-900 px-2 py-1 text-rose-300">
              FC: {currentDagNode.heart_rate_bpm} bpm
            </span>
            <span className="rounded bg-slate-900 px-2 py-1 text-amber-300">
              PA Sistolica: {currentDagNode.systolic_bp_mmhg} mmHg
            </span>
            <span className="rounded bg-slate-900 px-2 py-1 text-cyan-300">
              SpO2: {currentDagNode.spo2_percent}%
            </span>
          </div>
          <p className="text-sm text-slate-200">{currentDagNode.clinical_vignette}</p>
          <div className="flex flex-wrap gap-2">
            {currentDagNode.transitions.map((transition) => (
              <button
                key={transition.action_id}
                type="button"
                onClick={() => setActiveDagNodeId(transition.target_node_id)}
                className="rounded bg-indigo-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-indigo-500"
                data-testid={`dag-transition-${transition.action_id}`}
              >
                {transition.label}
              </button>
            ))}
          </div>
        </div>
      )}

      <footer className="flex flex-wrap items-center justify-between gap-2 border-t border-slate-800 pt-3">
        <span className="text-xs text-slate-400">
          Schedulazione Mnemonica FSRS v5 (Ultimo voto:{' '}
          {fsrsReviewHistory[questionId] ?? 'Non valutato'}):
        </span>
        <div className="flex gap-2" data-testid="fsrs-rating-buttons">
          {FSRS_BUTTONS.map((btn) => (
            <button
              key={btn.grade}
              type="button"
              onClick={() => recordFsrsRating(questionId, btn.grade)}
              className={`rounded px-3 py-1 text-xs font-bold text-white ${btn.color}`}
              data-testid={`fsrs-grade-${btn.grade}`}
            >
              {btn.label}
            </button>
          ))}
        </div>
      </footer>
    </section>
  );
};
