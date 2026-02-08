# 💊 ADVANCED MEDICATION SUGGESTION ENGINE - EXPERT LEVEL
# Enterprise-grade AI-powered clinical decision support system

import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional, Any
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from collections import defaultdict
import re

# =============================================================================
# CONFIGURATION & CONSTANTS
# =============================================================================

class SeverityLevel(Enum):
    MILD = "Mild"
    MODERATE = "Moderate"
    SEVERE = "Severe"
    CRITICAL = "Critical"
    LIFE_THREATENING = "Life-Threatening"

class PregnancyCategory(Enum):
    A = "A - No risk in controlled studies"
    B = "B - No risk in animal studies"
    C = "C - Risk cannot be ruled out"
    D = "D - Positive evidence of risk"
    X = "X - Contraindicated in pregnancy"
    N = "N - Not classified"

class ControlledSubstanceSchedule(Enum):
    NONE = "Not Controlled"
    I = "Schedule I"
    II = "Schedule II"
    III = "Schedule III"
    IV = "Schedule IV"
    V = "Schedule V"

class MetabolismPathway(Enum):
    CYP1A2 = "CYP1A2"
    CYP2C9 = "CYP2C9"
    CYP2C19 = "CYP2C19"
    CYP2D6 = "CYP2D6"
    CYP3A4 = "CYP3A4"
    CYP2E1 = "CYP2E1"
    UGT = "UGT Glucuronidation"
    RENAL = "Renal Elimination"

# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PharmacokineticProfile:
    """Pharmacokinetic parameters for a medication"""
    bioavailability: float
    half_life_hours: float
    time_to_peak_hours: float
    volume_of_distribution: float
    protein_binding: float
    metabolism_pathway: List[MetabolismPathway]
    excretion_route: str
    active_metabolites: List[str] = field(default_factory=list)

@dataclass
class DosingAdjustment:
    """Dosing adjustments for specific populations"""
    renal_impairment: Dict[str, str]
    hepatic_impairment: Dict[str, str]
    pediatric_dosing: str
    geriatric_dosing: str
    obesity_dosing: str
    pregnancy_adjustment: str

@dataclass
class DrugMonitoring:
    """Therapeutic drug monitoring parameters"""
    requires_monitoring: bool
    therapeutic_range_min: float
    therapeutic_range_max: float
    toxic_level: float
    sampling_time: str
    monitoring_frequency: str

@dataclass
class ClinicalEvidence:
    """Clinical trial evidence for medication"""
    evidence_level: str
    number_needed_to_treat: Optional[float]
    number_needed_to_harm: Optional[float]
    key_trials: List[str]
    guidelines_recommending: List[str]
    cochrane_review: Optional[str]

@dataclass
class AdvancedMedication:
    """Comprehensive medication data structure"""
    generic_name: str
    brand_names: List[str]
    drug_class: str
    mechanism_of_action: str
    standard_dosage: str
    dosage_forms: List[str]
    frequency: str
    duration: str
    max_daily_dose: str
    side_effects: Dict[str, List[str]]
    contraindications: List[str]
    black_box_warnings: List[str]
    precautions: List[str]
    pregnancy_category: PregnancyCategory
    lactation_safety: str
    controlled_schedule: ControlledSubstanceSchedule
    indications: List[str]
    off_label_uses: List[str]
    effectiveness: float
    time_to_effect: str
    pharmacokinetics: PharmacokineticProfile
    monitoring: DrugMonitoring
    dosing_adjustments: DosingAdjustment
    clinical_evidence: ClinicalEvidence
    cost_per_unit: float
    cost_per_course: float
    generic_available: bool
    insurance_coverage: str

@dataclass
class PatientProfile:
    """Comprehensive patient profile for personalized recommendations"""
    age: int
    weight_kg: float
    height_cm: float
    sex: str
    creatinine_clearance: float
    gfr: float
    child_pugh_score: Optional[str]
    cyp2d6_status: str
    cyp2c19_status: str
    hla_b5701: bool
    allergies: List[str]
    current_medications: List[str]
    comorbidities: List[str]
    previous_adverse_reactions: List[Dict[str, str]]
    pregnant: bool
    lactating: bool
    pediatric: bool
    geriatric: bool
    lab_values: Dict[str, float]

@dataclass
class DrugInteraction:
    """Comprehensive drug interaction data"""
    drug1: str
    drug2: str
    severity: str
    mechanism: str
    clinical_effect: str
    management: str
    documentation_level: str
    onset: str
    evidence_references: List[str]

# =============================================================================
# COMPREHENSIVE MEDICATION DATABASE
# =============================================================================

