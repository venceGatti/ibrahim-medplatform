import React from 'react';
import type { CalloutSeverity, ClinicalSheetBlock } from '../interfaces/sduiContracts';
import { MolecularStructureViewer } from './MolecularStructureViewer';
import { VirtualBlockWindow } from './VirtualBlockWindow';

export interface ClinicalSheetBlockViewProps {
  readonly block: ClinicalSheetBlock;
  readonly scrollTopPx?: number;
  readonly onScrollOffsetChange?: (scrollTopPx: number) => void;
}

export function resolveCalloutThemeClasses(severity: CalloutSeverity): string {
  if (severity === 'RED_FLAG' || severity === 'CRITICAL') {
    return 'border-red-600 bg-red-50 text-red-950';
  }
  if (severity === 'BLACKBOX') {
    return 'border-slate-950 bg-red-950 text-red-100 ring-2 ring-red-500';
  }
  if (severity === 'WARNING') {
    return 'border-amber-500 bg-amber-50 text-amber-950';
  }
  if (severity === 'CLINICAL_PEARL') {
    return 'border-emerald-500 bg-emerald-50 text-emerald-950';
  }
  return 'border-blue-500 bg-blue-50 text-blue-950';
}

export const ClinicalSheetBlockView: React.FC<ClinicalSheetBlockViewProps> = ({
  block,
  scrollTopPx = 0,
  onScrollOffsetChange,
}) => {
  const paragraphs = block.content_markdown
    .split(/\r?\n/)
    .map((line) => line.trim())
    .filter((line) => line.length > 0);

  const mediaHashes = block.media_sha256_hashes ?? [];

  return (
    <section
      className="space-y-4 rounded-xl border border-slate-800 bg-slate-900/90 p-5 shadow-md"
      data-testid={`clinical-sheet-${block.sheet_id}`}
    >
      <header className="border-b border-slate-800 pb-3">
        <div className="flex items-center justify-between">
          <span className="rounded bg-blue-950 px-2.5 py-0.5 text-xs font-semibold text-blue-300">
            Monografia Clinica • {block.sheet_id}
          </span>
          <span className="text-xs text-slate-400">Schema: {block.block_type}</span>
        </div>
        <h2 className="mt-2 text-xl font-bold text-white">{block.title}</h2>
      </header>

      {block.callouts.length > 0 && (
        <div className="space-y-2" data-testid="clinical-sheet-callouts">
          {block.callouts.map((calloutEntry, idx) => (
            <div
              key={`callout-${block.sheet_id}-${idx}`}
              className={`rounded-md border-l-4 p-3 text-sm font-medium ${resolveCalloutThemeClasses(
                calloutEntry.severity
              )}`}
              data-testid={`callout-${calloutEntry.severity}`}
            >
              <div className="font-bold uppercase tracking-wide">
                [{calloutEntry.severity}] {calloutEntry.title ?? ''}
              </div>
              <p className="mt-1">{calloutEntry.message}</p>
            </div>
          ))}
        </div>
      )}

      <VirtualBlockWindow
        paragraphs={paragraphs}
        initialScrollTopPx={scrollTopPx}
        onScrollOffsetChange={onScrollOffsetChange}
      />

      {mediaHashes.length > 0 && (
        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2" data-testid="clinical-sheet-media">
          {mediaHashes.map((sha256Hash) => (
            <figure
              key={sha256Hash}
              className="overflow-hidden rounded-lg border border-slate-700 bg-slate-950 p-2"
            >
              <img
                src={`med-asset://images/${sha256Hash}.webp`}
                alt={`Reperto clinico ${sha256Hash.slice(0, 12)}`}
                loading="lazy"
                className="max-h-56 w-full object-contain"
              />
              <figcaption className="mt-1 truncate text-xs text-slate-400">
                med-asset://images/{sha256Hash}.webp
              </figcaption>
            </figure>
          ))}
        </div>
      )}

      {block.molecule_sha256_svg && (
        <MolecularStructureViewer
          moleculeId={`mol-${block.sheet_id}`}
          moleculeName={`Struttura Farmacologica (${block.title})`}
          svgSha256={block.molecule_sha256_svg}
          pdbSha256={block.molecule_sha256_pdb}
        />
      )}
    </section>
  );
};
