import { describe, expect, it } from 'vitest';
import { fireEvent, render, screen } from '@testing-library/react';
import {
  DAGNodeNotFoundError,
  listRegisteredBlockAliases,
  resolveCanonicalBlockType,
  SDUINodeNotFoundError,
} from '../base/sduiRegistry';
import {
  evaluateHotspotHitWithTolerance,
  evaluatePointInPolygonEvenOdd,
  normalizeClickCoordinates,
} from '../base/hotspotGeometry';
import { computeCkdEpi2021Egfr, useMedClientStore } from '../base/useMedClientStore';
import { SidecarIpcClient } from '../base/sidecarIpcClient';
import {
  computeVirtualWindowRange,
  MAX_MOUNTED_DOM_NODES,
  VirtualBlockWindow,
} from '../implementations/VirtualBlockWindow';
import { SingletonWebGLBroker } from '../implementations/SingletonWebGLBroker';
import { MolecularStructureViewer } from '../implementations/MolecularStructureViewer';
import { MedClientAppShell } from '../implementations/MedClientAppShell';
import { ExamSimulatorBlockView } from '../implementations/ExamSimulatorBlockView';
import { lookupHpoWithSymSpell } from '../implementations/SymptomMatcherBlockView';
import { resolveEgfrBadgeTheme } from '../implementations/DrugSafetyBlockView';

