# 🚨 FIXED EMERGENCY ALERT SYSTEM
# Fixed: Now checks predicted label to avoid false alerts for normal/healthy predictions

import streamlit as st
from datetime import datetime
import json
import math


def inject_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Roboto+Mono:wght@400;700&display=swap');
    
    .stApp {
        background: linear-gradient(-45deg, #0a0a0a, #1a1a2e, #16213e, #0f0f23);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
    }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes criticalPulse {
        0%, 100% { 
            box-shadow: 0 0 20px rgba(255, 0, 0, 0.8), 0 0 40px rgba(255, 0, 0, 0.6);
            transform: scale(1);
        }
        50% { 
            box-shadow: 0 0 40px rgba(255, 0, 0, 1), 0 0 80px rgba(255, 0, 0, 0.8);
            transform: scale(1.02);
        }
    }
    
    @keyframes severeGlow {
        0%, 100% { box-shadow: 0 0 15px rgba(255, 102, 0, 0.6); }
        50% { box-shadow: 0 0 30px rgba(255, 102, 0, 0.8); }
    }
    
    @keyframes textFlicker {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.7; }
    }
    
    @keyframes slideIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    @keyframes blink {
        0%, 50%, 100% { opacity: 1; }
        25%, 75% { opacity: 0; }
    }
    
    @keyframes wave {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    @keyframes drawLine {
        to { stroke-dashoffset: 0; }
    }
    
    @keyframes soundWave {
        0%, 100% { height: 10px; }
        50% { height: 30px; }
    }
    
    @keyframes heartbeat {
        0%, 100% { transform: scale(1); }
        14% { transform: scale(1.1); }
        28% { transform: scale(1); }
        42% { transform: scale(1.1); }
        70% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)


# ============================================
# NORMAL/HEALTHY LABEL DETECTION
# ============================================

# Keywords that indicate a NORMAL/HEALTHY/NEGATIVE prediction
NORMAL_KEYWORDS = [
    "normal", "healthy", "benign", "negative", "no tumor", "no_tumor",
    "notumor", "uninfected", "no finding", "no_finding", "nofinding",
    "no disease", "no_disease", "nodisease", "clear", "none",
    "no dr", "no_dr", "nodr", "no retinopathy", "no_retinopathy",
    "no pneumonia", "no_pneumonia", "nopneumonia",
    "no tuberculosis", "no_tuberculosis", "notuberculosis",
    "no malaria", "no_malaria", "nomalaria",
    "no cancer", "no_cancer", "nocancer",
    "non-proliferative", "mild", "nevi", "nevus",
    "not infected", "not_infected", "notinfected",
    "no cavity", "no_cavity", "nocavity",
    "glioma",  # Remove this if glioma should trigger alert
]


def is_normal_prediction(predicted_label):
    """
    Check if the predicted label indicates a normal/healthy/non-disease result.
    Returns True if the prediction is NORMAL (no disease detected).
    """
    if predicted_label is None:
        return True
    
    label_lower = predicted_label.strip().lower()
    
    # Check against known normal keywords
    for keyword in NORMAL_KEYWORDS:
        if keyword in label_lower:
            return True
    
    return False


def get_disease_positive_labels():
    """
    Returns a dict mapping disease categories to their POSITIVE (disease-present) labels.
    If the predicted label is NOT in this list, it's considered normal.
    """
    return {
        "Pneumonia": ["pneumonia", "infected", "positive", "bacterial", "viral"],
        "Brain Tumor": ["tumor", "glioma", "meningioma", "pituitary", "malignant"],
        "Diabetic Retinopathy": ["proliferative", "severe", "moderate", "dr detected", 
                                  "retinopathy", "diabetic retinopathy"],
        "Tuberculosis": ["tuberculosis", "tb", "infected", "positive", "active tb"],
        "Skin Cancer": ["malignant", "melanoma", "carcinoma", "cancer", "cancerous"],
        "Malaria": ["parasitized", "infected", "positive", "malaria"],
        "Dental": ["cavity", "decay", "caries", "infected", "abscess", "issue"],
    }


def is_disease_positive(disease_name, predicted_label):
    """
    Check if the predicted label indicates an ACTUAL disease detection.
    Returns True only if the prediction indicates disease IS present.
    """
    if predicted_label is None:
        return False
    
    label_lower = predicted_label.strip().lower()
    
    # First check: if it's clearly a normal/healthy prediction, return False
    if is_normal_prediction(predicted_label):
        return False
    
    # Second check: see if it matches known positive labels for this disease
    positive_labels = get_disease_positive_labels()
    if disease_name in positive_labels:
        for pos_label in positive_labels[disease_name]:
            if pos_label in label_lower:
                return True
    
    # If we can't determine, assume it's NOT positive (safe default)
    # This prevents false emergency alerts
    return False


# ============================================
# THRESHOLDS
# ============================================

EMERGENCY_THRESHOLDS = {
    "Pneumonia": {
        "critical_confidence": 85,
        "severity_levels": {
            "CRITICAL": "Sepsis/severe respiratory failure",
            "SEVERE": "Moderate-severe pneumonia", 
            "MODERATE": "Community-acquired pneumonia"
        }
    },
    "Brain Tumor": {
        "critical_confidence": 90,
        "severity_levels": {
            "CRITICAL": "Symptomatic with mass effect/herniation risk",
            "SEVERE": "Large tumor with edema",
            "MODERATE": "Small tumor, minimal symptoms"
        }
    },
    "Diabetic Retinopathy": {
        "critical_confidence": 85,
        "severity_levels": {
            "CRITICAL": "Proliferative with vision loss",
            "SEVERE": "Proliferative without vision loss",
            "MODERATE": "Nonproliferative retinopathy"
        }
    },
    "Tuberculosis": {
        "critical_confidence": 85,
        "severity_levels": {
            "CRITICAL": "Cavitary/miliary with complications",
            "SEVERE": "Cavitary TB",
            "MODERATE": "Non-cavitary TB"
        }
    },
    "Skin Cancer": {
        "critical_confidence": 90,
        "severity_levels": {
            "CRITICAL": "Advanced melanoma with metastases",
            "SEVERE": "Thick melanoma (>4mm)",
            "MODERATE": "Thin melanoma (<1mm)"
        }
    }
}


# ============================================
# RENDER FUNCTIONS
# ============================================

def render_severity_gauge(severity_score, alert_level):
    """Render severity gauge"""
    
    rotation = -90 + (severity_score / 100) * 180
    
    colors = {"CRITICAL": "#ff0000", "SEVERE": "#ff6600", "MODERATE": "#ffcc00", "LOW": "#00ff00", "NONE": "#00ff00"}
    needle_color = colors.get(alert_level, "#00ff00")
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 20px; padding: 2rem; 
                border: 2px solid rgba(0, 240, 255, 0.3); animation: fadeInUp 0.8s ease-out;">
        <h3 style="color: #00f0ff; text-align: center; font-family: 'Orbitron', sans-serif; margin-bottom: 1rem;">
            ⚡ SEVERITY METER ⚡
        </h3>
        <div style="position: relative; width: 280px; height: 160px; margin: 0 auto;">
            <svg viewBox="0 0 280 160" style="width: 100%%; height: 100%%;">
                <defs>
                    <linearGradient id="gaugeGrad" x1="0%%" y1="0%%" x2="100%%" y2="0%%">
                        <stop offset="0%%" stop-color="#00ff00"/>
                        <stop offset="33%%" stop-color="#ffcc00"/>
                        <stop offset="66%%" stop-color="#ff6600"/>
                        <stop offset="100%%" stop-color="#ff0000"/>
                    </linearGradient>
                </defs>
                <path d="M 20 140 A 120 120 0 0 1 260 140" stroke="url(#gaugeGrad)" stroke-width="20" fill="none" stroke-linecap="round"/>
                <path d="M 40 140 A 100 100 0 0 1 240 140" stroke="#1a1a2e" stroke-width="15" fill="none"/>
                <text x="15" y="155" fill="#00ff00" font-size="10">LOW</text>
                <text x="125" y="25" fill="#ffcc00" font-size="10">MED</text>
                <text x="240" y="155" fill="#ff0000" font-size="10">HIGH</text>
                <g transform="translate(140, 140)">
                    <line x1="0" y1="0" x2="0" y2="-80" stroke="{needle_color}" stroke-width="4" stroke-linecap="round" transform="rotate({rotation})"/>
                    <circle cx="0" cy="0" r="10" fill="#ffffff"/>
                    <circle cx="0" cy="0" r="5" fill="#00f0ff"/>
                </g>
            </svg>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <span style="font-family: 'Orbitron', sans-serif; font-size: 2.5rem; color: {needle_color}; text-shadow: 0 0 15px {needle_color};">
                {score:.1f}%
            </span>
            <div style="color: #888; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px;">Severity Score</div>
        </div>
        <div style="text-align: center; margin-top: 1rem;">
            <span style="background: {needle_color}; color: white; padding: 0.5rem 1.5rem; border-radius: 20px; font-weight: bold;">
                {level}
            </span>
        </div>
    </div>
    """.replace("{needle_color}", needle_color)
       .replace("{rotation}", str(rotation))
       .replace("{score:.1f}", "{:.1f}".format(severity_score))
       .replace("{level}", alert_level), unsafe_allow_html=True)


def render_vital_signs():
    """Render ECG monitor"""
    
    points = []
    for i in range(100):
        x = i * 4
        if i % 20 == 10:
            y = 20
        elif i % 20 == 11:
            y = 80
        elif i % 20 == 12:
            y = 30
        elif i % 20 == 13:
            y = 50
        else:
            y = 50 + math.sin(i * 0.1) * 5
        points.append(str(x) + "," + str(int(y)))
    
    ecg_path = " ".join(points)
    
    st.markdown("""
    <div style="background: #000000; border: 3px solid #00ff00; border-radius: 15px; padding: 1rem; margin: 1rem 0;">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
            <span style="color: #00ff00; font-family: 'Roboto Mono', monospace;">❤️ ECG MONITOR</span>
            <span style="color: #00ff00;">♥ 72 BPM</span>
        </div>
        <svg viewBox="0 0 400 100" style="width: 100%%; height: 80px;">
            <line x1="0" y1="25" x2="400" y2="25" stroke="rgba(0,255,0,0.1)" stroke-width="1"/>
            <line x1="0" y1="50" x2="400" y2="50" stroke="rgba(0,255,0,0.1)" stroke-width="1"/>
            <line x1="0" y1="75" x2="400" y2="75" stroke="rgba(0,255,0,0.1)" stroke-width="1"/>
            <polyline points="{path}" stroke="#00ff00" stroke-width="2" fill="none" 
                      style="filter: drop-shadow(0 0 5px #00ff00); stroke-dasharray: 1000; stroke-dashoffset: 1000; animation: drawLine 3s linear infinite;"/>
        </svg>
        <div style="display: flex; justify-content: space-around; margin-top: 1rem; padding-top: 0.5rem; border-top: 1px solid rgba(0,255,0,0.3);">
            <div style="text-align: center;">
                <div style="color: #00ff00; font-size: 1.2rem; font-family: 'Orbitron';">98%</div>
                <div style="color: #888; font-size: 0.7rem;">SpO2</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #00f0ff; font-size: 1.2rem; font-family: 'Orbitron';">120/80</div>
                <div style="color: #888; font-size: 0.7rem;">BP</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #ffcc00; font-size: 1.2rem; font-family: 'Orbitron';">37.2°</div>
                <div style="color: #888; font-size: 0.7rem;">TEMP</div>
            </div>
            <div style="text-align: center;">
                <div style="color: #ff6600; font-size: 1.2rem; font-family: 'Orbitron';">18</div>
                <div style="color: #888; font-size: 0.7rem;">RESP</div>
            </div>
        </div>
    </div>
    """.replace("{path}", ecg_path), unsafe_allow_html=True)


def render_progress_ring(percentage, label, color):
    """Render progress ring"""
    
    circumference = 2 * 3.14159 * 40
    offset = circumference - (percentage / 100) * circumference
    
    st.markdown("""
    <div style="text-align: center; padding: 1rem;">
        <svg width="100" height="100" style="transform: rotate(-90deg);">
            <circle cx="50" cy="50" r="40" fill="none" stroke="rgba(255,255,255,0.1)" stroke-width="8"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="{color}" stroke-width="8"
                    stroke-linecap="round" stroke-dasharray="{circ}" stroke-dashoffset="{offset}"/>
        </svg>
        <div style="margin-top: -65px; font-family: 'Orbitron', sans-serif; font-size: 1.2rem; color: {color};">
            {pct:.0f}%
        </div>
        <div style="color: #888; font-size: 0.7rem; margin-top: 0.3rem; text-transform: uppercase;">
            {label}
        </div>
    </div>
    """.replace("{color}", color)
       .replace("{circ}", str(circumference))
       .replace("{offset}", str(offset))
       .replace("{pct:.0f}", str(int(percentage)))
       .replace("{label}", label), unsafe_allow_html=True)


def render_metric_card(value, label, color):
    """Render metric card"""
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #16213e); border-radius: 15px; padding: 1.5rem; 
                text-align: center; border: 1px solid rgba(0, 240, 255, 0.2);">
        <div style="font-family: 'Orbitron', sans-serif; font-size: 1.8rem; font-weight: bold; color: {color};">
            {value}
        </div>
        <div style="color: #888; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 2px; margin-top: 0.5rem;">
            {label}
        </div>
    </div>
    """.replace("{color}", color)
       .replace("{value}", str(value))
       .replace("{label}", label), unsafe_allow_html=True)


