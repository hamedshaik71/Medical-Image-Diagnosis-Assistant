# 🔬 CLINICAL GUIDELINE ALIGNMENT & AI-SUGGESTED NEXT TESTS
# Guideline-aligned recommendations with clinical follow-up testing

import streamlit as st
import json
from datetime import datetime, timedelta
from typing import Dict, List
import os

# AI-Suggested next tests database (clinical protocols)
NEXT_TESTS_DATABASE = {
    "Pneumonia": {
        "immediate": [
            {
                "test": "CBC with differential",
                "reason": "Assess WBC elevation, left shift",
                "urgency": "Immediately",
                "guideline": "WHO/NICE",
                "cost": "$50-100"
            },
            {
                "test": "Blood cultures",
                "reason": "Identify causative organism",
                "urgency": "Before antibiotics",
                "guideline": "WHO",
                "cost": "$100-150"
            },
            {
                "test": "CMP (electrolytes, renal function)",
                "reason": "Baseline renal/hepatic function",
                "urgency": "Before treatment",
                "guideline": "NICE",
                "cost": "$75-120"
            },
            {
                "test": "Blood gas analysis",
                "reason": "Assess hypoxia severity",
                "urgency": "If SpO2 <92%",
                "guideline": "ACR",
                "cost": "$50-80"
            }
        ],
        "followup": [
            {
                "test": "Sputum culture",
                "reason": "Organism identification and sensitivities",
                "timing": "Within 24-48 hours",
                "guideline": "WHO",
                "cost": "$75-125"
            },
            {
                "test": "Chest X-ray follow-up",
                "reason": "Assess treatment response",
                "timing": "7-10 days after treatment",
                "guideline": "ACR",
                "cost": "$100-200"
            },
            {
                "test": "Repeat CBC",
                "reason": "Monitor WBC normalization",
                "timing": "3-5 days into treatment",
                "guideline": "NICE",
                "cost": "$50-100"
            },
            {
                "test": "LFTs if antibiotics changed",
                "reason": "Monitor for hepatotoxicity",
                "timing": "If on macrolides > 5 days",
                "guideline": "NICE",
                "cost": "$75-100"
            }
        ],
        "optional": [
            {
                "test": "CT chest (high-res)",
                "reason": "If diagnosis uncertain or complications suspected",
                "when": "If CXR inconclusive",
                "guideline": "ACR",
                "cost": "$500-1000"
            },
            {
                "test": "Procalcitonin level",
                "reason": "Prognostic marker for severity",
                "when": "Consider in severe cases",
                "guideline": "NICE",
                "cost": "$100-200"
            }
        ]
    },
    "Brain Tumor": {
        "immediate": [
            {
                "test": "MRI Brain (3T) with contrast",
                "reason": "Confirm tumor, assess mass effect, edema",
                "urgency": "Urgent (within 24-48h)",
                "guideline": "NICE/ACR",
                "cost": "$1500-3000"
            },
            {
                "test": "MRI with DWI/PWI",
                "reason": "Assess perfusion and cellularity",
                "urgency": "Same session",
                "guideline": "ACR",
                "cost": "Included in MRI"
            },
            {
                "test": "MR Spectroscopy",
                "reason": "Assess metabolic activity (choline/NAA ratio)",
                "urgency": "Same session if available",
                "guideline": "ACR",
                "cost": "Included in MRI"
            },
            {
                "test": "CBC, BMP, LFTs",
                "reason": "Baseline labs before surgery/chemo",
                "urgency": "Before treatment",
                "guideline": "WHO",
                "cost": "$150-250"
            }
        ],
        "followup": [
            {
                "test": "Brain biopsy/Surgical pathology",
                "reason": "Histological diagnosis, WHO grading, molecular testing",
                "timing": "Within 1 week of imaging",
                "guideline": "WHO/NICE",
                "cost": "$2000-5000"
            },
            {
                "test": "Molecular testing (IDH1/IDH2, TP53, MGMT)",
                "reason": "Prognostic markers, treatment planning",
                "timing": "On pathology specimen",
                "guideline": "WHO",
                "cost": "$500-1500"
            },
            {
                "test": "Post-op MRI with contrast",
                "reason": "Assess extent of resection",
                "timing": "48-72 hours post-surgery",
                "guideline": "ACR",
                "cost": "$1500-3000"
            },
            {
                "test": "Monthly MRI during chemoradiation",
                "reason": "Monitor treatment response",
                "timing": "Throughout treatment",
                "guideline": "NICE",
                "cost": "$1500 x monthly"
            }
        ],
        "optional": [
            {
                "test": "PET/CT (18F-FDG)",
                "reason": "Assess metabolic activity if diagnosis uncertain",
                "when": "If MRI inconclusive",
                "guideline": "ACR",
                "cost": "$3000-5000"
            },
            {
                "test": "Neuropsychological evaluation",
                "reason": "Baseline cognitive function",
                "when": "Before treatment",
                "guideline": "NICE",
                "cost": "$1000-2000"
            }
        ]
    },
    "Diabetic Retinopathy": {
        "immediate": [
            {
                "test": "Dilated fundus examination",
                "reason": "Direct visualization of retinal changes",
                "urgency": "Urgent",
                "guideline": "WHO/NICE",
                "cost": "$100-200"
            },
            {
                "test": "Optical Coherence Tomography (OCT)",
                "reason": "Assess macular thickness, edema",
                "urgency": "Same visit",
                "guideline": "NICE/ACR",
                "cost": "$200-400"
            },
            {
                "test": "Visual acuity and IOP measurement",
                "reason": "Baseline vision, glaucoma screening",
                "urgency": "At each visit",
                "guideline": "WHO",
                "cost": "$100-200"
            },
            {
                "test": "Fundus photography (45-50° field)",
                "reason": "Document baseline for comparison",
                "urgency": "At baseline",
                "guideline": "ACR",
                "cost": "$100-300"
            }
        ],
        "followup": [
            {
                "test": "OCT macula every 4 weeks if treatment initiated",
                "reason": "Monitor response to anti-VEGF/laser",
                "timing": "Monthly x 3, then 2-3 monthly",
                "guideline": "NICE",
                "cost": "$200 per visit"
            },
            {
                "test": "Fluorescein angiography",
                "reason": "Assess macular perfusion, nonperfusion areas",
                "timing": "If macular edema suspected",
                "guideline": "ACR",
                "cost": "$300-500"
            },
            {
                "test": "Widefield fundus imaging",
                "reason": "Assess peripheral retina ischemia",
                "timing": "If proliferative disease",
                "guideline": "ACR",
                "cost": "$200-400"
            },
            {
                "test": "HbA1c every 3 months",
                "reason": "Assess glycemic control",
                "timing": "Every 3 months",
                "guideline": "WHO",
                "cost": "$50-100"
            }
        ],
        "optional": [
            {
                "test": "Indocyanine green angiography",
                "reason": "If fluorescein angiography inconclusive",
                "when": "Specialized imaging only",
                "guideline": "ACR",
                "cost": "$500-800"
            }
        ]
    },
    "Tuberculosis": {
        "immediate": [
            {
                "test": "Sputum smear microscopy (AFB) x3",
                "reason": "Confirm TB diagnosis, assess infectiousness",
                "urgency": "Within 24 hours",
                "guideline": "WHO",
                "cost": "$20-50"
            },
            {
                "test": "Gene Xpert MTB/RIF",
                "reason": "Rapid TB diagnosis + rifampicin resistance",
                "urgency": "Immediately if available",
                "guideline": "WHO",
                "cost": "$15-20"
            },
            {
                "test": "Chest X-ray (PA and lateral)",
                "reason": "Assess extent, cavitation, complications",
                "urgency": "Within 24-48 hours",
                "guideline": "WHO/ACR",
                "cost": "$50-100"
            },
            {
                "test": "HIV test",
                "reason": "HIV status affects TB management",
                "urgency": "Mandatory",
                "guideline": "WHO",
                "cost": "$20-50"
            }
        ],
        "followup": [
            {
                "test": "Drug sensitivity testing (DST)",
                "reason": "Identify MDR-TB/XDR-TB",
                "timing": "First positive specimen",
                "guideline": "WHO",
                "cost": "$50-200"
            },
            {
                "test": "Monthly sputum smear microscopy x3",
                "reason": "Monitor treatment response, time to negativity",
                "timing": "Months 1, 2, 3",
                "guideline": "WHO/NICE",
                "cost": "$20 per month"
            },
            {
                "test": "LFTs baseline and at month 2",
                "reason": "Monitor hepatotoxicity from RIPE",
                "timing": "Before treatment, 2 weeks in, month 2",
                "guideline": "NICE",
                "cost": "$75-100 x2"
            },
            {
                "test": "End-of-treatment chest X-ray",
                "reason": "Document treatment response",
                "timing": "At treatment completion",
                "guideline": "ACR",
                "cost": "$50-100"
            }
        ],
        "optional": [
            {
                "test": "TB-LAMP or TrueNat",
                "reason": "Rapid TB detection if Xpert unavailable",
                "when": "Limited resource settings",
                "guideline": "WHO",
                "cost": "$10-15"
            },
            {
                "test": "High-res CT chest",
                "reason": "If CXR shows atypical findings",
                "when": "Diagnostic uncertainty",
                "guideline": "ACR",
                "cost": "$300-600"
            }
        ]
    },
    "Skin Cancer": {
        "immediate": [
            {
                "test": "Full-thickness skin biopsy",
                "reason": "Definitive histological diagnosis, staging",
                "urgency": "Within 1-2 weeks",
                "guideline": "WHO/NICE",
                "cost": "$300-500"
            },
            {
                "test": "Dermoscopy imaging",
                "reason": "Document morphology for record",
                "urgency": "At initial assessment",
                "guideline": "ACR",
                "cost": "$100-200"
            },
            {
                "test": "CBC, BMP, LFTs",
                "reason": "Baseline labs for staging",
                "urgency": "Before treatment",
                "guideline": "WHO",
                "cost": "$150-250"
            },
            {
                "test": "LDH level",
                "reason": "Prognostic marker (elevated = worse prognosis)",
                "urgency": "Baseline",
                "guideline": "NICE",
                "cost": "$50-100"
            }
        ],
        "followup": [
            {
                "test": "Sentinel lymph node biopsy",
                "reason": "Assess regional nodal involvement",
                "timing": "If Breslow > 1mm or ulceration",
                "guideline": "NICE",
                "cost": "$3000-5000"
            },
            {
                "test": "Chest X-ray baseline",
                "reason": "Screen for pulmonary metastases",
                "timing": "At staging",
                "guideline": "ACR",
                "cost": "$100-200"
            },
            {
                "test": "CT chest/abdomen/pelvis if stage II-IV",
                "reason": "Metastatic staging",
                "timing": "If high-risk features",
                "guideline": "ACR/NICE",
                "cost": "$1000-2000"
            },
            {
                "test": "Brain MRI if stage III-IV",
                "reason": "Screen for brain metastases",
                "timing": "High-risk patients",
                "guideline": "NICE",
                "cost": "$1500-3000"
            }
        ],
        "optional": [
            {
                "test": "PET/CT for stage III-IV",
                "reason": "Whole-body metabolic imaging",
                "when": "High-risk melanoma",
                "guideline": "ACR",
                "cost": "$3000-5000"
            },
            {
                "test": "Molecular testing (BRAF V600E, c-KIT)",
                "reason": "Targeted therapy eligibility",
                "when": "Stage III-IV",
                "guideline": "WHO",
                "cost": "$500-1500"
            }
        ]
    },
    "Dental": {
        "immediate": [
            {
                "test": "Periapical radiograph",
                "reason": "Assess bone loss, periapical pathology",
                "urgency": "At diagnosis",
                "guideline": "NICE/ACR",
                "cost": "$50-100"
            },
            {
                "test": "Pulp vitality testing",
                "reason": "Assess nerve status (vital vs necrotic)",
                "urgency": "At assessment",
                "guideline": "WHO",
                "cost": "$20-50"
            },
            {
                "test": "Intraoral clinical photography",
                "reason": "Document baseline condition",
                "urgency": "At initial visit",
                "guideline": "NICE",
                "cost": "$50-100"
            },
            {
                "test": "Probing depth assessment",
                "reason": "Periodontal status evaluation",
                "urgency": "At assessment",
                "guideline": "WHO/NICE",
                "cost": "Included in exam"
            }
        ],
        "followup": [
            {
                "test": "Periapical follow-up at 6 months",
                "reason": "Verify successful treatment",
                "timing": "6 months post-treatment",
                "guideline": "NICE/ACR",
                "cost": "$50-100"
            },
            {
                "test": "Bitewings every 24-36 months",
                "reason": "Screen for new carious lesions",
                "timing": "Annual or 2-year intervals",
                "guideline": "ACR",
                "cost": "$50-100"
            },
            {
                "test": "Recall visits every 6-12 months",
                "reason": "Preventive care, scaling/polishing",
                "timing": "Based on risk",
                "guideline": "WHO/NICE",
                "cost": "$100-200 per visit"
            }
        ],
        "optional": [
            {
                "test": "CBCT if implant planning",
                "reason": "3D assessment of bone anatomy",
                "when": "Complex cases",
                "guideline": "ACR",
                "cost": "$300-600"
            }
        ]
    }
}