ADVANCED_MEDICATION_DATABASE = {
    "Pneumonia": {
        "first_line": [
            AdvancedMedication(
                generic_name="Amoxicillin-Clavulanate",
                brand_names=["Augmentin", "Clavamox"],
                drug_class="Beta-lactam/Beta-lactamase inhibitor",
                mechanism_of_action="Inhibits bacterial cell wall synthesis; clavulanate prevents beta-lactamase degradation",
                standard_dosage="875mg/125mg",
                dosage_forms=["Tablet", "Suspension", "Chewable"],
                frequency="Every 12 hours",
                duration="7-10 days",
                max_daily_dose="4000mg/500mg",
                side_effects={
                    "common": ["Diarrhea (9%)", "Nausea (3%)", "Rash (3%)"],
                    "uncommon": ["Vomiting", "Abdominal pain", "Headache"],
                    "rare": ["Hepatotoxicity", "Seizures"],
                    "serious": ["Anaphylaxis", "C. difficile colitis", "Stevens-Johnson Syndrome"]
                },
                contraindications=[
                    "Penicillin allergy",
                    "Previous hepatic dysfunction with amoxicillin-clavulanate",
                    "Infectious mononucleosis"
                ],
                black_box_warnings=[],
                precautions=[
                    "Renal impairment requires dose adjustment",
                    "Monitor for superinfection",
                    "May cause false-positive urine glucose"
                ],
                pregnancy_category=PregnancyCategory.B,
                lactation_safety="Compatible with breastfeeding",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Community-acquired pneumonia", "Sinusitis", "Otitis media"],
                off_label_uses=["Dental prophylaxis", "Animal bites"],
                effectiveness=0.92,
                time_to_effect="24-72 hours",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=74.0,
                    half_life_hours=1.3,
                    time_to_peak_hours=1.5,
                    volume_of_distribution=0.3,
                    protein_binding=18.0,
                    metabolism_pathway=[MetabolismPathway.RENAL],
                    excretion_route="Renal (60-70% unchanged)",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Clinical response"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={
                        "GFR 10-30": "875/125mg q12h or 500/125mg q8h",
                        "GFR <10": "500/125mg q12h",
                        "Hemodialysis": "500/125mg q12h + dose after HD"
                    },
                    hepatic_impairment={
                        "Child-Pugh A": "No adjustment",
                        "Child-Pugh B-C": "Use with caution"
                    },
                    pediatric_dosing="25-45mg/kg/day divided q12h",
                    geriatric_dosing="No adjustment if adequate renal function",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="No adjustment needed"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=8.0,
                    number_needed_to_harm=50.0,
                    key_trials=["CAP-START", "COMMUNITY-ACQUIRED PNEUMONIA TRIALS"],
                    guidelines_recommending=["IDSA/ATS CAP Guidelines", "NICE Guidelines"],
                    cochrane_review="CD006723"
                ),
                cost_per_unit=1.50,
                cost_per_course=42.00,
                generic_available=True,
                insurance_coverage="Tier 1 - Preferred Generic"
            ),
            AdvancedMedication(
                generic_name="Azithromycin",
                brand_names=["Zithromax", "Z-Pack", "Zmax"],
                drug_class="Macrolide antibiotic",
                mechanism_of_action="Binds to 50S ribosomal subunit, inhibiting bacterial protein synthesis",
                standard_dosage="500mg day 1, then 250mg days 2-5",
                dosage_forms=["Tablet", "Suspension", "IV", "Extended-release"],
                frequency="Once daily",
                duration="5 days (Z-Pack) or 3 days (high dose)",
                max_daily_dose="500mg",
                side_effects={
                    "common": ["Diarrhea (5%)", "Nausea (3%)", "Abdominal pain (3%)"],
                    "uncommon": ["Headache", "Dizziness", "Rash"],
                    "rare": ["Hearing loss", "Myasthenia gravis exacerbation"],
                    "serious": ["QT prolongation", "Torsades de pointes", "Hepatotoxicity"]
                },
                contraindications=[
                    "Known hypersensitivity to macrolides",
                    "History of cholestatic jaundice with azithromycin",
                    "Concurrent use with pimozide"
                ],
                black_box_warnings=[],
                precautions=[
                    "QT prolongation risk - avoid with other QT-prolonging drugs",
                    "Myasthenia gravis may worsen",
                    "Hepatic dysfunction monitoring"
                ],
                pregnancy_category=PregnancyCategory.B,
                lactation_safety="Compatible with breastfeeding",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["CAP", "Acute bacterial sinusitis", "Pharyngitis"],
                off_label_uses=["MAC prophylaxis", "Traveler's diarrhea"],
                effectiveness=0.88,
                time_to_effect="24-48 hours",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=37.0,
                    half_life_hours=68.0,
                    time_to_peak_hours=2.5,
                    volume_of_distribution=31.1,
                    protein_binding=51.0,
                    metabolism_pathway=[MetabolismPathway.CYP3A4],
                    excretion_route="Biliary (major), Renal (6%)",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="ECG if QT risk factors"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={
                        "GFR >10": "No adjustment",
                        "GFR <10": "Use with caution"
                    },
                    hepatic_impairment={
                        "Child-Pugh A-C": "Use with caution, monitor LFTs"
                    },
                    pediatric_dosing="10mg/kg day 1, 5mg/kg days 2-5",
                    geriatric_dosing="No adjustment",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="No adjustment"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=10.0,
                    number_needed_to_harm=100.0,
                    key_trials=["AZITHROMYCIN CAP STUDIES"],
                    guidelines_recommending=["IDSA/ATS", "ERS/ESCMID"],
                    cochrane_review="CD002199"
                ),
                cost_per_unit=3.50,
                cost_per_course=17.50,
                generic_available=True,
                insurance_coverage="Tier 1 - Preferred Generic"
            )
        ],
        "second_line": [
            AdvancedMedication(
                generic_name="Levofloxacin",
                brand_names=["Levaquin"],
                drug_class="Fluoroquinolone (Respiratory)",
                mechanism_of_action="Inhibits DNA gyrase and topoisomerase IV, preventing DNA replication",
                standard_dosage="750mg",
                dosage_forms=["Tablet", "IV", "Oral solution"],
                frequency="Once daily",
                duration="5-7 days",
                max_daily_dose="750mg",
                side_effects={
                    "common": ["Nausea (7%)", "Headache (6%)", "Diarrhea (5%)"],
                    "uncommon": ["Dizziness", "Insomnia", "Photosensitivity"],
                    "rare": ["Tendon rupture", "Peripheral neuropathy", "CNS effects"],
                    "serious": ["Aortic dissection", "QT prolongation", "Hypoglycemia"]
                },
                contraindications=[
                    "Hypersensitivity to fluoroquinolones",
                    "History of tendon disorders with fluoroquinolones",
                    "Myasthenia gravis"
                ],
                black_box_warnings=[
                    "⚠️ Tendinitis and tendon rupture risk",
                    "⚠️ Peripheral neuropathy risk",
                    "⚠️ CNS effects (seizures, increased ICP)",
                    "⚠️ Myasthenia gravis exacerbation",
                    "⚠️ Aortic aneurysm/dissection risk"
                ],
                precautions=[
                    "Avoid in patients >60 years if alternatives exist",
                    "Avoid concurrent corticosteroid use",
                    "QT prolongation risk"
                ],
                pregnancy_category=PregnancyCategory.C,
                lactation_safety="Not recommended",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["CAP", "Nosocomial pneumonia", "Sinusitis"],
                off_label_uses=["TB treatment", "Anthrax prophylaxis"],
                effectiveness=0.95,
                time_to_effect="24-48 hours",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=99.0,
                    half_life_hours=8.0,
                    time_to_peak_hours=1.5,
                    volume_of_distribution=1.1,
                    protein_binding=31.0,
                    metabolism_pathway=[MetabolismPathway.RENAL],
                    excretion_route="Renal (87% unchanged)",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Blood glucose if diabetic"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={
                        "GFR 20-49": "750mg q48h",
                        "GFR 10-19": "750mg x1, then 500mg q48h",
                        "GFR <10/HD": "750mg x1, then 500mg q48h"
                    },
                    hepatic_impairment={
                        "All": "No adjustment needed"
                    },
                    pediatric_dosing="Not recommended (cartilage toxicity)",
                    geriatric_dosing="Use with caution, prefer alternatives",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="Avoid - use alternatives"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=6.0,
                    number_needed_to_harm=25.0,
                    key_trials=["PROVE", "LEVAQUIN CAP TRIALS"],
                    guidelines_recommending=["IDSA/ATS (reserve for penicillin allergy)"],
                    cochrane_review="CD004418"
                ),
                cost_per_unit=8.50,
                cost_per_course=59.50,
                generic_available=True,
                insurance_coverage="Tier 2 - Prior auth may be required"
            )
        ],
        "supportive": []
    },
    "Brain Tumor": {
        "first_line": [
            AdvancedMedication(
                generic_name="Temozolomide",
                brand_names=["Temodar", "Temodal"],
                drug_class="Alkylating agent (Imidazotetrazine)",
                mechanism_of_action="Prodrug that methylates DNA at O6-guanine, N7-guanine, and N3-adenine",
                standard_dosage="150-200mg/m²",
                dosage_forms=["Capsule", "IV infusion"],
                frequency="Once daily",
                duration="5 days per 28-day cycle",
                max_daily_dose="200mg/m²",
                side_effects={
                    "common": ["Nausea (53%)", "Vomiting (42%)", "Fatigue (34%)", "Constipation (33%)"],
                    "uncommon": ["Alopecia", "Rash", "Anorexia"],
                    "rare": ["Myelodysplastic syndrome", "Aplastic anemia"],
                    "serious": ["Myelosuppression", "Opportunistic infections", "Hepatotoxicity"]
                },
                contraindications=[
                    "Hypersensitivity to dacarbazine",
                    "Severe myelosuppression"
                ],
                black_box_warnings=[
                    "⚠️ Myelosuppression - monitor CBC",
                    "⚠️ Risk of myelodysplastic syndrome/secondary malignancies"
                ],
                precautions=[
                    "PCP prophylaxis recommended during radiation",
                    "Antiemetic prophylaxis required",
                    "MGMT methylation status affects response"
                ],
                pregnancy_category=PregnancyCategory.D,
                lactation_safety="Contraindicated",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Glioblastoma", "Anaplastic astrocytoma"],
                off_label_uses=["Melanoma", "Neuroendocrine tumors"],
                effectiveness=0.78,
                time_to_effect="6-8 weeks for assessment",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=100.0,
                    half_life_hours=1.8,
                    time_to_peak_hours=1.0,
                    volume_of_distribution=0.4,
                    protein_binding=15.0,
                    metabolism_pathway=[MetabolismPathway.CYP3A4],
                    excretion_route="Renal (38%)",
                    active_metabolites=["MTIC"]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=True,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="CBC weekly during first cycle, then every 4 weeks"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={
                        "CrCl >30": "No adjustment",
                        "CrCl <30": "Use with caution, limited data"
                    },
                    hepatic_impairment={
                        "Mild-Moderate": "Use with caution",
                        "Severe": "Not recommended"
                    },
                    pediatric_dosing="Same as adults (limited data)",
                    geriatric_dosing="No adjustment, monitor closely",
                    obesity_dosing="Use actual body weight for BSA",
                    pregnancy_adjustment="Contraindicated"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=8.0,
                    number_needed_to_harm=3.0,
                    key_trials=["STUPP TRIAL", "EORTC 26981-22981/NCIC CE3"],
                    guidelines_recommending=["NCCN CNS Cancers", "ESMO Guidelines"],
                    cochrane_review="CD007294"
                ),
                cost_per_unit=350.00,
                cost_per_course=8750.00,
                generic_available=True,
                insurance_coverage="Specialty Tier - Prior auth required"
            )
        ],
        "second_line": [],
        "supportive": [
            AdvancedMedication(
                generic_name="Dexamethasone",
                brand_names=["Decadron", "DexPak"],
                drug_class="Corticosteroid (Glucocorticoid)",
                mechanism_of_action="Reduces cerebral edema by stabilizing blood-brain barrier",
                standard_dosage="4-8mg",
                dosage_forms=["Tablet", "IV", "IM", "Oral solution"],
                frequency="2-4 times daily",
                duration="As needed, taper when possible",
                max_daily_dose="24mg",
                side_effects={
                    "common": ["Insomnia", "Increased appetite", "Mood changes"],
                    "uncommon": ["Hyperglycemia", "Hypertension", "Gastritis"],
                    "rare": ["Avascular necrosis", "Adrenal suppression"],
                    "serious": ["Immunosuppression", "GI perforation", "Psychosis"]
                },
                contraindications=[
                    "Systemic fungal infections",
                    "Live vaccine administration"
                ],
                black_box_warnings=[],
                precautions=[
                    "Taper slowly to prevent adrenal crisis",
                    "Monitor blood glucose",
                    "PCP prophylaxis if prolonged use"
                ],
                pregnancy_category=PregnancyCategory.C,
                lactation_safety="Use with caution",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Cerebral edema", "Inflammation", "Multiple myeloma"],
                off_label_uses=["COVID-19", "Antiemetic"],
                effectiveness=0.90,
                time_to_effect="1-3 hours",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=78.0,
                    half_life_hours=3.0,
                    time_to_peak_hours=1.5,
                    volume_of_distribution=0.9,
                    protein_binding=77.0,
                    metabolism_pathway=[MetabolismPathway.CYP3A4],
                    excretion_route="Renal",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=True,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Blood glucose, blood pressure"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={"All": "No adjustment"},
                    hepatic_impairment={"All": "No adjustment"},
                    pediatric_dosing="0.03-0.15 mg/kg/day divided q6-12h",
                    geriatric_dosing="Use lowest effective dose",
                    obesity_dosing="Ideal body weight dosing",
                    pregnancy_adjustment="Use lowest effective dose"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="B",
                    number_needed_to_treat=2.0,
                    number_needed_to_harm=10.0,
                    key_trials=["Multiple RCTs"],
                    guidelines_recommending=["NCCN CNS Cancers", "AANS/CNS Guidelines"],
                    cochrane_review="CD003240"
                ),
                cost_per_unit=0.25,
                cost_per_course=15.00,
                generic_available=True,
                insurance_coverage="Tier 1 - Preferred Generic"
            )
        ]
    },
    "Diabetic Retinopathy": {
        "first_line": [
            AdvancedMedication(
                generic_name="Bevacizumab",
                brand_names=["Avastin"],
                drug_class="Anti-VEGF monoclonal antibody",
                mechanism_of_action="Binds to VEGF-A, inhibiting angiogenesis and vascular permeability",
                standard_dosage="1.25mg/0.05mL",
                dosage_forms=["Intravitreal injection"],
                frequency="Every 4-6 weeks",
                duration="As needed based on response",
                max_daily_dose="1.25mg per injection",
                side_effects={
                    "common": ["Eye pain", "Floaters", "Subconjunctival hemorrhage"],
                    "uncommon": ["Increased IOP", "Vitreous hemorrhage"],
                    "rare": ["Retinal detachment", "Endophthalmitis"],
                    "serious": ["Stroke", "MI (rare with intravitreal)", "Arterial thromboembolism"]
                },
                contraindications=[
                    "Active ocular infection",
                    "Active periocular infection",
                    "Hypersensitivity to bevacizumab"
                ],
                black_box_warnings=[],
                precautions=[
                    "Monitor IOP post-injection",
                    "Risk of endophthalmitis",
                    "Careful in patients with recent stroke/MI"
                ],
                pregnancy_category=PregnancyCategory.C,
                lactation_safety="Unknown - use caution",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Diabetic macular edema", "Wet AMD", "RVO"],
                off_label_uses=["Diabetic retinopathy", "Neovascular glaucoma"],
                effectiveness=0.89,
                time_to_effect="1-2 weeks",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=100.0,
                    half_life_hours=168.0,
                    time_to_peak_hours=24.0,
                    volume_of_distribution=0.05,
                    protein_binding=0,
                    metabolism_pathway=[],
                    excretion_route="Proteolytic degradation",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=True,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="IOP check, OCT every 4-6 weeks"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={"All": "No adjustment for intravitreal"},
                    hepatic_impairment={"All": "No adjustment for intravitreal"},
                    pediatric_dosing="Not established",
                    geriatric_dosing="No adjustment",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="Avoid if possible"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=5.0,
                    number_needed_to_harm=100.0,
                    key_trials=["DRCR.net Protocol T", "BOLT"],
                    guidelines_recommending=["AAO Guidelines", "ICO Guidelines"],
                    cochrane_review="CD007419"
                ),
                cost_per_unit=50.00,
                cost_per_course=600.00,
                generic_available=False,
                insurance_coverage="Specialty - Usually covered"
            )
        ],
        "second_line": [],
        "supportive": [
            AdvancedMedication(
                generic_name="Metformin",
                brand_names=["Glucophage", "Fortamet"],
                drug_class="Biguanide",
                mechanism_of_action="Decreases hepatic glucose production, increases insulin sensitivity",
                standard_dosage="500-1000mg",
                dosage_forms=["Tablet", "Extended-release tablet", "Solution"],
                frequency="Twice daily with meals",
                duration="Long-term",
                max_daily_dose="2550mg",
                side_effects={
                    "common": ["GI upset (30%)", "Diarrhea", "Nausea", "Metallic taste"],
                    "uncommon": ["Vitamin B12 deficiency", "Weight loss"],
                    "rare": ["Lactic acidosis"],
                    "serious": ["Lactic acidosis (rare but fatal)"]
                },
                contraindications=[
                    "eGFR <30 mL/min",
                    "Metabolic acidosis",
                    "Severe hepatic impairment"
                ],
                black_box_warnings=[
                    "⚠️ Lactic acidosis - rare but potentially fatal"
                ],
                precautions=[
                    "Hold before iodinated contrast procedures",
                    "Monitor renal function",
                    "Hold during acute illness"
                ],
                pregnancy_category=PregnancyCategory.B,
                lactation_safety="Compatible with breastfeeding",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Type 2 diabetes"],
                off_label_uses=["PCOS", "Weight management", "Prediabetes"],
                effectiveness=0.85,
                time_to_effect="2-4 weeks for full effect",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=55.0,
                    half_life_hours=6.2,
                    time_to_peak_hours=2.5,
                    volume_of_distribution=654.0,
                    protein_binding=0,
                    metabolism_pathway=[MetabolismPathway.RENAL],
                    excretion_route="Renal (90% unchanged)",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=True,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Renal function, B12 annually"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={
                        "eGFR 30-45": "Max 1000mg/day, monitor closely",
                        "eGFR <30": "Contraindicated"
                    },
                    hepatic_impairment={"All": "Avoid in severe impairment"},
                    pediatric_dosing="10-16 years: same as adults",
                    geriatric_dosing="Start low, titrate based on renal function",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="Often continued, insulin preferred"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=14.0,
                    number_needed_to_harm=200.0,
                    key_trials=["UKPDS", "DPP"],
                    guidelines_recommending=["ADA Standards", "EASD Guidelines"],
                    cochrane_review="CD002966"
                ),
                cost_per_unit=0.10,
                cost_per_course=36.00,
                generic_available=True,
                insurance_coverage="Tier 1 - Preferred Generic"
            )
        ]
    },
    "Tuberculosis": {
        "first_line": [
            AdvancedMedication(
                generic_name="Rifampicin",
                brand_names=["Rifadin", "Rimactane"],
                drug_class="Rifamycin antibiotic",
                mechanism_of_action="Inhibits bacterial DNA-dependent RNA polymerase",
                standard_dosage="10mg/kg (max 600mg)",
                dosage_forms=["Capsule", "IV", "Suspension"],
                frequency="Once daily",
                duration="6 months (with other agents)",
                max_daily_dose="600mg",
                side_effects={
                    "common": ["Orange discoloration of fluids", "GI upset", "Rash"],
                    "uncommon": ["Flu-like syndrome", "Thrombocytopenia"],
                    "rare": ["Acute renal failure", "Hemolytic anemia"],
                    "serious": ["Hepatotoxicity", "Drug-induced lupus", "Thrombocytopenia"]
                },
                contraindications=[
                    "Jaundice",
                    "Concurrent protease inhibitors",
                    "Hypersensitivity to rifamycins"
                ],
                black_box_warnings=[],
                precautions=[
                    "Major CYP450 inducer - check all drug interactions",
                    "Monitor LFTs monthly",
                    "Decreases effectiveness of many drugs"
                ],
                pregnancy_category=PregnancyCategory.C,
                lactation_safety="Compatible - monitor infant for jaundice",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Tuberculosis", "Latent TB", "Leprosy"],
                off_label_uses=["MRSA infections", "Brucellosis"],
                effectiveness=0.92,
                time_to_effect="2 weeks for sterilization",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=95.0,
                    half_life_hours=3.0,
                    time_to_peak_hours=2.0,
                    volume_of_distribution=0.65,
                    protein_binding=80.0,
                    metabolism_pathway=[MetabolismPathway.CYP3A4],
                    excretion_route="Biliary (60%), Renal (30%)",
                    active_metabolites=["25-desacetylrifampicin"]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=True,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="LFTs monthly, CBC if symptoms"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={"All": "No adjustment needed"},
                    hepatic_impairment={"Moderate-Severe": "Reduce dose or avoid"},
                    pediatric_dosing="10-20mg/kg/day (max 600mg)",
                    geriatric_dosing="No adjustment",
                    obesity_dosing="Use ideal body weight",
                    pregnancy_adjustment="Vitamin K supplementation in last weeks"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=3.0,
                    number_needed_to_harm=30.0,
                    key_trials=["British MRC Trials", "USPHS Studies"],
                    guidelines_recommending=["WHO TB Guidelines", "ATS/IDSA"],
                    cochrane_review="CD001150"
                ),
                cost_per_unit=0.50,
                cost_per_course=90.00,
                generic_available=True,
                insurance_coverage="Tier 1 - Often covered by TB programs"
            )
        ],
        "second_line": [],
        "supportive": []
    },
    "Skin Cancer": {
        "first_line": [
            AdvancedMedication(
                generic_name="Fluorouracil (Topical)",
                brand_names=["Efudex", "Carac", "Tolak"],
                drug_class="Antimetabolite (Pyrimidine analog)",
                mechanism_of_action="Inhibits thymidylate synthase, blocking DNA synthesis",
                standard_dosage="5% cream",
                dosage_forms=["Cream", "Solution"],
                frequency="Twice daily",
                duration="2-4 weeks",
                max_daily_dose="Application to affected area",
                side_effects={
                    "common": ["Erythema", "Pain", "Erosion", "Crusting"],
                    "uncommon": ["Photosensitivity", "Hyperpigmentation"],
                    "rare": ["Scarring", "Allergic contact dermatitis"],
                    "serious": ["Severe inflammatory reaction", "Eye irritation if exposed"]
                },
                contraindications=[
                    "Pregnancy",
                    "DPD deficiency",
                    "Hypersensitivity to fluorouracil"
                ],
                black_box_warnings=[],
                precautions=[
                    "Avoid sun exposure during treatment",
                    "Severe inflammatory reaction expected",
                    "Avoid eyes, nose, mouth"
                ],
                pregnancy_category=PregnancyCategory.X,
                lactation_safety="Contraindicated",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Actinic keratosis", "Superficial BCC"],
                off_label_uses=["Bowen's disease", "Keratoacanthoma"],
                effectiveness=0.85,
                time_to_effect="4-8 weeks post-treatment",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=5.0,
                    half_life_hours=0.3,
                    time_to_peak_hours=1.0,
                    volume_of_distribution=0.1,
                    protein_binding=10.0,
                    metabolism_pathway=[MetabolismPathway.CYP2C9],
                    excretion_route="Renal (7-20%)",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Clinical assessment weekly"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={"All": "Minimal systemic absorption"},
                    hepatic_impairment={"All": "Minimal systemic absorption"},
                    pediatric_dosing="Not typically used",
                    geriatric_dosing="Standard dosing",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="Contraindicated"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=2.0,
                    number_needed_to_harm=5.0,
                    key_trials=["Multiple RCTs for AK"],
                    guidelines_recommending=["AAD Guidelines", "NCCN Guidelines"],
                    cochrane_review="CD009125"
                ),
                cost_per_unit=150.00,
                cost_per_course=150.00,
                generic_available=True,
                insurance_coverage="Tier 2-3"
            )
        ],
        "second_line": [],
        "supportive": []
    },
    "Malaria": {
        "first_line": [
            AdvancedMedication(
                generic_name="Artemether-Lumefantrine",
                brand_names=["Coartem", "Riamet"],
                drug_class="Artemisinin combination therapy (ACT)",
                mechanism_of_action="Artemether: rapid parasite clearance; Lumefantrine: prevents recrudescence",
                standard_dosage="80mg/480mg",
                dosage_forms=["Tablet", "Dispersible tablet"],
                frequency="Twice daily",
                duration="3 days",
                max_daily_dose="160mg/960mg",
                side_effects={
                    "common": ["Headache", "Anorexia", "Dizziness", "Nausea"],
                    "uncommon": ["Sleep disturbance", "Palpitations"],
                    "rare": ["QT prolongation", "Hypersensitivity"],
                    "serious": ["Severe hypersensitivity", "Cardiac arrhythmias"]
                },
                contraindications=[
                    "First trimester pregnancy",
                    "Severe malaria",
                    "Concurrent QT-prolonging drugs"
                ],
                black_box_warnings=[],
                precautions=[
                    "Take with fatty food for absorption",
                    "ECG monitoring if cardiac history",
                    "Not for severe/complicated malaria"
                ],
                pregnancy_category=PregnancyCategory.C,
                lactation_safety="Compatible",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Uncomplicated P. falciparum malaria"],
                off_label_uses=["Mixed malaria infections"],
                effectiveness=0.95,
                time_to_effect="24-48 hours for symptom relief",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=85.0,
                    half_life_hours=120.0,
                    time_to_peak_hours=2.0,
                    volume_of_distribution=1.7,
                    protein_binding=99.5,
                    metabolism_pathway=[MetabolismPathway.CYP3A4],
                    excretion_route="Fecal (primarily)",
                    active_metabolites=["Dihydroartemisinin"]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Parasitemia on day 3"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={"All": "No adjustment"},
                    hepatic_impairment={"Severe": "Use with caution"},
                    pediatric_dosing="Weight-based (5-35kg): 1-4 tablets per dose",
                    geriatric_dosing="No adjustment",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="Avoid first trimester"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=1.0,
                    number_needed_to_harm=500.0,
                    key_trials=["Multiple WHO-sponsored trials"],
                    guidelines_recommending=["WHO Malaria Guidelines", "CDC Guidelines"],
                    cochrane_review="CD007483"
                ),
                cost_per_unit=2.50,
                cost_per_course=15.00,
                generic_available=True,
                insurance_coverage="Usually covered, may need travel justification"
            )
        ],
        "second_line": [],
        "supportive": []
    },
    "Dental Caries": {
        "first_line": [
            AdvancedMedication(
                generic_name="Amoxicillin",
                brand_names=["Amoxil", "Trimox"],
                drug_class="Aminopenicillin",
                mechanism_of_action="Inhibits bacterial cell wall synthesis",
                standard_dosage="500mg",
                dosage_forms=["Capsule", "Tablet", "Suspension"],
                frequency="Three times daily",
                duration="7 days",
                max_daily_dose="3000mg",
                side_effects={
                    "common": ["Diarrhea", "Nausea", "Rash"],
                    "uncommon": ["Vomiting", "Candidiasis"],
                    "rare": ["Seizures", "Hepatitis"],
                    "serious": ["Anaphylaxis", "C. difficile colitis"]
                },
                contraindications=[
                    "Penicillin allergy",
                    "Infectious mononucleosis"
                ],
                black_box_warnings=[],
                precautions=[
                    "Renal adjustment in severe impairment",
                    "Cross-reactivity with cephalosporins possible"
                ],
                pregnancy_category=PregnancyCategory.B,
                lactation_safety="Compatible",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Dental infections", "Sinusitis", "Otitis media"],
                off_label_uses=["H. pylori eradication"],
                effectiveness=0.90,
                time_to_effect="24-48 hours",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=80.0,
                    half_life_hours=1.0,
                    time_to_peak_hours=1.5,
                    volume_of_distribution=0.3,
                    protein_binding=20.0,
                    metabolism_pathway=[MetabolismPathway.RENAL],
                    excretion_route="Renal (60% unchanged)",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Clinical response"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={
                        "GFR 10-30": "250-500mg q12h",
                        "GFR <10": "250-500mg q24h"
                    },
                    hepatic_impairment={"All": "No adjustment"},
                    pediatric_dosing="25-50mg/kg/day divided q8h",
                    geriatric_dosing="Renal adjustment if needed",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="No adjustment"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=5.0,
                    number_needed_to_harm=100.0,
                    key_trials=["Multiple dental infection trials"],
                    guidelines_recommending=["ADA Guidelines", "AAPD Guidelines"],
                    cochrane_review="CD004969"
                ),
                cost_per_unit=0.25,
                cost_per_course=10.50,
                generic_available=True,
                insurance_coverage="Tier 1 - Preferred Generic"
            )
        ],
        "second_line": [],
        "supportive": [
            AdvancedMedication(
                generic_name="Chlorhexidine Gluconate",
                brand_names=["Peridex", "Periogard"],
                drug_class="Antiseptic",
                mechanism_of_action="Disrupts bacterial cell membranes",
                standard_dosage="0.12%",
                dosage_forms=["Oral rinse"],
                frequency="Twice daily",
                duration="7-14 days",
                max_daily_dose="30mL/day",
                side_effects={
                    "common": ["Tooth staining", "Taste alteration", "Tartar increase"],
                    "uncommon": ["Tongue discoloration", "Mucosal irritation"],
                    "rare": ["Parotid swelling"],
                    "serious": ["Severe allergic reaction (rare)"]
                },
                contraindications=["Hypersensitivity to chlorhexidine"],
                black_box_warnings=[],
                precautions=[
                    "Do not swallow",
                    "Rinse after meals",
                    "May stain restorations"
                ],
                pregnancy_category=PregnancyCategory.B,
                lactation_safety="Compatible",
                controlled_schedule=ControlledSubstanceSchedule.NONE,
                indications=["Gingivitis", "Periodontal disease"],
                off_label_uses=["Post-surgical rinse", "Implant maintenance"],
                effectiveness=0.85,
                time_to_effect="1-2 weeks",
                pharmacokinetics=PharmacokineticProfile(
                    bioavailability=0.0,
                    half_life_hours=0,
                    time_to_peak_hours=0,
                    volume_of_distribution=0,
                    protein_binding=0,
                    metabolism_pathway=[],
                    excretion_route="Not absorbed",
                    active_metabolites=[]
                ),
                monitoring=DrugMonitoring(
                    requires_monitoring=False,
                    therapeutic_range_min=0,
                    therapeutic_range_max=0,
                    toxic_level=0,
                    sampling_time="N/A",
                    monitoring_frequency="Dental exam"
                ),
                dosing_adjustments=DosingAdjustment(
                    renal_impairment={"All": "No adjustment"},
                    hepatic_impairment={"All": "No adjustment"},
                    pediatric_dosing="Not recommended <18 years",
                    geriatric_dosing="Standard dosing",
                    obesity_dosing="Standard dosing",
                    pregnancy_adjustment="No adjustment"
                ),
                clinical_evidence=ClinicalEvidence(
                    evidence_level="A",
                    number_needed_to_treat=3.0,
                    number_needed_to_harm=20.0,
                    key_trials=["Multiple gingivitis trials"],
                    guidelines_recommending=["ADA Guidelines"],
                    cochrane_review="CD008676"
                ),
                cost_per_unit=15.00,
                cost_per_course=15.00,
                generic_available=True,
                insurance_coverage="Tier 1"
            )
        ]
    }
}

