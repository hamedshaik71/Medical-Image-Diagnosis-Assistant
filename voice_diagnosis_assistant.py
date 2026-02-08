# 🎤 COMPREHENSIVE VOICE-BASED DIAGNOSIS ASSISTANT
# Smart, condition-aware, instant voice responses

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
import os
import base64
from io import BytesIO
import hashlib
import uuid

# Try to import TTS libraries
try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except ImportError:
    PYTTSX3_AVAILABLE = False


# ============================================
# GENERATE UNIQUE KEY PREFIX
# ============================================

def get_unique_key(base_key: str) -> str:
    """Generate a unique key for Streamlit widgets"""
    if 'voice_assistant_key_prefix' not in st.session_state:
        st.session_state.voice_assistant_key_prefix = f"va_{uuid.uuid4().hex[:8]}"
    return f"{st.session_state.voice_assistant_key_prefix}_{base_key}"


# ============================================
# PATIENT CONTEXT - What data is available?
# ============================================

def get_default_patient_context() -> Dict:
    """Get default patient context with all available/unavailable data flags"""
    return {
        # Patient Info
        "patient_id": None,
        "patient_name": None,
        "patient_age": None,
        "patient_gender": None,
        
        # Current Diagnosis
        "current_diagnosis": None,
        "confidence": 0.0,
        "severity": "moderate",
        "affected_region": "affected area",
        
        # Current Findings
        "current_findings": "findings to be documented",
        "comparison_result": "comparison pending",
        
        # Historical Data Availability
        "has_previous_scans": False,
        "previous_scan_count": 0,
        "previous_scan_dates": [],
        "last_scan_date": "previous visit",
        "last_scan_findings": "no previous findings",
        
        # Lab Results
        "has_lab_results": False,
        "lab_results": {},
        "lab_date": "pending",
        "wbc": "pending",
        "wbc_interpretation": "awaiting results",
        "crp": "pending",
        "crp_interpretation": "awaiting results",
        "procalcitonin": "pending",
        "procalcitonin_interpretation": "awaiting results",
        
        # Vitals
        "has_vitals": False,
        "vitals": {},
        "vitals_date": None,
        
        # Treatment History
        "has_treatment_history": False,
        "current_medications": [],
        "allergies": [],
        "past_treatments": [],
        
        # Medical History
        "has_medical_history": False,
        "conditions": [],
        "surgeries": [],
        "family_history": [],
        
        # Insurance/Billing
        "has_insurance": False,
        "insurance_provider": None,
        
        # Doctor Info
        "attending_physician": None,
        "specialist_referral": None,
        
        # Appointment
        "has_follow_up": False,
        "follow_up_date": None,
        
        # Additional context
        "location": "identified region",
        "size": "to be measured",
        "current_size": "current measurement",
        "previous_size": "previous measurement",
        "size_change": "change assessment pending",
        "urgency_timeframe": "as scheduled",
        "pneumonia_type": "community-acquired",
        "additional_treatment_notes": "",
        "additional_comparison_notes": "",
        "new_lesions": "none identified",
        "resolved_lesions": "none noted",
        "detailed_findings": "detailed assessment pending",
        "macular_findings": "macular assessment pending",
        "additional_lab_interpretation": "",
        
        # Flags
        "is_emergency": False,
        "is_admitted": False,
        "is_pregnant": False,
        "is_pediatric": False,
        "is_geriatric": False
    }


def safe_get_context(context: Dict, key: str, default: str = "") -> str:
    """Safely get context value with fallback to default"""
    if context is None:
        return default
    value = context.get(key)
    if value is None or value == "":
        return default
    return str(value)


# ============================================
# COMPREHENSIVE QUESTION DATABASE
# ============================================

