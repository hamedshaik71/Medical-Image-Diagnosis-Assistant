# 🔗 SYMPTOM + IMAGE FUSION ENGINE
# Combines patient symptoms with medical imaging for enhanced diagnosis

import streamlit as st
import numpy as np
from datetime import datetime
from typing import Dict, List, Tuple

# Symptom-Disease mapping database
SYMPTOM_DISEASE_MAP = {
    "Pneumonia": {
        "primary_symptoms": [
            "Cough",
            "Chest pain",
            "Fever",
            "Shortness of breath",
            "Fatigue"
        ],
        "secondary_symptoms": [
            "Chills",
            "Headache",
            "Muscle pain",
            "Loss of appetite"
        ],
        "symptom_weight": 0.4,  # How much symptoms contribute to final score
        "image_weight": 0.6     # How much imaging contributes to final score
    },
    "Brain Tumor": {
        "primary_symptoms": [
            "Headaches",
            "Vision problems",
            "Balance issues",
            "Nausea/vomiting",
            "Seizures"
        ],
        "secondary_symptoms": [
            "Memory problems",
            "Concentration difficulty",
            "Speech problems",
            "Hearing changes"
        ],
        "symptom_weight": 0.35,
        "image_weight": 0.65
    },
    "Diabetic Retinopathy": {
        "primary_symptoms": [
            "Blurred vision",
            "Floaters",
            "Vision loss",
            "Eye pain",
            "Difficulty reading"
        ],
        "secondary_symptoms": [
            "Flashes of light",
            "Color vision changes",
            "Dark spots"
        ],
        "symptom_weight": 0.3,
        "image_weight": 0.7
    },
    "Tuberculosis": {
        "primary_symptoms": [
            "Persistent cough",
            "Cough with blood",
            "Chest pain",
            "Fever",
            "Night sweats"
        ],
        "secondary_symptoms": [
            "Weight loss",
            "Fatigue",
            "Loss of appetite",
            "Chills"
        ],
        "symptom_weight": 0.45,
        "image_weight": 0.55
    },
    "Skin Cancer": {
        "primary_symptoms": [
            "Skin changes",
            "New mole",
            "Changing mole",
            "Skin growth",
            "Itching"
        ],
        "secondary_symptoms": [
            "Bleeding mole",
            "Asymmetric mole",
            "Irregular borders",
            "Multiple colors"
        ],
        "symptom_weight": 0.5,
        "image_weight": 0.5
    },
    "Malaria": {
        "primary_symptoms": [
            "Fever",
            "Chills",
            "Sweating",
            "Headache",
            "Muscle pain"
        ],
        "secondary_symptoms": [
            "Nausea",
            "Vomiting",
            "Diarrhea",
            "Loss of appetite"
        ],
        "symptom_weight": 0.55,
        "image_weight": 0.45
    },
    "Dental": {
        "primary_symptoms": [
            "Tooth pain",
            "Gum swelling",
            "Difficulty chewing",
            "Tooth sensitivity",
            "Gum bleeding"
        ],
        "secondary_symptoms": [
            "Jaw pain",
            "Bad breath",
            "Discolored teeth",
            "Loose teeth"
        ],
        "symptom_weight": 0.45,
        "image_weight": 0.55
    }
}


