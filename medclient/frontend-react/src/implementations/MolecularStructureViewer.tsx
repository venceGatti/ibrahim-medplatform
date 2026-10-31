import React, { useEffect, useRef, useState } from 'react';
import { SingletonWebGLBroker } from './SingletonWebGLBroker';

export interface MolecularStructureViewerProps {
  readonly moleculeId: string;
  readonly moleculeName: string;
  readonly svgSha256: string;
  readonly pdbSha256?: string;
}

export const MolecularStructureViewer: React.FC<MolecularStructureViewerProps> = ({
  moleculeId,
  moleculeName,
  svgSha256,
  pdbSha256,
}) => {
  const [renderMode, setRenderMode] = useState<'SVG_2D' | 'WEBGL_3D'>('SVG_2D');
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const broker = SingletonWebGLBroker.getInstance();

  useEffect(() => {
    if (renderMode === 'WEBGL_3D' && canvasRef.current) {
      broker.acquireContext(moleculeId, canvasRef.current, () => {
        setRenderMode('SVG_2D');
      });
    }
    return () => {
      broker.releaseContext(moleculeId);
    };
  }, [renderMode, moleculeId, broker]);

  const handleActivate3D = (): void => {
    setRenderMode('WEBGL_3D');
  };

  const handleReleaseTo2D = (): void => {
    broker.releaseContext(moleculeId);
    setRenderMode('SVG_2D');
  };

  const svgAssetUri = `med-asset://molecules/${svgSha256}.svg`;
  const pdbAssetUri = pdbSha256 ? `med-asset://structures/${pdbSha256}.pdb` : '';

  return (
    <div
      className="rounded-lg border border-slate-700 bg-slate-900 p-4 shadow-sm"
      data-testid={`molecular-viewer-${moleculeId}`}
    >
      <div className="mb-3 flex items-center justify-between">
        <div>
          <h4 className="text-sm font-semibold text-slate-100">{moleculeName}</h4>
          <span className="text-xs text-slate-400">
            Modalita attiva: {renderMode === 'SVG_2D' ? 'SVG 2D (0 MB VRAM)' : 'WebGL 3D Singleton'}
          </span>
        </div>
        <div className="flex gap-2">
          {renderMode === 'SVG_2D' ? (
            <button
              type="button"
              onClick={handleActivate3D}
              className="rounded bg-blue-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-blue-700"
            >
              Esplora Modello 3D
            </button>
          ) : (
            <button
              type="button"
              onClick={handleReleaseTo2D}
              className="rounded bg-amber-600 px-3 py-1.5 text-xs font-medium text-white shadow-sm hover:bg-amber-700"
            >
              Ritorna a 2D SVG
            </button>
          )}
        </div>
      </div>

      {renderMode === 'SVG_2D' ? (
        <div
          className="flex flex-col items-center justify-center rounded bg-slate-950 p-4"
          data-testid={`svg-fallback-${moleculeId}`}
        >
          <img
            src={svgAssetUri}
            alt={`Struttura 2D ${moleculeName}`}
            loading="lazy"
            className="max-h-48 w-auto object-contain"
          />
          <p className="mt-2 text-xs text-slate-400">
             Asset Zero-Copy: <code>{svgAssetUri}</code>
          </p>
        </div>
      ) : (
        <div
          className="flex flex-col items-center justify-center rounded bg-slate-950 p-4"
          data-testid={`webgl-canvas-container-${moleculeId}`}
        >
          <canvas
            ref={canvasRef}
            width={360}
            height={220}
            onContextMenu={(ev) => ev.preventDefault()}
            className="rounded border border-blue-500/40 bg-black"
            data-testid={`webgl-canvas-${moleculeId}`}
          />
          {pdbAssetUri.length > 0 && (
            <p className="mt-2 text-xs text-blue-300">
              Coordinate 3D: <code>{pdbAssetUri}</code> (Contesti attivi:{' '}
              {broker.activeContextCount()})
            </p>
          )}
        </div>
      )}
    </div>
  );
};
