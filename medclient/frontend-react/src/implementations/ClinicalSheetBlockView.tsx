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
    return 'border-rose-600 bg-rose-600/10 text-rose-100';
  }
  if (severity === 'BLACKBOX') {
    return 'border-amber-500 bg-amber-500/10 text-amber-200';
  }
  if (severity === 'WARNING') {
    return 'border-amber-500 bg-amber-500/10 text-amber-200';
  }
  if (severity === 'CLINICAL_PEARL' || severity === 'EXAM_TIP') {
    return 'border-sky-600 bg-sky-600/10 text-sky-100';
  }
  return 'border-blue-500 bg-blue-500/10 text-blue-100';
}

export function resolveCalloutBadgeClasses(severity: CalloutSeverity): string {
  if (severity === 'RED_FLAG' || severity === 'CRITICAL') {
    return 'bg-rose-600 text-white';
  }
  if (severity === 'BLACKBOX') {
    return 'bg-amber-500 text-slate-950 font-black';
  }
  if (severity === 'CLINICAL_PEARL' || severity === 'EXAM_TIP') {
    return 'bg-sky-600 text-white';
  }
  if (severity === 'WARNING') {
    return 'bg-amber-500 text-slate-950 font-bold';
  }
  return 'bg-blue-600 text-white';
}

function renderCalloutIcon(severity: CalloutSeverity): React.ReactNode {
  if (severity === 'RED_FLAG' || severity === 'CRITICAL') {
    return (
      <svg
        className="h-5 w-5 shrink-0 text-rose-500"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth="2"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 9v3.75m-9.303 3.376c-.866 1.5.217 3.374 1.948 3.374h14.71c1.73 0 2.813-1.874 1.948-3.374L13.949 3.378c-.866-1.5-3.032-1.5-3.898 0L2.697 16.126zM12 15.75h.007v.008H12v-.008z"
        />
      </svg>
    );
  }
  if (severity === 'BLACKBOX') {
    return (
      <svg
        className="h-5 w-5 shrink-0 text-amber-400"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth="2"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
        />
      </svg>
    );
  }
  if (severity === 'CLINICAL_PEARL' || severity === 'EXAM_TIP') {
    return (
      <svg
        className="h-5 w-5 shrink-0 text-sky-400"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth="2"
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M12 18v-5.25m0 0a6.01 6.01 0 001.5-.189m-1.5.189a6.01 6.01 0 01-1.5-.189m3.75 7.478a12.06 12.06 0 01-4.5 0m3.75 2.383a14.406 14.406 0 01-3 0M14.25 18v-.192c0-.983.658-1.823 1.508-2.316a7.5 7.5 0 10-7.516 0c.85.493 1.508 1.333 1.508 2.316V18"
        />
      </svg>
    );
  }
  return (
    <svg
      className="h-5 w-5 shrink-0 text-blue-400"
      fill="none"
      viewBox="0 0 24 24"
      strokeWidth="2"
      stroke="currentColor"
      aria-hidden="true"
    >
      <path
        strokeLinecap="round"
        strokeLinejoin="round"
        d="M11.25 11.25l.041-.02a.75.75 0 011.063.852l-.708 2.836a.75.75 0 001.063.853l.041-.021M21 12a9 9 0 11-18 0 9 9 0 0118 0zm-9-3.75h.008v.008H12V8.25z"
      />
    </svg>
  );
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
        <div className="space-y-3" data-testid="clinical-sheet-callouts">
          {block.callouts.map((calloutEntry, idx) => (
            <div
              key={`callout-${block.sheet_id}-${idx}`}
              className={`rounded-lg border-l-4 p-4 text-sm font-medium shadow-sm ${resolveCalloutThemeClasses(
                calloutEntry.severity
              )}`}
              data-testid={`callout-${calloutEntry.severity}`}
            >
              <div className="flex items-center gap-2">
                {renderCalloutIcon(calloutEntry.severity)}
                <span
                  className={`rounded px-2 py-0.5 text-xs font-black uppercase tracking-wide ${resolveCalloutBadgeClasses(
                    calloutEntry.severity
                  )}`}
                >
                  {calloutEntry.severity}
                </span>
                {calloutEntry.title && (
                  <h3 className="font-bold tracking-tight text-white">{calloutEntry.title}</h3>
                )}
              </div>
              <p className="mt-2 text-xs leading-relaxed opacity-95">{calloutEntry.message}</p>
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