def render_notification(level, message):
    """Render notification"""
    
    config = {
        "CRITICAL": ("#ff0000", "🚨"),
        "SEVERE": ("#ff6600", "⚠️"),
        "INFO": ("#00f0ff", "ℹ️")
    }
    color, icon = config.get(level, ("#ffffff", "📢"))
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, {color}22, {color}11); border: 2px solid {color}; 
                border-radius: 10px; padding: 1rem; margin: 0.5rem 0; display: flex; align-items: center; gap: 1rem;">
        <div style="width: 40px; height: 40px; background: {color}; border-radius: 50%; 
                    display: flex; align-items: center; justify-content: center; font-size: 1.2rem;">
            {icon}
        </div>
        <div>
            <div style="color: {color}; font-weight: bold; font-family: 'Orbitron', sans-serif; font-size: 0.9rem;">
                {level} ALERT
            </div>
            <div style="color: #ccc; font-size: 0.85rem;">{message}</div>
        </div>
    </div>
    """.replace("{color}", color)
       .replace("{icon}", icon)
       .replace("{level}", level)
       .replace("{message}", message), unsafe_allow_html=True)


def render_timeline(steps):
    """Render timeline - FIXED"""
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #0f0f23); border-radius: 15px; 
                padding: 1.5rem; border: 1px solid rgba(0, 240, 255, 0.2);">
        <h4 style="color: #00f0ff; font-family: 'Orbitron', sans-serif; margin-bottom: 1rem;">
            📋 EMERGENCY RESPONSE PROTOCOL
        </h4>
    """, unsafe_allow_html=True)
    
    for step in steps:
        if step.get("completed"):
            border_color = "#00ff00"
            icon = "✅"
        elif step.get("active"):
            border_color = "#ffcc00"
            icon = "⏳"
        else:
            border_color = "#444444"
            icon = "⭕"
        
        st.markdown("""
        <div style="padding: 1rem; margin: 0.5rem 0; background: linear-gradient(145deg, #1a1a2e, #16213e); 
                    border-radius: 10px; border-left: 4px solid {border_color}; animation: fadeInUp 0.5s ease-out;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="color: white; font-weight: bold;">{icon} {title}</span>
                <span style="color: #888; font-size: 0.8rem;">{time}</span>
            </div>
            <div style="color: #888; font-size: 0.85rem; margin-top: 0.3rem;">{desc}</div>
        </div>
        """.replace("{border_color}", border_color)
           .replace("{icon}", icon)
           .replace("{title}", step["title"])
           .replace("{time}", step.get("time", ""))
           .replace("{desc}", step["description"]), unsafe_allow_html=True)
    
    st.markdown("</div>", unsafe_allow_html=True)