# =============================================================================
# DRUG INTERACTION DATABASE
# =============================================================================

ADVANCED_DRUG_INTERACTIONS = [
    DrugInteraction(
        drug1="Warfarin",
        drug2="Aspirin",
        severity="Major",
        mechanism="Additive anticoagulant/antiplatelet effects",
        clinical_effect="Increased risk of major and GI bleeding",
        management="Avoid if possible. If necessary, use lowest aspirin dose, add PPI",
        documentation_level="Established",
        onset="Delayed",
        evidence_references=["WARIS II", "ACTIVE W Trial"]
    ),
    DrugInteraction(
        drug1="Metformin",
        drug2="Iodinated Contrast",
        severity="Major",
        mechanism="Contrast-induced nephropathy may decrease metformin clearance",
        clinical_effect="Risk of lactic acidosis",
        management="Hold metformin day of and 48h after contrast",
        documentation_level="Established",
        onset="Delayed",
        evidence_references=["ACR Manual on Contrast Media"]
    ),
    DrugInteraction(
        drug1="ACE Inhibitor",
        drug2="Potassium",
        severity="Major",
        mechanism="ACE inhibitors reduce aldosterone, decreasing potassium excretion",
        clinical_effect="Hyperkalemia - risk of cardiac arrhythmias",
        management="Monitor potassium, avoid supplements unless hypokalemic",
        documentation_level="Established",
        onset="Delayed",
        evidence_references=["Multiple observational studies"]
    ),
    DrugInteraction(
        drug1="Fluoroquinolone",
        drug2="QT-Prolonging Drugs",
        severity="Major",
        mechanism="Additive QT prolongation",
        clinical_effect="Torsades de pointes, ventricular arrhythmias",
        management="Avoid combination. If necessary, ECG monitoring",
        documentation_level="Established",
        onset="Rapid",
        evidence_references=["FDA Safety Communication 2018"]
    ),
    DrugInteraction(
        drug1="SSRI",
        drug2="MAOI",
        severity="Contraindicated",
        mechanism="Excessive serotonin accumulation",
        clinical_effect="Serotonin syndrome: hyperthermia, rigidity, death",
        management="Absolute contraindication. 14-day washout required",
        documentation_level="Established",
        onset="Rapid",
        evidence_references=["FDA Black Box Warning"]
    ),
    DrugInteraction(
        drug1="Rifampicin",
        drug2="Oral Contraceptives",
        severity="Major",
        mechanism="CYP3A4 induction reduces contraceptive levels",
        clinical_effect="Contraceptive failure, unintended pregnancy",
        management="Use alternative contraception during and 28 days after rifampicin",
        documentation_level="Established",
        onset="Delayed",
        evidence_references=["Multiple pharmacokinetic studies"]
    )
]

