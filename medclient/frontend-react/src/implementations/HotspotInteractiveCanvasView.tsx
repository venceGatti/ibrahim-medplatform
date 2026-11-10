/**
 * Dedicated Hotspot interactive canvas overlay subview (ensures < 350 lines).
 */
import React from 'react';
import type { NormalizedVertex2D } from '../interfaces/sduiContracts';

export interface HotspotInteractiveCanvasViewProps {
  readonly imageUri?: string;
  readonly targetPolygons: readonly (readonly NormalizedVertex2D[])[];
  readonly lastClickCoords: NormalizedVertex2D | null;
  readonly hotspotHitStatus: 'IDLE' | 'HIT' | 'MISS';
  readonly onCanvasClick: (mouseEv: React.MouseEvent<HTMLDivElement>) => void;
}

export const HotspotInteractiveCanvasView: React.FC<HotspotInteractiveCanvasViewProps> = ({
  imageUri,
  targetPolygons,
  lastClickCoords,
  hotspotHitStatus,
  onCanvasClick,
}) => {
  return (
    <div className="space-y-3" data-testid="exam-mode-hotspot">
      <div
        onClick={onCanvasClick}
        className="relative flex h-64 w-full cursor-crosshair items-center justify-center overflow-hidden rounded-lg border border-slate-700 bg-slate-950 shadow-inner"
        data-testid="hotspot-interactive-canvas"
      >
        <span className="pointer-events-none select-none text-xs text-slate-400">
          Clicca sulla lesione anatomica ({imageUri ?? 'med-asset://images/cxr.webp'})
        </span>

        <svg
          className="pointer-events-none absolute inset-0 h-full w-full"
          viewBox="0 0 1000 1000"
          preserveAspectRatio="none"
          data-testid="hotspot-feedback-overlay"
        >
          {targetPolygons.map((polygonVertices, polyIdx) => (
            <polygon
              key={`target-poly-${polyIdx}`}
              points={polygonVertices
                .map(([vx, vy]) => `${Math.round(vx * 1000)},${Math.round(vy * 1000)}`)
                .join(' ')}
              fill="rgba(59, 130, 246, 0.08)"
              stroke="#3b82f6"
              strokeWidth="1.5"
              strokeDasharray="4 4"
              opacity={0.7}
            />
          ))}

          {lastClickCoords && hotspotHitStatus !== 'IDLE' && (
            <g
              data-testid="hotspot-feedback-ring"
              data-hit-status={hotspotHitStatus}
            >
              <circle
                cx={Math.round(lastClickCoords[0] * 1000)}
                cy={Math.round(lastClickCoords[1] * 1000)}
                r="32"
                fill={
                  hotspotHitStatus === 'HIT'
                    ? 'rgba(16, 185, 129, 0.15)'
                    : 'rgba(244, 63, 94, 0.15)'
                }
                className="animate-ping"
              />
              <circle
                cx={Math.round(lastClickCoords[0] * 1000)}
                cy={Math.round(lastClickCoords[1] * 1000)}
                r="20"
                fill={
                  hotspotHitStatus === 'HIT'
                    ? 'rgba(16, 185, 129, 0.3)'
                    : 'rgba(244, 63, 94, 0.3)'
                }
                stroke={hotspotHitStatus === 'HIT' ? '#10b981' : '#f43f5e'}
                strokeWidth="3"
              />
              <circle
                cx={Math.round(lastClickCoords[0] * 1000)}
                cy={Math.round(lastClickCoords[1] * 1000)}
                r="4"
                fill={hotspotHitStatus === 'HIT' ? '#34d399' : '#fb7185'}
              />
            </g>
          )}
        </svg>
      </div>
      <div
        className={`flex items-center justify-between rounded-md border px-3 py-2 text-xs font-semibold ${
          hotspotHitStatus === 'HIT'
            ? 'border-emerald-500/60 bg-emerald-950/80 text-emerald-200'
            : hotspotHitStatus === 'MISS'
              ? 'border-rose-500/60 bg-rose-950/80 text-rose-200'
              : 'border-slate-800 bg-slate-950 text-slate-400'
        }`}
        data-testid="hotspot-hit-feedback"
      >
        <span>
          Esito Ray-Casting [0,1]²: {hotspotHitStatus}
          {lastClickCoords &&
            ` (u=${lastClickCoords[0].toFixed(3)}, v=${lastClickCoords[1].toFixed(3)})`}
        </span>
        <span className="font-mono text-[11px] uppercase tracking-wide">
          {hotspotHitStatus === 'HIT'
            ? '✓ BERSAGLIO CENTRATO (R_tol ≤ 0.02)'
            : hotspotHitStatus === 'MISS'
              ? '✕ FUORI TOLLERANZA'
              : 'In attesa di selezione'}
        </span>
      </div>
    </div>
  );
};