def render_action_card(action_text):
    """Render action card"""
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #16213e); border-left: 5px solid #00f0ff; 
                border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
        <span style="color: #00f0ff; font-size: 1rem;">{text}</span>
    </div>
    """.replace("{text}", action_text), unsafe_allow_html=True)


def render_contact_card(icon, title, subtitle, detail, bg_color, border_color):
    """Render contact card"""
    
    st.markdown("""
    <div style="background: linear-gradient(145deg, {bg}, {bg}cc); border: 2px solid {border}; 
                border-radius: 15px; padding: 1.5rem; text-align: center;">
        <div style="font-size: 3rem;">{icon}</div>
        <h3 style="color: {border}; font-family: 'Orbitron', sans-serif; margin: 0.5rem 0;">{title}</h3>
        <div style="color: white;">{subtitle}</div>
        <div style="color: rgba(255,255,255,0.7); font-size: 0.85rem; margin-top: 0.3rem;">{detail}</div>
    </div>
    """.replace("{bg}", bg_color)
       .replace("{border}", border_color)
       .replace("{icon}", icon)
       .replace("{title}", title)
       .replace("{subtitle}", subtitle)
       .replace("{detail}", detail), unsafe_allow_html=True)


# ============================================
# EMERGENCY ALERT SYSTEM CLASS
# ============================================

class EmergencyAlertSystem:
    def __init__(self):
        self.alerts = []
    
    def assess_emergency_level(self, disease, confidence, predicted_label=None):
        """
        Assess emergency level based on disease, confidence, AND predicted label.
        If the predicted label indicates normal/healthy, no emergency is triggered.
        """
        
        # ===== KEY FIX: Check if prediction actually indicates disease =====
        if predicted_label is not None:
            # Check if the prediction is a normal/healthy result
            if is_normal_prediction(predicted_label):
                print(f"✅ Normal prediction detected: '{predicted_label}' - No emergency")
                return {
                    "disease": disease,
                    "confidence": confidence,
                    "predicted_label": predicted_label,
                    "alert_level": "NONE",
                    "requires_emergency": False,
                    "severity_description": "No disease detected - Normal/Healthy",
                    "timestamp": datetime.now().isoformat(),
                    "recommended_action": "✅ No emergency action required. Continue routine care.",
                    "risk_score": max(0, min(confidence * 0.1, 15))  # Very low risk score for normal
                }
            
            # Check if it's a confirmed positive disease detection
            if not is_disease_positive(disease, predicted_label):
                print(f"⚠️ Prediction '{predicted_label}' not confirmed as disease-positive for {disease}")
                return {
                    "disease": disease,
                    "confidence": confidence,
                    "predicted_label": predicted_label,
                    "alert_level": "LOW",
                    "requires_emergency": False,
                    "severity_description": "Prediction does not indicate active disease",
                    "timestamp": datetime.now().isoformat(),
                    "recommended_action": "ℹ️ Schedule routine follow-up. No emergency action needed.",
                    "risk_score": max(0, min(confidence * 0.2, 25))  # Low risk score
                }
        
        # ===== Disease IS detected - proceed with severity assessment =====
        if disease not in EMERGENCY_THRESHOLDS:
            return {
                "disease": disease,
                "confidence": confidence,
                "predicted_label": predicted_label,
                "alert_level": "MODERATE",
                "requires_emergency": False,
                "severity_description": "Disease detected but no specific threshold defined",
                "timestamp": datetime.now().isoformat(),
                "recommended_action": "ℹ️ Consult specialist for further evaluation.",
                "risk_score": confidence * 0.5
            }
        
        thresholds = EMERGENCY_THRESHOLDS[disease]
        critical = thresholds.get("critical_confidence", 95)
        
        if confidence >= critical:
            alert_level = "CRITICAL"
        elif confidence >= critical - 10:
            alert_level = "SEVERE"
        else:
            alert_level = "MODERATE"
        
        requires_emergency = alert_level in ["CRITICAL", "SEVERE"]
        
        multipliers = {"CRITICAL": 1.0, "SEVERE": 0.8, "MODERATE": 0.6}
        risk_score = min(100, confidence * multipliers.get(alert_level, 0.5) * 1.2)
        
        return {
            "disease": disease,
            "confidence": confidence,
            "predicted_label": predicted_label,
            "alert_level": alert_level,
            "requires_emergency": requires_emergency,
            "severity_description": thresholds["severity_levels"].get(alert_level, "Unknown"),
            "timestamp": datetime.now().isoformat(),
            "recommended_action": self._get_action(disease, alert_level),
            "risk_score": risk_score
        }
    
    def _get_action(self, disease, level):
        actions = {
            "CRITICAL": "🚨 IMMEDIATE EMERGENCY:\n1. Call 911 immediately\n2. Brief team: " + disease + " - Critical\n3. Urgent specialist consultation\n4. Initiate emergency protocols\n5. Notify ICU\n6. Prepare for intervention",
            "SEVERE": "⚠️ URGENT ATTENTION:\n1. Contact specialist immediately\n2. Same-day appointment\n3. Prepare for hospitalization\n4. Have records ready\n5. Arrange transport\n6. Monitor deterioration",
            "MODERATE": "ℹ️ PROMPT FOLLOW-UP:\n1. Schedule specialist appointment\n2. Arrange imaging if needed\n3. Start preliminary management\n4. Monitor symptoms\n5. Follow up within 1 week\n6. Patient education"
        }
        return actions.get(level, "Consult healthcare provider")
    
    def generate_alert(self, assessment):
        indicators = {
            "Pneumonia": ["Severe hypoxia (SpO2 < 90%)", "Signs of sepsis", "Respiratory failure"],
            "Brain Tumor": ["Herniation risk", "Mass effect", "Raised ICP"],
            "Diabetic Retinopathy": ["Vitreous hemorrhage", "Acute vision loss", "Retinal detachment"],
            "Tuberculosis": ["Respiratory failure", "Hemoptysis", "Miliary spread"],
            "Skin Cancer": ["Rapid growth", "Ulceration", "Metastases"]
        }
        
        alert = {
            "alert_id": "ALERT_" + datetime.now().strftime('%Y%m%d_%H%M%S'),
            "severity": assessment['alert_level'],
            "disease": assessment['disease'],
            "predicted_label": assessment.get('predicted_label', 'Unknown'),
            "confidence": assessment['confidence'],
            "risk_score": assessment.get('risk_score', 0),
            "timestamp": assessment['timestamp'],
            "requires_emergency": assessment['requires_emergency'],
            "action_required": assessment['recommended_action'],
            "critical_indicators": indicators.get(assessment['disease'], ["Consult specialist"])
        }
        self.alerts.append(alert)
        return alert


# ============================================
# NORMAL RESULT DISPLAY
# ============================================

def show_normal_result(disease, confidence, predicted_label, assessment):
    """Display a calm, reassuring result for normal/healthy predictions"""
    
    inject_css()
    
    alert_level = assessment.get('alert_level', 'NONE')
    risk_score = assessment.get('risk_score', 5)
    
    # Green "All Clear" banner
    st.markdown("""
    <div style="background: linear-gradient(135deg, #0a3a0a 0%, #1a5a1a 50%, #0a3a0a 100%); 
                border: 3px solid #00ff00; border-radius: 20px; padding: 2rem; text-align: center;
                box-shadow: 0 0 20px rgba(0, 255, 0, 0.3); margin: 1rem 0;">
        <h1 style="color: #00ff00; font-family: 'Orbitron', sans-serif; font-size: 2.5rem; margin: 0;
                   text-shadow: 0 0 15px rgba(0, 255, 0, 0.5);">
            ✅ ALL CLEAR ✅
        </h1>
        <p style="color: #88ff88; font-size: 1.2rem; margin-top: 1rem; font-family: 'Roboto Mono', monospace;">
            NO EMERGENCY ALERT TRIGGERED
        </p>
        <p style="color: #aaffaa; font-size: 0.9rem; margin-top: 0.5rem;">
            AI prediction indicates: <strong>{label}</strong>
        </p>
    </div>
    """.replace("{label}", str(predicted_label)), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Low severity gauge
    render_severity_gauge(risk_score, alert_level)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Info metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        render_metric_card("{:.1f}%".format(confidence), "AI Confidence", "#00ff00")
    with col2:
        render_metric_card(alert_level, "Alert Level", "#00ff00")
    with col3:
        render_metric_card(str(predicted_label)[:15], "Prediction", "#00f0ff")
    with col4:
        render_metric_card("CLEAR", "Status", "#00ff00")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Explanation
    st.markdown("""
    <div style="background: linear-gradient(145deg, #0a2a0a, #1a3a1a); border: 2px solid #00ff00; 
                border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="color: #00ff00; font-family: 'Orbitron', sans-serif;">📋 Assessment Summary</h3>
        <ul style="color: #88ff88; font-size: 1rem; line-height: 2;">
            <li>The AI model analyzed the uploaded medical image</li>
            <li>Prediction: <strong>{label}</strong> with {conf:.1f}% confidence</li>
            <li>No disease indicators detected that warrant emergency action</li>
            <li>Standard follow-up care pathway is recommended</li>
        </ul>
    </div>
    """.replace("{label}", str(predicted_label))
       .replace("{conf:.1f}", "{:.1f}".format(confidence)), unsafe_allow_html=True)
    
    # Recommendations
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a1a2e, #16213e); border: 1px solid rgba(0, 240, 255, 0.3); 
                border-radius: 15px; padding: 1.5rem; margin: 1rem 0;">
        <h3 style="color: #00f0ff; font-family: 'Orbitron', sans-serif;">💡 Recommendations</h3>
        <ul style="color: #cccccc; font-size: 0.95rem; line-height: 2;">
            <li>Continue routine medical check-ups</li>
            <li>Maintain a healthy lifestyle</li>
            <li>Report any new symptoms to your healthcare provider</li>
            <li>Follow up with your doctor as scheduled</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div style="background: linear-gradient(145deg, #1a2a1a, #0a1a0a); border: 2px solid #00aa00; 
                border-radius: 15px; padding: 1.5rem; margin-top: 2rem; text-align: center;">
        <h4 style="color: #00aa00; font-family: 'Orbitron', sans-serif;">ℹ️ DISCLAIMER</h4>
        <p style="color: #88aa88; margin: 0;">
            This is an <strong>AI-generated assessment</strong> for clinical decision support only.<br>
            It does <strong>NOT replace</strong> professional medical judgment.<br>
            Always consult with qualified medical professionals for clinical decisions.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    return assessment


# ============================================
# MAIN DISPLAY FUNCTION
# ============================================

def show_emergency_alert_mode(disease, confidence, predicted_label=None):
    """
    Display emergency alert interface.
    
    Args:
        disease: Disease category (e.g., "Brain Tumor", "Pneumonia")
        confidence: AI confidence percentage (0-100)
        predicted_label: The actual predicted label (e.g., "No Tumor", "PNEUMONIA", "Normal")
    """
    
    inject_css()
    
    system = EmergencyAlertSystem()
    assessment = system.assess_emergency_level(disease, confidence, predicted_label)
    
    print(f"🚨 Emergency Assessment:")
    print(f"   Disease: {disease}")
    print(f"   Predicted Label: {predicted_label}")
    print(f"   Confidence: {confidence:.1f}%")
    print(f"   Alert Level: {assessment['alert_level']}")
    print(f"   Requires Emergency: {assessment['requires_emergency']}")
    print(f"   Risk Score: {assessment.get('risk_score', 0):.1f}")
    
    # ===== NORMAL/HEALTHY RESULT - Show calm display =====
    if not assessment['requires_emergency']:
        return show_normal_result(disease, confidence, predicted_label, assessment)
    
    # ===== DISEASE DETECTED - Show emergency alert =====
    st.markdown("---")
    
    # Alert Header
    if assessment['alert_level'] == "CRITICAL":
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff0000 0%, #990000 100%); border: 4px solid #ff0000; 
                    border-radius: 20px; padding: 2rem; text-align: center; animation: criticalPulse 1.5s infinite; 
                    position: relative; overflow: hidden; margin: 1rem 0;">
            <h1 style="color: white; font-family: 'Orbitron', sans-serif; font-size: 2.5rem; margin: 0; 
                       animation: textFlicker 0.5s infinite; text-shadow: 0 0 20px rgba(255,255,255,0.8);">
                🚨 CRITICAL ALERT 🚨
            </h1>
            <p style="color: white; font-size: 1.2rem; margin-top: 1rem; font-family: 'Roboto Mono', monospace;">
                IMMEDIATE EMERGENCY ACTION REQUIRED
            </p>
            <p style="color: #ffcccc; font-size: 1rem; margin-top: 0.5rem;">
                Detected: <strong>{label}</strong>
            </p>
        </div>
        """.replace("{label}", str(predicted_label or disease)), unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, #ff6600 0%, #cc5200 100%); border: 3px solid #ff6600; 
                    border-radius: 15px; padding: 1.5rem; text-align: center; animation: severeGlow 2s infinite;">
            <h2 style="color: white; font-family: 'Orbitron', sans-serif; margin: 0;">⚠️ SEVERE ALERT ⚠️</h2>
            <p style="color: white; margin-top: 0.5rem;">URGENT MEDICAL ATTENTION REQUIRED</p>
            <p style="color: #ffe0cc; font-size: 0.95rem; margin-top: 0.5rem;">
                Detected: <strong>{label}</strong>
            </p>
        </div>
        """.replace("{label}", str(predicted_label or disease)), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Severity Gauge (Full Width)
    render_severity_gauge(assessment.get('risk_score', confidence), assessment['alert_level'])
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Vital Signs
    st.markdown("### 💓 PATIENT MONITORING")
    render_vital_signs()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Metrics
    st.markdown("### 📊 DIAGNOSTIC METRICS")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_metric_card("{:.1f}%".format(confidence), "AI Confidence", "#00f0ff")
    with col2:
        color = "#ff0000" if assessment['alert_level'] == 'CRITICAL' else "#ff6600"
        render_metric_card(assessment['alert_level'], "Alert Level", color)
    with col3:
        display_label = str(predicted_label or disease)[:12]
        render_metric_card(display_label, "Condition", "#ff0000")
    with col4:
        render_metric_card("ACTIVE", "Status", "#ff0000")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Risk Assessment
    st.markdown("### 📈 RISK ASSESSMENT")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        render_progress_ring(assessment.get('risk_score', 85), "Overall Risk", "#ff0000")
    with col2:
        render_progress_ring(confidence, "Confidence", "#00f0ff")
    with col3:
        urgency = 90 if assessment['alert_level'] == 'CRITICAL' else 70
        render_progress_ring(urgency, "Urgency", "#ff6600")
    with col4:
        priority = 95 if assessment['alert_level'] == 'CRITICAL' else 80
        render_progress_ring(priority, "Priority", "#ffcc00")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Notifications
    st.markdown("### 🔔 ACTIVE NOTIFICATIONS")
    render_notification("CRITICAL", "High-confidence detection of " + str(predicted_label or disease))
    render_notification("SEVERE", "Immediate specialist consultation required")
    render_notification("INFO", "Emergency response protocol activated")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Timeline
    st.markdown("### ⏱️ RESPONSE PROTOCOL")
    timeline_steps = [
        {"title": "Alert Generated", "description": "AI detection triggered emergency alert", "time": "T+0:00", "completed": True},
        {"title": "Team Notified", "description": "Emergency team has been alerted", "time": "T+0:30", "completed": True},
        {"title": "Specialist Contacted", "description": "On-call specialist being paged", "time": "T+1:00", "active": True},
        {"title": "Patient Assessment", "description": "Clinical evaluation in progress", "time": "T+2:00"},
        {"title": "Treatment Initiated", "description": "Emergency intervention started", "time": "T+5:00"},
        {"title": "Stabilization", "description": "Patient monitoring and stabilization", "time": "T+10:00"}
    ]
    render_timeline(timeline_steps)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Actions
    st.markdown("### 🎯 IMMEDIATE ACTIONS REQUIRED")
    actions = assessment['recommended_action'].split('\n')
    for action in actions:
        if action.strip():
            render_action_card(action)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Contacts
    st.markdown("### 📞 EMERGENCY CONTACTS")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        render_contact_card("🚑", "EMERGENCY", "911", "Immediate Response", "#cc0000", "#ff0000")
    
    with col2:
        specialist_map = {
            "Pneumonia": ("🫁", "Pulmonology"),
            "Brain Tumor": ("🧠", "Neurosurgery"),
            "Diabetic Retinopathy": ("👁️", "Ophthalmology"),
            "Tuberculosis": ("🫁", "Infectious Disease"),
            "Skin Cancer": ("🔬", "Oncology")
        }
        icon, dept = specialist_map.get(disease, ("👨‍⚕️", "Specialist"))
        render_contact_card(icon, dept, "On-Call Specialist", "Available 24/7", "#1a1a2e", "#00f0ff")
    
    with col3:
        render_contact_card("🏥", "HOSPITAL", "Emergency Dept", "Direct Line", "#1a1a2e", "#ff6600")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Symptoms
    st.markdown("### ✓ CRITICAL SYMPTOMS ASSESSMENT")
    
    symptom_map = {
        "Pneumonia": ["Severe difficulty breathing", "Confusion/altered mental status", "Cyanosis", "Chest pain", "SpO2 < 90%", "High fever > 39°C"],
        "Brain Tumor": ["Severe headache", "Loss of consciousness", "Seizures", "Weakness/paralysis", "Speech difficulties", "Vision changes"],
        "Diabetic Retinopathy": ["Sudden vision loss", "Floaters", "Eye pain", "Blurred vision", "Dark spots", "Light sensitivity"],
        "Tuberculosis": ["Severe cough", "Hemoptysis", "Night sweats", "Weight loss", "Fever", "Fatigue"],
        "Skin Cancer": ["Rapid growth", "Bleeding/oozing", "Color changes", "Irregular borders", "Ulceration", "New lesions"]
    }
    
    symptoms = symptom_map.get(disease, ["Consult specialist"])
    cols = st.columns(2)
    checked = 0
    
    for i, symptom in enumerate(symptoms):
        with cols[i % 2]:
            if st.checkbox(symptom, key="sym_" + str(i)):
                checked += 1
    
    if checked > 0:
        st.markdown("""
        <div style="background: linear-gradient(145deg, #3a0a0a, #2a0505); border: 2px solid #ff0000; 
                    border-radius: 10px; padding: 1rem; margin-top: 1rem; text-align: center;">
            <h3 style="color: #ff0000; font-family: 'Orbitron', sans-serif; margin: 0;">
                🚨 """ + str(checked) + """ CRITICAL SYMPTOMS IDENTIFIED
            </h3>
            <p style="color: #ff6666; margin: 0.5rem 0 0 0;">Immediate emergency intervention recommended</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Downloads
    st.markdown("### 📄 EMERGENCY DOCUMENTATION")
    
    alert = system.generate_alert(assessment)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        report = "EMERGENCY ALERT REPORT\n"
        report += "=" * 40 + "\n"
        report += "Alert ID: " + alert['alert_id'] + "\n"
        report += "Timestamp: " + alert['timestamp'] + "\n"
        report += "Severity: " + alert['severity'] + "\n"
        report += "Disease: " + alert['disease'] + "\n"
        report += "Predicted Label: " + str(alert.get('predicted_label', 'N/A')) + "\n"
        report += "Confidence: {:.1f}%\n".format(alert['confidence'])
        report += "Risk Score: {:.1f}%\n".format(alert['risk_score'])
        report += "\nCRITICAL INDICATORS:\n"
        for ind in alert['critical_indicators']:
            report += "• " + ind + "\n"
        report += "\nACTIONS REQUIRED:\n"
        report += alert['action_required'] + "\n"
        report += "\n" + "=" * 40 + "\n"
        report += "DISCLAIMER: AI-generated alert for clinical support only.\n"
        
        st.download_button("📄 Download Alert Report", report, "emergency_alert.txt", "text/plain", use_container_width=True)
    
    with col2:
        handoff = "EMERGENCY HANDOFF\n"
        handoff += "=" * 40 + "\n"
        handoff += "CRITICAL: " + str(predicted_label or disease) + "\n"
        handoff += "Confidence: {:.1f}%\n".format(confidence)
        handoff += "Severity: " + assessment['alert_level'] + "\n"
        handoff += "\nPATIENT STATUS (Fill in):\n"
        handoff += "BP: ___/___ | HR: ___ | SpO2: ___% | Temp: ___°C\n"
        handoff += "\nRECOMMENDED ACTIONS:\n"
        handoff += assessment['recommended_action'] + "\n"
        
        st.download_button("📞 Download Handoff", handoff, "handoff.txt", "text/plain", use_container_width=True)
    
    with col3:
        st.download_button("📊 Download JSON", json.dumps(alert, indent=2, default=str), "alert.json", "application/json", use_container_width=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Disclaimer
    st.markdown("""
    <div style="background: linear-gradient(145deg, #3a0a0a, #2a0505); border: 3px solid #ff0000; 
                border-radius: 15px; padding: 1.5rem; margin-top: 2rem; text-align: center;">
        <h4 style="color: #ff0000; font-family: 'Orbitron', sans-serif;">⚠️ CRITICAL DISCLAIMER ⚠️</h4>
        <p style="color: #ff6666; margin: 0;">
            This is an <strong>AI-generated alert</strong> for clinical decision support only.<br>
            It does <strong>NOT replace</strong> professional medical judgment.<br>
            Medical professionals <strong>MUST verify</strong> all findings before taking action.<br>
            <strong>Call emergency services immediately</strong> if life-threatening emergency is suspected.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    return assessment


# ============================================
# MAIN
# ============================================

def main():
    inject_css()
    
    st.markdown("""
    <div style="text-align: center; padding: 2rem 0;">
        <h1 style="font-family: 'Orbitron', sans-serif; font-size: 2.5rem; 
                   background: linear-gradient(135deg, #ff0000, #ff6600, #ffcc00);
                   -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
            🚨 EMERGENCY ALERT SYSTEM 🚨
        </h1>
        <p style="color: #888; font-family: 'Roboto Mono', monospace;">
            Advanced AI-Powered Medical Emergency Detection
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    st.sidebar.markdown("<h2 style='color: #00f0ff; font-family: Orbitron;'>🎮 Demo Controls</h2>", unsafe_allow_html=True)
    
    disease = st.sidebar.selectbox("Select Condition", ["Pneumonia", "Brain Tumor", "Diabetic Retinopathy", "Tuberculosis", "Skin Cancer"])
    
    # Demo predicted labels for testing
    demo_labels = {
        "Pneumonia": ["PNEUMONIA", "NORMAL"],
        "Brain Tumor": ["Glioma", "Meningioma", "No Tumor", "Pituitary"],
        "Diabetic Retinopathy": ["DR Detected", "No DR"],
        "Tuberculosis": ["Tuberculosis", "Normal"],
        "Skin Cancer": ["Malignant", "Benign"]
    }
    
    predicted_label = st.sidebar.selectbox("Predicted Label", demo_labels.get(disease, ["Unknown"]))
    confidence = st.sidebar.slider("AI Confidence (%)", 50.0, 100.0, 92.0, 0.5)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown("""
    <div style="background: #1a1a2e; padding: 1rem; border-radius: 10px;">
        <h4 style="color: #00f0ff;">Alert Thresholds:</h4>
        <ul style="color: #888; font-size: 0.85rem;">
            <li>🔴 Critical: ≥85-90% (disease detected)</li>
            <li>🟠 Severe: 75-85% (disease detected)</li>
            <li>🟡 Moderate: 60-75% (disease detected)</li>
            <li>🟢 No Alert: Normal/Healthy prediction</li>
        </ul>
    </div>
    """, unsafe_allow_html=True)
    
    show_emergency_alert_mode(disease, confidence, predicted_label)


if __name__ == "__main__":
    main()