# =============================================================================
# PHARMACOGENOMIC DATABASE
# =============================================================================

PHARMACOGENOMIC_DATA = {
    "CYP2D6": {
        "poor_metabolizer": {
            "affected_drugs": ["Codeine", "Tramadol", "Tamoxifen", "Metoprolol"],
            "recommendations": {
                "Codeine": "AVOID - no analgesic effect",
                "Tramadol": "AVOID - reduced efficacy",
                "Tamoxifen": "Consider aromatase inhibitor",
                "Metoprolol": "Reduce dose by 75%"
            }
        },
        "ultrarapid_metabolizer": {
            "affected_drugs": ["Codeine", "Tramadol"],
            "recommendations": {
                "Codeine": "AVOID - risk of fatal toxicity",
                "Tramadol": "AVOID - increased toxicity risk"
            }
        }
    },
    "CYP2C19": {
        "poor_metabolizer": {
            "affected_drugs": ["Clopidogrel", "Omeprazole"],
            "recommendations": {
                "Clopidogrel": "Consider prasugrel or ticagrelor",
                "Omeprazole": "Reduce dose by 50%"
            }
        }
    },
    "HLA-B*5701": {
        "positive": {
            "affected_drugs": ["Abacavir"],
            "recommendations": {
                "Abacavir": "CONTRAINDICATED - fatal hypersensitivity risk"
            }
        }
    }
}

