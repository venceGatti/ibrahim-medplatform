import React from 'react';
import type { DifferentialCandidate } from '../interfaces/sduiContracts';

export function buildRadarPolygonPoints(candidates: readonly DifferentialCandidate[]): string {
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

export interface DifferentialRadarDisplayProps {
  readonly candidates: readonly DifferentialCandidate[];
  readonly radarPoints: string;
}

export const DifferentialRadarDisplay: React.FC<DifferentialRadarDisplayProps> = ({
  candidates,
  radarPoints,
}) => {
  return (
    <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
      <div className="space-y-3 md:col-span-2" data-testid="differential-probability-bars">
        <h3 className="text-sm font-bold text-slate-200">
          Diagnosi Differenziale Bayesiana (Log-Odds Softmax)
        </h3>
        {candidates.map((candidate) => {
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
  );
};
