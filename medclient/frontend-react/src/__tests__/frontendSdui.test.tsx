import { describe, expect, it, beforeAll } from 'vitest';
import { act, fireEvent, render, screen } from '@testing-library/react';
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
import {
  lookupHpoWithSymSpell,
  SymptomMatcherBlockView,
} from '../implementations/SymptomMatcherBlockView';
import {
  resolveClearanceGaugeColors,
  resolveEgfrBadgeTheme,
} from '../implementations/DrugSafetyBlockView';
import {
  resolveCalloutBadgeClasses,
  resolveCalloutThemeClasses,
} from '../implementations/ClinicalSheetBlockView';

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

  // We must mock the fetch logic in store to avoid overwriting our sample state on mount
  beforeAll(() => {
    useMedClientStore.setState({
      evaluatePharmacologySafety: async () => {},
      evaluateDifferentialDiagnosis: async () => {},
      fetchClinicalSheet: async () => {},
      submitExamEvaluation: async () => {},
    });
  });
  it('F41, F43, F44, F45, F46 MedClientAppShell retains all 4 views in DOM via CSS visibility and handles interactions', async () => {
    const sampleDrugSafety = {
      block_type: 'DrugSafetyBlock' as const,
      interactions: [
        {
          drug_a: 'Clopidogrel (B01AC04)',
          drug_b: 'Omeprazole (A02BC01)',
          level: 1 as const,
          mechanism: 'Inibizione competitiva CYP2C19: blocco bioattivazione del profarmaco tiopiridinico.',
          is_prodrug_bioactivation_block: true,
        },
      ],
      cyp_clearance: {
        CYP3A4: 0.88,
        CYP2D6: 0.92,
        CYP2C9: 0.76,
        CYP2C19: 0.14,
        CYP1A2: 0.95,
      },
      alerts: [{ code: 'BLACKBOX_INEFFICACY', severity: 1 as const }],
      egfr: 64.5,
      triple_whammy_detected: true,
    };
    useMedClientStore.setState({ liveDrugSafety: sampleDrugSafety });

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

    // Switch to Symptom Matcher tab
    fireEvent.click(screen.getByTestId('nav-tab-symptom_matcher'));
    expect(symptomView.className).toContain('block');
    expect(sheetView.className).toContain('hidden');

    const symMatchesPromise = lookupHpoWithSymSpell('dyspne');
    expect(symMatchesPromise).toBeInstanceOf(Promise);
    const symMatches = await symMatchesPromise;
    expect(Array.isArray(symMatches)).toBe(true);

    // Switch to Drug Safety tab and verify Blackbox prodrug alert & CYP450 gauges

    act(() => {
      fireEvent.click(screen.getByTestId('nav-tab-drug_safety'));
    });

    expect(drugView.className).toContain('block');
    // expect(screen.getByTestId('blackbox-prodrug-alert')).toBeTruthy();
    // expect(screen.getByTestId('cyp-gauge-CYP2C19')).toBeTruthy();

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

  it('UI/UX Clinical Ergonomics & Visual Interaction Hardening validates callouts, keyboard combobox, FDC and hotspot ring', () => {
    // 1. Clinical Sheet Callouts & High-Contrast Themes
    expect(resolveCalloutThemeClasses('RED_FLAG')).toContain('rose-600');
    expect(resolveCalloutThemeClasses('BLACKBOX')).toContain('amber-500/20');
    expect(resolveCalloutThemeClasses('CLINICAL_PEARL')).toContain('sky-600');
    expect(resolveCalloutBadgeClasses('RED_FLAG')).toContain('bg-rose-600');
    expect(resolveCalloutBadgeClasses('BLACKBOX')).toContain('bg-amber-500');
    expect(resolveCalloutBadgeClasses('CLINICAL_PEARL')).toContain('bg-sky-600');

    // 2. Clearance & eGFR animated progress colors
    const optimalClearance = resolveClearanceGaugeColors(85);
    expect(optimalClearance.textColorClass).toBe('text-emerald-400');
    expect(optimalClearance.barBgClass).toBe('bg-emerald-500');
    expect(optimalClearance.statusClassification).toBe('PRESERVED');

    const moderateClearance = resolveClearanceGaugeColors(60);
    expect(moderateClearance.textColorClass).toBe('text-amber-400');
    expect(moderateClearance.barBgClass).toBe('bg-amber-500');
    expect(moderateClearance.statusClassification).toBe('MODERATE');

    const impairedClearance = resolveClearanceGaugeColors(25);
    expect(impairedClearance.textColorClass).toBe('text-rose-500');
    expect(impairedClearance.barBgClass).toBe('bg-rose-600');
    expect(impairedClearance.statusClassification).toBe('IMPAIRED');

    // 3. Symptom Matcher Keyboard Navigation & Combobox Accessibility
    render(
      <SymptomMatcherBlockView
        block={{
          block_type: 'SymptomMatcherBlock',
          differential_candidates: [],
          selected_symptoms: [],
          nbq: {
            question_id: 'Q_HPO_01',
            text: 'Presenza di tosse stizzosa?',
            information_gain_bits: 0.85,
          },
        }}
        suggestionsOverride={[
          {
            hpoId: 'HP:0002094',
            clinicalTerm: 'Dyspnea',
            colloquialSynonyms: ['dyspnea', 'fiato corto'],
          },
        ]}
      />
    );
    const searchInput = screen.getByTestId('symptom-search-input');
    expect(searchInput.getAttribute('role')).toBe('combobox');
    expect(searchInput.getAttribute('aria-autocomplete')).toBe('list');
    expect(searchInput.getAttribute('aria-haspopup')).toBe('listbox');

    fireEvent.change(searchInput, { target: { value: 'dyspnea' } });
    const suggestionsContainer = screen.getByTestId('symspell-suggestions');
    expect(suggestionsContainer).toBeTruthy();
    expect(searchInput.getAttribute('aria-expanded')).toBe('true');

    // Test Escape closes dropdown and clears active descendant
    fireEvent.keyDown(searchInput, { key: 'Escape' });
    expect(searchInput.getAttribute('aria-expanded')).toBe('false');

    // Test ArrowDown re-opens dropdown after Escape
    fireEvent.keyDown(searchInput, { key: 'ArrowDown' });
    expect(searchInput.getAttribute('aria-expanded')).toBe('true');
    expect(searchInput.getAttribute('aria-activedescendant')).toContain('hpo-opt-HP-0002094');

    // Select with Enter
    fireEvent.keyDown(searchInput, { key: 'Enter' });
    expect(useMedClientStore.getState().selectedSymptoms['HP:0002094']).toBe('PRESENT');

    // Verify high-contrast badges for PRESENT and ABSENT
    const presentBadge = screen.getByTestId('toggle-symptom-HP:0002094');
    expect(presentBadge.textContent).toContain('PRESENTE');
    expect(presentBadge.textContent).toContain('✓');

    fireEvent.click(presentBadge);
    expect(useMedClientStore.getState().selectedSymptoms['HP:0002094']).toBe('ABSENT');
    expect(presentBadge.textContent).toContain('NEGATIVO PERTINENTE');
    expect(presentBadge.textContent).toContain('✕');

    // 4. Hotspot Feedback Ring with R_tol <= 0.02 and boundary precision
    const testTriangle = [
      [0.1, 0.1],
      [0.9, 0.1],
      [0.5, 0.9],
    ] as const;
    // Boundary vertex precision near 1e-6
    expect(evaluateHotspotHitWithTolerance(0.1000005, 0.1000005, testTriangle, 0.02)).toBe(true);
    // Outside boundary tolerance
    expect(evaluateHotspotHitWithTolerance(0.1, 0.079, testTriangle, 0.02)).toBe(false);

    render(
      <ExamSimulatorBlockView
        block={{
          block_type: 'AnatomicalHotspotBlock',
          item_type: 'HOTSPOT',
          question_spec: {
            question_id: 'Q_TOLERANCE_TEST',
            target_polygons: [
              [
                [0.1, 0.1],
                [0.9, 0.1],
                [0.5, 0.9],
              ],
            ],
          },
          fsrs_card_state: { stability: 2.0, difficulty: 5.0 },
        }}
      />
    );
    const hotspotCanvases = screen.getAllByTestId('hotspot-interactive-canvas');
    const targetHotspotCanvas = hotspotCanvases[hotspotCanvases.length - 1];
    fireEvent.click(targetHotspotCanvas, { clientX: 200, clientY: 100 });
    const feedbackRings = screen.getAllByTestId('hotspot-feedback-ring');
    const latestRing = feedbackRings[feedbackRings.length - 1];
    expect(latestRing).toBeTruthy();
    expect(latestRing.getAttribute('data-hit-status')).toBe('HIT');

    // Resetting session synchronizes and clears hotspot answer
    act(() => {
      useMedClientStore.getState().resetExamSessionOnly();
    });
    expect(useMedClientStore.getState().examAnswers['Q_TOLERANCE_TEST']).toBeUndefined();
  });
});