# =============================================================================
# MEDICATION ENGINE CLASS
# =============================================================================

class AdvancedMedicationEngine:
    """Enterprise-grade medication suggestion system"""
    
    def __init__(self):
        self.medication_database = ADVANCED_MEDICATION_DATABASE
        self.interaction_database = ADVANCED_DRUG_INTERACTIONS
        self.pharmacogenomics = PHARMACOGENOMIC_DATA
        self.audit_log = []
    
    def calculate_bmi(self, weight_kg: float, height_cm: float) -> float:
        height_m = height_cm / 100
        return weight_kg / (height_m ** 2)
    
    def calculate_bsa(self, weight_kg: float, height_cm: float) -> float:
        return np.sqrt((height_cm * weight_kg) / 3600)
    
    def calculate_creatinine_clearance(self, age: int, weight_kg: float, 
                                        serum_creatinine: float, sex: str) -> float:
        crcl = ((140 - age) * weight_kg) / (72 * serum_creatinine)
        if sex.lower() == "female":
            crcl *= 0.85
        return crcl
    
    def calculate_ideal_body_weight(self, height_cm: float, sex: str) -> float:
        height_inches = height_cm / 2.54
        if sex.lower() == "male":
            return 50 + 2.3 * (height_inches - 60)
        else:
            return 45.5 + 2.3 * (height_inches - 60)
    
    def get_medications_for_disease(self, disease: str) -> Dict:
        if disease in self.medication_database:
            return self.medication_database[disease]
        
        for key in self.medication_database.keys():
            if key.lower() in disease.lower() or disease.lower() in key.lower():
                return self.medication_database[key]
        
        return {}
    
    def check_all_interactions(self, medications: List[str]) -> List[DrugInteraction]:
        found_interactions = []
        
        for i, drug1 in enumerate(medications):
            for drug2 in medications[i+1:]:
                for interaction in self.interaction_database:
                    if (self._fuzzy_match(drug1, interaction.drug1) and 
                        self._fuzzy_match(drug2, interaction.drug2)) or \
                       (self._fuzzy_match(drug1, interaction.drug2) and 
                        self._fuzzy_match(drug2, interaction.drug1)):
                        found_interactions.append(interaction)
        
        severity_order = {"Contraindicated": 0, "Major": 1, "Moderate": 2, "Minor": 3}
        found_interactions.sort(key=lambda x: severity_order.get(x.severity, 4))
        
        return found_interactions
    
    def _fuzzy_match(self, drug1: str, drug2: str) -> bool:
        drug1_lower = drug1.lower()
        drug2_lower = drug2.lower()
        
        if drug1_lower == drug2_lower:
            return True
        
        if drug1_lower in drug2_lower or drug2_lower in drug1_lower:
            return True
        
        drug_classes = {
            "ace inhibitor": ["lisinopril", "enalapril", "ramipril", "captopril"],
            "ssri": ["sertraline", "fluoxetine", "paroxetine", "citalopram"],
            "maoi": ["phenelzine", "tranylcypromine", "selegiline"],
            "fluoroquinolone": ["ciprofloxacin", "levofloxacin", "moxifloxacin"],
            "nsaid": ["ibuprofen", "naproxen", "diclofenac", "meloxicam"]
        }
        
        for drug_class, members in drug_classes.items():
            if drug1_lower in members and drug_class in drug2_lower:
                return True
            if drug2_lower in members and drug_class in drug1_lower:
                return True
        
        return False
    
    def check_allergies(self, medication: AdvancedMedication, 
                       allergies: List[str]) -> Dict[str, Any]:
        allergy_results = {
            "direct_allergy": False,
            "cross_reactivity": False,
            "allergy_details": [],
            "safe_to_use": True
        }
        
        cross_reactivity_map = {
            "penicillin": {
                "drugs": ["amoxicillin", "ampicillin", "piperacillin"],
                "related": ["cephalosporin"],
                "cross_react_rate": "1-10%"
            },
            "sulfa": {
                "drugs": ["sulfamethoxazole", "sulfasalazine"],
                "related": ["thiazide", "furosemide"],
                "cross_react_rate": "Low"
            }
        }
        
        med_name_lower = medication.generic_name.lower()
        
        for allergy in allergies:
            allergy_lower = allergy.lower()
            
            if allergy_lower in med_name_lower:
                allergy_results["direct_allergy"] = True
                allergy_results["safe_to_use"] = False
                allergy_results["allergy_details"].append({
                    "type": "Direct allergy",
                    "allergen": allergy,
                    "medication": medication.generic_name,
                    "severity": "Contraindicated"
                })
            
            for allergen_class, data in cross_reactivity_map.items():
                if allergy_lower in data["drugs"] or allergen_class in allergy_lower:
                    for related in data["related"]:
                        if related in med_name_lower or related in medication.drug_class.lower():
                            allergy_results["cross_reactivity"] = True
                            allergy_results["allergy_details"].append({
                                "type": "Potential cross-reactivity",
                                "allergen": allergy,
                                "medication": medication.generic_name,
                                "rate": data["cross_react_rate"],
                                "severity": "Use with caution"
                            })
        
        return allergy_results
    
    def check_pharmacogenomics(self, medication: AdvancedMedication,
                               patient: PatientProfile) -> Dict[str, Any]:
        pgx_results = {
            "has_implications": False,
            "recommendations": [],
            "genes_affected": []
        }
        
        med_name = medication.generic_name.lower()
        
        if patient.cyp2d6_status:
            status = patient.cyp2d6_status.lower().replace("-", "_").replace(" ", "_")
            if status in self.pharmacogenomics.get("CYP2D6", {}):
                pgx_data = self.pharmacogenomics["CYP2D6"][status]
                for drug in pgx_data["affected_drugs"]:
                    if drug.lower() in med_name:
                        pgx_results["has_implications"] = True
                        pgx_results["genes_affected"].append("CYP2D6")
                        pgx_results["recommendations"].append({
                            "gene": "CYP2D6",
                            "status": patient.cyp2d6_status,
                            "drug": drug,
                            "recommendation": pgx_data["recommendations"].get(drug, "Review dosing")
                        })
        
        if patient.hla_b5701:
            pgx_data = self.pharmacogenomics.get("HLA-B*5701", {}).get("positive", {})
            for drug in pgx_data.get("affected_drugs", []):
                if drug.lower() in med_name:
                    pgx_results["has_implications"] = True
                    pgx_results["genes_affected"].append("HLA-B*5701")
                    pgx_results["recommendations"].append({
                        "gene": "HLA-B*5701",
                        "status": "Positive",
                        "drug": drug,
                        "recommendation": pgx_data["recommendations"].get(drug, "AVOID")
                    })
        
        return pgx_results
    
    def adjust_dosing(self, medication: AdvancedMedication,
                     patient: PatientProfile) -> Dict[str, Any]:
        adjustments = {
            "original_dose": medication.standard_dosage,
            "adjusted_dose": medication.standard_dosage,
            "adjustments_applied": [],
            "warnings": [],
            "requires_monitoring": []
        }
        
        if patient.gfr < 60:
            renal_adj = medication.dosing_adjustments.renal_impairment
            for gfr_range, dosing in renal_adj.items():
                if self._check_gfr_range(patient.gfr, gfr_range):
                    adjustments["adjusted_dose"] = dosing
                    adjustments["adjustments_applied"].append(
                        f"Renal adjustment (GFR {patient.gfr:.0f}): {dosing}"
                    )
                    adjustments["requires_monitoring"].append("Renal function")
                    break
        
        if patient.child_pugh_score:
            hepatic_adj = medication.dosing_adjustments.hepatic_impairment
            for score, dosing in hepatic_adj.items():
                if patient.child_pugh_score in score:
                    if dosing != "No adjustment":
                        adjustments["adjustments_applied"].append(
                            f"Hepatic adjustment (Child-Pugh {patient.child_pugh_score}): {dosing}"
                        )
                        adjustments["requires_monitoring"].append("Liver function")
                    break
        
        if patient.geriatric:
            geriatric_dose = medication.dosing_adjustments.geriatric_dosing
            if geriatric_dose != "No adjustment":
                adjustments["adjustments_applied"].append(f"Geriatric: {geriatric_dose}")
                adjustments["warnings"].append("Consider starting at lower dose in elderly")
        
        if patient.pediatric:
            ped_dose = medication.dosing_adjustments.pediatric_dosing
            adjustments["adjusted_dose"] = ped_dose
            adjustments["adjustments_applied"].append(f"Pediatric: {ped_dose}")
        
        if patient.pregnant:
            if medication.pregnancy_category in [PregnancyCategory.D, PregnancyCategory.X]:
                adjustments["warnings"].append(
                    f"⚠️ PREGNANCY WARNING: Category {medication.pregnancy_category.value}"
                )
        
        bmi = self.calculate_bmi(patient.weight_kg, patient.height_cm)
        if bmi >= 30:
            adjustments["adjustments_applied"].append(
                f"Obesity (BMI {bmi:.1f}): {medication.dosing_adjustments.obesity_dosing}"
            )
        
        return adjustments
    
    def _check_gfr_range(self, gfr: float, gfr_range: str) -> bool:
        gfr_range = gfr_range.upper().replace("GFR", "").replace("EGFR", "").strip()
        
        if "<" in gfr_range:
            try:
                threshold = float(re.search(r'\d+', gfr_range).group())
                return gfr < threshold
            except:
                return False
        elif ">" in gfr_range:
            try:
                threshold = float(re.search(r'\d+', gfr_range).group())
                return gfr > threshold
            except:
                return False
        elif "-" in gfr_range:
            try:
                parts = re.findall(r'\d+', gfr_range)
                return float(parts[0]) <= gfr <= float(parts[1])
            except:
                return False
        
        return False
    
    def calculate_medication_score(self, medication: AdvancedMedication,
                                   patient: PatientProfile,
                                   current_medications: List[str]) -> Dict[str, Any]:
        score_breakdown = {
            "effectiveness_score": 0,
            "safety_score": 0,
            "practicality_score": 0,
            "cost_score": 0,
            "overall_score": 0,
            "recommendation_level": "",
            "flags": []
        }
        
        # Effectiveness (0-35 points)
        effectiveness = medication.effectiveness * 35
        score_breakdown["effectiveness_score"] = min(35, effectiveness)
        
        # Safety (0-30 points)
        safety = 30
        safety -= len(medication.side_effects.get("serious", [])) * 3
        safety -= len(medication.black_box_warnings) * 5
        
        for ci in medication.contraindications:
            if any(ci.lower() in cond.lower() for cond in patient.comorbidities):
                safety -= 10
                score_breakdown["flags"].append(f"Contraindication: {ci}")
        
        allergy_check = self.check_allergies(medication, patient.allergies)
        if allergy_check["direct_allergy"]:
            safety = 0
            score_breakdown["flags"].append("ALLERGY - Do not use")
        elif allergy_check["cross_reactivity"]:
            safety -= 10
            score_breakdown["flags"].append("Potential cross-reactivity")
        
        interactions = self.check_all_interactions(
            current_medications + [medication.generic_name]
        )
        for interaction in interactions:
            if interaction.severity == "Contraindicated":
                safety = 0
            elif interaction.severity == "Major":
                safety -= 10
            elif interaction.severity == "Moderate":
                safety -= 5
        
        score_breakdown["safety_score"] = max(0, min(30, safety))
        
        # Practicality (0-20 points)
        practicality = 20
        if "once daily" in medication.frequency.lower():
            practicality += 0
        elif "twice daily" in medication.frequency.lower():
            practicality -= 2
        else:
            practicality -= 5
        
        if medication.monitoring.requires_monitoring:
            practicality -= 3
        
        score_breakdown["practicality_score"] = max(0, min(20, practicality))
        
        # Cost (0-15 points)
        cost = 15
        if medication.cost_per_course > 1000:
            cost = 2
        elif medication.cost_per_course > 500:
            cost = 5
        elif medication.cost_per_course > 100:
            cost = 8
        elif medication.cost_per_course > 50:
            cost = 12
        
        if medication.generic_available:
            cost += 2
        
        score_breakdown["cost_score"] = min(15, cost)
        
        # Overall score
        score_breakdown["overall_score"] = (
            score_breakdown["effectiveness_score"] +
            score_breakdown["safety_score"] +
            score_breakdown["practicality_score"] +
            score_breakdown["cost_score"]
        )
        
        # Recommendation level
        total = score_breakdown["overall_score"]
        if total >= 85:
            score_breakdown["recommendation_level"] = "Highly Recommended"
        elif total >= 70:
            score_breakdown["recommendation_level"] = "Recommended"
        elif total >= 55:
            score_breakdown["recommendation_level"] = "Consider with caution"
        elif total >= 40:
            score_breakdown["recommendation_level"] = "Use only if alternatives unavailable"
        else:
            score_breakdown["recommendation_level"] = "Not recommended"
        
        return score_breakdown