describe('WP-4 MedClient React 19 SDUI & Engine Suite (F41-F48)', () => {
  it('ROA-02 Dual Component Registry resolves canonical & legacy aliases and throws SDUINodeNotFoundError on unknown types', () => {
    expect(resolveCanonicalBlockType('ClinicalSheetBlock')).toBe('ClinicalSheetBlock');
    expect(resolveCanonicalBlockType('MarkdownBlock')).toBe('ClinicalSheetBlock');
    expect(resolveCanonicalBlockType('SymptomMatcherBlock')).toBe('SymptomMatcherBlock');
    expect(resolveCanonicalBlockType('DifferentialDiagnosisBlock')).toBe('SymptomMatcherBlock');
    expect(resolveCanonicalBlockType('DrugSafetyBlock')).toBe('DrugSafetyBlock');
    expect(resolveCanonicalBlockType('ExamSimulatorBlock')).toBe('ExamSimulatorBlock');
    expect(resolveCanonicalBlockType('InteractiveFlowchartBlock')).toBe('ExamSimulatorBlock');
    expect(resolveCanonicalBlockType('ClinicalExamBlock')).toBe('ExamSimulatorBlock');
    expect(resolveCanonicalBlockType('AnatomicalHotspotBlock')).toBe('ExamSimulatorBlock');
    expect(listRegisteredBlockAliases().length).toBe(9);

    expect(() => resolveCanonicalBlockType('UnknownWidgetBlock')).toThrow(SDUINodeNotFoundError);
    const dagErr = new DAGNodeNotFoundError('OrphanNode');
    expect(dagErr).toBeInstanceOf(SDUINodeNotFoundError);
  });

  it('ROA-16 Hotspot Geometry normalizes [0,1]^2 coordinates and evaluates Even-Odd Ray-Casting with tolerance <= 0.02', () => {
    const [uCoord, vCoord] = normalizeClickCoordinates(200, 150, {
      left: 100,
      top: 50,
      width: 400,
      height: 200,
    });
    expect(uCoord).toBeCloseTo(0.25, 4);
    expect(vCoord).toBeCloseTo(0.5, 4);

    const trianglePolygon = [
      [0.2, 0.2],
      [0.8, 0.2],
      [0.5, 0.8],
    ] as const;

    expect(evaluatePointInPolygonEvenOdd(0.5, 0.4, trianglePolygon)).toBe(true);
    expect(evaluatePointInPolygonEvenOdd(0.05, 0.05, trianglePolygon)).toBe(false);
    expect(evaluatePointInPolygonEvenOdd(0.5, 0.5, [[0.1, 0.1], [0.2, 0.2]])).toBe(false);

    // Near top edge (v = 0.188 is within R_tol = 0.02 of segment v = 0.2)
    expect(evaluateHotspotHitWithTolerance(0.5, 0.188, trianglePolygon, 0.02)).toBe(true);
    // Outside tolerance (v = 0.15 is 0.05 away from segment v = 0.2)
    expect(evaluateHotspotHitWithTolerance(0.5, 0.15, trianglePolygon, 0.02)).toBe(false);
    // Out of [0,1]^2 bounds rejected
    expect(evaluateHotspotHitWithTolerance(-0.1, 0.5, trianglePolygon, 0.02)).toBe(false);
  });

  it('F42 Zustand Persistent Store retains tab scroll offsets, symptoms, CKD-EPI 2021 eGFR, and isolated exam reset', () => {
    const store = useMedClientStore.getState();
    store.setSearchQuery('Clopidogrel');
    store.setTabScrollOffset('clinical_sheet', 320);
    store.setActiveTab('drug_safety');
    store.recordExamAnswer('Q_TEST', 2);

    expect(useMedClientStore.getState().activeTab).toBe('drug_safety');
    expect(useMedClientStore.getState().tabScrollOffsets.clinical_sheet).toBe(320);
    expect(useMedClientStore.getState().searchQuery).toBe('Clopidogrel');

    // Isolated exam reset preserves searchQuery and scroll offsets
    useMedClientStore.getState().resetExamSessionOnly();
    expect(useMedClientStore.getState().searchQuery).toBe('Clopidogrel');
    expect(Object.keys(useMedClientStore.getState().examAnswers).length).toBe(0);

    const egfrNormal = computeCkdEpi2021Egfr(45, true, 0.8);
    expect(egfrNormal).toBeGreaterThan(80);
    expect(resolveEgfrBadgeTheme(85).colorName).toBe('green');
    expect(resolveEgfrBadgeTheme(45).colorName).toBe('orange');
    expect(resolveEgfrBadgeTheme(20).colorName).toBe('red');
  });

  it('F47 Virtual DOM Windowing bounds mounted DOM nodes to <= 30 even for 500 items', () => {
    const windowCalc = computeVirtualWindowRange(500, 600, 40, 800, 4);
    expect(windowCalc.mountedCount).toBeLessThan(MAX_MOUNTED_DOM_NODES);
    expect(windowCalc.totalHeightPx).toBe(20000);

    // Zero row height division guard and negative scroll clamping
    const zeroRowGuard = computeVirtualWindowRange(100, 600, 0, -50, 2);
    expect(zeroRowGuard.startIndex).toBe(0);
    expect(zeroRowGuard.mountedCount).toBeLessThan(MAX_MOUNTED_DOM_NODES);

    const manyParagraphs = Array.from({ length: 200 }, (_, idx) => `Paragrafo clinico #${idx}`);
    render(<VirtualBlockWindow paragraphs={manyParagraphs} viewportHeightPx={400} rowHeightPx={50} />);
    const mountedNodes = screen.getAllByTestId('virtual-mounted-node');
    expect(mountedNodes.length).toBeLessThan(MAX_MOUNTED_DOM_NODES);
  });

  it('F48 & ROA-12 SingletonWebGLBroker defaults to 2D SVG and enforces at most 1 active WebGL context', () => {
    const broker = SingletonWebGLBroker.getInstance();
    const canvasA = document.createElement('canvas');
    const canvasB = document.createElement('canvas');
    let preemptedA = false;

    broker.acquireContext('MOL_A', canvasA, () => {
      preemptedA = true;
    });
    expect(broker.activeOwner()).toBe('MOL_A');
    expect(broker.activeContextCount()).toBe(1);

    broker.acquireContext('MOL_B', canvasB, () => {
      preemptedA = false;
    });
    expect(preemptedA).toBe(true);
    expect(broker.activeOwner()).toBe('MOL_B');
    expect(broker.activeContextCount()).toBe(1);

    broker.releaseContext('MOL_B');
    expect(broker.activeContextCount()).toBe(0);

    const validHash = '0123456789abcdef0123456789abcdef0123456789abcdef0123456789abcdef';
    render(
      <MolecularStructureViewer
        moleculeId="CLOPIDOGREL_01"
        moleculeName="Clopidogrel Bisulfate"
        svgSha256={validHash}
        pdbSha256={validHash}
      />
    );
    expect(screen.getByTestId('svg-fallback-CLOPIDOGREL_01')).toBeTruthy();
    fireEvent.click(screen.getByText('Esplora Modello 3D'));
    expect(screen.getByTestId('webgl-canvas-container-CLOPIDOGREL_01')).toBeTruthy();
  });

  it('F41, F43, F44, F45, F46 MedClientAppShell retains all 4 views in DOM via CSS visibility and handles interactions', () => {
    render(<MedClientAppShell />);

    // Rule 8: All 4 views exist simultaneously in the DOM
    const sheetView = screen.getByTestId('dom-retained-view-clinical_sheet');
    const symptomView = screen.getByTestId('dom-retained-view-symptom_matcher');
    const drugView = screen.getByTestId('dom-retained-view-drug_safety');
    const examView = screen.getByTestId('dom-retained-view-exam_simulator');

    expect(sheetView).toBeTruthy();
    expect(symptomView).toBeTruthy();
    expect(drugView).toBeTruthy();
    expect(examView).toBeTruthy();

    // Switch to Symptom Matcher tab and verify SymSpell typo correction
    fireEvent.click(screen.getByTestId('nav-tab-symptom_matcher'));
    expect(symptomView.className).toContain('block');
    expect(sheetView.className).toContain('hidden');

    const symMatches = lookupHpoWithSymSpell('dyspne');
    expect(symMatches.length).toBeGreaterThan(0);
    expect(symMatches[0].hpoId).toBe('HP:0002094');

    // Switch to Drug Safety tab and verify Blackbox prodrug alert & CYP450 gauges
    fireEvent.click(screen.getByTestId('nav-tab-drug_safety'));
    expect(drugView.className).toContain('block');
    expect(screen.getByTestId('blackbox-prodrug-alert')).toBeTruthy();
    expect(screen.getByTestId('cyp-gauge-CYP2C19')).toBeTruthy();

    // Verify Hotspot & DAG ExamSimulator modes
    render(
      <ExamSimulatorBlockView
        block={{
          block_type: 'AnatomicalHotspotBlock',
          item_type: 'IMAGE_HOTSPOT',
          question_spec: {
            question_id: 'Q_HOTSPOT_1',
            image_uri: 'med-asset://images/cxr_01.webp',
            target_polygons: [
              [
                [0.1, 0.1],
                [0.9, 0.1],
                [0.5, 0.9],
              ],
            ],
          },
          fsrs_card_state: { stability: 3.5, difficulty: 4.8 },
        }}
      />
    );
    fireEvent.click(screen.getByTestId('hotspot-interactive-canvas'), {
      clientX: 200,
      clientY: 100,
    });
    expect(screen.getByTestId('hotspot-hit-feedback').textContent).toContain('HIT');
  });

  it('SidecarIpcClient enforces 127.0.0.1 loopback and exponential backoff', () => {
    expect(
      () =>
        new SidecarIpcClient({
          port: 54321,
          ipcSecretToken: 'valid-secret',
          hostAddress: '::1',
        })
    ).toThrow(/127\.0\.0\.1/);

    const client = new SidecarIpcClient({
      port: 54321,
      ipcSecretToken: 'valid-uuid-token',
      baseBackoffMs: 20,
    });
    expect(client.currentCircuitState()).toBe('CLOSED');
    expect(client.computeBackoffDelayMs(0)).toBe(20);
    expect(client.computeBackoffDelayMs(2)).toBe(80);
  });
});
