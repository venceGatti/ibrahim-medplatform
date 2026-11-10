import type { ActiveTabIdentifier } from '../interfaces/engineContracts';
import type { CanonicalBlockType } from '../interfaces/sduiContracts';

export const SIDECAR_IPC_ENDPOINTS = {
  CLINICAL_SHEET: '/api/v3/sheets/{sheet_id}',
  ENGINE_EVALUATE: '/api/v3/engine/evaluate',
  PHARMA_EVALUATE: '/api/v3/pharma/evaluate',
  EXAM_EVALUATE: '/api/v3/exam/evaluate',
  AGENT_HEALTH: '/agent/health',
  AGENT_EXECUTE: '/agent/execute',
} as const;

export const STORAGE_KEY_MEDCLIENT = 'medclient_persistent_state_v1';

export function computeCkdEpi2021Egfr(
  ageYears: number,
  isFemale: boolean,
  serumCreatinineMgDl: number
): number {
  const safeCreatinine = Math.max(0.1, serumCreatinineMgDl);
  const clampedAge = Math.max(18, Math.min(120, ageYears));
  const kappa = isFemale ? 0.7 : 0.9;
  const alpha = isFemale ? -0.241 : -0.302;
  const sexMultiplier = isFemale ? 1.012 : 1.0;

  const ratio = safeCreatinine / kappa;
  const minTerm = Math.pow(Math.min(ratio, 1.0), alpha);
  const maxTerm = Math.pow(Math.max(ratio, 1.0), -1.2);
  const ageTerm = Math.pow(0.9938, clampedAge);

  const rawEgfr = 142.0 * minTerm * maxTerm * ageTerm * sexMultiplier;
  return Math.round(rawEgfr * 100) / 100;
}

export function mapTabToCanonicalBlock(tabId: ActiveTabIdentifier): CanonicalBlockType {
  switch (tabId) {
    case 'clinical_sheet':
      return 'ClinicalSheetBlock';
    case 'symptom_matcher':
      return 'SymptomMatcherBlock';
    case 'drug_safety':
      return 'DrugSafetyBlock';
    case 'exam_simulator':
      return 'ExamSimulatorBlock';
    default:
      return 'ClinicalSheetBlock';
  }
}