# =============================================================================
# VISUALIZATION FUNCTIONS
# =============================================================================

def create_medication_comparison_chart(medications: List[AdvancedMedication]) -> go.Figure:
    """Create radar chart comparing medications"""
    
    categories = ['Effectiveness', 'Safety', 'Convenience', 'Cost-Effectiveness', 'Evidence']
    
    fig = go.Figure()
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B']
    
    for i, med in enumerate(medications[:5]):
        effectiveness = med.effectiveness * 100
        safety = max(0, 100 - len(med.side_effects.get("serious", [])) * 15 - 
                    len(med.black_box_warnings) * 20)
        convenience = 90 if "once" in med.frequency.lower() else (
            70 if "twice" in med.frequency.lower() else 50
        )
        cost_eff = max(0, 100 - (med.cost_per_course / 100) * 10)
        evidence_map = {"A": 100, "B": 80, "C": 60, "D": 40}
        evidence = evidence_map.get(med.clinical_evidence.evidence_level, 50)
        
        values = [effectiveness, safety, convenience, cost_eff, evidence]
        values.append(values[0])
        
        fig.add_trace(go.Scatterpolar(
            r=values,
            theta=categories + [categories[0]],
            fill='toself',
            name=med.generic_name,
            line_color=colors[i % len(colors)],
            opacity=0.7
        ))
    
    fig.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 100])),
        showlegend=True,
        title="Medication Comparison",
        height=450
    )
    
    return fig


def create_cost_comparison(medications: List[AdvancedMedication]) -> go.Figure:
    """Create cost comparison chart"""
    
    names = [med.generic_name for med in medications]
    costs = [med.cost_per_course for med in medications]
    colors = ['#2E86AB', '#A23B72', '#F18F01', '#C73E1D', '#3B1F2B', '#48A9A6']
    
    fig = go.Figure(data=[
        go.Bar(
            x=names,
            y=costs,
            marker_color=colors[:len(medications)],
            text=[f"${c:.0f}" for c in costs],
            textposition='outside'
        )
    ])
    
    fig.update_layout(
        title="Cost per Treatment Course",
        yaxis_title="Cost ($)",
        height=400
    )
    
    return fig


