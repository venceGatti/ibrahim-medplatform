import type { RenalPatientParameters } from '../interfaces/engineContracts';
import type { DrugSafetyBlock, ExamSimulatorBlock } from '../interfaces/sduiContracts';
import { sidecarIpcClient } from './useMedClientStore';

export const DRUG_CATALOG: Record<
  string,
  { inn: string; single: number; daily: number; prodrug: boolean; fm?: Record<string, number> }
> = {
  B01AC04: { inn: 'Clopidogrel', single: 75.0, daily: 75.0, prodrug: true, fm: { CYP2C19: 0.85 } },
  A02BC01: { inn: 'Omeprazole', single: 20.0, daily: 20.0, prodrug: false, fm: { CYP2C19: 0.7 } },
  C09CA04: { inn: 'Irbesartan', single: 150.0, daily: 150.0, prodrug: false },
  C03AA03: { inn: 'Hydrochlorothiazide', single: 12.5, daily: 12.5, prodrug: false },
  M01AE01: { inn: 'Ibuprofen', single: 400.0, daily: 1200.0, prodrug: false },
};

export async function requestPharmacologyEvaluation(
  activeMedications: readonly string[],
  renal: RenalPatientParameters
): Promise<DrugSafetyBlock> {
  const prescribedDrugs = activeMedications.map((atc) => {
    const info = DRUG_CATALOG[atc] ?? { inn: atc, single: 50.0, daily: 100.0, prodrug: false };
    return {
      atc_code: atc,
      inn_name: info.inn,
      single_dose_mg: info.single,
      daily_dose_mg: info.daily,
      route: 'oral',
      is_prodrug: info.prodrug,
      is_narrow_therapeutic_index: false,
      qtc_base_risk: 0.0,
      is_ras_blocker: atc === 'C09CA04',
      is_diuretic: atc === 'C03AA03',
      is_nsaid: atc === 'M01AE01',
      fm_cyp: info.fm ?? {},
    };
  });

  const queryParams = {
    patient_id: 'PATIENT_LOCAL_01',
    age: renal.ageYears,
    is_female: renal.isFemale,
    serum_creatinine_mg_dl: renal.serumCreatinineMgDl,
    serum_potassium_meq_l: 4.2,
  };

  return sidecarIpcClient.evaluatePharmacology<DrugSafetyBlock>(
    { prescribed_drugs: prescribedDrugs },
    queryParams
  );
}

export async function requestExamEvaluation(
  itemType: string,
  userSelection: unknown
): Promise<ExamSimulatorBlock> {
  const payload = {
    item_type: itemType,
    item_data: {
      question_id: 'Q_CARDIO_01',
      stem: 'Quale gastroprotettore e preferibile associare alla DAPT con Clopidogrel per preservare la funzione CYP2C19?',
      options: [
        'Omeprazolo 40 mg',
        'Pantoprazolo 20 mg',
        'Esomeprazolo 40 mg',
        'Fluconazolo 200 mg',
      ],
      correct_index: 1,
      allowed_transitions: { ACT_FLUIDS: 'STEP_02' },
      target_polygons: [
        [
          [0.1, 0.1],
          [0.9, 0.1],
          [0.5, 0.9],
        ],
      ],
    },
    user_selection: userSelection,
    fsrs_card_state: { stability: 6.4, difficulty: 4.1, elapsed_days: 1.0, reps: 4, lapses: 0 },
  };
  return sidecarIpcClient.evaluateExam<ExamSimulatorBlock>(payload);
}
