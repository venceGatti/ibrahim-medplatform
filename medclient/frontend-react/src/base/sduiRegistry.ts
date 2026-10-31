import type { CanonicalBlockType, SDUIAnyBlock } from '../interfaces/sduiContracts';

export class SDUINodeNotFoundError extends Error {
  public readonly offendingBlockType: string;

  public constructor(offendingBlockType: string) {
    super(
      `SDUINodeNotFoundError: Il block_type '${offendingBlockType}' non e' registrato nel Dual Component Registry (ROA-02). Nessun fallback silenzioso consentito.`
    );
    this.name = 'SDUINodeNotFoundError';
    this.offendingBlockType = offendingBlockType;
  }
}

export class DAGNodeNotFoundError extends SDUINodeNotFoundError {
  public constructor(offendingNodeType: string) {
    super(offendingNodeType);
    this.name = 'DAGNodeNotFoundError';
  }
}

const DUAL_COMPONENT_REGISTRY: Readonly<Record<string, CanonicalBlockType>> = {
  // 4 Canonical Block Types (Sez. 3.6)
  ClinicalSheetBlock: 'ClinicalSheetBlock',
  SymptomMatcherBlock: 'SymptomMatcherBlock',
  DrugSafetyBlock: 'DrugSafetyBlock',
  ExamSimulatorBlock: 'ExamSimulatorBlock',

  // 5 Legacy Alias Block Types (Sez. 11.4 / ROA-02)
  MarkdownBlock: 'ClinicalSheetBlock',
  DifferentialDiagnosisBlock: 'SymptomMatcherBlock',
  InteractiveFlowchartBlock: 'ExamSimulatorBlock',
  ClinicalExamBlock: 'ExamSimulatorBlock',
  AnatomicalHotspotBlock: 'ExamSimulatorBlock',
};

export function resolveCanonicalBlockType(rawBlockType: string): CanonicalBlockType {
  const trimmedType = rawBlockType.trim();
  const mappedCanonical = DUAL_COMPONENT_REGISTRY[trimmedType];
  if (!mappedCanonical) {
    throw new SDUINodeNotFoundError(rawBlockType);
  }
  return mappedCanonical;
}

export function validateAndResolveBlock(candidateBlock: SDUIAnyBlock): CanonicalBlockType {
  if (!candidateBlock || typeof candidateBlock.block_type !== 'string') {
    throw new SDUINodeNotFoundError('UNDEFINED_BLOCK_TYPE');
  }
  return resolveCanonicalBlockType(candidateBlock.block_type);
}

export function listRegisteredBlockAliases(): readonly string[] {
  return Object.keys(DUAL_COMPONENT_REGISTRY);
}