def create_pk_visualization(pk: PharmacokineticProfile, med_name: str) -> go.Figure:
    """Create pharmacokinetic profile visualization"""
    
    t = np.linspace(0, 48, 200)
    ka = 1.5
    ke = 0.693 / max(pk.half_life_hours, 0.1)
    
    C = (pk.bioavailability / 100) * (ka / (ka - ke + 0.001)) * (np.exp(-ke * t) - np.exp(-ka * t))
    C = C / (C.max() + 0.001) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=t, y=C,
        mode='lines',
        name='Plasma Concentration',
        line=dict(color='#2E86AB', width=3),
        fill='tozeroy',
        fillcolor='rgba(46, 134, 171, 0.3)'
    ))
    
    fig.add_hline(y=50, line_dash="dash", line_color="green",
                  annotation_text=f"t½: {pk.half_life_hours}h")
    
    fig.update_layout(
        title=f'Pharmacokinetic Profile: {med_name}',
        xaxis_title="Time (hours)",
        yaxis_title="Relative Concentration (%)",
        height=350
    )
    
    return fig


# =============================================================================
# MAIN UI FUNCTION - FIXED (NO NESTED EXPANDERS)
# =============================================================================

def show_advanced_medication_suggestions(disease: str, confidence: float):
    """Main UI for advanced medication suggestions - Fixed version without nested expanders"""
    
    st.markdown("## 💊 AI-Powered Medication Decision Support")
    st.markdown("---")
    
    engine = AdvancedMedicationEngine()
    
    # Determine severity
    if confidence < 40:
        severity = SeverityLevel.MILD
    elif confidence < 60:
        severity = SeverityLevel.MODERATE
    elif confidence < 80:
        severity = SeverityLevel.SEVERE
    else:
        severity = SeverityLevel.CRITICAL
    
    # Header metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎯 Diagnosis", disease)
    with col2:
        severity_icon = {"MILD": "🟢", "MODERATE": "🟡", "SEVERE": "🟠", "CRITICAL": "🔴"}
        st.metric("📊 Severity", f"{severity_icon.get(severity.name, '⚪')} {severity.value}")
    with col3:
        st.metric("🔬 Confidence", f"{confidence:.1f}%")
    with col4:
        st.metric("📅 Date", datetime.now().strftime("%Y-%m-%d"))
    
    st.markdown("---")
    
    # ==========================================================================
    # PATIENT PROFILE SECTION
    # ==========================================================================
    
    st.markdown("### 👤 Patient Profile")
    
    with st.expander("📋 Enter Patient Information", expanded=False):
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.markdown("**Demographics**")
            age = st.number_input("Age (years)", 0, 120, 45, key="med_age")
            sex = st.selectbox("Biological Sex", ["Male", "Female"], key="med_sex")
            weight = st.number_input("Weight (kg)", 1.0, 300.0, 70.0, key="med_weight")
            height = st.number_input("Height (cm)", 50.0, 250.0, 170.0, key="med_height")
        
        with col2:
            st.markdown("**Organ Function**")
            serum_cr = st.number_input("Serum Creatinine (mg/dL)", 0.1, 15.0, 1.0, key="med_scr")
            gfr_input = st.number_input("eGFR (mL/min/1.73m²)", 5.0, 150.0, 90.0, key="med_gfr")
            child_pugh = st.selectbox("Child-Pugh Score", [None, "A", "B", "C"], key="med_cp")
        
        with col3:
            st.markdown("**Special Populations**")
            pregnant = st.checkbox("Pregnant", key="med_preg")
            lactating = st.checkbox("Lactating", key="med_lact")
            
            st.markdown("**Pharmacogenomics**")
            cyp2d6 = st.selectbox("CYP2D6", ["Unknown", "Normal", "Poor Metabolizer", "Ultra-rapid"], key="med_cyp2d6")
            hla_b5701 = st.checkbox("HLA-B*5701 Positive", key="med_hla")
        
        st.markdown("---")
        
        col1, col2 = st.columns(2)
        with col1:
            allergies_text = st.text_area("Drug Allergies (one per line)", height=100, key="med_allergies")
        with col2:
            current_meds_text = st.text_area("Current Medications (one per line)", height=100, key="med_current")
    
    # Parse inputs
    allergies = [a.strip() for a in allergies_text.split('\n') if a.strip()] if 'allergies_text' in dir() else []
    current_medications = [m.strip().split()[0] if m.strip() else "" 
                          for m in current_meds_text.split('\n') if m.strip()] if 'current_meds_text' in dir() else []
    
    # Create patient profile with defaults
    pediatric = age < 18 if 'age' in dir() else False
    geriatric = age >= 65 if 'age' in dir() else False
    
    patient = PatientProfile(
        age=age if 'age' in dir() else 45,
        weight_kg=weight if 'weight' in dir() else 70.0,
        height_cm=height if 'height' in dir() else 170.0,
        sex=sex if 'sex' in dir() else "Male",
        creatinine_clearance=90.0,
        gfr=gfr_input if 'gfr_input' in dir() else 90.0,
        child_pugh_score=child_pugh if 'child_pugh' in dir() else None,
        cyp2d6_status=cyp2d6 if 'cyp2d6' in dir() and cyp2d6 != "Unknown" else "",
        cyp2c19_status="",
        hla_b5701=hla_b5701 if 'hla_b5701' in dir() else False,
        allergies=allergies,
        current_medications=current_medications,
        comorbidities=[],
        previous_adverse_reactions=[],
        pregnant=pregnant if 'pregnant' in dir() else False,
        lactating=lactating if 'lactating' in dir() else False,
        pediatric=pediatric,
        geriatric=geriatric,
        lab_values={}
    )
    
    # Display calculated values
    if 'weight' in dir() and 'height' in dir():
        bmi = engine.calculate_bmi(weight, height)
        bsa = engine.calculate_bsa(weight, height)
        
        st.markdown("#### 📊 Calculated Parameters")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("BMI", f"{bmi:.1f} kg/m²")
        with col2:
            st.metric("BSA", f"{bsa:.2f} m²")
        with col3:
            st.metric("IBW", f"{engine.calculate_ideal_body_weight(height, sex):.1f} kg")
        with col4:
            st.metric("GFR Status", "Normal" if gfr_input >= 60 else "Reduced")
    
    st.markdown("---")
    
    # ==========================================================================
    # MEDICATION SUGGESTIONS
    # ==========================================================================
    
    st.markdown("### 💊 AI-Generated Medication Recommendations")
    
    # Get medications for disease
    meds_data = engine.get_medications_for_disease(disease)
    
    if not meds_data:
        st.warning(f"⚠️ No medication protocols found for '{disease}'.")
        st.info("Please consult clinical references for treatment options.")
        return
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["🥇 Medications", "📊 Comparison", "📥 Export"])
    
    all_medications = []
    
    with tab1:
        # First-line medications
        first_line = meds_data.get("first_line", [])
        
        if first_line:
            st.markdown("#### 🥇 First-Line Agents (Recommended)")
            
            for i, med in enumerate(first_line):
                all_medications.append(med)
                score = engine.calculate_medication_score(med, patient, current_medications)
                
                with st.expander(
                    f"💚 {med.generic_name} ({', '.join(med.brand_names[:2])}) - "
                    f"Score: {score['overall_score']:.0f}/100 | {score['recommendation_level']}",
                    expanded=(i == 0)
                ):
                    # Black box warnings at top
                    if med.black_box_warnings:
                        st.error("⚠️ **BLACK BOX WARNING**\n\n" + "\n\n".join(med.black_box_warnings))
                    
                    # Use tabs instead of nested expanders
                    med_tab1, med_tab2, med_tab3, med_tab4 = st.tabs([
                        "📋 Prescribing Info", "⚠️ Safety", "👤 Patient-Specific", "📈 PK/Evidence"
                    ])
                    
                    with med_tab1:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown(f"""
                            **Drug Class:** {med.drug_class}
                            
                            **Mechanism:** {med.mechanism_of_action}
                            
                            **Dosage:** {med.standard_dosage}
                            
                            **Frequency:** {med.frequency}
                            
                            **Duration:** {med.duration}
                            
                            **Max Daily Dose:** {med.max_daily_dose}
                            """)
                        
                        with col2:
                            st.markdown(f"""
                            **Available Forms:** {', '.join(med.dosage_forms)}
                            
                            **Time to Effect:** {med.time_to_effect}
                            
                            **Effectiveness:** {med.effectiveness * 100:.0f}%
                            
                            **Cost per Course:** ${med.cost_per_course:.2f}
                            
                            **Generic Available:** {'Yes ✅' if med.generic_available else 'No ❌'}
                            
                            **Insurance:** {med.insurance_coverage}
                            """)
                    
                    with med_tab2:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Common Side Effects:**")
                            for se in med.side_effects.get("common", [])[:5]:
                                st.markdown(f"• {se}")
                            
                            st.markdown("**Serious Adverse Effects:**")
                            for se in med.side_effects.get("serious", [])[:5]:
                                st.markdown(f"• ⚠️ {se}")
                        
                        with col2:
                            st.markdown(f"""
                            **Pregnancy Category:** {med.pregnancy_category.value}
                            
                            **Lactation:** {med.lactation_safety}
                            
                            **Controlled Status:** {med.controlled_schedule.value}
                            """)
                            
                            st.markdown("**Contraindications:**")
                            for ci in med.contraindications[:5]:
                                st.markdown(f"• {ci}")
                    
                    with med_tab3:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Dosing Adjustments**")
                            dosing = engine.adjust_dosing(med, patient)
                            
                            st.markdown(f"**Original Dose:** {dosing['original_dose']}")
                            st.markdown(f"**Adjusted Dose:** {dosing['adjusted_dose']}")
                            
                            if dosing['adjustments_applied']:
                                st.markdown("**Adjustments Applied:**")
                                for adj in dosing['adjustments_applied']:
                                    st.markdown(f"• {adj}")
                            
                            if dosing['warnings']:
                                for warn in dosing['warnings']:
                                    st.warning(warn)
                        
                        with col2:
                            st.markdown("**Safety Checks**")
                            
                            # Allergy check
                            allergy_result = engine.check_allergies(med, patient.allergies)
                            if allergy_result['direct_allergy']:
                                st.error("🚫 **DIRECT ALLERGY DETECTED**")
                            elif allergy_result['cross_reactivity']:
                                st.warning("⚠️ **Potential Cross-Reactivity**")
                            else:
                                st.success("✅ No allergy concerns")
                            
                            # Drug interactions
                            interactions = engine.check_all_interactions(
                                current_medications + [med.generic_name]
                            )
                            if interactions:
                                st.markdown("**Drug Interactions:**")
                                for interaction in interactions[:3]:
                                    if interaction.severity == "Contraindicated":
                                        st.error(f"🚫 {interaction.drug1} + {interaction.drug2}")
                                    elif interaction.severity == "Major":
                                        st.warning(f"⚠️ {interaction.drug1} + {interaction.drug2}")
                            else:
                                st.success("✅ No interactions detected")
                            
                            # Pharmacogenomics
                            pgx = engine.check_pharmacogenomics(med, patient)
                            if pgx['has_implications']:
                                st.warning("🧬 Pharmacogenomic implications found")
                                for rec in pgx['recommendations']:
                                    st.markdown(f"• {rec['gene']}: {rec['recommendation']}")
                    
                    with med_tab4:
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            st.markdown("**Pharmacokinetics**")
                            pk = med.pharmacokinetics
                            st.markdown(f"""
                            - Bioavailability: {pk.bioavailability}%
                            - Half-life: {pk.half_life_hours} hours
                            - Time to Peak: {pk.time_to_peak_hours} hours
                            - Protein Binding: {pk.protein_binding}%
                            - Excretion: {pk.excretion_route}
                            """)
                            
                            # PK Chart
                            if pk.half_life_hours > 0:
                                pk_fig = create_pk_visualization(pk, med.generic_name)
                                st.plotly_chart(pk_fig, use_container_width=True)
                        
                        with col2:
                            st.markdown("**Clinical Evidence**")
                            ev = med.clinical_evidence
                            st.markdown(f"""
                            - Evidence Level: {ev.evidence_level}
                            - NNT: {ev.number_needed_to_treat or 'N/A'}
                            - NNH: {ev.number_needed_to_harm or 'N/A'}
                            - Cochrane: {ev.cochrane_review or 'N/A'}
                            """)
                            
                            st.markdown("**Key Trials:**")
                            for trial in ev.key_trials[:3]:
                                st.markdown(f"• {trial}")
                            
                            st.markdown("**Guidelines:**")
                            for guide in ev.guidelines_recommending[:3]:
                                st.markdown(f"• {guide}")
        
        # Second-line medications
        second_line = meds_data.get("second_line", [])
        
        if second_line:
            st.markdown("#### 🥈 Second-Line Agents")
            
            for med in second_line:
                all_medications.append(med)
                score = engine.calculate_medication_score(med, patient, current_medications)
                
                with st.expander(f"🟡 {med.generic_name} - Score: {score['overall_score']:.0f}/100"):
                    if med.black_box_warnings:
                        st.error("⚠️ **BLACK BOX WARNING**\n\n" + "\n\n".join(med.black_box_warnings))
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        **Drug Class:** {med.drug_class}
                        **Dosage:** {med.standard_dosage} {med.frequency}
                        **Duration:** {med.duration}
                        """)
                    with col2:
                        st.markdown(f"""
                        **Effectiveness:** {med.effectiveness * 100:.0f}%
                        **Cost:** ${med.cost_per_course:.2f}
                        **Evidence:** {med.clinical_evidence.evidence_level}
                        """)
        
        # Supportive medications
        supportive = meds_data.get("supportive", [])
        
        if supportive:
            st.markdown("#### 🆘 Supportive Care")
            
            for med in supportive:
                all_medications.append(med)
                
                with st.expander(f"🆘 {med.generic_name}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"""
                        **Purpose:** Symptom management
                        **Dosage:** {med.standard_dosage} {med.frequency}
                        **Duration:** {med.duration}
                        """)
                    with col2:
                        st.markdown(f"""
                        **Cost:** ${med.cost_per_course:.2f}
                        **Generic:** {'Yes' if med.generic_available else 'No'}
                        """)
    
    with tab2:
        st.markdown("### 📊 Comparative Analysis")
        
        if len(all_medications) >= 2:
            # Radar comparison
            comparison_fig = create_medication_comparison_chart(all_medications)
            st.plotly_chart(comparison_fig, use_container_width=True)
            
            # Cost comparison
            cost_fig = create_cost_comparison(all_medications)
            st.plotly_chart(cost_fig, use_container_width=True)
            
            # Comparison table
            comparison_data = []
            for med in all_medications:
                score = engine.calculate_medication_score(med, patient, current_medications)
                comparison_data.append({
                    "Medication": med.generic_name,
                    "Class": med.drug_class,
                    "Effectiveness": f"{med.effectiveness * 100:.0f}%",
                    "Score": f"{score['overall_score']:.0f}/100",
                    "Evidence": med.clinical_evidence.evidence_level,
                    "Cost": f"${med.cost_per_course:.2f}",
                    "Generic": "✅" if med.generic_available else "❌"
                })
            
            st.dataframe(pd.DataFrame(comparison_data), use_container_width=True)
        else:
            st.info("Need at least 2 medications for comparison.")
    
    with tab3:
        st.markdown("### 📥 Export Options")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # JSON Report
            report_data = {
                "report_type": "Medication Recommendation",
                "generated": datetime.now().isoformat(),
                "diagnosis": disease,
                "confidence": confidence,
                "severity": severity.value,
                "medications": [
                    {
                        "name": med.generic_name,
                        "dosage": med.standard_dosage,
                        "frequency": med.frequency,
                        "duration": med.duration,
                        "effectiveness": med.effectiveness
                    }
                    for med in all_medications
                ]
            }
            
            st.download_button(
                "📋 Download JSON Report",
                json.dumps(report_data, indent=2),
                f"medication_report_{datetime.now().strftime('%Y%m%d')}.json",
                "application/json"
            )
        
        with col2:
            # CSV
            if all_medications:
                csv_data = pd.DataFrame([
                    {
                        "Medication": med.generic_name,
                        "Dosage": med.standard_dosage,
                        "Frequency": med.frequency,
                        "Duration": med.duration,
                        "Cost": med.cost_per_course
                    }
                    for med in all_medications
                ])
                
                st.download_button(
                    "📊 Download CSV",
                    csv_data.to_csv(index=False),
                    f"medications_{datetime.now().strftime('%Y%m%d')}.csv",
                    "text/csv"
                )
        
        with col3:
            # Text summary
            summary = f"""