class SymptomImageFusionEngine:
    """Combines symptom and imaging data for enhanced diagnosis"""
    
    def __init__(self):
        self.symptom_scores = {}
        self.image_scores = {}
        self.fusion_weight = 0.5
    
    def calculate_symptom_score(self, disease: str, 
                               symptoms: List[str]) -> Tuple[float, Dict]:
        """
        Calculate symptom-based confidence score
        
        Args:
            disease: Disease name
            symptoms: List of reported symptoms
            
        Returns:
            Tuple of (score, detailed_analysis)
        """
        if disease not in SYMPTOM_DISEASE_MAP:
            return 0.0, {"error": f"No symptom data for {disease}"}
        
        disease_data = SYMPTOM_DISEASE_MAP[disease]
        primary_symptoms = disease_data["primary_symptoms"]
        secondary_symptoms = disease_data["secondary_symptoms"]
        
        # Score calculation
        primary_matches = sum(
            1 for s in symptoms 
            if any(ps.lower() in s.lower() or s.lower() in ps.lower() 
                   for ps in primary_symptoms)
        )
        
        secondary_matches = sum(
            1 for s in symptoms 
            if any(ss.lower() in s.lower() or s.lower() in ss.lower() 
                   for ss in secondary_symptoms)
        )
        
        # Weighted score
        max_primary = len(primary_symptoms)
        max_secondary = len(secondary_symptoms)
        
        primary_score = (primary_matches / max(max_primary, 1)) * 0.7  # 70% weight
        secondary_score = (secondary_matches / max(max_secondary, 1)) * 0.3  # 30% weight
        
        symptom_score = (primary_score + secondary_score) * 100
        
        analysis = {
            "disease": disease,
            "primary_matches": primary_matches,
            "primary_total": max_primary,
            "secondary_matches": secondary_matches,
            "secondary_total": max_secondary,
            "symptom_score": symptom_score,
            "matched_symptoms": [
                s for s in symptoms 
                if any(
                    ps.lower() in s.lower() or s.lower() in ps.lower()
                    for ps in primary_symptoms + secondary_symptoms
                )
            ]
        }
        
        return min(symptom_score, 100), analysis
    
    def fuse_scores(self, symptom_score: float, image_score: float,
                   disease: str) -> Dict:
        """
        Fuse symptom and image scores using weighted combination
        
        Args:
            symptom_score: Score from symptoms (0-100)
            image_score: Score from imaging (0-100)
            disease: Disease name for weights
            
        Returns:
            Fused diagnosis report
        """
        if disease not in SYMPTOM_DISEASE_MAP:
            # Default weights if disease not found
            symptom_weight = 0.5
            image_weight = 0.5
        else:
            symptom_weight = SYMPTOM_DISEASE_MAP[disease]["symptom_weight"]
            image_weight = SYMPTOM_DISEASE_MAP[disease]["image_weight"]
        
        # Fused score
        fused_score = (symptom_score * symptom_weight + 
                      image_score * image_weight)
        
        # Confidence level
        if fused_score >= 80:
            confidence_level = "Very High"
            confidence_color = "🟢"
        elif fused_score >= 60:
            confidence_level = "High"
            confidence_color = "🟢"
        elif fused_score >= 40:
            confidence_level = "Moderate"
            confidence_color = "🟡"
        else:
            confidence_level = "Low"
            confidence_color = "🔴"
        
        # Agreement analysis
        score_diff = abs(symptom_score - image_score)
        if score_diff < 10:
            agreement = "Strong Agreement"
        elif score_diff < 20:
            agreement = "Good Agreement"
        else:
            agreement = "Conflicting Signals"
        
        return {
            "fused_score": fused_score,
            "symptom_score": symptom_score,
            "image_score": image_score,
            "symptom_weight": symptom_weight * 100,
            "image_weight": image_weight * 100,
            "confidence_level": confidence_level,
            "confidence_color": confidence_color,
            "agreement": agreement,
            "score_difference": score_diff,
            "recommendation": self._get_recommendation(
                fused_score, 
                agreement
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    def _get_recommendation(self, score: float, agreement: str) -> str:
        """Generate recommendation based on fusion results"""
        
        if score >= 80 and agreement in ["Strong Agreement", "Good Agreement"]:
            return "High confidence in diagnosis. Proceed with treatment planning."
        elif score >= 60 and agreement in ["Strong Agreement", "Good Agreement"]:
            return "Good confidence. Consider confirmatory tests if needed."
        elif score >= 60 and agreement == "Conflicting Signals":
            return "Mixed signals. Recommend additional diagnostic tests."
        elif score >= 40:
            return "Low-moderate confidence. Further investigation recommended."
        else:
            return "Very low confidence. Diagnosis uncertain. Seek additional opinions."


def show_symptom_image_fusion(disease: str, image_confidence: float):
    """Display symptom-image fusion interface"""
    
    st.markdown("### 🔗 Symptom + Image Fusion Analysis")
    st.info(
        "Combine patient symptoms with medical imaging for "
        "enhanced diagnostic accuracy"
    )
    
    engine = SymptomImageFusionEngine()
    
    # Left column - Symptom collection
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.markdown("#### 🩺 Step 1: Patient Symptoms")
        
        disease_data = SYMPTOM_DISEASE_MAP.get(disease, {})
        primary_symptoms = disease_data.get("primary_symptoms", [])
        secondary_symptoms = disease_data.get("secondary_symptoms", [])
        
        selected_symptoms = []
        
        if primary_symptoms:
            st.write("**Common Symptoms (Primary):**")
            for symptom in primary_symptoms:
                if st.checkbox(symptom, key=f"primary_{symptom}"):
                    selected_symptoms.append(symptom)
        
        if secondary_symptoms:
            st.write("**Associated Symptoms (Secondary):**")
            for symptom in secondary_symptoms:
                if st.checkbox(symptom, key=f"secondary_{symptom}"):
                    selected_symptoms.append(symptom)
        
        st.write("**Other Symptoms:**")
        other_symptoms = st.text_area(
            "Enter other symptoms (comma-separated)",
            placeholder="e.g., Dizziness, Nausea, Back pain",
            key="other_symptoms"
        ).split(",")
        
        other_symptoms = [s.strip() for s in other_symptoms if s.strip()]
        selected_symptoms.extend(other_symptoms)
        
        # Calculate symptom score
        symptom_score, symptom_analysis = engine.calculate_symptom_score(
            disease,
            selected_symptoms
        )
    
    with col2:
        st.markdown("#### 🖼️ Step 2: Imaging Analysis")
        
        st.metric("AI Image Confidence", f"{image_confidence:.1f}%")
        
        # Image-based parameters
        st.write("**Imaging Findings:**")
        
        lesion_size = st.slider(
            "Lesion Size/Severity",
            0.0, 10.0, 5.0,
            help="0=minimal, 10=severe",
            key="lesion_size"
        )
        
        spread_extent = st.slider(
            "Spread/Extent",
            0.0, 10.0, 5.0,
            help="0=localized, 10=widespread",
            key="spread_extent"
        )
        
        # Calculate imaging score from parameters
        imaging_base_score = image_confidence
        severity_adjustment = (lesion_size + spread_extent) / 2 * 0.5
        imaging_score = imaging_base_score + severity_adjustment
        imaging_score = min(imaging_score, 100)
    
    st.markdown("---")
    
    # Fusion analysis
    if selected_symptoms:
        st.markdown("### 🔄 Fusion Analysis Results")
        
        # Get fusion results
        fusion_results = engine.fuse_scores(
            symptom_score,
            imaging_score,
            disease
        )
        
        # Display results in columns
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric(
                "Symptom Score",
                f"{fusion_results['symptom_score']:.1f}%",
                f"{fusion_results['symptom_weight']:.0f}% weight"
            )
        
        with col2:
            st.metric(
                "Image Score",
                f"{fusion_results['image_score']:.1f}%",
                f"{fusion_results['image_weight']:.0f}% weight"
            )
        
        with col3:
            st.metric(
                f"{fusion_results['confidence_color']} Fused Score",
                f"{fusion_results['fused_score']:.1f}%",
                fusion_results['confidence_level']
            )
        
        with col4:
            st.metric(
                "Data Agreement",
                fusion_results['agreement'],
                f"Δ {fusion_results['score_difference']:.1f}%"
            )
        
        st.markdown("---")
        
        # Detailed analysis
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.markdown("#### 📊 Score Breakdown")
            
            # Create visual representation
            st.write("**Score Contribution:**")
            
            symptom_contribution = (
                fusion_results['symptom_score'] * 
                fusion_results['symptom_weight'] / 100
            )
            image_contribution = (
                fusion_results['image_score'] * 
                fusion_results['image_weight'] / 100
            )
            
            st.write(f"Symptoms: {symptom_contribution:.1f}%")
            st.write(f"Imaging: {image_contribution:.1f}%")
            
            # Visualization
            data = {
                "Symptoms": fusion_results['symptom_score'],
                "Imaging": fusion_results['image_score'],
                "Fused": fusion_results['fused_score']
            }
            
            st.bar_chart(data)
        
        with col2:
            st.markdown("#### 🎯 Clinical Recommendation")
            
            recommendation = fusion_results['recommendation']
            
            if "High confidence" in recommendation:
                st.success(f"✅ {recommendation}")
            elif "Consider" in recommendation:
                st.info(f"ℹ️ {recommendation}")
            elif "Further" in recommendation:
                st.warning(f"⚠️ {recommendation}")
            else:
                st.error(f"❌ {recommendation}")
            
            st.markdown("---")
            
            st.write("**Symptom Summary:**")
            if selected_symptoms:
                st.write(f"- **Reported Symptoms**: {len(selected_symptoms)}")
                st.write(f"- **Disease Match**: {len(symptom_analysis.get('matched_symptoms', []))}/{len(primary_symptoms)}")
                
                matched = symptom_analysis.get('matched_symptoms', [])
                if matched:
                    st.write(f"- **Matching Symptoms**: {', '.join(matched)}")
        
        st.markdown("---")
        
        # Download fusion report
        st.markdown("#### 📥 Export Fusion Report")
        
        report_text = f"""
SYMPTOM + IMAGE FUSION REPORT
=============================
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

DIAGNOSIS: {disease}
==================

SYMPTOM ANALYSIS
================
Symptom Score: {fusion_results['symptom_score']:.1f}%
Weight: {fusion_results['symptom_weight']:.0f}%
Reported Symptoms: {len(selected_symptoms)}
Matched Symptoms: {len(symptom_analysis.get('matched_symptoms', []))}

Matched Findings:
{chr(10).join([f'  - {s}' for s in symptom_analysis.get('matched_symptoms', [])])}

IMAGE ANALYSIS
==============
Image Score: {fusion_results['image_score']:.1f}%
Weight: {fusion_results['image_weight']:.0f}%
Lesion Size: {lesion_size:.1f}/10
Spread Extent: {spread_extent:.1f}/10

FUSION RESULTS
==============
Fused Confidence: {fusion_results['fused_score']:.1f}%
Confidence Level: {fusion_results['confidence_level']}
Data Agreement: {fusion_results['agreement']}
Score Difference: {fusion_results['score_difference']:.1f}%

RECOMMENDATION
==============
{fusion_results['recommendation']}

NEXT STEPS
==========
1. Review findings with patient
2. Consider additional confirmatory tests if needed
3. Develop treatment plan based on confidence level
4. Schedule follow-up evaluation
"""
        
        st.download_button(
            label="📄 Download Fusion Report",
            data=report_text,
            file_name=f"fusion_report_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
            mime="text/plain"
        )
    
    else:
        st.warning("⚠️ Select at least one symptom to perform fusion analysis")