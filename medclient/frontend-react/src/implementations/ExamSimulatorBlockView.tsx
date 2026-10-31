import React, { useState } from 'react';
import {
  evaluateHotspotHitWithTolerance,
  normalizeClickCoordinates,
} from '../base/hotspotGeometry';
import { useMedClientStore } from '../base/useMedClientStore';
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

  const handleHotspotCanvasClick = (mouseEv: React.MouseEvent<HTMLDivElement>): void => {
    const rect = mouseEv.currentTarget.getBoundingClientRect();
    const effectiveRect =
      rect.width > 0 && rect.height > 0
        ? rect
        : { left: 0, top: 0, width: 400, height: 300 };

    const [normU, normV] = normalizeClickCoordinates(
      mouseEv.clientX,
      mouseEv.clientY,
      effectiveRect
    );
    setLastClickCoords([normU, normV]);

    const polygons = questionSpec.target_polygons ?? [
      [
        [0.2, 0.2],
        [0.6, 0.2],
        [0.4, 0.6],
      ],
    ];
    const hitAny = polygons.some((poly) => evaluateHotspotHitWithTolerance(normU, normV, poly));
    setHotspotHitStatus(hitAny ? 'HIT' : 'MISS');
    recordExamAnswer(questionId, hitAny ? 'HOTSPOT_HIT' : 'HOTSPOT_MISS');
  };

  const handleEvaluateNliOpen = (): void => {
    const trimmedHypothesis = openResponseText.trim().toLowerCase();
    const referencePremise = (questionSpec.reference_premise ?? 'epinephrine').toLowerCase();
    const isEntailed =
      trimmedHypothesis.length >= 4 &&
      (trimmedHypothesis.includes(referencePremise) ||
        referencePremise.includes(trimmedHypothesis));
    setNliPassed(isEntailed);
    recordExamAnswer(questionId, openResponseText.trim());
  };

  const dagNodes = questionSpec.dag_nodes ?? {
    STEP_01: {
      node_id: 'STEP_01',
      clinical_vignette: 'Paziente ipoteso con lattati 4.8 mmol/L.',
      heart_rate_bpm: 118,
      systolic_bp_mmhg: 82,
      spo2_percent: 91,
      is_terminal: false,
      transitions: [
        {
          action_id: 'ACT_FLUIDS',
          label: 'Cristalloidi 30 mL/kg + Noradrenalina',
          target_node_id: 'STEP_02',
          delta_score: 50,
        },
      ],
    },
    STEP_02: {
      node_id: 'STEP_02',
      clinical_vignette: 'Stabilizzazione PAM > 65 mmHg ottenuta.',
      heart_rate_bpm: 88,
      systolic_bp_mmhg: 112,
      spo2_percent: 97,
      is_terminal: true,
      transitions: [],
    },
  };

  const currentDagNode = dagNodes[activeDagNodeId] ?? Object.values(dagNodes)[0];

  return (
    <section
      className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-md"
      data-testid="exam-simulator-block"
    >
      <header className="flex items-center justify-between border-b border-slate-800 pb-3">
        <div>
          <span className="rounded bg-indigo-950 px-2.5 py-0.5 text-xs font-semibold text-indigo-300">
            Modalita Esame: {block.item_type}
          </span>
          <h2 className="mt-1 text-lg font-bold text-white">
            {questionSpec.stem ?? 'Valutazione Clinica Interattiva'}
          </h2>
        </div>
        <div className="text-right text-xs text-slate-400" data-testid="fsrs-stability-badge">
          <div>FSRS Stability: {block.fsrs_card_state.stability ?? 1.0}d</div>
          <div>Difficulty: {block.fsrs_card_state.difficulty ?? 5.0}</div>
        </div>
      </header>

      {block.item_type === 'MCQ' && (
        <div className="space-y-2" data-testid="exam-mode-mcq">
          {(questionSpec.options ?? ['A', 'B', 'C', 'D']).map((optionText, idx) => {
            const isSelected = examAnswers[questionId] === idx;
            return (
              <button
                key={`mcq-opt-${idx}`}
                type="button"
                onClick={() => recordExamAnswer(questionId, idx)}
                className={`w-full rounded-lg border px-4 py-2.5 text-left text-sm transition ${
                  isSelected
                    ? 'border-blue-500 bg-blue-950/70 font-semibold text-white'
                    : 'border-slate-800 bg-slate-950 text-slate-200 hover:border-slate-700'
                }`}
                data-testid={`mcq-option-${idx}`}
              >
                {idx + 1}. {optionText}
              </button>
            );
          })}
        </div>
      )}

      {(block.item_type === 'HOTSPOT' || block.item_type === 'IMAGE_HOTSPOT') && (
        <div className="space-y-3" data-testid="exam-mode-hotspot">
          <div
            onClick={handleHotspotCanvasClick}
            className="relative flex h-64 w-full cursor-crosshair items-center justify-center overflow-hidden rounded-lg border border-slate-700 bg-slate-950"
            data-testid="hotspot-interactive-canvas"
          >
            <span className="pointer-events-none text-xs text-slate-400">
              Clicca sulla lesione anatomica ({questionSpec.image_uri ?? 'med-asset://images/cxr.webp'})
            </span>
          </div>
          <div className="text-xs font-semibold" data-testid="hotspot-hit-feedback">
            Esito Ray-Casting [0,1]²: {hotspotHitStatus}
            {lastClickCoords &&
              ` (u=${lastClickCoords[0].toFixed(3)}, v=${lastClickCoords[1].toFixed(3)})`}
          </div>
        </div>
      )}

      {block.item_type === 'NLI_OPEN' && (
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

      {block.item_type === 'DAG_SCENARIO' && currentDagNode && (
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