MEDICATION SUMMARY
==================
Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Diagnosis: {disease}
Confidence: {confidence:.1f}%
Severity: {severity.value}

RECOMMENDATIONS:
"""
            for med in all_medications:
                summary += f"""
{med.generic_name}
- Dosage: {med.standard_dosage} {med.frequency}
- Duration: {med.duration}
- Cost: ${med.cost_per_course:.2f}
"""
            
            st.download_button(
                "📄 Download Summary",
                summary,
                f"summary_{datetime.now().strftime('%Y%m%d')}.txt",
                "text/plain"
            )
    
    # Disclaimer
    st.markdown("---")
    st.warning("""
    ⚠️ **CLINICAL DISCLAIMER**: This AI-powered system is designed to ASSIST healthcare 
    professionals, not replace clinical judgment. All medication recommendations require 
    verification by a licensed healthcare provider. The prescribing physician bears 
    ultimate responsibility for all treatment decisions.
    """)


# =============================================================================
# WRAPPER FUNCTION FOR BACKWARD COMPATIBILITY
# =============================================================================

def show_medication_suggestions(disease: str, confidence: float):
    """Wrapper function for backward compatibility"""
    show_advanced_medication_suggestions(disease, confidence)


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    st.set_page_config(
        page_title="Medication Decision Support",
        page_icon="💊",
        layout="wide"
    )
    
    st.title("💊 AI-Powered Medication Decision Support")
    
    disease = st.selectbox(
        "Select Condition",
        options=list(ADVANCED_MEDICATION_DATABASE.keys())
    )
    
    confidence = st.slider("Diagnostic Confidence (%)", 10.0, 100.0, 75.0)
    
    show_medication_suggestions(disease, confidence)