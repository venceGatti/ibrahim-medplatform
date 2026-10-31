import React from 'react';
import { useMedClientStore } from '../base/useMedClientStore';
import type { DrugSafetyBlock } from '../interfaces/sduiContracts';

const CANONICAL_CYP_ENZYMES = ['CYP3A4', 'CYP2D6', 'CYP2C9', 'CYP2C19', 'CYP1A2'] as const;

export function resolveEgfrBadgeTheme(egfrValue: number): {
  readonly colorName: 'green' | 'orange' | 'red';
  readonly badgeClass: string;
  readonly stageLabel: string;
} {
  if (egfrValue >= 60.0) {
    return {
      colorName: 'green',
      badgeClass: 'border-emerald-500 bg-emerald-950/80 text-emerald-200',
      stageLabel: 'Funzione Renale Conservata (G1-G2)',
    };
  }
  if (egfrValue >= 30.0) {
    return {
      colorName: 'orange',
      badgeClass: 'border-amber-500 bg-amber-950/80 text-amber-200',
      stageLabel: 'Insufficienza Renale Moderata (G3a-G3b)',
    };
  }
  return {
    colorName: 'red',
    badgeClass: 'border-red-600 bg-red-950/90 text-red-200',
    stageLabel: 'Insufficienza Renale Severa (G4-G5)',
  };
}

export function resolveClearanceGaugeColors(percentageScore: number): {
  readonly textColorClass: string;
  readonly barBgClass: string;
  readonly statusClassification: 'PRESERVED' | 'MODERATE' | 'IMPAIRED';
} {
  if (percentageScore > 80) {
    return {
      textColorClass: 'text-emerald-400',
      barBgClass: 'bg-emerald-500',
      statusClassification: 'PRESERVED',
    };
  }
  if (percentageScore >= 40) {
    return {
      textColorClass: 'text-amber-400',
      barBgClass: 'bg-amber-500',
      statusClassification: 'MODERATE',
    };
  }
  return {
    textColorClass: 'text-rose-500',
    barBgClass: 'bg-rose-600',
    statusClassification: 'IMPAIRED',
  };
}

export function resolveInteractionSeverityLabel(level: 1 | 2 | 3 | 4): string {
  const labels: Record<1 | 2 | 3 | 4, string> = {
    1: 'CONTRAINDICATED',
    2: 'MAJOR',
    3: 'MODERATE',
    4: 'MINOR',
  };
  return labels[level];
}

export interface DrugSafetyBlockViewProps {
  readonly block: DrugSafetyBlock;
}

