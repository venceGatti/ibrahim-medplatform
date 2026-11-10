/**
 * Radar polygon and HPO lookup helpers for SymptomMatcherBlockView (keeps file < 350 lines).
 */
import type { DifferentialCandidate } from '../interfaces/sduiContracts';
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