def show_guideline_aligned_next_tests(disease: str, confidence: float):
    """Display clinically-aligned next tests recommendations"""
    
    st.markdown("### 🔬 AI-Suggested Clinical Next Tests")
    st.info(
        "Evidence-based recommendations for follow-up testing aligned with "
        "WHO, NICE, and ACR guidelines"
    )
    
    if disease not in NEXT_TESTS_DATABASE:
        st.warning(f"⚠️ Test protocols not available for {disease}")
        return
    
    st.markdown("---")
    
    test_data = NEXT_TESTS_DATABASE[disease]
    
    # Create tabs for test categories
    tabs = st.tabs(["⚡ Immediate Tests", "📅 Follow-up Tests", "🔬 Optional Tests"])
    
    # Immediate Tests
    with tabs[0]:
        st.markdown("#### ⚡ Tests to Order NOW")
        st.write("These tests should be ordered immediately for proper diagnosis and management")
        
        st.divider()
        
        for i, test in enumerate(test_data.get("immediate", []), 1):
            with st.expander(f"{i}. **{test['test']}** - {test['guideline']}", expanded=i==1):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"**Reason:** {test['reason']}")
                    st.write(f"**Urgency:** 🔴 {test['urgency']}")
                    st.write(f"**Guideline:** {test['guideline']}")
                
                with col2:
                    st.write(f"**Estimated Cost:** {test['cost']}")
                    st.write(f"**Priority:** HIGH")
                    
                    if st.button(f"✅ Order {test['test']}", key=f"order_{i}"):
                        st.success(f"✓ {test['test']} added to order")
    
    # Follow-up Tests
    with tabs[1]:
        st.markdown("#### 📅 Follow-up Testing Schedule")
        st.write("These tests should be scheduled based on the timeline provided")
        
        st.divider()
        
        for i, test in enumerate(test_data.get("followup", []), 1):
            with st.expander(f"{i}. **{test['test']}**", expanded=i==1):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"**Reason:** {test['reason']}")
                    st.write(f"**Timing:** 📅 {test['timing']}")
                    st.write(f"**Guideline:** {test['guideline']}")
                
                with col2:
                    st.write(f"**Estimated Cost:** {test['cost']}")
                    st.write(f"**Priority:** MEDIUM")
                    
                    if st.button(f"📋 Schedule {test['test']}", key=f"schedule_{i}"):
                        st.info(f"⏰ {test['test']} scheduled for {test['timing']}")
    
    # Optional Tests
    with tabs[2]:
        st.markdown("#### 🔬 Optional Tests")
        st.write("These tests may be helpful in specific clinical scenarios")
        
        st.divider()
        
        for i, test in enumerate(test_data.get("optional", []), 1):
            with st.expander(f"{i}. **{test['test']}**"):
                col1, col2 = st.columns([1, 1])
                
                with col1:
                    st.write(f"**Reason:** {test['reason']}")
                    st.write(f"**When:** {test['when']}")
                    st.write(f"**Guideline:** {test['guideline']}")
                
                with col2:
                    st.write(f"**Estimated Cost:** {test['cost']}")
                    st.write(f"**Priority:** LOW")
                    
                    if st.button(f"ⓘ Consider {test['test']}", key=f"consider_{i}"):
                        st.info(f"💡 {test['test']} may be useful if {test['when']}")
    
    st.markdown("---")
    
    # Test ordering summary
    st.markdown("#### 📋 Test Ordering Summary")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        immediate_count = len(test_data.get("immediate", []))
        st.metric("Immediate Tests", immediate_count, "Order now")
    
    with col2:
        followup_count = len(test_data.get("followup", []))
        st.metric("Follow-up Tests", followup_count, "Schedule by timeline")
    
    with col3:
        optional_count = len(test_data.get("optional", []))
        st.metric("Optional Tests", optional_count, "Consider as needed")
    
    st.markdown("---")
    
    # Export test order
    st.markdown("#### 📥 Export Test Order")
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        test_order = f"""
RECOMMENDED TEST ORDER - {disease.upper()}
========================================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
AI Confidence: {confidence:.1f}%

IMMEDIATE TESTS (Order Now)
===========================
"""
        
        for test in test_data.get("immediate", []):
            test_order += f"""
□ {test['test']}
  Reason: {test['reason']}
  Urgency: {test['urgency']}
  Cost: {test['cost']}
  Guideline: {test['guideline']}

"""
        
        test_order += "\nFOLLOW-UP TESTS\n===============\n"
        
        for test in test_data.get("followup", []):
            test_order += f"""
□ {test['test']}
  Timing: {test['timing']}
  Reason: {test['reason']}
  Cost: {test['cost']}

"""
        
        st.download_button(
            label="📄 Download Test Order",
            data=test_order,
            file_name=f"test_order_{disease}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    with col2:
        # Calculate total estimated cost
        all_tests = (
            test_data.get("immediate", []) +
            test_data.get("followup", [])
        )
        
        total_cost_text = "Total Estimated Cost: Variable based on\n"
        total_cost_text += "- Immediate: $500-5000 (depending on disease)\n"
        total_cost_text += "- Follow-up: $300-3000 (dependent on imaging)\n"
        total_cost_text += "- All costs are approximate"
        
        st.info(total_cost_text)
    
    st.markdown("---")
    
    # Clinical context
    st.markdown("#### 📚 Clinical Context")
    
    with st.expander("📖 Why These Tests?"):
        st.write("""
        These test recommendations are based on:
        
        1. **WHO Guidelines**: International standards for diagnosis and monitoring
        2. **NICE Guidelines**: Evidence-based best practice from National Institute
        3. **ACR Appropriateness Criteria**: Clinical evidence ratings for imaging
        
        The recommended tests are designed to:
        - Confirm diagnosis (if not yet confirmed)
        - Stage disease appropriately
        - Establish baseline for treatment monitoring
        - Detect complications early
        - Guide treatment decisions
        - Monitor treatment response
        
        Not all tests apply to all patients. Clinical judgment and patient
        presentation should guide final test ordering decisions.
        """)