QUESTION_DATABASE = {
    "compare": {
        "keywords": ["compare", "previous", "last", "before", "prior", "change", "changed", 
                    "difference", "different", "earlier", "old", "baseline", "progression",
                    "worse", "better", "improved", "worsened", "same"],
        "requires": ["has_previous_scans"],
        "no_data_response": "I don't have any previous scans on record for this patient. "
                           "This appears to be the first imaging study in our system. "
                           "Would you like me to explain the current findings instead?"
    },
    "explain": {
        "keywords": ["explain", "why", "what is", "what does", "meaning", "means", 
                    "understand", "tell me", "describe", "definition", "cause",
                    "how", "reason", "indicate", "shows", "showing", "see"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I don't have a diagnosis to explain yet. "
                           "Please upload a medical image first so I can analyze it and provide an explanation."
    },
    "treatment": {
        "keywords": ["treatment", "treat", "therapy", "medication", "medicine", "drug",
                    "manage", "management", "cure", "heal", "fix", "prescription",
                    "dose", "dosage", "take", "give", "administer", "remedy"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I cannot recommend treatment without a confirmed diagnosis. "
                           "Please complete the diagnostic workup first."
    },
    "severity": {
        "keywords": ["severity", "serious", "severe", "bad", "dangerous", "critical",
                    "mild", "moderate", "grade", "stage", "level", "extent",
                    "how bad", "worry", "worried", "concern", "alarming"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I cannot assess severity without first completing the diagnosis."
    },
    "prognosis": {
        "keywords": ["prognosis", "outcome", "survive", "survival", "recover", "recovery",
                    "future", "expect", "expectation", "live", "life", "chance",
                    "odds", "hope", "hopeful", "long term", "outlook"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I cannot provide a prognosis without a confirmed diagnosis."
    },
    "next_step": {
        "keywords": ["next", "then", "after", "follow", "followup", "follow-up",
                    "what now", "what do", "should", "recommend", "suggest",
                    "action", "plan", "step", "proceed", "continue"],
        "requires": ["current_diagnosis"],
        "no_data_response": "To recommend next steps, I first need to complete the diagnosis."
    },
    "emergency": {
        "keywords": ["emergency", "urgent", "immediately", "now", "critical", "danger",
                    "911", "ambulance", "hospital", "ER", "help", "dying",
                    "life threatening", "serious", "acute", "sudden"],
        "requires": [],
        "no_data_response": None
    },
    "differential": {
        "keywords": ["differential", "other", "else", "could be", "maybe", "possibly",
                    "alternative", "rule out", "exclude", "instead", "or",
                    "might be", "what else", "consider", "possibility"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I need to see the imaging first to provide differential diagnoses."
    },
    "labs": {
        "keywords": ["lab", "laboratory", "blood", "test", "results", "values",
                    "CBC", "chemistry", "panel", "marker", "level", "count"],
        "requires": ["has_lab_results"],
        "no_data_response": "I don't have any laboratory results on file for this patient. "
                           "Would you like me to recommend which lab tests should be ordered?"
    },
    "medication": {
        "keywords": ["medication", "medicine", "drug", "pill", "prescription", "dose",
                    "taking", "current", "allergy", "allergies", "interaction"],
        "requires": ["has_treatment_history"],
        "no_data_response": "I don't have the patient's current medication list on file."
    },
    "vitals": {
        "keywords": ["vital", "vitals", "blood pressure", "heart rate", "pulse",
                    "temperature", "oxygen", "saturation", "respiratory"],
        "requires": ["has_vitals"],
        "no_data_response": "I don't have the patient's vital signs recorded."
    },
    "history": {
        "keywords": ["history", "past", "previous", "before", "earlier", "chronic",
                    "condition", "disease", "surgery", "operation", "family"],
        "requires": ["has_medical_history"],
        "no_data_response": "I don't have the patient's medical history on record."
    },
    "cause": {
        "keywords": ["cause", "caused", "why", "reason", "how did", "origin",
                    "source", "trigger", "factor", "risk", "lead to"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I need to first identify the condition before explaining its cause."
    },
    "symptoms": {
        "keywords": ["symptom", "symptoms", "feel", "feeling", "pain", "ache",
                    "hurt", "discomfort", "sign", "signs", "experience"],
        "requires": [],
        "no_data_response": None
    },
    "lifestyle": {
        "keywords": ["lifestyle", "diet", "exercise", "food", "eat", "drink",
                    "alcohol", "smoke", "smoking", "sleep", "stress", "work"],
        "requires": ["current_diagnosis"],
        "no_data_response": "I need a diagnosis first to provide specific lifestyle recommendations."
    },
    "repeat": {
        "keywords": ["repeat", "again", "what", "say", "sorry", "didn't hear",
                    "pardon", "come again", "one more time", "clarify"],
        "requires": [],
        "no_data_response": None
    },
    "cost": {
        "keywords": ["cost", "price", "expensive", "afford", "insurance", "coverage",
                    "pay", "payment", "bill", "billing", "money"],
        "requires": [],
        "no_data_response": None
    },
    "second_opinion": {
        "keywords": ["second opinion", "another doctor", "specialist", "expert",
                    "confirm", "verify", "sure", "certain", "double check"],
        "requires": [],
        "no_data_response": None
    },
    "general": {
        "keywords": ["hello", "hi", "hey", "thanks", "thank you", "bye",
                    "goodbye", "help", "assist", "can you", "please"],
        "requires": [],
        "no_data_response": None
    }
}


# ============================================
# DISEASE-SPECIFIC RESPONSE TEMPLATES
# ============================================

DISEASE_RESPONSES = {
    "Pneumonia": {
        "compare": {
            "has_data": "Comparing to your previous scan from {last_scan_date}. "
                       "The previous study showed {last_scan_findings}. "
                       "Current imaging shows {current_findings}. "
                       "Overall assessment: {comparison_result}.",
            "no_data": "I don't have any previous scans on record for comparison. "
                      "This appears to be the first chest imaging in our system. "
                      "Current findings show {current_findings}. "
                      "Would you like me to explain what I see in this scan?"
        },
        "explain": {
            "basic": "You have pneumonia, which is an infection in your lungs. "
                    "The white areas on the scan show where your lungs are filled with fluid and infection. "
                    "This is affecting your {affected_region}. "
                    "The good news is that pneumonia is treatable with antibiotics.",
            "detailed": "The imaging shows consolidation in the {affected_region}, "
                       "which indicates pneumonia. Pneumonia occurs when bacteria, viruses, or other pathogens "
                       "infect the air sacs in your lungs, causing them to fill with fluid and pus."
        },
        "treatment": {
            "basic": "The main treatment is antibiotics. You'll likely be prescribed Amoxicillin "
                    "500 milligrams, taken 3 times daily for 7 to 10 days. "
                    "Make sure to complete the full course even if you feel better. "
                    "Also important: rest, drink plenty of fluids, and use fever reducers if needed.",
            "detailed": "Treatment protocol for {pneumonia_type} pneumonia: "
                       "First-line: Amoxicillin 500mg three times daily for 7-10 days. "
                       "Alternative if penicillin allergic: Azithromycin 500mg day 1, then 250mg days 2-5. "
                       "Supportive care: Oxygen therapy if SpO2 below 94 percent, IV fluids if dehydrated."
        },
        "severity": {
            "mild": "This appears to be mild pneumonia. The infection is limited to a small area. "
                   "You should recover well with oral antibiotics at home.",
            "moderate": "This is moderate pneumonia. The infection covers a significant portion of your lung. "
                       "You may need closer monitoring. Some patients need hospital admission.",
            "severe": "This is severe pneumonia requiring immediate attention. "
                     "The infection is extensive. Hospital admission is strongly recommended."
        },
        "prognosis": "With appropriate treatment, most pneumonia cases resolve within 2 to 3 weeks. "
                    "You should start feeling better within 48 to 72 hours of starting antibiotics. "
                    "Most people recover completely with no long-term effects.",
        "next_step": "Here's what we need to do next: "
                    "First, start the prescribed antibiotics today. "
                    "Second, get a follow-up chest X-ray in 7 to 10 days to confirm improvement. "
                    "Third, return for clinical review in 3 days.",
        "emergency": "For pneumonia, seek emergency care immediately if you experience: "
                    "Severe difficulty breathing or shortness of breath at rest, "
                    "Oxygen saturation below 92 percent, "
                    "Confusion or altered mental status, "
                    "Fever above 104 degrees Fahrenheit that doesn't respond to medication, "
                    "Coughing up blood, or "
                    "Bluish color of lips or fingernails.",
        "differential": "While pneumonia is the most likely diagnosis, "
                       "other conditions to consider include: "
                       "Tuberculosis, especially if you have risk factors, "
                       "Lung cancer, particularly in smokers, "
                       "Pulmonary edema from heart failure, and "
                       "Pulmonary embolism with infarction.",
        "labs": {
            "has_data": "Looking at your lab results from {lab_date}: "
                       "White blood cell count is {wbc}, which is {wbc_interpretation}. "
                       "CRP is {crp}, indicating {crp_interpretation}.",
            "no_data": "I don't have lab results for this patient. "
                      "For pneumonia, I recommend ordering: "
                      "Complete blood count, C-reactive protein, and blood cultures if septic."
        },
        "cause": "Pneumonia is usually caused by bacteria, viruses, or sometimes fungi. "
                "Common bacterial causes include Streptococcus pneumoniae. "
                "Risk factors include: smoking, chronic lung disease, and weakened immune system.",
        "symptoms": "With pneumonia, you may experience: "
                   "Cough with yellow, green, or bloody mucus, "
                   "Fever and chills, "
                   "Shortness of breath, "
                   "Chest pain that worsens with breathing, "
                   "Fatigue and weakness.",
        "lifestyle": "While recovering from pneumonia: "
                    "Get plenty of rest. "
                    "Drink lots of fluids to help loosen mucus. "
                    "Avoid smoking and secondhand smoke. "
                    "Gradually return to normal activities as you feel better."
    },
    
    "Brain Tumor": {
        "compare": {
            "has_data": "Comparing to the prior MRI from {last_scan_date}. "
                       "Previous study showed {last_scan_findings}. "
                       "The lesion now measures {current_size}, previously was {previous_size}. "
                       "This represents a {size_change} in size.",
            "no_data": "I don't have any previous brain imaging for comparison. "
                      "Current findings show an abnormality in the {location}. "
                      "Baseline measurements have been recorded for future comparison."
        },
        "explain": {
            "basic": "The MRI shows an abnormal growth in your brain called a tumor. "
                    "It's located in the {location}. "
                    "We need additional tests to determine the exact type and best treatment.",
            "detailed": "The imaging reveals an abnormality in the {location}. "
                       "We need to assess the enhancement pattern, surrounding edema, "
                       "and mass effect on adjacent structures."
        },
        "treatment": {
            "basic": "Treatment typically involves a combination of surgery, radiation, and chemotherapy. "
                    "The first step is usually surgery to remove as much tumor as safely possible. "
                    "A team of specialists will work together on your treatment plan.",
            "detailed": "Recommended treatment will depend on final pathology. "
                       "Options include: neurosurgical resection, radiation therapy, chemotherapy, "
                       "and targeted therapy if applicable."
        },
        "severity": {
            "mild": "Based on imaging, this appears to be a lower-grade lesion. "
                   "These typically grow more slowly and have better outcomes. "
                   "However, we need tissue diagnosis to confirm.",
            "moderate": "The imaging features are concerning and require further evaluation. "
                       "A multidisciplinary team approach is essential.",
            "severe": "This is a critical situation. The tumor is causing significant effects. "
                     "Urgent neurosurgical consultation is required."
        },
        "prognosis": "Prognosis for brain tumors varies significantly based on type, grade, and location. "
                    "Modern treatments have significantly improved outcomes. "
                    "Your neurosurgeon will give you more specific information after the biopsy.",
        "next_step": "Here are the immediate next steps: "
                    "1. Urgent neurosurgery referral within 24 to 48 hours. "
                    "2. Additional imaging if needed. "
                    "3. Surgical planning for biopsy or resection. "
                    "4. Multidisciplinary tumor board discussion.",
        "emergency": "For brain tumors, seek emergency care immediately if you experience: "
                    "Sudden severe headache, the worst of your life, "
                    "Sudden vision changes or loss of vision, "
                    "Sudden weakness or numbness on one side, "
                    "Seizures, especially if new, "
                    "Sudden confusion or difficulty speaking, or "
                    "Loss of consciousness.",
        "differential": "The differential diagnosis includes: "
                       "Primary brain tumors such as glioma or meningioma, "
                       "Metastatic disease from other cancers, "
                       "Brain abscess if there's infection history, and "
                       "Demyelinating disease. "
                       "Tissue diagnosis is essential for confirmation.",
        "cause": "The exact cause of most brain tumors is unknown. "
                "Known risk factors include: "
                "Previous radiation exposure to the head, "
                "Certain genetic syndromes, and "
                "Family history of brain tumors.",
        "symptoms": "Brain tumor symptoms include: "
                   "Persistent or worsening headaches, "
                   "Seizures or convulsions, "
                   "Vision or hearing problems, "
                   "Balance difficulties, "
                   "Personality or behavior changes, "
                   "Memory problems, and "
                   "Nausea and vomiting.",
        "lifestyle": "While managing a brain tumor: "
                    "Avoid driving until cleared by your doctor. "
                    "Get adequate rest and sleep. "
                    "Stay hydrated and maintain good nutrition. "
                    "Avoid alcohol as it can interact with medications."
    },
    
    "Diabetic Retinopathy": {
        "compare": {
            "has_data": "Comparing fundus images from {last_scan_date}. "
                       "Previous findings: {last_scan_findings}. "
                       "Current examination shows: {current_findings}. "
                       "Change assessment: {comparison_result}.",
            "no_data": "I don't have previous retinal images for comparison. "
                      "Current findings show {current_findings}. "
                      "Baseline documentation completed for future monitoring."
        },
        "explain": {
            "basic": "You have diabetic retinopathy, which means diabetes is affecting your eyes. "
                    "The small blood vessels in your retina are damaged from high blood sugar. "
                    "This can cause vision problems if not treated.",
            "detailed": "The fundus examination reveals diabetic retinopathy. "
                       "Key findings include microaneurysms, hemorrhages, and possible exudates. "
                       "These changes result from chronic hyperglycemia damaging retinal vessels."
        },
        "treatment": {
            "basic": "Treatment depends on the severity. "
                    "Most importantly, control your blood sugar to prevent progression. "
                    "You may need eye injections or laser treatment. "
                    "Regular eye check-ups every 3 to 6 months are essential.",
            "detailed": "Treatment recommendations: "
                       "1. Glycemic control: Target HbA1c below 7 percent. "
                       "2. Blood pressure control: Target below 130 over 80. "
                       "3. Anti-VEGF injections for macular edema. "
                       "4. Laser photocoagulation for proliferative disease."
        },
        "severity": {
            "mild": "This is mild non-proliferative diabetic retinopathy. "
                   "There are a few microaneurysms but no significant vision threat currently. "
                   "Focus on excellent diabetes control.",
            "moderate": "This is moderate non-proliferative diabetic retinopathy. "
                       "There are multiple hemorrhages and microaneurysms. "
                       "Eye exams every 6 months recommended.",
            "severe": "This is severe or proliferative diabetic retinopathy. "
                     "There is significant risk of vision loss. "
                     "Urgent ophthalmology treatment is needed."
        },
        "prognosis": "With proper treatment and diabetes control, most patients can preserve their vision. "
                    "Early detection and treatment are key. "
                    "Modern treatments are very effective at preventing blindness.",
        "next_step": "Immediate next steps: "
                    "1. Schedule ophthalmology appointment within {urgency_timeframe}. "
                    "2. Get OCT scan to evaluate macular thickness. "
                    "3. Optimize diabetes management with your primary doctor. "
                    "4. Check HbA1c if not done recently.",
        "emergency": "Seek immediate eye care if you experience: "
                    "Sudden vision loss or blackout of vision, "
                    "Sudden increase in floaters, "
                    "Flashes of light, "
                    "A curtain or shadow over part of your vision, or "
                    "Sudden eye pain.",
        "cause": "Diabetic retinopathy is caused by damage to blood vessels from high blood sugar. "
                "Risk factors include: duration of diabetes, poor blood sugar control, "
                "high blood pressure, and high cholesterol.",
        "symptoms": "Diabetic retinopathy symptoms include: "
                   "Blurry or fluctuating vision, "
                   "Dark spots or floaters, "
                   "Difficulty seeing at night, "
                   "Colors appearing faded, and "
                   "Vision loss. "
                   "Note: Early stages often have no symptoms.",
        "lifestyle": "To protect your eyes: "
                    "Maintain strict blood sugar control, this is the most important factor. "
                    "Control blood pressure and cholesterol. "
                    "Quit smoking if you smoke. "
                    "Get regular eye exams as recommended."
    },
    
    "Tuberculosis": {
        "compare": {
            "has_data": "Comparing chest X-rays from {last_scan_date}. "
                       "Previous imaging showed {last_scan_findings}. "
                       "Current findings: {current_findings}. "
                       "Disease extent comparison: {comparison_result}.",
            "no_data": "No previous chest imaging is available for comparison. "
                      "Current imaging shows {current_findings}. "
                      "Baseline recorded for monitoring treatment response."
        },
        "explain": {
            "basic": "The imaging shows signs of tuberculosis, or TB. "
                    "TB is a bacterial infection that primarily affects the lungs. "
                    "TB is contagious but treatable with the right antibiotics.",
            "detailed": "Imaging findings are consistent with tuberculosis. "
                       "Upper lobe predominance is typical for reactivation TB. "
                       "Cavitation, if present, indicates high bacterial burden."
        },
        "treatment": {
            "basic": "TB is treated with a combination of 4 antibiotics for 6 months. "
                    "The medications are Rifampicin, Isoniazid, Pyrazinamide, and Ethambutol. "
                    "It's critical to take every dose. Missing doses can cause drug resistance.",
            "detailed": "Standard TB treatment, known as RIPE regimen: "
                       "Intensive phase of 2 months: Rifampicin, Isoniazid, Pyrazinamide, Ethambutol daily. "
                       "Continuation phase of 4 months: Rifampicin and Isoniazid daily. "
                       "Directly Observed Therapy is recommended."
        },
        "severity": {
            "mild": "This appears to be minimal or early TB. "
                   "Standard treatment should be very effective. "
                   "Prognosis is excellent with proper treatment.",
            "moderate": "This is moderate TB with significant lung involvement. "
                       "Standard treatment is effective but monitoring is important.",
            "severe": "This is advanced or extensive TB. "
                     "May require hospitalization initially. "
                     "Close monitoring for drug toxicity is essential."
        },
        "prognosis": "With proper treatment, TB cure rate is 85 to 90 percent. "
                    "Most patients become non-infectious within 2 weeks of starting treatment. "
                    "Complete treatment takes 6 months minimum.",
        "next_step": "Immediate action plan for TB: "
                    "1. Infection control: respiratory isolation until confirmed non-infectious. "
                    "2. Diagnostic workup: sputum for AFB smear times 3, culture, Gene Xpert. "
                    "3. HIV testing is mandatory for all TB patients. "
                    "4. Contact tracing for close contacts.",
        "emergency": "Seek immediate care if you develop: "
                    "Coughing up large amounts of blood, "
                    "Severe difficulty breathing, "
                    "High fever that doesn't respond to medication, "
                    "Severe chest pain, or "
                    "Signs of medication toxicity like jaundice.",
        "cause": "TB is caused by a bacterium called Mycobacterium tuberculosis. "
                "It spreads through the air when an infected person coughs or sneezes. "
                "Risk factors include: close contact with TB patients, "
                "weakened immune system, and crowded living conditions.",
        "symptoms": "TB symptoms include: "
                   "Persistent cough lasting more than 3 weeks, "
                   "Coughing up blood, "
                   "Night sweats, "
                   "Unexplained weight loss, "
                   "Fever, especially in the evening, and "
                   "Fatigue and weakness.",
        "lifestyle": "While being treated for TB: "
                    "Take all medications exactly as prescribed, every day. "
                    "Cover your mouth when coughing or sneezing. "
                    "Stay home until your doctor says you're no longer infectious. "
                    "Avoid alcohol as it can harm your liver with TB medications."
    },
    
    "Skin Cancer": {
        "compare": {
            "has_data": "Comparing lesion images from {last_scan_date}. "
                       "Previous measurements: {last_scan_findings}. "
                       "Current size: {current_size}. "
                       "Size change: {size_change}.",
            "no_data": "No previous images of this lesion are available. "
                      "Current lesion assessment shows: {current_findings}. "
                      "Baseline measurements recorded for the {location}."
        },
        "explain": {
            "basic": "The lesion shows features concerning for skin cancer. "
                    "The irregular shape, uneven color, and borders are warning signs. "
                    "We need to do a biopsy to examine the cells. "
                    "Skin cancer caught early is very treatable.",
            "detailed": "Analysis reveals concerning features using ABCDE criteria: "
                       "Asymmetry, Border irregularity, Color variation, "
                       "Diameter, and Evolution or change over time."
        },
        "treatment": {
            "basic": "Treatment depends on the type and stage of skin cancer. "
                    "The first step is a biopsy to get an exact diagnosis. "
                    "Most skin cancers are treated with surgical removal. "
                    "Follow-up skin checks are important.",
            "detailed": "Treatment approach: "
                       "1. Diagnostic biopsy is recommended first. "
                       "2. If melanoma confirmed: wide local excision with appropriate margins. "
                       "3. Sentinel lymph node biopsy if thickness exceeds 0.8 millimeters. "
                       "4. For advanced disease: immunotherapy or targeted therapy."
        },
        "severity": {
            "mild": "This lesion has features that should be monitored. "
                   "Monitoring for changes is recommended.",
            "moderate": "This lesion has moderately concerning features. "
                       "Biopsy is recommended to determine the exact diagnosis.",
            "severe": "This lesion has highly suspicious features for melanoma. "
                     "Urgent biopsy is essential."
        },
        "prognosis": "Prognosis for skin cancer depends on the type and stage. "
                    "Early-stage melanoma has a 5-year survival rate over 90 percent. "
                    "The key is early detection and complete removal.",
        "next_step": "Here are the next steps: "
                    "1. Schedule skin biopsy within 1 to 2 weeks. "
                    "2. Once pathology returns, plan definitive treatment. "
                    "3. Full body skin examination for other suspicious lesions. "
                    "4. Sun protection counseling.",
        "emergency": "Seek immediate care if you notice: "
                    "Rapid growth of the lesion, "
                    "Bleeding that won't stop, "
                    "Sudden color changes, especially darkening, or "
                    "New lumps around the lesion or in lymph node areas.",
        "cause": "Skin cancer is primarily caused by ultraviolet radiation from: "
                "Sun exposure, especially sunburns in childhood, and "
                "Tanning beds. "
                "Risk factors include: fair skin, many moles, and family history.",
        "symptoms": "Skin cancer warning signs include: "
                   "New growth or sore that doesn't heal, "
                   "Change in existing mole: size, shape, or color, "
                   "Asymmetry, irregular borders, multiple colors, and "
                   "Diameter larger than a pencil eraser.",
        "lifestyle": "To prevent and manage skin cancer: "
                    "Use broad-spectrum sunscreen SPF 30 or higher daily. "
                    "Wear protective clothing and hats outdoors. "
                    "Avoid sun exposure during peak hours. "
                    "Never use tanning beds. "
                    "Perform monthly self-skin exams."
    }
}


# ============================================
# GENERAL RESPONSES
# ============================================

GENERAL_RESPONSES = {
    "greeting": {
        "hello": "Hello! I'm your AI diagnosis assistant. I'm here to help explain your medical findings. What would you like to know?",
        "hi": "Hi there! How can I help you understand your diagnosis today?",
        "hey": "Hey! I'm ready to answer your questions. What would you like to know?"
    },
    "help": {
        "basic": "I can help you with: "
                "Explaining your diagnosis, "
                "Comparing with previous scans if available, "
                "Discussing treatment options, "
                "Explaining what to expect next, and "
                "Answering questions about severity and prognosis."
    },
    "thanks": {
        "basic": "You're welcome! Is there anything else you'd like to know about your diagnosis?"
    },
    "goodbye": {
        "basic": "Goodbye! Take care and follow up with your healthcare team if you have more questions."
    },
    "unclear": {
        "no_question": "I didn't quite catch that. Could you please rephrase your question?",
        "not_understood": "I'm not sure I understand. Try asking about the diagnosis, treatment, or next steps."
    },
    "no_diagnosis": {
        "basic": "I don't have a diagnosis to discuss yet. "
                "Please upload a medical image first so I can analyze it."
    },
    "cost": {
        "basic": "For specific cost information, please contact the billing department. "
                "Costs vary based on your insurance coverage and specific procedures needed."
    },
    "second_opinion": {
        "basic": "Getting a second opinion is always your right and often a good idea. "
                "We can arrange for your images and reports to be sent to another specialist."
    },
    "repeat": {
        "basic": "I'll be happy to repeat that. What would you like me to clarify?"
    }
}


# ============================================
# AUDIO GENERATION
# ============================================

@st.cache_data(ttl=3600)
def generate_cached_audio(text: str, engine: str = 'gtts') -> bytes:
    """Generate and cache audio for instant playback"""
    if not text or len(text.strip()) == 0:
        return None
        
    if engine == 'gtts' and GTTS_AVAILABLE:
        try:
            tts = gTTS(text=text, lang='en', slow=False)
            audio_buffer = BytesIO()
            tts.write_to_fp(audio_buffer)
            audio_buffer.seek(0)
            return audio_buffer.read()
        except Exception as e:
            return None
    elif engine == 'pyttsx3' and PYTTSX3_AVAILABLE:
        try:
            engine_obj = pyttsx3.init()
            engine_obj.setProperty('rate', 160)
            temp_file = f"temp_audio_{hashlib.md5(text.encode()).hexdigest()[:8]}.mp3"
            engine_obj.save_to_file(text, temp_file)
            engine_obj.runAndWait()
            if os.path.exists(temp_file):
                with open(temp_file, 'rb') as f:
                    audio_bytes = f.read()
                os.remove(temp_file)
                return audio_bytes
            return None
        except Exception as e:
            return None
    return None


def create_autoplay_audio(audio_bytes: bytes) -> str:
    """Create auto-playing HTML audio element"""
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        return f'''
        <audio autoplay>
            <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
        </audio>
        '''
    return ""


# ============================================
# VOICE ASSISTANT CLASS
# ============================================

class VoiceAssistant:
    """Comprehensive voice assistant with condition-aware responses"""
    
    def __init__(self, patient_context: Dict, disease: str, confidence: float):
        self.context = patient_context if patient_context else get_default_patient_context()
        self.disease = disease
        self.confidence = confidence
        self.last_response = ""
        self.last_intent = ""
    
    def recognize_intent(self, text: str) -> Tuple[str, str]:
        """Recognize intent and complexity from user input"""
        if not text:
            return "unclear", "basic"
            
        text_lower = text.lower().strip()
        
        # Check for greetings
        if any(word in text_lower for word in ["hello", "hi", "hey"]):
            return "greeting", "basic"
        
        # Check for thanks
        if any(word in text_lower for word in ["thank", "thanks"]):
            return "thanks", "basic"
        
        # Check for goodbye
        if any(word in text_lower for word in ["bye", "goodbye", "see you"]):
            return "goodbye", "basic"
        
        # Match against question database
        for intent, data in QUESTION_DATABASE.items():
            if any(keyword in text_lower for keyword in data["keywords"]):
                complexity = self._determine_complexity(text_lower)
                return intent, complexity
        
        return "unclear", "basic"
    
    def _determine_complexity(self, text: str) -> str:
        """Determine if question is basic, medium, or advanced"""
        advanced_keywords = ["molecular", "staging", "TNM", "biomarker", "protocol", "statistics"]
        if any(kw in text for kw in advanced_keywords):
            return "advanced"
        
        medium_keywords = ["specific", "detail", "how long", "percentage", "rate", "option"]
        if any(kw in text for kw in medium_keywords):
            return "medium"
        
        return "basic"
    
    def check_data_availability(self, intent: str) -> Tuple[bool, str]:
        """Check if required data is available for the intent"""
        if intent not in QUESTION_DATABASE:
            return True, None
        
        requirements = QUESTION_DATABASE[intent].get("requires", [])
        
        for req in requirements:
            if req == "current_diagnosis":
                if not self.disease:
                    return False, QUESTION_DATABASE[intent].get("no_data_response", 
                        "I need a diagnosis first to answer this question.")
            elif req == "has_previous_scans":
                if not self.context.get("has_previous_scans", False):
                    return False, QUESTION_DATABASE[intent].get("no_data_response",
                        "No previous scans available for comparison.")
            elif req == "has_lab_results":
                if not self.context.get("has_lab_results", False):
                    return False, QUESTION_DATABASE[intent].get("no_data_response",
                        "No lab results on file.")
            elif req == "has_vitals":
                if not self.context.get("has_vitals", False):
                    return False, QUESTION_DATABASE[intent].get("no_data_response",
                        "Vital signs not recorded.")
            elif req == "has_treatment_history":
                if not self.context.get("has_treatment_history", False):
                    return False, QUESTION_DATABASE[intent].get("no_data_response",
                        "No treatment history available.")
            elif req == "has_medical_history":
                if not self.context.get("has_medical_history", False):
                    return False, QUESTION_DATABASE[intent].get("no_data_response",
                        "Medical history not on file.")
        
        return True, None
    
    def generate_response(self, text: str) -> str:
        """Generate appropriate response based on input"""
        
        if not self.disease:
            return GENERAL_RESPONSES["no_diagnosis"]["basic"]
        
        intent, complexity = self.recognize_intent(text)
        self.last_intent = intent
        
        # Handle general responses
        if intent in ["greeting", "thanks", "goodbye", "unclear"]:
            response = self._get_general_response(intent)
            self.last_response = response
            return response
        
        # Check data availability
        data_available, no_data_response = self.check_data_availability(intent)
        
        if not data_available:
            self.last_response = no_data_response
            return no_data_response
        
        # Get disease-specific response
        response = self._get_disease_response(intent, complexity)
        self.last_response = response
        return response
    
    def _get_general_response(self, intent: str) -> str:
        """Get general response"""
        if intent in GENERAL_RESPONSES:
            responses = GENERAL_RESPONSES[intent]
            if isinstance(responses, dict):
                return responses.get("basic", list(responses.values())[0])
            return responses
        return GENERAL_RESPONSES["unclear"]["not_understood"]
    
    def _get_disease_response(self, intent: str, complexity: str) -> str:
        """Get disease-specific response"""
        if self.disease not in DISEASE_RESPONSES:
            return f"I don't have detailed information for {self.disease}. Please consult with your healthcare provider."
        
        disease_data = DISEASE_RESPONSES[self.disease]
        
        if intent not in disease_data:
            return f"I don't have specific {intent} information for {self.disease}. Can I help with something else?"
        
        response_data = disease_data[intent]
        
        # Handle different response structures
        if isinstance(response_data, dict):
            if "has_data" in response_data:
                if self.context.get("has_previous_scans", False):
                    template = response_data["has_data"]
                else:
                    template = response_data["no_data"]
            elif complexity in response_data:
                template = response_data[complexity]
            elif "basic" in response_data:
                template = response_data["basic"]
            else:
                template = list(response_data.values())[0]
        else:
            template = response_data
        
        return self._fill_template(template)
    
    def _fill_template(self, template: str) -> str:
        """Fill in template with context data"""
        fill_context = {
            "disease": self.disease or "condition",
            "confidence": f"{self.confidence:.1f}",
            "last_scan_date": safe_get_context(self.context, "last_scan_date", "previous visit"),
            "last_scan_findings": safe_get_context(self.context, "last_scan_findings", "previous findings"),
            "current_findings": safe_get_context(self.context, "current_findings", "current pathology"),
            "affected_region": safe_get_context(self.context, "affected_region", "affected area"),
            "severity": safe_get_context(self.context, "severity", "moderate"),
            "location": safe_get_context(self.context, "location", "identified region"),
            "size": safe_get_context(self.context, "size", "measured dimensions"),
            "current_size": safe_get_context(self.context, "current_size", "current measurements"),
            "previous_size": safe_get_context(self.context, "previous_size", "previous measurements"),
            "size_change": safe_get_context(self.context, "size_change", "change noted"),
            "comparison_result": safe_get_context(self.context, "comparison_result", "findings compared"),
            "urgency_timeframe": safe_get_context(self.context, "urgency_timeframe", "as soon as possible"),
            "pneumonia_type": safe_get_context(self.context, "pneumonia_type", "community-acquired"),
            "lab_date": safe_get_context(self.context, "lab_date", "recent"),
            "wbc": safe_get_context(self.context, "wbc", "value pending"),
            "wbc_interpretation": safe_get_context(self.context, "wbc_interpretation", "awaiting interpretation"),
            "crp": safe_get_context(self.context, "crp", "value pending"),
            "crp_interpretation": safe_get_context(self.context, "crp_interpretation", "awaiting interpretation")
        }
        
        try:
            return template.format(**fill_context)
        except KeyError:
            return template


# ============================================
# MAIN UI FUNCTION
# ============================================

def show_voice_diagnosis_assistant(disease: str = None, confidence: float = 0.0):
    """Main voice assistant UI with instant audio responses"""
    
    st.markdown("### 🎤 Voice-Based Diagnosis Assistant")
    
    # Initialize session state with proper defaults
    if 'voice_patient_context' not in st.session_state:
        st.session_state.voice_patient_context = get_default_patient_context()
    if 'voice_history' not in st.session_state:
        st.session_state.voice_history = []
    if 'voice_last_audio' not in st.session_state:
        st.session_state.voice_last_audio = None
    if 'voice_auto_play' not in st.session_state:
        st.session_state.voice_auto_play = True
    if 'voice_input_text' not in st.session_state:
        st.session_state.voice_input_text = ""
    
    # Determine available TTS engine
    available_engines = []
    if GTTS_AVAILABLE:
        available_engines.append("gtts")
    if PYTTSX3_AVAILABLE:
        available_engines.append("pyttsx3")
    if not available_engines:
        available_engines = ["none"]
    
    if 'voice_tts_engine' not in st.session_state:
        st.session_state.voice_tts_engine = available_engines[0]
    elif st.session_state.voice_tts_engine not in available_engines:
        st.session_state.voice_tts_engine = available_engines[0]
    
    # Update context with current diagnosis
    if disease:
        st.session_state.voice_patient_context["current_diagnosis"] = disease
        st.session_state.voice_patient_context["confidence"] = confidence
    
    # TTS Status Header
    col1, col2, col3 = st.columns([2, 2, 1])
    with col1:
        tts_status = "✅ Ready" if (GTTS_AVAILABLE or PYTTSX3_AVAILABLE) else "❌ Install gtts: pip install gtts"
        st.caption(f"Text-to-Speech: {tts_status}")
    with col2:
        st.caption(f"Disease: {disease if disease else 'Not diagnosed'}")
    with col3:
        st.session_state.voice_auto_play = st.checkbox(
            "Auto-play", 
            value=st.session_state.voice_auto_play,
            key=get_unique_key("auto_play_cb")
        )
    
    st.markdown("---")
    
    # Context Settings Expander
    with st.expander("📋 Patient Data Context (Click to configure available data)", expanded=False):
        st.write("**Configure what patient data is available:**")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.session_state.voice_patient_context["has_previous_scans"] = st.checkbox(
                "Has Previous Scans", 
                value=bool(st.session_state.voice_patient_context.get("has_previous_scans", False)),
                key=get_unique_key("chk_prev_scans")
            )
            if st.session_state.voice_patient_context["has_previous_scans"]:
                st.session_state.voice_patient_context["last_scan_date"] = st.text_input(
                    "Last Scan Date", 
                    value=safe_get_context(st.session_state.voice_patient_context, "last_scan_date", "2024-01-15"),
                    key=get_unique_key("txt_last_scan_date")
                )
                st.session_state.voice_patient_context["last_scan_findings"] = st.text_area(
                    "Previous Findings",
                    value=safe_get_context(st.session_state.voice_patient_context, "last_scan_findings", "Minimal findings noted"),
                    height=68,
                    key=get_unique_key("txt_last_scan_findings")
                )
        
        with col2:
            st.session_state.voice_patient_context["has_lab_results"] = st.checkbox(
                "Has Lab Results",
                value=bool(st.session_state.voice_patient_context.get("has_lab_results", False)),
                key=get_unique_key("chk_lab_results")
            )
            if st.session_state.voice_patient_context["has_lab_results"]:
                st.session_state.voice_patient_context["lab_date"] = st.text_input(
                    "Lab Date",
                    value=safe_get_context(st.session_state.voice_patient_context, "lab_date", "2024-12-01"),
                    key=get_unique_key("txt_lab_date")
                )
                st.session_state.voice_patient_context["wbc"] = st.text_input(
                    "WBC Count",
                    value=safe_get_context(st.session_state.voice_patient_context, "wbc", "12,500"),
                    key=get_unique_key("txt_wbc")
                )
        
        with col3:
            st.session_state.voice_patient_context["has_vitals"] = st.checkbox(
                "Has Vitals",
                value=bool(st.session_state.voice_patient_context.get("has_vitals", False)),
                key=get_unique_key("chk_vitals")
            )
            st.session_state.voice_patient_context["has_treatment_history"] = st.checkbox(
                "Has Treatment History",
                value=bool(st.session_state.voice_patient_context.get("has_treatment_history", False)),
                key=get_unique_key("chk_treatment")
            )
            st.session_state.voice_patient_context["has_medical_history"] = st.checkbox(
                "Has Medical History",
                value=bool(st.session_state.voice_patient_context.get("has_medical_history", False)),
                key=get_unique_key("chk_medical")
            )
        
        # Current findings
        st.write("**Current Scan Context:**")
        col1, col2 = st.columns(2)
        with col1:
            st.session_state.voice_patient_context["current_findings"] = st.text_area(
                "Current Findings",
                value=safe_get_context(st.session_state.voice_patient_context, "current_findings", "Consolidation in right lower lobe"),
                height=68,
                key=get_unique_key("txt_current_findings")
            )
            st.session_state.voice_patient_context["affected_region"] = st.text_input(
                "Affected Region",
                value=safe_get_context(st.session_state.voice_patient_context, "affected_region", "right lower lobe"),
                key=get_unique_key("txt_affected_region")
            )
        with col2:
            # Fix for the severity field - validate before using
            current_severity = st.session_state.voice_patient_context.get("severity")
            severity_options = ["mild", "moderate", "severe"]
            if current_severity not in severity_options:
                current_severity = "moderate"
            
            st.session_state.voice_patient_context["severity"] = st.selectbox(
                "Severity",
                severity_options,
                index=severity_options.index(current_severity),
                key=get_unique_key("sel_severity")
            )
            
            st.session_state.voice_patient_context["comparison_result"] = st.text_input(
                "Comparison Result",
                value=safe_get_context(st.session_state.voice_patient_context, "comparison_result", "slight progression noted"),
                key=get_unique_key("txt_comparison")
            )
    
    st.markdown("---")
    
    # Voice Input Section
    st.markdown("#### 🎙️ Ask Your Question")
    
    # Quick question buttons - 2 rows
    st.write("**Quick Questions:**")
    
    quick_questions = [
        ("📊 Compare scans", "Compare with my previous scan"),
        ("❓ Explain", "Explain the findings"),
        ("💊 Treatment", "What is the treatment"),
        ("⚠️ Severity", "How serious is this"),
        ("📈 Prognosis", "What is the prognosis"),
        ("➡️ Next steps", "What are the next steps"),
        ("🚨 Emergency", "What are the emergency signs"),
        ("🔬 Differential", "What else could it be")
    ]
    
    # First row of quick questions
    cols_row1 = st.columns(4)
    for i in range(4):
        label, question = quick_questions[i]
        with cols_row1[i]:
            if st.button(label, key=get_unique_key(f"quick_row1_{i}"), use_container_width=True):
                st.session_state.voice_input_text = question
                st.rerun()
    
    # Second row of quick questions
    cols_row2 = st.columns(4)
    for i in range(4, 8):
        label, question = quick_questions[i]
        with cols_row2[i - 4]:
            if st.button(label, key=get_unique_key(f"quick_row2_{i}"), use_container_width=True):
                st.session_state.voice_input_text = question
                st.rerun()
    
    st.write("")
    
    # Text input for questions
    voice_input = st.text_input(
        "Type or speak your question:",
        placeholder="e.g., 'Compare with previous scan', 'What's the treatment?', 'Is this serious?'",
        key=get_unique_key("voice_input_field"),
        value=st.session_state.voice_input_text
    )
    
    # Reset the stored input after it's been used
    if voice_input != st.session_state.voice_input_text:
        st.session_state.voice_input_text = voice_input
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        get_response = st.button(
            "🔊 Get Voice Response", 
            use_container_width=True, 
            type="primary",
            key=get_unique_key("btn_get_response")
        )
    
    with col2:
        if st.button("🗑️ Clear", use_container_width=True, key=get_unique_key("btn_clear")):
            st.session_state.voice_last_audio = None
            st.session_state.voice_input_text = ""
            st.rerun()
    
    # Process and respond
    if get_response and voice_input:
        
        # Initialize assistant
        assistant = VoiceAssistant(
            patient_context=st.session_state.voice_patient_context,
            disease=disease,
            confidence=confidence
        )
        
        # Generate response
        with st.spinner("Generating response..."):
            response_text = assistant.generate_response(voice_input)
        
        st.markdown("---")
        
        # Display response
        st.markdown("#### 🤖 AI Response")
        
        # Response info
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Intent", assistant.last_intent.replace("_", " ").title())
        with col2:
            word_count = len(response_text.split())
            st.metric("Words", word_count)
        with col3:
            duration = max(5, word_count // 3)
            st.metric("Est. Duration", f"~{duration}s")
        
        # Response text
        st.info(response_text)
        
        # Generate audio immediately
        if GTTS_AVAILABLE or PYTTSX3_AVAILABLE:
            with st.spinner("Generating audio..."):
                audio_bytes = generate_cached_audio(response_text, st.session_state.voice_tts_engine)
            
            if audio_bytes:
                st.session_state.voice_last_audio = audio_bytes
                
                # Auto-play audio
                if st.session_state.voice_auto_play:
                    st.markdown(create_autoplay_audio(audio_bytes), unsafe_allow_html=True)
                    st.success("🔊 Playing audio response...")
                
                # Manual play button and controls
                st.markdown("#### 🎧 Audio Controls")
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    audio_base64 = base64.b64encode(audio_bytes).decode()
                    st.markdown(f'''
                    <audio controls style="width: 100%;">
                        <source src="data:audio/mp3;base64,{audio_base64}" type="audio/mp3">
                    </audio>
                    ''', unsafe_allow_html=True)
                
                with col2:
                    st.download_button(
                        "📥 Download",
                        data=audio_bytes,
                        file_name=f"response_{datetime.now().strftime('%H%M%S')}.mp3",
                        mime="audio/mp3",
                        use_container_width=True,
                        key=get_unique_key("btn_download_audio")
                    )
                
                with col3:
                    if st.button("🔄 Replay", use_container_width=True, key=get_unique_key("btn_replay")):
                        st.markdown(create_autoplay_audio(audio_bytes), unsafe_allow_html=True)
            else:
                st.warning("Could not generate audio. Displaying text response only.")
        else:
            st.warning("TTS not available. Install with: `pip install gtts`")
            # Browser TTS fallback
            safe_text = response_text.replace("'", "\\'").replace('"', '\\"').replace('\n', ' ')
            st.markdown(f'''
            <script>
            function speakNow() {{
                const text = '{safe_text}';
                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = 1.0;
                window.speechSynthesis.speak(utterance);
            }}
            speakNow();
            </script>
            ''', unsafe_allow_html=True)
        
        # Save to history
        st.session_state.voice_history.append({
            "timestamp": datetime.now().isoformat(),
            "question": voice_input,
            "intent": assistant.last_intent,
            "response": response_text,
            "disease": disease
        })
        
        # Clear input after processing
        st.session_state.voice_input_text = ""
        
        st.markdown("---")
        
        # Suggested follow-ups based on intent
        st.markdown("#### 💭 Follow-up Questions")
        
        follow_up_map = {
            "compare": ["What's the treatment now?", "Is it getting worse?", "What should I watch for?"],
            "explain": ["What's the treatment?", "How serious is this?", "What caused this?"],
            "treatment": ["Any side effects?", "How long is treatment?", "Any alternatives?"],
            "severity": ["What's the treatment?", "What's the prognosis?", "Need emergency care?"],
            "prognosis": ["What affects the outcome?", "What can I do?", "When will I recover?"],
            "next_step": ["When is the follow-up?", "What tests are needed?", "How to prepare?"],
            "emergency": ["What symptoms to watch?", "When to call 911?", "Where to go?"],
            "differential": ["How certain is the diagnosis?", "What tests confirm it?", "Most likely?"],
            "labs": ["What do results mean?", "Any concerning values?", "Need more tests?"],
            "cause": ["Could I have prevented it?", "Risk factors?", "Is it genetic?"],
            "symptoms": ["What's normal?", "When to worry?", "How to manage symptoms?"],
            "lifestyle": ["Diet recommendations?", "Exercise allowed?", "Work restrictions?"]
        }
        
        suggestions = follow_up_map.get(assistant.last_intent, 
                                       ["Tell me more", "What's next?", "Any concerns?"])
        
        cols = st.columns(len(suggestions))
        for i, suggestion in enumerate(suggestions):
            with cols[i]:
                if st.button(
                    f"🎤 {suggestion}", 
                    key=get_unique_key(f"follow_{i}"), 
                    use_container_width=True
                ):
                    st.session_state.voice_input_text = suggestion
                    st.rerun()
    
    elif get_response and not voice_input:
        st.warning("Please enter a question first!")
    
    st.markdown("---")
    
    # Session History
    with st.expander(f"📝 Session History ({len(st.session_state.voice_history)} interactions)"):
        if st.session_state.voice_history:
            for i, entry in enumerate(reversed(st.session_state.voice_history[-10:]), 1):
                st.write(f"**{i}. [{entry['timestamp'][11:19]}]** - *{entry['intent']}*")
                st.write(f"❓ {entry['question']}")
                st.write(f"🤖 {entry['response'][:200]}{'...' if len(entry['response']) > 200 else ''}")
                st.divider()
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear History", key=get_unique_key("btn_clear_history")):
                    st.session_state.voice_history = []
                    st.rerun()
            with col2:
                history_text = "\n\n".join([
                    f"[{e['timestamp']}]\nQ: {e['question']}\nA: {e['response']}"
                    for e in st.session_state.voice_history
                ])
                st.download_button(
                    "📥 Export History",
                    data=history_text,
                    file_name=f"voice_history_{datetime.now().strftime('%Y%m%d')}.txt",
                    mime="text/plain",
                    key=get_unique_key("btn_export_history")
                )
        else:
            st.info("No interactions yet. Ask a question to get started!")
    
    # Voice Settings
    with st.expander("⚙️ Voice Settings"):
        col1, col2 = st.columns(2)
        
        with col1:
            if len(available_engines) > 0 and available_engines[0] != "none":
                current_engine_index = 0
                if st.session_state.voice_tts_engine in available_engines:
                    current_engine_index = available_engines.index(st.session_state.voice_tts_engine)
                
                st.session_state.voice_tts_engine = st.selectbox(
                    "TTS Engine",
                    available_engines,
                    index=current_engine_index,
                    key=get_unique_key("sel_tts_engine")
                )
            else:
                st.warning("No TTS engine available")
        
        with col2:
            st.write("**Installation:**")
            st.code("pip install gtts pyttsx3", language="bash")


# ============================================
# MAIN ENTRY POINT
# ============================================

if __name__ == "__main__":
    st.set_page_config(page_title="Voice Diagnosis Assistant", layout="wide")
    
    st.title("🎤 Voice Diagnosis Assistant Demo")
    
    # Demo with sample disease
    demo_disease = st.selectbox(
        "Select demo disease:",
        [None, "Pneumonia", "Brain Tumor", "Diabetic Retinopathy", "Tuberculosis", "Skin Cancer"],
        index=1,
        key="demo_disease_select"
    )
    
    demo_confidence = st.slider("Confidence", 0.0, 100.0, 92.5, key="demo_confidence_slider")
    
    st.markdown("---")
    
    show_voice_diagnosis_assistant(demo_disease, demo_confidence)