export const DrugSafetyBlockView: React.FC<DrugSafetyBlockViewProps> = ({ block }) => {
  const renalParameters = useMedClientStore((state) => state.renalParameters);
  const updateRenalParameters = useMedClientStore((state) => state.updateRenalParameters);
  const activeMedications = useMedClientStore((state) => state.activeMedications);

  const displayedEgfr = block.egfr ?? renalParameters.calculatedEgfr;
  const egfrTheme = resolveEgfrBadgeTheme(displayedEgfr);
  const egfrScaledPercentage = Math.min(100, Math.max(0, Math.round((displayedEgfr / 120) * 100)));
  const egfrGaugeColors = resolveClearanceGaugeColors(egfrScaledPercentage);

  const hasBlackboxProdrugAlert = block.alerts.some(
    (safetyAlert) => safetyAlert.code === 'BLACKBOX_INEFFICACY' || safetyAlert.severity === 1
  );

  return (
    <section
      className="space-y-5 rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-md"
      data-testid="drug-safety-block"
    >
      <div className="flex flex-col justify-between gap-4 border-b border-slate-800 pb-4 md:flex-row md:items-center">
        <div>
          <h2 className="text-lg font-bold text-white">
            Sicurezza Farmacologica CYP450 &amp; Funzione Renale CKD-EPI 2021
          </h2>
          <p className="text-xs text-slate-400">
            Principi attivi in terapia ({activeMedications.length}): {activeMedications.join(', ')}
          </p>
        </div>

        <div
          className={`min-w-64 rounded-lg border px-4 py-2.5 shadow-sm ${egfrTheme.badgeClass}`}
          data-testid="egfr-status-badge"
          data-color={egfrTheme.colorName}
        >
          <div className="flex items-center justify-between text-xs font-semibold uppercase">
            <span>{egfrTheme.stageLabel}</span>
            <span className={egfrGaugeColors.textColorClass}>{egfrScaledPercentage}%</span>
          </div>
          <div className="font-mono text-lg font-bold">
            eGFR: {displayedEgfr.toFixed(1)} mL/min/1.73m²
          </div>
          <div className="mt-1.5 h-2 w-full overflow-hidden rounded-full bg-slate-800">
            <div
              style={{ width: `${egfrScaledPercentage}%` }}
              className={`h-full transition-all duration-500 ease-out ${egfrGaugeColors.barBgClass}`}
              data-testid="egfr-progress-bar"
            />
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 gap-3 rounded-lg border border-slate-800 bg-slate-950 p-3 sm:grid-cols-3">
        <div>
          <label className="block text-xs text-slate-400">Eta Paziente (anni)</label>
          <input
            type="number"
            min={18}
            max={115}
            value={renalParameters.ageYears}
            onChange={(ev) =>
              updateRenalParameters(
                Number(ev.target.value) || 65,
                renalParameters.isFemale,
                renalParameters.serumCreatinineMgDl
              )
            }
            className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-white"
            data-testid="input-renal-age"
          />
        </div>
        <div>
          <label className="block text-xs text-slate-400">Creatinina Sierica (mg/dL)</label>
          <input
            type="number"
            step="0.1"
            min={0.2}
            max={15.0}
            value={renalParameters.serumCreatinineMgDl}
            onChange={(ev) =>
              updateRenalParameters(
                renalParameters.ageYears,
                renalParameters.isFemale,
                Number(ev.target.value) || 1.0
              )
            }
            className="mt-1 w-full rounded border border-slate-700 bg-slate-900 px-2 py-1 text-sm text-white"
            data-testid="input-renal-creatinine"
          />
        </div>
        <div className="flex items-end">
          <button
            type="button"
            onClick={() =>
              updateRenalParameters(
                renalParameters.ageYears,
                !renalParameters.isFemale,
                renalParameters.serumCreatinineMgDl
              )
            }
            className="w-full rounded border border-slate-700 bg-slate-800 px-3 py-1.5 text-xs font-semibold text-slate-200 hover:bg-slate-700"
          >
            Sesso Biologico: {renalParameters.isFemale ? 'Femminile' : 'Maschile'}
          </button>
        </div>
      </div>

      {hasBlackboxProdrugAlert && (
        <div
          className="relative rounded-xl border-2 border-rose-600 bg-rose-950 p-4 text-rose-100 shadow-2xl ring-2 ring-rose-600/50"
          data-testid="blackbox-prodrug-alert"
        >
          <div className="flex flex-wrap items-center justify-between gap-2">
            <div className="flex items-center gap-2">
              <span className="rounded bg-rose-600 px-2.5 py-0.5 text-xs font-black uppercase tracking-wider text-white">
                ALLERTA IMPERATIVA BLACKBOX LEVEL 1
              </span>
              <span className="font-bold tracking-wide text-rose-200">
                BLOCCO BIOATTIVAZIONE PROFARMACO (ROA-10)
              </span>
            </div>
            <span className="rounded border border-rose-400/30 bg-rose-900/60 px-2 py-0.5 text-[11px] font-mono text-rose-200">
              CYP2C19-MEDIATO
            </span>
          </div>

          <p className="mt-2 text-sm font-semibold text-white">
            Interazione critica Clopidogrel + Inibitore di Pompa Protonica (Omeprazolo): inibizione
            competitiva della conversione epatica nel metabolita tiolico attivo con perdita di
            efficacia antiaggregante piastrinica e aumento del rischio di trombosi dello stent.
          </p>

          <div className="mt-3 rounded-lg border border-amber-500/50 bg-amber-950/70 p-3 text-xs text-amber-200">
            <div className="font-bold uppercase tracking-wider text-amber-300">
              Indicazione Linea Guida Clinica Alternativa (ESC / FDA / CPIC):
            </div>
            <ul className="mt-1 list-inside list-disc space-y-0.5 text-slate-200">
              <li>
                <strong className="text-white">Gastroprotezione alternativa:</strong> Sostituire
                Omeprazolo/Esomeprazolo con <span className="font-bold text-emerald-300">Pantoprazolo</span> (minimo potenziale di inibizione su CYP2C19).
              </li>
              <li>
                <strong className="text-white">Opzione antiaggregante alternativa:</strong> Se indicato,
                valutare switch da Clopidogrel a <span className="font-bold text-emerald-300">Prasugrel</span> o <span className="font-bold text-emerald-300">Ticagrelor</span> (farmacocinetica indipendente dall&apos;isoenzima CYP2C19).
              </li>
            </ul>
          </div>
        </div>
      )}

      {block.triple_whammy_detected && (
        <div
          className="rounded-lg border border-rose-500 bg-rose-950/80 p-3 text-xs font-semibold text-rose-200"
          data-testid="triple-whammy-alert"
        >
          ALLERTA TRIPLE WHAMMY AKI: Co-somministrazione ACE-i/ARB + Diuretico + FANS ad alto rischio di
          insufficienza renale acuta emodinamica.
        </div>
      )}

      {block.fdc_decompositions && block.fdc_decompositions.length > 0 && (
        <div className="space-y-1.5" data-testid="fdc-decomposition-badges">
          <span className="text-xs font-bold uppercase tracking-wider text-purple-300">
            Decomposizione FDC (Combinazioni a Dose Fissa)
          </span>
          <div className="flex flex-wrap gap-2 pt-0.5">
            {block.fdc_decompositions.map((fdcDecomposition) => (
              <div
                key={fdcDecomposition.brand_or_combo_name}
                className="inline-flex items-center gap-1.5 rounded-lg border border-purple-500/40 bg-purple-950/60 px-3 py-1.5 text-xs text-purple-200 shadow-sm"
                data-testid={`fdc-badge-${fdcDecomposition.brand_or_combo_name}`}
              >
                <span className="font-extrabold text-purple-400">FDC:</span>
                <span className="font-bold text-white">{fdcDecomposition.brand_or_combo_name}</span>
                <span className="text-purple-300">&rarr;</span>
                <span className="font-medium text-purple-100">
                  {fdcDecomposition.active_principles.join(' + ')}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="space-y-2" data-testid="cyp450-clearance-gauges">
        <h3 className="text-sm font-bold text-slate-200">
          Capacita di Clearance Residua Isoenzimi Citocromo P450
        </h3>
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-5">
          {CANONICAL_CYP_ENZYMES.map((enzymeId) => {
            const rawClearance = block.cyp_clearance[enzymeId] ?? 1.0;
            const boundedClearance = Math.max(0.0, Math.min(1.0, rawClearance));
            const pct = Math.round(boundedClearance * 100);
            const gaugeColors = resolveClearanceGaugeColors(pct);
            return (
              <div
                key={enzymeId}
                className="rounded-lg border border-slate-800 bg-slate-950 p-3 shadow-sm"
                data-testid={`cyp-gauge-${enzymeId}`}
              >
                <div className="flex justify-between text-xs font-bold">
                  <span className="text-slate-300">{enzymeId}</span>
                  <span className={gaugeColors.textColorClass}>{pct}%</span>
                </div>
                <div className="mt-2 h-2.5 w-full overflow-hidden rounded-full bg-slate-800">
                  <div
                    style={{ width: `${pct}%` }}
                    className={`h-full transition-all duration-500 ease-out ${gaugeColors.barBgClass}`}
                  />
                </div>
              </div>
            );
          })}
        </div>
      </div>

      <div className="space-y-2" data-testid="drug-interaction-list">
        <h3 className="text-sm font-bold text-slate-200">
          Matrice Interazioni Farmacodinamiche / Farmacocinetiche ({block.interactions.length})
        </h3>
        {block.interactions.length === 0 ? (
          <p className="text-xs text-emerald-400" data-testid="clean-interactions-state">
            Nessuna interazione clinicamente significativa rilevata nel piano terapeutico.
          </p>
        ) : (
          block.interactions.map((interaction, idx) => (
            <div
              key={`${interaction.drug_a}-${interaction.drug_b}-${idx}`}
              className="flex items-center justify-between rounded border border-slate-800 bg-slate-950 p-3 text-xs"
            >
              <div>
                <span className="font-bold text-white">
                  {interaction.drug_a} + {interaction.drug_b}
                </span>
                <p className="text-slate-400">{interaction.mechanism}</p>
              </div>
              <span className="rounded bg-red-900/70 px-2.5 py-1 font-bold text-red-200">
                Level {interaction.level}: {resolveInteractionSeverityLabel(interaction.level)}
              </span>
            </div>
          ))
        )}
      </div>
    </section>
  );
};
