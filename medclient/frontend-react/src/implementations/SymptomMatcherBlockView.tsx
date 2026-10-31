import React, { useState, useEffect } from 'react';
import { useMedClientStore } from '../base/useMedClientStore';
import type { DifferentialCandidate, SymptomMatcherBlock } from '../interfaces/sduiContracts';

import { sidecarIpcClient } from '../base/useMedClientStore';
import type { HybridSearchResponse } from '../interfaces/sduiContracts';

export interface HpoLexiconEntry {
  readonly hpoId: string;
  readonly clinicalTerm: string;
  readonly colloquialSynonyms: readonly string[];
}

export async function lookupHpoWithSymSpell(rawInput: string): Promise<readonly HpoLexiconEntry[]> {
  const cleanedQuery = rawInput.toLowerCase().trim();
  if (cleanedQuery.length < 2) {
    return [];
  }
  try {
    const searchResponse = await sidecarIpcClient.searchHybrid<HybridSearchResponse>(cleanedQuery);
    return (searchResponse?.matches ?? []).map((match) => ({
      hpoId: match.concept_id.toUpperCase().startsWith('HP:')
        ? match.concept_id.toUpperCase()
        : `HP:${match.concept_id.toUpperCase()}`,
      clinicalTerm: match.title,
      colloquialSynonyms: [match.title.toLowerCase()],
    }));
  } catch {
    return [];
  }
}

function buildRadarPolygonPoints(candidates: readonly DifferentialCandidate[]): string {
  if (candidates.length === 0) {
    return '100,100';
  }
  const center = 100;
  const maxRadius = 75;
  return candidates
    .map((candidate, idx) => {
      const angleRad = (Math.PI * 2 * idx) / Math.max(3, candidates.length) - Math.PI / 2;
      const clampedProb = Math.max(0.05, Math.min(1.0, candidate.probability));
      const pointX = Math.round(center + Math.cos(angleRad) * maxRadius * clampedProb);
      const pointY = Math.round(center + Math.sin(angleRad) * maxRadius * clampedProb);
      return `${pointX},${pointY}`;
    })
    .join(' ');
}

export interface SymptomMatcherBlockViewProps {
  readonly block: SymptomMatcherBlock;
  readonly suggestionsOverride?: readonly HpoLexiconEntry[];
}

export const SymptomMatcherBlockView: React.FC<SymptomMatcherBlockViewProps> = ({
  block,
  suggestionsOverride,
}) => {
  const [symptomInput, setSymptomInput] = useState<string>('');
  const [highlightedIndex, setHighlightedIndex] = useState<number>(-1);
  const [isDropdownVisible, setIsDropdownVisible] = useState<boolean>(true);
  const [asyncSuggestions, setAsyncSuggestions] = useState<readonly HpoLexiconEntry[]>([]);

  const selectedSymptoms = useMedClientStore((state) => state.selectedSymptoms);
  const toggleSymptomPolarity = useMedClientStore((state) => state.toggleSymptomPolarity);
  const removeSymptom = useMedClientStore((state) => state.removeSymptom);

  useEffect(() => {
    if (Object.keys(selectedSymptoms).length === 0 && block.selected_symptoms) {
      block.selected_symptoms.forEach((code) => {
        toggleSymptomPolarity(code, 'PRESENT');
      });
    }
  }, [block.selected_symptoms, selectedSymptoms, toggleSymptomPolarity]);

  useEffect(() => {
    let isActive = true;
    const trimmed = symptomInput.trim();
    if (trimmed.length < 2) {
      setAsyncSuggestions([]);
      return;
    }

    lookupHpoWithSymSpell(trimmed)
      .then((results) => {
        if (isActive) {
          setAsyncSuggestions(results);
        }
      })
      .catch(() => {
        if (isActive) {
          setAsyncSuggestions([]);
        }
      });

    return () => {
      isActive = false;
    };
  }, [symptomInput]);

  const rawSuggestions = suggestionsOverride ?? asyncSuggestions;
  const triage = block.triage_telemetry;
  const radarPoints = buildRadarPolygonPoints(block.differential_candidates);

  const activeOptionId =
    isDropdownVisible && highlightedIndex >= 0 && highlightedIndex < rawSuggestions.length
      ? `hpo-opt-${rawSuggestions[highlightedIndex].hpoId.replace(':', '-')}`
      : undefined;

  const handleInputKeyDown = (keyboardEvent: React.KeyboardEvent<HTMLInputElement>): void => {
    if (rawSuggestions.length === 0) {
      return;
    }
    if (keyboardEvent.key === 'ArrowDown') {
      keyboardEvent.preventDefault();
      setIsDropdownVisible(true);
      setHighlightedIndex((previousIndex) =>
        previousIndex + 1 >= rawSuggestions.length ? 0 : previousIndex + 1
      );
    } else if (keyboardEvent.key === 'ArrowUp') {
      keyboardEvent.preventDefault();
      setIsDropdownVisible(true);
      setHighlightedIndex((previousIndex) =>
        previousIndex <= 0 ? rawSuggestions.length - 1 : previousIndex - 1
      );
    } else if (keyboardEvent.key === 'Enter') {
      if (rawSuggestions.length > 0) {
        keyboardEvent.preventDefault();
        const targetIndex =
          highlightedIndex >= 0 && highlightedIndex < rawSuggestions.length ? highlightedIndex : 0;
        const selectedEntry = rawSuggestions[targetIndex];
        toggleSymptomPolarity(selectedEntry.hpoId, 'PRESENT');
        setSymptomInput('');
        setHighlightedIndex(-1);
        setIsDropdownVisible(false);
      }
    } else if (keyboardEvent.key === 'Escape') {
      keyboardEvent.preventDefault();
      setIsDropdownVisible(false);
      setHighlightedIndex(-1);
    }
  };

  return (
    <section
      className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-md"
      data-testid="symptom-matcher-block"
    >
      {triage && triage.alert_level === 'RED_CRITICAL' && (
        <div
          className="rounded-lg border-2 border-red-500 bg-red-950/90 p-4 text-red-100 shadow-lg"
          data-testid="emergency-red-critical-banner"
        >
          <div className="flex items-center justify-between font-bold">
            <span>ALLERTA EMERGENZA CLINICA (RED_CRITICAL)</span>
            <span className="rounded bg-red-600 px-2 py-0.5 text-xs text-white">
              qSOFA: {triage.qsofa_score} | NEWS2: {triage.news2_score} | SI:{' '}
              {triage.shock_index.toFixed(2)}
            </span>
          </div>
          <p className="mt-1 text-xs text-red-200">
            {triage.trigger_reason ?? 'Instabilita emodinamica rilevata: attivare protocollo sepsi/shock.'}
          </p>
        </div>
      )}

      <div className="space-y-2">
        <label
          htmlFor="symptom-search-field"
          className="block text-xs font-semibold uppercase tracking-wider text-slate-400"
        >
          Ricerca Sintomi HPO (Sinonimi Colloquiali &amp; SymSpell d&le;2)
        </label>
        <input
          id="symptom-search-field"
          name="symptom_search"
          type="text"
          role="combobox"
          aria-haspopup="listbox"
          aria-autocomplete="list"
          aria-expanded={isDropdownVisible && rawSuggestions.length > 0}
          aria-controls="symspell-suggestions-list"
          aria-activedescendant={activeOptionId}
          value={symptomInput}
          onChange={(ev) => {
            setSymptomInput(ev.target.value);
            setIsDropdownVisible(true);
            setHighlightedIndex(-1);
          }}
          onKeyDown={handleInputKeyDown}
          aria-label="Es. fiato corto, dyspne (typo), dolore toracico..."
          className="w-full rounded-md border border-slate-700 bg-slate-950 px-3 py-2 text-sm text-white focus:border-blue-500 focus:outline-none"
          data-testid="symptom-search-input"
        />
        {isDropdownVisible && rawSuggestions.length > 0 && (
          <div
            id="symspell-suggestions-list"
            role="listbox"
            aria-label="Suggerimenti vocabolario HPO"
            className="flex flex-wrap gap-2 pt-1"
            data-testid="symspell-suggestions"
          >
            {rawSuggestions.map((entry, optionIndex) => {
              const optionElementId = `hpo-opt-${entry.hpoId.replace(':', '-')}`;
              const isOptionHighlighted = highlightedIndex === optionIndex;
              return (
                <button
                  key={entry.hpoId}
                  id={optionElementId}
                  role="option"
                  aria-selected={isOptionHighlighted}
                  type="button"
                  onClick={() => {
                    toggleSymptomPolarity(entry.hpoId, 'PRESENT');
                    setSymptomInput('');
                    setHighlightedIndex(-1);
                    setIsDropdownVisible(false);
                  }}
                  className={`flex items-center gap-1.5 rounded px-2.5 py-1 text-xs font-semibold transition ${
                    isOptionHighlighted
                      ? 'bg-blue-600 text-white ring-2 ring-blue-300'
                      : 'bg-blue-900/60 text-blue-200 hover:bg-blue-800'
                  }`}
                  data-testid={`suggestion-item-${entry.hpoId}`}
                >
                  <span className="font-bold">+</span>
                  <span>{entry.clinicalTerm}</span>
                  <span className="font-mono text-blue-300">({entry.hpoId})</span>
                </button>
              );
            })}
          </div>
        )}
      </div>

      <div className="flex flex-wrap gap-2.5" data-testid="active-symptom-tags">
        {Object.entries(selectedSymptoms).map(([hpoCode, polarity]) => {
          const isPresent = polarity === 'PRESENT';
          return (
            <div
              key={hpoCode}
              className={`flex items-center gap-2 rounded-full border px-3 py-1 text-xs font-bold shadow-sm transition ${
                isPresent
                  ? 'border-emerald-500 bg-emerald-950/80 text-emerald-100 ring-1 ring-emerald-500/50'
                  : 'border-rose-500 bg-rose-950/80 text-rose-100 ring-1 ring-rose-500/50'
              }`}
              data-testid={`symptom-tag-${hpoCode}`}
            >
              <button
                type="button"
                onClick={() =>
                  toggleSymptomPolarity(hpoCode, isPresent ? 'ABSENT' : 'PRESENT')
                }
                className="flex items-center gap-1.5"
                data-testid={`toggle-symptom-${hpoCode}`}
                aria-label={`Inverti polarita ${hpoCode}`}
              >
                {isPresent ? (
                  <span
                    className="flex h-3.5 w-3.5 items-center justify-center rounded-full bg-emerald-500 text-[10px] font-black text-slate-950"
                    aria-hidden="true"
                  >
                    ✓
                  </span>
                ) : (
                  <span
                    className="flex h-3.5 w-3.5 items-center justify-center rounded-full bg-rose-600 text-[10px] font-black text-white"
                    aria-hidden="true"
                  >
                    ✕
                  </span>
                )}
                <span>
                  {hpoCode}: {isPresent ? 'PRESENTE' : 'NEGATIVO PERTINENTE'}
                </span>
              </button>
              <button
                type="button"
                onClick={() => removeSymptom(hpoCode)}
                className="ml-1 text-slate-400 hover:text-white"
                aria-label={`Rimuovi ${hpoCode}`}
              >
                ×
              </button>
            </div>
          );
        })}
      </div>

      <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
        <div className="space-y-3 md:col-span-2" data-testid="differential-probability-bars">
          <h3 className="text-sm font-bold text-slate-200">
            Diagnosi Differenziale Bayesiana (Log-Odds Softmax)
          </h3>
          {block.differential_candidates.map((candidate) => {
            const pct = Math.round(Math.max(0, Math.min(1, candidate.probability)) * 100);
            return (
              <div key={candidate.disease_id} className="space-y-1">
                <div className="flex justify-between text-xs">
                  <span className="font-semibold text-white">
                    {candidate.name} ({candidate.disease_id})
                  </span>
                  <span className="font-mono text-blue-300">{pct}%</span>
                </div>
                <div className="h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
                  <div
                    style={{ width: `${pct}%` }}
                    className="h-full rounded-full bg-blue-500 transition-all"
                  />
                </div>
              </div>
            );
          })}
        </div>

        <div className="flex flex-col items-center justify-center rounded-lg border border-slate-800 bg-slate-950 p-3">
          <span className="mb-1 text-xs font-semibold text-slate-400"> Spettro Probabilita SVG</span>
          <svg width={180} height={180} viewBox="0 0 200 200" data-testid="differential-radar-svg">
            <circle cx="100" cy="100" r="75" fill="none" stroke="#334155" strokeDasharray="3 3" />
            <circle cx="100" cy="100" r="40" fill="none" stroke="#1e293b" />
            <polygon
              points={radarPoints}
              fill="rgba(59, 130, 246, 0.35)"
              stroke="#3b82f6"
              strokeWidth="2"
            />
          </svg>
        </div>
      </div>

      {block.nbq && block.nbq.text && (
        <div
          className="flex flex-col justify-between gap-3 rounded-lg border border-indigo-500/40 bg-indigo-950/40 p-4 sm:flex-row sm:items-center"
          data-testid="nbq-interactive-card"
        >
          <div>
            <span className="text-xs font-bold uppercase text-indigo-300">
              Next-Best-Question (Max Information Gain)
            </span>
            <p className="mt-0.5 text-sm font-medium text-white">{block.nbq.text}</p>
          </div>
          <div className="flex gap-2">
            <button
              type="button"
              onClick={() =>
                toggleSymptomPolarity(block.nbq.hpo_id ?? block.nbq.question_id ?? 'HP:NBQ', 'PRESENT')
              }
              className="rounded bg-emerald-600 px-3 py-1.5 text-xs font-semibold text-white hover:bg-emerald-500"
            >
              Presente
            </button>
            <button
              type="button"
              onClick={() =>
                toggleSymptomPolarity(block.nbq.hpo_id ?? block.nbq.question_id ?? 'HP:NBQ', 'ABSENT')
              }
              className="rounded bg-rose-700 px-3 py-1.5 text-xs font-semibold text-white hover:bg-rose-600"
            >
              Assente
            </button>
          </div>
        </div>
      )}
    </section>
  );
};
