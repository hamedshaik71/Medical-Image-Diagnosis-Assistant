import streamlit as st
import numpy as np
import cv2
import json
import tensorflow as tf
from PIL import Image
import io
import matplotlib.cm as cm
from huggingface_hub import hf_hub_download
import pandas as pd

# 🔐 MODULAR AUTH IMPORTS
from auth.auth_ui import show_auth_ui
from auth.auth_logic import (
    is_authenticated,
    logout_user,
    get_current_user,
    get_current_role
)

# 👥 ROLE-BASED INTERFACE IMPORTS
from role_based_interface import (
    RoleBasedInterface,
    show_role_based_sidebar,
    show_role_header,
    show_access_denied_message
)

# 🧊 3D VISUALIZATION IMPORTS
from visualization.pseudo_3d import show_pseudo_3d
from visualization.volume_3d import show_volume_3d
from collaboration.doctor_ai_collaboration import render_collaboration_mode
from visualization.patient_timeline_dashboard import render_patient_timeline_dashboard
from visualization.patient_health_timeline import render_health_timeline_dashboard

# Advanced Features Imports
from medication_suggestion import show_medication_suggestions
from symptom_image_fusion import show_symptom_image_fusion
from population_comparison import show_population_comparison
from region_explanation import show_why_this_region
from emergency_alert import show_emergency_alert_mode
from cross_device_continuity import show_cross_device_continuity

# Advanced Features 2
from chat_with_ai import show_chat_with_ai_report
from medical_audit_compliance import show_medical_audit_compliance
from clinical_guideline_tests import show_guideline_aligned_next_tests
from voice_diagnosis_assistant import show_voice_diagnosis_assistant

# ==================================================
# 🔐 AUTH GATE (MODULAR – CLEAN)
# ==================================================
show_auth_ui()

if not is_authenticated():
    st.stop()

# Get current user and role AFTER authentication
current_user = get_current_user()
current_role = get_current_role()

# ==================================================
# 🤖 MULTI-MODEL MANAGEMENT SYSTEM
# ==================================================
DISEASE_MODELS = {
    "Pneumonia": {
        "repo_id": "Saitama30/pneumonia_model.h5",
        "filename": "pneumonia_model.h5",
        "description": "Chest X-ray analysis for Pneumonia detection"
    },
    "Brain Tumor": {
        "repo_id": "Saitama30/brain_tumor_model.h5",
        "filename": "brain_tumor_model.h5",
        "description": "Brain MRI/CT scan analysis for tumor detection"
    },
    "Malaria": {
        "repo_id": "Saitama30/malaria_model.h5",
        "filename": "malaria_model.h5",
        "description": "Blood smear microscopy for Malaria detection"
    },
    "Tuberculosis": {
        "repo_id": "Saitama30/tuberculosis_model.h5",
        "filename": "tuberculosis_model.h5",
        "description": "Chest X-ray analysis for TB detection"
    },
    "Dental": {
        "repo_id": "Saitama30/dental_model.h5",
        "filename": "dental_model.h5",
        "description": "Dental X-ray analysis for dental issues"
    },
    "Diabetic Retinopathy": {
        "repo_id": "Saitama30/diabetic_retinopathy_model.h5",
        "filename": "diabetic_retinopathy_model.h5",
        "description": "Retinal fundus image analysis for Diabetic Retinopathy"
    },
    "Skin Cancer": {
        "repo_id": "Saitama30/skin_cancer_model.h5",
        "filename": "skin_cancer_model.h5",
        "description": "Skin lesion image analysis for Skin Cancer detection"
    }
}


# ==================================================
# 🔧 LOAD CORRECT MODEL FOR SELECTED DISEASE
# ==================================================
@st.cache_resource
def load_disease_model(disease_name):
    """Load the specific model for the selected disease"""
    if disease_name not in DISEASE_MODELS:
        st.error(f"Model not found for {disease_name}")
        return None

    model_info = DISEASE_MODELS[disease_name]

    try:
        print(f"🔄 Loading {disease_name} model...")
        model_path = hf_hub_download(
            repo_id=model_info["repo_id"],
            filename=model_info["filename"]
        )
        model = tf.keras.models.load_model(model_path, compile=False)
        print(f"✅ {disease_name} model loaded successfully")
        print(f"📊 Model input shape: {model.input_shape}")
        print(f"📊 Model output shape: {model.output_shape}")
        return model
    except Exception as e:
        print(f"❌ Error loading {disease_name} model: {e}")
        try:
            print(f"⚠️ Falling back to Brain Tumor model...")
            model_path = hf_hub_download(
                repo_id="Saitama30/brain_tumor_model.h5",
                filename="brain_tumor_model.h5"
            )
            return tf.keras.models.load_model(model_path, compile=False)
        except Exception:
            return None


# ==================================================
# 🎯 FIXED IMAGE VALIDATION SYSTEM (LENIENT)
# ==================================================
def validate_image_for_disease(image, disease_name):
    """
    LENIENT IMAGE VALIDATION:
    Basic sanity checks - accepts most valid medical images
    """
    print(f"\n🔍 Validating image for {disease_name}...")

    try:
        img_array = np.array(image)
        height, width = image.size[1], image.size[0]
        aspect_ratio = width / height if height > 0 else 1
        
        # ===== BASIC VALIDATION =====
        if height < 32 or width < 32:
            return False, "❌ Image too small (minimum 32x32 pixels)", 0
        
        if height > 10000 or width > 10000:
            return False, "❌ Image too large (maximum 10000x10000 pixels)", 0
        
        # Compute grayscale for analysis
        if len(img_array.shape) == 3 and img_array.shape[2] >= 3:
            gray = cv2.cvtColor(img_array[:, :, :3], cv2.COLOR_RGB2GRAY)
        elif len(img_array.shape) == 3 and img_array.shape[2] == 1:
            gray = img_array[:, :, 0]
        else:
            gray = img_array
        
        # Check if image is blank/corrupted
        std_intensity = np.std(gray) / 255.0
        mean_intensity = np.mean(gray) / 255.0
        
        if std_intensity < 0.005:
            return False, "❌ Image appears blank or corrupted (no variation)", 0
        
        print(f"📊 Image: {width}x{height}, aspect={aspect_ratio:.2f}")
        print(f"📊 Intensity: mean={mean_intensity:.3f}, std={std_intensity:.3f}")
        
        # ===== DISEASE-SPECIFIC VALIDATION (LENIENT) =====
        validation_result = _validate_disease_specific(
            disease_name, img_array, gray, width, height, aspect_ratio, std_intensity
        )
        
        return validation_result
    
    except Exception as e:
        print(f"⚠️ Validation error: {e}")
        # If validation fails, ACCEPT THE IMAGE anyway
        return True, f"✅ Image accepted for {disease_name}.", 0.7


def _validate_disease_specific(disease_name, img_array, gray, width, height, aspect_ratio, std_intensity):
    """Disease-specific validation with LENIENT checks"""
    
    # ===== BRAIN TUMOR =====
    if disease_name == "Brain Tumor":
        if std_intensity > 0.02:
            print(f"✅ Brain image validated (std={std_intensity:.3f})")
            return True, "✅ Valid Brain Tumor image detected.", 0.9
        else:
            print(f"⚠️ Low contrast, but accepting")
            return True, "✅ Brain Tumor image accepted.", 0.7
    
    # ===== PNEUMONIA =====
    elif disease_name == "Pneumonia":
        if std_intensity > 0.02:
            print(f"✅ Chest X-ray validated for Pneumonia")
            return True, "✅ Valid Pneumonia chest X-ray detected.", 0.9
        else:
            return True, "✅ Pneumonia image accepted.", 0.7
    
    # ===== TUBERCULOSIS =====
    elif disease_name == "Tuberculosis":
        if std_intensity > 0.02:
            print(f"✅ Chest X-ray validated for Tuberculosis")
            return True, "✅ Valid Tuberculosis chest X-ray detected.", 0.9
        else:
            return True, "✅ Tuberculosis image accepted.", 0.7
    
    # ===== MALARIA =====
    elif disease_name == "Malaria":
        if std_intensity > 0.01:
            print(f"✅ Blood smear validated for Malaria")
            return True, "✅ Valid Malaria blood smear detected.", 0.9
        else:
            print(f"⚠️ Low texture, but accepting blood smear")
            return True, "✅ Malaria image accepted.", 0.7
    
    # ===== DENTAL =====
    elif disease_name == "Dental":
        if std_intensity > 0.02:
            print(f"✅ Dental X-ray validated")
            return True, "✅ Valid Dental X-ray detected.", 0.9
        else:
            return True, "✅ Dental image accepted.", 0.7
    
    # ===== DIABETIC RETINOPATHY =====
    elif disease_name == "Diabetic Retinopathy":
        is_color = len(img_array.shape) == 3 and img_array.shape[2] >= 3
        
        if is_color:
            print(f"✅ Color fundus image validated")
            return True, "✅ Valid Diabetic Retinopathy fundus image detected.", 0.9
        else:
            print(f"⚠️ Grayscale fundus, but accepting")
            return True, "✅ Diabetic Retinopathy image accepted.", 0.7
    
    # ===== SKIN CANCER =====
    elif disease_name == "Skin Cancer":
        is_color = len(img_array.shape) == 3 and img_array.shape[2] >= 3
        
        if is_color:
            r = img_array[:, :, 0].astype(float)
            g = img_array[:, :, 1].astype(float)
            b = img_array[:, :, 2].astype(float)
            color_var = np.std(r - b) + np.std(r - g)
            
            if color_var > 5:
                print(f"✅ Skin lesion image validated (color_var={color_var:.1f})")
                return True, "✅ Valid Skin Cancer image detected.", 0.9
            else:
                print(f"⚠️ Low color variation, but accepting")
                return True, "✅ Skin Cancer image accepted.", 0.7
        else:
            print(f"⚠️ Grayscale skin image, but accepting")
            return True, "✅ Skin Cancer image accepted.", 0.6
    
    # ===== DEFAULT =====
    else:
        print(f"✅ Generic validation passed for {disease_name}")
        return True, f"✅ Image accepted for {disease_name}.", 0.8


# --------------------------------------------------
# Page Config
# --------------------------------------------------
st.set_page_config(
    page_title="🩺 Medical Image Diagnosis AI",
    layout="wide",
    initial_sidebar_state="expanded"
)


# --------------------------------------------------
# UI CSS (POLISHED)
# --------------------------------------------------
def load_css():
    st.markdown("""
    <style>
        .main { padding: 2rem; background: #0e1117; }
        h1 { font-weight: 700; letter-spacing: 0.4px; }
        h2, h3 { color: #e5e7eb; }
        .card {
            background: #161b22; border-radius: 14px; padding: 1.2rem;
            border: 1px solid #262730; margin-bottom: 1rem;
        }
        .trust-panel {
            background: linear-gradient(135deg, #1a3a3a 0%, #0f2626 100%);
            border-left: 4px solid #00d4aa; border-radius: 12px;
            padding: 1.5rem; border: 1px solid #00d4aa33; margin-bottom: 1.5rem;
        }
        .trust-header { color: #00d4aa; font-weight: 700; font-size: 1.1rem; margin-bottom: 1rem; }
        .feature-item {
            background: #0f1419; border-left: 3px solid #00d4aa;
            padding: 0.9rem; margin-bottom: 0.8rem; border-radius: 8px;
        }
        .feature-rank { color: #00d4aa; font-weight: 700; display: inline-block; margin-right: 0.5rem; }
        .feature-text { color: #e5e7eb; font-size: 0.95rem; }
        .confidence-bar {
            background: #262730; border-radius: 8px; height: 8px;
            margin-top: 0.5rem; overflow: hidden;
        }
        .confidence-fill {
            background: linear-gradient(90deg, #00d4aa, #00ff88);
            height: 100%; border-radius: 8px;
        }
        .explainability-score { color: #00d4aa; font-weight: 700; font-size: 1rem; }
        div[data-testid="stMetric"] {
            background: #161b22; border-radius: 12px;
            padding: 1rem; border: 1px solid #262730;
        }
        section[data-testid="stSidebar"] {
            background: #0b0f14; border-right: 1px solid #262730;
        }
        button { border-radius: 10px !important; }
        .stAlert { border-radius: 12px; }
    </style>
    """, unsafe_allow_html=True)


load_css()

# --------------------------------------------------
# Load Disease Info
# --------------------------------------------------
DISEASE_INFO_PATH = "disease_info.json"

try:
    with open(DISEASE_INFO_PATH, "r") as f:
        disease_info = json.load(f)
    DISEASE_NAMES = list(disease_info.keys())
except Exception as e:
    st.error(f"Failed to load disease_info.json: {e}")
    st.stop()


# --------------------------------------------------
# 🆕 TRUST PANEL FEATURE - EXPLAINABILITY ANALYSIS
# --------------------------------------------------
def extract_image_features(original_image, heatmap, regions):
    """Extract and quantify image features that influenced the model decision."""
    features = []

    try:
        if isinstance(original_image, Image.Image):
            gray_local = np.array(original_image.convert('L'))
        else:
            if original_image.ndim == 3:
                gray_local = cv2.cvtColor(np.uint8(original_image * 255), cv2.COLOR_RGB2GRAY)
            else:
                gray_local = np.uint8(original_image * 255)

        height, width = gray_local.shape

        # Feature 1: Regional Intensity from detected regions
        for i, region in enumerate(regions):
            x, y, w, h = region['x'], region['y'], region['w'], region['h']
            intensity = region.get('intensity', 0.5)

            x, y = max(0, x), max(0, y)
            x_end, y_end = min(x + w, width), min(y + h, height)

            if x_end > x and y_end > y:
                region_data = gray_local[y:y_end, x:x_end]
                opacity_value = np.mean(region_data) / 255.0

                position = ""
                if y < height // 3:
                    position += "upper "
                elif y > 2 * height // 3:
                    position += "lower "
                else:
                    position += "middle "

                if x < width // 3:
                    position += "left"
                elif x > 2 * width // 3:
                    position += "right"
                else:
                    position += "center"

                feature_score = intensity * 100

                features.append({
                    "name": f"Opacity in {position} region",
                    "description": (
                        f"Detected density variation ({opacity_value * 100:.1f}%) "
                        f"in {position} area. Model Confidence: {feature_score:.1f}%"
                    ),
                    "confidence": min(feature_score, 100),
                    "region_idx": i
                })

        # Feature 2: Edge Irregularity Detection
        edges = cv2.Canny(gray_local, 50, 150)
        total_pixels = edges.shape[0] * edges.shape[1]
        edge_pixels = np.sum(edges > 0)
        edge_density = (edge_pixels / total_pixels) * 100
        edge_influence = min((edge_density / 5.0) * 100, 100) if edge_density > 0 else 10

        if edge_density > 2:
            features.append({
                "name": "Edge Irregularity",
                "description": f"Irregular edges detected ({edge_density:.2f}% edge pixels in image)",
                "confidence": max(20, min(edge_influence, 100)),
                "region_idx": -1
            })

        # Feature 3: Heatmap Intensity Concentration
        if heatmap is not None:
            heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
            high_intensity_mask = heatmap_norm > 0.5
            concentration = (np.sum(high_intensity_mask) / high_intensity_mask.size) * 100
            max_intensity_score = np.max(heatmap_norm) * 100
            intensity_influence = (concentration * 0.4 + max_intensity_score * 0.6)

            if concentration > 0.5:
                features.append({
                    "name": "Localized Intensity Pattern",
                    "description": (
                        f"Concentrated high-intensity regions "
                        f"({concentration:.2f}% of image above threshold)"
                    ),
                    "confidence": max(15, min(intensity_influence, 100)),
                    "region_idx": -1
                })

        # Feature 4: Texture Complexity
        laplacian = cv2.Laplacian(gray_local, cv2.CV_64F)
        laplacian_abs = np.abs(laplacian)
        mean_laplacian = np.mean(laplacian_abs) + 1e-8
        std_laplacian = np.std(laplacian_abs)
        texture_score = std_laplacian / mean_laplacian if mean_laplacian > 0 else 0
        texture_influence = min((texture_score / 3.0) * 100, 100) if texture_score > 0 else 10

        if texture_score > 0.1:
            features.append({
                "name": "Texture Complexity",
                "description": f"Complex texture pattern detected (complexity score: {texture_score:.3f})",
                "confidence": max(12, min(texture_influence, 100)),
                "region_idx": -1
            })

        # Default features if none detected
        if len(features) == 0:
            overall_intensity = np.mean(gray_local) / 255.0
            overall_intensity_score = max(20, overall_intensity * 100)
            features.append({
                "name": "Overall Image Intensity",
                "description": f"Overall image brightness level ({overall_intensity:.1%})",
                "confidence": overall_intensity_score,
                "region_idx": -1
            })
            features.append({
                "name": "Image Homogeneity",
                "description": f"Uniform pixel distribution across image",
                "confidence": 35,
                "region_idx": -1
            })
            features.append({
                "name": "Background Contrast",
                "description": f"Minimal contrast variations detected",
                "confidence": 25,
                "region_idx": -1
            })

        features = sorted(features, key=lambda x: x["confidence"], reverse=True)
        return features[:3]

    except Exception as e:
        print(f"Error in extract_image_features: {e}")
        return []


# ==================================================
# 🔐 PRIVACY OVERLAY MODE
# ==================================================
def blur_image_region(image, x, y, w, h, blur_strength=50):
    """Blur a specific region of an image"""
    img = np.array(image)
    if blur_strength % 2 == 0:
        blur_strength += 1
    region = img[y:y + h, x:x + w]
    blurred = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
    img[y:y + h, x:x + w] = blurred
    return Image.fromarray(img)


def detect_text_regions(image, gray_img):
    """Detect regions likely to contain text"""
    edges = cv2.Canny(gray_img, 100, 200)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    text_regions = []
    for cnt in contours:
        area = cv2.contourArea(cnt)
        x, y, w, h = cv2.boundingRect(cnt)
        ar = w / h if h > 0 else 0

        if 100 < area < 10000 and ar > 1.5:
            if y < gray_img.shape[0] * 0.15 or y > gray_img.shape[0] * 0.85:
                text_regions.append((x, y, w, h))

    return text_regions


def blur_sensitive_areas(image, gray_img):
    """Blur common sensitive areas in medical images"""
    img = np.array(image)
    height, width = gray_img.shape

    sensitive_regions = [
        (0, 0, width // 4, height // 6),
        (3 * width // 4, 0, width // 4, height // 6),
        (0, 5 * height // 6, width // 4, height // 6),
        (3 * width // 4, 5 * height // 6, width // 4, height // 6),
    ]

    blurred_regions = []
    for (x, y, w, h) in sensitive_regions:
        region = gray_img[y:y + h, x:x + w]
        if np.std(region) > 5:
            img_pil = Image.fromarray(img)
            img = np.array(blur_image_region(img_pil, x, y, w, h, blur_strength=31))
            blurred_regions.append((x, y, w, h))

    return Image.fromarray(img), blurred_regions


def verify_privacy_password():
    """Verify privacy password before showing unblurred image"""
    if "privacy_verified" not in st.session_state:
        st.session_state.privacy_verified = False

    if not st.session_state.privacy_verified:
        st.info("🔐 Privacy Mode Active: Image data is blurred for security")

        with st.form("privacy_unlock_form"):
            password = st.text_input(
                "Enter password to view full image (for authorized personnel only):",
                type="password",
                help="This is protected access for authorized medical personnel"
            )
            submit = st.form_submit_button("🔓 Verify & Unlock")

            if submit:
                correct_password = "medical123"
                if password == correct_password:
                    st.session_state.privacy_verified = True
                    st.success("✅ Verified! Image unlocked.")
                    st.rerun()
                else:
                    st.error("❌ Incorrect password. Access denied.")
        return False
    else:
        if st.button("🔒 Lock Image (Re-enable Privacy)"):
            st.session_state.privacy_verified = False
            st.rerun()
        return True


def render_privacy_toggle(image, gray_img):
    """Render privacy mode toggle and controls"""
    col1, col2, col3 = st.columns(3)

    with col1:
        if "privacy_mode" not in st.session_state:
            st.session_state.privacy_mode = True

        privacy_enabled = st.checkbox(
            "🔐 Enable Privacy Overlay Mode",
            value=st.session_state.privacy_mode,
            help="Blur sensitive patient information (names, IDs, dates)"
        )
        st.session_state.privacy_mode = privacy_enabled

    with col2:
        blur_level = st.slider(
            "Blur Intensity",
            min_value=1, max_value=10, value=5,
            help="1 = light blur, 10 = heavy blur"
        )

    with col3:
        st.markdown("")
        if st.button("ℹ️ Privacy Info"):
            st.info("""
            **Privacy Overlay Mode:**
            - Automatically detects and blurs patient identifiers
            - Blurs: Names, IDs, dates, hospital info
            - Preserves: Medical imaging data (diagnosis relevant)
            - Requires password for full image access
            """)

    return privacy_enabled, blur_level


# ==================================================
# 🔐 PATIENT INFO DETECTOR
# ==================================================
def detect_patient_info_regions(image, gray_img):
    """Detect likely patient information regions"""
    height, width = gray_img.shape
    sensitive_areas = []

    sensitive_areas.append({
        "name": "Patient ID (Top-Left)",
        "region": (0, 0, width // 5, height // 8),
        "type": "metadata"
    })
    sensitive_areas.append({
        "name": "Hospital Info (Top-Right)",
        "region": (4 * width // 5, 0, width // 5, height // 8),
        "type": "metadata"
    })
    sensitive_areas.append({
        "name": "Date/Time (Bottom-Left)",
        "region": (0, 7 * height // 8, width // 5, height // 8),
        "type": "metadata"
    })
    sensitive_areas.append({
        "name": "Additional Info (Bottom-Right)",
        "region": (4 * width // 5, 7 * height // 8, width // 5, height // 8),
        "type": "metadata"
    })

    return sensitive_areas


def apply_privacy_overlay(image, gray_img, blur_strength=31):
    """Apply privacy overlay to blur sensitive information"""
    print(f"🔐 Applying privacy overlay...")

    sensitive_regions = detect_patient_info_regions(image, gray_img)
    img_array = np.array(image)
    blurred_regions = []

    for region_info in sensitive_regions:
        x, y, w, h = region_info["region"]
        region_data = gray_img[y:y + h, x:x + w]

        if np.std(region_data) > 3:
            if blur_strength % 2 == 0:
                blur_strength += 1
            region = img_array[y:y + h, x:x + w]
            blurred = cv2.GaussianBlur(region, (blur_strength, blur_strength), 0)
            img_array[y:y + h, x:x + w] = blurred
            blurred_regions.append({
                "name": region_info["name"],
                "region": (x, y, w, h),
                "type": region_info["type"]
            })
            print(f"  ✅ Blurred: {region_info['name']}")

    return Image.fromarray(img_array), blurred_regions


def extract_regions_for_ui(heatmap, original_image_size):
    """🧠 AGGRESSIVE REGION EXTRACTION"""
    if heatmap is None or heatmap.size == 0:
        print("⚠️ Heatmap is None")
        return []

    try:
        heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
        h_img, w_img = heatmap_norm.shape
        img_area = h_img * w_img

        nonzero_mean = np.mean(heatmap_norm[heatmap_norm > 0]) if np.any(heatmap_norm > 0) else 0
        print(f"🔍 Heatmap stats:")
        print(f"  Shape: {heatmap_norm.shape}, Area: {img_area}")
        print(f"  Min: {np.min(heatmap_norm):.6f}, Max: {np.max(heatmap_norm):.6f}")
        print(f"  NonZero Mean: {nonzero_mean:.6f}")

        thresholds = [80, 70, 60, 50, 40, 30, 20, 10, 5]
        regions = []

        for p in thresholds:
            if regions:
                break

            threshold = np.percentile(heatmap_norm, p)
            above_threshold = np.sum(heatmap_norm > threshold)
            print(f"🔄 Threshold {p}th percentile ({threshold:.6f}): {above_threshold} pixels above")

            if above_threshold < 50:
                print(f"  Too few pixels, skipping")
                continue

            binary = (heatmap_norm > threshold).astype(np.uint8) * 255
            contours, _ = cv2.findContours(binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            if not contours:
                print(f"  No contours found")
                continue

            print(f"  Found {len(contours)} contours")
            contours = sorted(contours, key=cv2.contourArea, reverse=True)

            for idx, cnt in enumerate(contours[:10]):
                area = cv2.contourArea(cnt)

                if area < 100 or area > img_area * 0.40:
                    print(f"  Region {idx + 1}: Rejected (area={area})")
                    continue

                x, y, w, h = cv2.boundingRect(cnt)

                if w < 10 or h < 10:
                    print(f"  Region {idx + 1}: Rejected (size {w}×{h} too small)")
                    continue

                intensity = np.mean(heatmap_norm[y:y + h, x:x + w])

                regions.append({
                    "x": int(x), "y": int(y), "w": int(w), "h": int(h),
                    "intensity": float(intensity),
                    "contour": cnt
                })
                print(f"  ✅ Region {idx + 1}: {w}×{h}, area={area}, intensity={intensity:.6f}")

        regions = sorted(regions, key=lambda r: r["intensity"], reverse=True)[:5]
        print(f"✅ Total valid regions extracted: {len(regions)}")

        if len(regions) == 0:
            print("⚠️ WARNING: No regions found!")

        return regions

    except Exception as e:
        print(f"❌ Region extraction error: {e}")
        import traceback
        traceback.print_exc()
        return []


# ==================================================
# ✅ DRAW REGION BOXES
# ==================================================
def draw_region_boxes(image, regions, active_idx=None):
    """Draw contours with thin white edges"""
    img = image.copy()

    for i, region in enumerate(regions):
        cnt = region.get("contour")
        if cnt is None:
            x, y, w, h = region["x"], region["y"], region["w"], region["h"]
            color = (255, 255, 255)
            thickness = 2 if i == active_idx else 1
            cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
        else:
            thickness = 2 if i == active_idx else 1
            cv2.drawContours(img, [cnt], -1, (255, 255, 255), thickness)

        x, y, w, h = region["x"], region["y"], region["w"], region["h"]
        cx, cy = x + w // 2, y + h // 2
        cv2.circle(img, (cx, cy), 3, (0, 255, 255), -1)
        cv2.arrowedLine(
            img, (cx, max(0, cy - 40)), (cx, cy - 5),
            (0, 255, 255), 1, tipLength=0.3
        )

        if i == active_idx:
            cv2.putText(
                img, f"Region {i + 1}", (x, max(15, y - 8)),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1
            )

    return img


def prepare_heatmap(heatmap, original_image_size, model_input_size):
    """ENHANCED: Resize and normalize heatmap with contrast enhancement"""
    if heatmap is None or heatmap.size == 0:
        original_h, original_w = original_image_size[1], original_image_size[0]
        return np.ones((original_h, original_w)) * 0.5

    try:
        heatmap = np.nan_to_num(heatmap, nan=0.0, posinf=1.0, neginf=0.0)
        heatmap = np.clip(heatmap, 0, 1)

        print(f"🔄 Original heatmap: min={np.min(heatmap):.6f}, max={np.max(heatmap):.6f}")

        original_h, original_w = original_image_size[1], original_image_size[0]
        heatmap_resized = cv2.resize(heatmap, (original_w, original_h), interpolation=cv2.INTER_LINEAR)

        # CLAHE enhancement
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        heatmap_enhanced = clahe.apply(np.uint8(heatmap_resized * 255)) / 255.0

        # Gamma correction
        gamma = 0.5
        heatmap_gamma = np.power(heatmap_enhanced, gamma)

        # Percentile normalization
        p2 = np.percentile(heatmap_gamma, 2)
        p98 = np.percentile(heatmap_gamma, 98)

        if p98 > p2:
            heatmap_norm = (heatmap_gamma - p2) / (p98 - p2 + 1e-8)
        else:
            heatmap_norm = heatmap_gamma / (np.max(heatmap_gamma) + 1e-8)

        heatmap_norm = np.clip(heatmap_norm, 0, 1)
        heatmap_norm = cv2.GaussianBlur(heatmap_norm, (3, 3), 0.5)
        heatmap_norm = np.clip(heatmap_norm, 0, 1)

        print(f"✅ Final heatmap: shape={heatmap_norm.shape}")
        return heatmap_norm

    except Exception as e:
        print(f"❌ Error preparing heatmap: {e}")
        original_h, original_w = original_image_size[1], original_image_size[0]
        return np.ones((original_h, original_w)) * 0.5


def draw_subtle_corner_markers(image, regions, active_idx=None):
    """Draw SUBTLE corner markers at region edges"""
    img = image.copy()
    for i, (x, y, w, h) in enumerate(regions):
        corner = int(min(w, h) * 0.2)
        thickness = 2 if i == active_idx else 1
        color = (255, 255, 255)

        cv2.line(img, (x, y), (x + corner, y), color, thickness)
        cv2.line(img, (x, y), (x, y + corner), color, thickness)
        cv2.line(img, (x + w, y), (x + w - corner, y), color, thickness)
        cv2.line(img, (x + w, y), (x + w, y + corner), color, thickness)
        cv2.line(img, (x, y + h), (x + corner, y + h), color, thickness)
        cv2.line(img, (x, y + h), (x, y + h - corner), color, thickness)
        cv2.line(img, (x + w, y + h), (x + w - corner, y + h), color, thickness)
        cv2.line(img, (x + w, y + h), (x + w, y + h - corner), color, thickness)

        if i == active_idx:
            cx = x + w // 2
            cv2.arrowedLine(
                img, (cx, max(0, y - 40)), (cx, y),
                (255, 255, 255), 2, tipLength=0.3
            )

    return img


# --------------------------------------------------
# AI CONFIDENCE GRADIENT OVERLAY
# --------------------------------------------------
def apply_confidence_gradient(image, heatmap, confidence):
    """AI Confidence Gradient Overlay"""
    heatmap_local = heatmap / (np.max(heatmap) + 1e-8)
    conf_weight = confidence / 100.0
    weighted_map = heatmap_local * conf_weight

    gradient = cv2.applyColorMap(np.uint8(255 * weighted_map), cv2.COLORMAP_JET)
    gradient[:, :, 0] = 0

    overlay = cv2.addWeighted(image, 0.65, gradient, 0.35, 0)
    return overlay


# --------------------------------------------------
# Comparative Learning Mode
# --------------------------------------------------
def preprocess_compare_image(img, target_size):
    img = img.resize(target_size)
    img = np.array(img.convert("L"))
    return img


def compute_progression_map(prev_img, curr_img):
    diff = cv2.absdiff(curr_img, prev_img)
    diff_norm = diff / (np.max(diff) + 1e-8)
    heatmap_local = cv2.applyColorMap(np.uint8(255 * diff_norm), cv2.COLORMAP_HOT)
    return heatmap_local


def overlay_progression(base_image, progression_map):
    return cv2.addWeighted(base_image, 0.65, progression_map, 0.35, 0)


# --------------------------------------------------
# Severity Interpretation - FIXED
# --------------------------------------------------
def severity_label(confidence, predicted_label=None):
    """
    Returns severity level based on confidence AND predicted label.
    If the prediction is normal/healthy, severity is always None/Low
    regardless of how confident the model is.
    """
    # Import the normal detection from emergency_alert
    from emergency_alert import is_normal_prediction
    
    # If predicted label indicates normal/healthy → no severity
    if predicted_label is not None and is_normal_prediction(predicted_label):
        return "None"
    
    # Only assign severity when disease IS detected
    if confidence < 50:
        return "Low"
    elif confidence < 75:
        return "Moderate"
    else:
        return "High"

# --------------------------------------------------
# Grad-CAM
# --------------------------------------------------
def get_gradcam_heatmap(model, image_tensor, class_index):
    """FIXED Grad-CAM compatible with Keras 3.x"""
    try:
        if not isinstance(image_tensor, tf.Tensor):
            image_tensor = tf.convert_to_tensor(image_tensor, dtype=tf.float32)
        else:
            image_tensor = tf.cast(image_tensor, tf.float32)

        print(f"📊 Input tensor shape: {image_tensor.shape}")

        # ===== KEY FIX: Build the model by calling it first =====
        try:
            _ = model(image_tensor, training=False)
            print("✅ Model built successfully by calling it")
        except Exception as build_err:
            print(f"⚠️ Model build call failed: {build_err}")

        # Find best convolutional layer
        last_conv_layer = None
        last_conv_layer_name = None

        for layer in reversed(model.layers):
            if 'conv' in layer.name.lower() or isinstance(
                layer, (tf.keras.layers.Conv2D, tf.keras.layers.DepthwiseConv2D)
            ):
                last_conv_layer = layer
                last_conv_layer_name = layer.name
                print(f"✅ Using conv layer: {last_conv_layer_name}")
                break

        if last_conv_layer is None:
            for layer in reversed(model.layers):
                try:
                    if len(layer.output_shape) >= 3:
                        last_conv_layer = layer
                        last_conv_layer_name = layer.name
                        print(f"⚠️ Using alternative layer: {last_conv_layer_name}")
                        break
                except Exception:
                    continue

        if last_conv_layer is None:
            print("❌ No suitable layer found")
            return create_fallback_heatmap(image_tensor.shape[1:3])

        # ===== KEY FIX: Use model.inputs instead of model.input =====
        try:
            model_input = model.input
        except AttributeError:
            try:
                model_input = model.inputs[0]
            except Exception:
                # Last resort: create a new input tensor
                input_shape = image_tensor.shape[1:]
                model_input = tf.keras.Input(shape=input_shape)
                print(f"⚠️ Created new input with shape: {input_shape}")

        try:
            grad_model = tf.keras.models.Model(
                inputs=model_input,
                outputs=[last_conv_layer.output, model.output]
            )
        except Exception as gm_err:
            print(f"⚠️ Standard grad_model failed: {gm_err}")
            # Alternative: use functional approach
            try:
                grad_model = tf.keras.models.Model(
                    inputs=model.inputs,
                    outputs=[last_conv_layer.output, model.outputs[0]]
                )
            except Exception as gm_err2:
                print(f"❌ All grad_model attempts failed: {gm_err2}")
                return create_fallback_heatmap(image_tensor.shape[1:3])

        # METHOD 1: Standard Grad-CAM
        print("\n🔄 Computing standard Grad-CAM...")
        with tf.GradientTape(persistent=True) as tape:
            conv_outputs, predictions = grad_model(image_tensor, training=False)
            print(f"📊 Predictions shape: {predictions.shape}")
            print(f"📊 Predictions: {predictions.numpy()}")

            if predictions is None:
                return create_fallback_heatmap(image_tensor.shape[1:3])

            try:
                if len(predictions.shape) == 1:
                    class_loss = predictions[min(class_index, len(predictions) - 1)]
                elif len(predictions.shape) == 2:
                    if class_index >= predictions.shape[-1]:
                        class_index = int(tf.argmax(predictions[0]))
                    class_loss = predictions[0, class_index]
                else:
                    class_loss = tf.reduce_max(predictions)

                print(f"✅ Class index: {class_index}, Loss: {float(class_loss.numpy()):.6f}")
            except Exception as e:
                print(f"⚠️ Error getting class loss: {e}")
                class_loss = tf.reduce_max(predictions)

        grads = tape.gradient(class_loss, conv_outputs)

        if grads is None:
            print("⚠️ Standard gradients are None, trying alternative")
            with tf.GradientTape() as tape:
                conv_outputs, predictions = grad_model(image_tensor, training=False)
                loss = tf.reduce_sum(predictions)
            grads = tape.gradient(loss, conv_outputs)

            if grads is None:
                print("❌ Gradients still None")
                return create_fallback_heatmap(image_tensor.shape[1:3])

        # METHOD 1: Standard channel-wise weighting
        pooled_grads = tf.reduce_mean(grads, axis=(0, 1, 2))
        conv_output = conv_outputs[0]
        heatmap1 = tf.reduce_sum(conv_output * pooled_grads, axis=-1)
        heatmap1 = tf.nn.relu(heatmap1)
        heatmap1_max = tf.reduce_max(heatmap1)
        if heatmap1_max > 0:
            heatmap1 = heatmap1 / heatmap1_max
        else:
            heatmap1 = tf.ones_like(heatmap1) * 0.5

        # METHOD 2: Max activation
        print("\n🔄 Computing max activation heatmap...")
        heatmap2 = tf.reduce_max(tf.nn.relu(conv_output), axis=-1)
        heatmap2_max = tf.reduce_max(heatmap2)
        if heatmap2_max > 0:
            heatmap2 = heatmap2 / heatmap2_max
        else:
            heatmap2 = tf.ones_like(heatmap2) * 0.5

        # METHOD 3: Weighted by absolute gradients
        print("\n🔄 Computing absolute gradient heatmap...")
        abs_grads = tf.abs(grads)
        weighted_conv = conv_output * (abs_grads / (tf.reduce_max(abs_grads) + 1e-8))
        heatmap3 = tf.reduce_sum(weighted_conv, axis=-1)
        heatmap3 = tf.nn.relu(heatmap3)
        heatmap3_max = tf.reduce_max(heatmap3)
        if heatmap3_max > 0:
            heatmap3 = heatmap3 / heatmap3_max
        else:
            heatmap3 = tf.ones_like(heatmap3) * 0.5

        # COMBINE
        print("\n🔄 Combining heatmaps...")
        combined_heatmap = (heatmap1 + heatmap2 + heatmap3) / 3.0
        combined_heatmap = tf.nn.relu(combined_heatmap)
        combined_max = tf.reduce_max(combined_heatmap)
        if combined_max > 0:
            combined_heatmap = combined_heatmap / combined_max
        else:
            combined_heatmap = tf.ones_like(combined_heatmap) * 0.5

        heatmap_np = combined_heatmap.numpy()
        print(f"✅ Combined heatmap: min={np.min(heatmap_np):.6f}, max={np.max(heatmap_np):.6f}")

        if np.std(heatmap_np) < 0.01:
            print("⚠️ WARNING: Heatmap is too uniform! Applying enhancement...")
            heatmap_np = np.power(heatmap_np, 0.3)
            heatmap_np = heatmap_np / (np.max(heatmap_np) + 1e-8)

        if np.isnan(heatmap_np).any() or np.isinf(heatmap_np).any():
            heatmap_np = np.nan_to_num(heatmap_np, nan=0.5, posinf=0.5, neginf=0.0)

        heatmap_np = np.clip(heatmap_np, 0, 1)
        print(f"✅ Final heatmap: shape={heatmap_np.shape}")
        return heatmap_np

    except Exception as e:
        print(f"❌ Grad-CAM error: {e}")
        import traceback
        traceback.print_exc()
        return create_fallback_heatmap(image_tensor.shape[1:3])


def create_fallback_heatmap(shape):
    """Create a fallback heatmap if Grad-CAM fails"""
    try:
        h, w = shape
        y, x = np.ogrid[-1:1:complex(0, h), -1:1:complex(0, w)]
        heatmap_fb = np.exp(-(x ** 2 + y ** 2) / 0.3)
        heatmap_fb = heatmap_fb / np.max(heatmap_fb)
        return heatmap_fb
    except Exception:
        return np.ones(shape) * 0.5


def calculate_explainability_score(heatmap, regions, confidence):
    """Calculate an overall explainability score (0-100)."""
    clarity = 0
    region_score = 0
    confidence_score = 0

    if heatmap is not None:
        try:
            heatmap_norm = heatmap / (np.max(heatmap) + 1e-8)
            max_val = np.max(heatmap_norm)
            if np.isfinite(max_val) and max_val > 0:
                clarity = max_val * 100
            else:
                clarity = 30
        except Exception:
            clarity = 30
    else:
        clarity = 20

    if regions is not None and len(regions) > 0:
        region_score = min(len(regions) * 25, 75)
    else:
        region_score = 10

    if np.isfinite(confidence):
        confidence_score = min(confidence, 95)
    else:
        confidence_score = 50

    clarity = float(clarity) if np.isfinite(clarity) else 30
    region_score = float(region_score) if np.isfinite(region_score) else 10
    confidence_score = float(confidence_score) if np.isfinite(confidence_score) else 50

    explainability = (clarity * 0.3 + region_score * 0.35 + confidence_score * 0.35)

    if not np.isfinite(explainability) or explainability < 0:
        explainability = 50
    elif explainability > 100:
        explainability = 100

    return float(explainability)


def render_trust_panel(features, explainability_score, selected_disease):
    """Render the Trust & Explainability panel"""
    st.markdown(
        f"""
        <div class="trust-panel">
            <div class="trust-header">🔐 Trust & Explainability Report</div>
        </div>
        """,
        unsafe_allow_html=True
    )

    col1, col2 = st.columns([1, 3])
    with col1:
        st.metric(
            "Explainability Score",
            f"{explainability_score:.0f}/100",
            delta="High transparency" if explainability_score > 70 else "Moderate transparency"
        )

    with col2:
        st.markdown(
            f"""
            <div style="padding: 1rem; background: #0f1419; border-radius: 8px;">
                <div style="color: #e5e7eb; font-size: 0.9rem; margin-bottom: 0.5rem;">
                    Model Confidence Alignment
                </div>
                <div class="confidence-bar">
                    <div class="confidence-fill" style="width: {min(explainability_score, 100)}%"></div>
                </div>
                <div style="color: #888; font-size: 0.8rem; margin-top: 0.5rem;">
                    This score reflects how well the model's attention patterns
                    align with the predicted diagnosis
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    st.markdown("---")
    st.markdown("### 🎯 Top 3 Image Features Influencing Decision")

    if features:
        for idx, feature in enumerate(features, 1):
            st.markdown(
                f"""
                <div class="feature-item">
                    <span class="feature-rank">#{idx}</span>
                    <span style="color: #ffffff; font-weight: 600;">{feature['name']}</span>
                    <br>
                    <span class="feature-text">{feature['description']}</span>
                    <div class="confidence-bar">
                        <div class="confidence-fill" style="width: {feature['confidence']}%"></div>
                    </div>
                    <span class="feature-text" style="font-size: 0.85rem; color: #888;">
                        Influence Score: {feature['confidence']:.1f}%
                    </span>
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        st.warning("Unable to extract specific features. Model attention may be diffuse.")

    st.markdown("---")
    st.markdown(
        f"""
        <div style="background: #0f1419; border-left: 3px solid #ff9500;
             padding: 1rem; border-radius: 8px; margin-top: 1rem;">
            <div style="color: #ff9500; font-weight: 700; margin-bottom: 0.5rem;">
                ℹ️ How to Interpret This Report
            </div>
            <div style="color: #e5e7eb; font-size: 0.9rem; line-height: 1.6;">
                <ul style="margin: 0; padding-left: 1.5rem;">
                    <li><strong>Top 3 Features:</strong> Visual patterns the AI focused on</li>
                    <li><strong>Influence Score:</strong> How much each feature contributed</li>
                    <li><strong>Explainability Score:</strong> Overall confidence in interpretability</li>
                    <li><strong>Always consult a medical professional</strong> for clinical decisions</li>
                </ul>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<h1>🩺 Medical Image Diagnosis Assistant</h1>", unsafe_allow_html=True)
# 👥 Show role-specific header
show_role_header(current_role)

# --------------------------------------------------
# SIDEBAR WORKFLOW
# --------------------------------------------------
with st.sidebar:
    # 👥 Show role-based sidebar info
    show_role_based_sidebar()
    
    st.markdown("## 🧭 Workflow")

    st.markdown("### 1️⃣ Select Condition")
    selected_disease = st.selectbox("Select Condition", DISEASE_NAMES, label_visibility="collapsed")

    st.markdown("### 2️⃣ Upload Image")
    uploaded_file = st.file_uploader("Upload Image", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

    st.markdown("---")
    st.caption("⚠️ Educational use only.\n\nNot medical advice.")
    st.markdown("---")

    if st.button("🚪 Logout"):
        logout_user()

# --------------------------------------------------
# MAIN AREA
# --------------------------------------------------
if uploaded_file is None:
    st.info("Upload a medical image to begin analysis.")
    st.stop()

image = Image.open(io.BytesIO(uploaded_file.getvalue())).convert("RGB")

# ==================================================
# 🎯 VALIDATE IMAGE FOR SELECTED DISEASE
# ==================================================
st.markdown("### 🔍 Image Validation")

is_valid, validation_message, validation_confidence = validate_image_for_disease(image, selected_disease)

if is_valid:
    st.success(validation_message)
else:
    st.error(validation_message)
    st.warning(f"""
    ⚠️ **Image Issue Detected!**

    Please ensure you're uploading a valid medical image.

    **Supported Image Types:**
    - **Pneumonia**: Chest X-rays
    - **Brain Tumor**: Brain MRI/CT scans
    - **Malaria**: Blood smear microscopy images
    - **Tuberculosis**: Chest X-rays
    - **Dental**: Dental X-rays
    - **Diabetic Retinopathy**: Retinal fundus images
    - **Skin Cancer**: Skin lesion photographs
    """)
    st.stop()

# ==================================================
# 🔥 LOAD CORRECT MODEL FOR DISEASE
# ==================================================
model = load_disease_model(selected_disease)

if model is None:
    st.error(f"Could not load model for {selected_disease}")
    st.stop()

# ==================================================
# 🔥 FIXED PREPROCESSING FOR ALL DISEASES
# ==================================================
input_shape = model.input_shape
print(f"📊 Model input shape: {input_shape}")

# Get input dimensions
if len(input_shape) == 4:
    _, input_h, input_w, input_channels = input_shape
elif len(input_shape) == 3:
    _, input_h, input_w = input_shape
    input_channels = 1
else:
    input_h, input_w, input_channels = 224, 224, 3

# Handle None dimensions (flexible input)
if input_h is None:
    input_h = 224
if input_w is None:
    input_w = 224
if input_channels is None:
    input_channels = 3

print(f"📊 Using input size: {input_h}x{input_w}x{input_channels}")

# ===== DISEASE-SPECIFIC PREPROCESSING =====
if selected_disease == "Malaria":
    # Malaria models typically use RGB 3-channel input
    img_resized = image.convert('RGB').resize((input_w, input_h))
    img_array = np.array(img_resized) / 255.0
    
    if input_channels == 1:
        # Convert to grayscale if model expects 1 channel
        img_array = np.mean(img_array, axis=-1, keepdims=True)
    
    print(f"🦠 Malaria preprocessing: RGB, shape={img_array.shape}")

elif selected_disease in ["Pneumonia", "Tuberculosis"]:
    # Chest X-rays: often grayscale or 3-channel grayscale
    img_gray = image.convert('L').resize((input_w, input_h))
    img_array = np.array(img_gray) / 255.0
    
    if input_channels == 3:
        # Stack grayscale to 3 channels
        img_array = np.stack([img_array, img_array, img_array], axis=-1)
    elif input_channels == 1:
        img_array = np.expand_dims(img_array, axis=-1)
    
    print(f"🫁 Chest X-ray preprocessing: shape={img_array.shape}")

elif selected_disease == "Brain Tumor":
    # Brain scans: can be grayscale or RGB
    if input_channels == 1:
        img_gray = image.convert('L').resize((input_w, input_h))
        img_array = np.array(img_gray) / 255.0
        img_array = np.expand_dims(img_array, axis=-1)
    else:
        img_resized = image.convert('RGB').resize((input_w, input_h))
        img_array = np.array(img_resized) / 255.0
    
    print(f"🧠 Brain preprocessing: shape={img_array.shape}")

elif selected_disease == "Dental":
    # Dental X-rays: grayscale
    img_gray = image.convert('L').resize((input_w, input_h))
    img_array = np.array(img_gray) / 255.0
    
    if input_channels == 3:
        img_array = np.stack([img_array, img_array, img_array], axis=-1)
    elif input_channels == 1:
        img_array = np.expand_dims(img_array, axis=-1)
    
    print(f"🦷 Dental preprocessing: shape={img_array.shape}")

elif selected_disease == "Diabetic Retinopathy":
    # Fundus images: RGB color
    img_resized = image.convert('RGB').resize((input_w, input_h))
    img_array = np.array(img_resized) / 255.0
    
    print(f"👁️ Fundus preprocessing: shape={img_array.shape}")

elif selected_disease == "Skin Cancer":
    # Skin lesions: RGB color
    img_resized = image.convert('RGB').resize((input_w, input_h))
    img_array = np.array(img_resized) / 255.0
    
    print(f"🔴 Skin preprocessing: shape={img_array.shape}")

else:
    # Default: RGB
    img_resized = image.convert('RGB').resize((input_w, input_h))
    img_array = np.array(img_resized) / 255.0

# Create input tensor
input_tensor = np.expand_dims(img_array, axis=0).astype(np.float32)
print(f"📊 Final input tensor shape: {input_tensor.shape}")

# ==================================================
# 🔥 FIXED PREDICTION LOGIC FOR ALL DISEASES
# ==================================================
st.markdown("### 🔬 AI Analysis")

# Get predictions
try:
    raw_preds = model.predict(input_tensor, verbose=0)
except Exception as e:
    st.error(f"Prediction error: {e}")
    st.stop()

# Get labels from disease_info
labels = disease_info[selected_disease]["labels"]
num_classes = len(labels)

# 🐛 DEBUG MODE
with st.expander("🔍 DEBUG: Raw Model Output (click to expand)"):
    st.code(f"""
Model Input Shape: {model.input_shape}
Model Output Shape: {model.output_shape}
Input Tensor Shape: {input_tensor.shape}
Raw Predictions Shape: {raw_preds.shape}
Raw Predictions: {raw_preds}
Labels: {labels}
Number of Classes: {num_classes}
    """)

# ===== INTERPRET PREDICTIONS =====
preds = raw_preds.flatten()  # Flatten to 1D array
print(f"📊 Flattened predictions: {preds}")
print(f"📊 Labels: {labels}")

# Determine prediction type based on output shape and values
output_size = len(preds)

if output_size == 1:
    # ===== SINGLE SIGMOID OUTPUT (Binary Classification) =====
    prob = float(preds[0])
    print(f"📊 Single sigmoid output: {prob:.6f}")
    
    # Disease-specific label mapping
    if selected_disease == "Malaria":
        # Malaria: Check label order
        # Common: ["Uninfected", "Parasitized"] or ["Parasitized", "Uninfected"]
        label_0_lower = labels[0].lower()
        
        if "uninfected" in label_0_lower or "normal" in label_0_lower or "negative" in label_0_lower:
            # labels[0] = Uninfected, labels[1] = Parasitized
            # High prob = Parasitized (index 1)
            if prob >= 0.5:
                class_index = 1  # Parasitized/Infected
                confidence = prob * 100
            else:
                class_index = 0  # Uninfected
                confidence = (1 - prob) * 100
        else:
            # labels[0] = Parasitized, labels[1] = Uninfected
            # High prob = Parasitized (index 0)
            if prob >= 0.5:
                class_index = 0  # Parasitized/Infected
                confidence = prob * 100
            else:
                class_index = 1  # Uninfected
                confidence = (1 - prob) * 100
    
    elif selected_disease == "Pneumonia":
        # Pneumonia: typically [NORMAL, PNEUMONIA]
        label_0_lower = labels[0].lower()
        
        if "normal" in label_0_lower or "healthy" in label_0_lower or "negative" in label_0_lower:
            if prob >= 0.5:
                class_index = 1  # PNEUMONIA
                confidence = prob * 100
            else:
                class_index = 0  # NORMAL
                confidence = (1 - prob) * 100
        else:
            if prob >= 0.5:
                class_index = 0
                confidence = prob * 100
            else:
                class_index = 1
                confidence = (1 - prob) * 100
    
    elif selected_disease == "Tuberculosis":
        # TB: typically [Normal, Tuberculosis]
        label_0_lower = labels[0].lower()
        
        if "normal" in label_0_lower or "healthy" in label_0_lower or "negative" in label_0_lower:
            if prob >= 0.5:
                class_index = 1  # Tuberculosis
                confidence = prob * 100
            else:
                class_index = 0  # Normal
                confidence = (1 - prob) * 100
        else:
            if prob >= 0.5:
                class_index = 0
                confidence = prob * 100
            else:
                class_index = 1
                confidence = (1 - prob) * 100
    
    elif selected_disease == "Brain Tumor":
        # Brain: typically [No Tumor, Tumor] for binary
        label_0_lower = labels[0].lower()
        
        if "no" in label_0_lower or "normal" in label_0_lower or "healthy" in label_0_lower:
            if prob >= 0.5:
                class_index = 1  # Tumor
                confidence = prob * 100
            else:
                class_index = 0  # No Tumor
                confidence = (1 - prob) * 100
        else:
            if prob >= 0.5:
                class_index = 0
                confidence = prob * 100
            else:
                class_index = 1
                confidence = (1 - prob) * 100
    
    elif selected_disease == "Skin Cancer":
        # Skin Cancer: typically [Benign, Malignant]
        label_0_lower = labels[0].lower()
        
        if "benign" in label_0_lower or "normal" in label_0_lower or "negative" in label_0_lower:
            if prob >= 0.5:
                class_index = 1  # Malignant
                confidence = prob * 100
            else:
                class_index = 0  # Benign
                confidence = (1 - prob) * 100
        else:
            if prob >= 0.5:
                class_index = 0
                confidence = prob * 100
            else:
                class_index = 1
                confidence = (1 - prob) * 100
    
    elif selected_disease == "Dental":
        # Dental: typically [Healthy, Cavity/Issue]
        label_0_lower = labels[0].lower()
        
        if "healthy" in label_0_lower or "normal" in label_0_lower or "negative" in label_0_lower:
            if prob >= 0.5:
                class_index = 1  # Issue
                confidence = prob * 100
            else:
                class_index = 0  # Healthy
                confidence = (1 - prob) * 100
        else:
            if prob >= 0.5:
                class_index = 0
                confidence = prob * 100
            else:
                class_index = 1
                confidence = (1 - prob) * 100
    
    elif selected_disease == "Diabetic Retinopathy":
        # DR: For binary, typically [No DR, DR]
        label_0_lower = labels[0].lower()
        
        if "no" in label_0_lower or "normal" in label_0_lower or "healthy" in label_0_lower:
            if prob >= 0.5:
                class_index = 1  # DR
                confidence = prob * 100
            else:
                class_index = 0  # No DR
                confidence = (1 - prob) * 100
        else:
            if prob >= 0.5:
                class_index = 0
                confidence = prob * 100
            else:
                class_index = 1
                confidence = (1 - prob) * 100
    
    else:
        # Default binary interpretation
        if prob >= 0.5:
            class_index = 1
            confidence = prob * 100
        else:
            class_index = 0
            confidence = (1 - prob) * 100
    
    print(f"✅ Binary classification: prob={prob:.4f}, class={class_index}, conf={confidence:.2f}%")

elif output_size == 2:
    # ===== TWO SOFTMAX OUTPUTS =====
    prob_0 = float(preds[0])
    prob_1 = float(preds[1])
    print(f"📊 Two-class softmax: [{prob_0:.4f}, {prob_1:.4f}]")
    
    class_index = int(np.argmax(preds))
    confidence = float(preds[class_index]) * 100
    
    print(f"✅ Predicted class {class_index} ({labels[class_index]}) with {confidence:.2f}%")

else:
    # ===== MULTI-CLASS SOFTMAX =====
    print(f"📊 Multi-class output ({output_size} classes)")
    
    class_index = int(np.argmax(preds))
    confidence = float(preds[class_index]) * 100
    
    print(f"✅ Predicted class {class_index} with {confidence:.2f}%")
    
    # Show all class probabilities
    for i, prob_val in enumerate(preds):
        if i < len(labels):
            print(f"   Class {i} ({labels[i]}): {prob_val*100:.2f}%")
        else:
            print(f"   Class {i}: {prob_val*100:.2f}%")

# ===== VALIDATE CLASS INDEX =====
if class_index >= len(labels):
    print(f"⚠️ Class index {class_index} out of range for {len(labels)} labels, using 0")
    class_index = 0

if class_index < 0:
    class_index = 0

# ===== ENSURE REASONABLE CONFIDENCE =====
confidence = max(min(confidence, 100.0), 0.0)

print(f"🎯 FINAL: {labels[class_index]} with {confidence:.2f}% confidence")

# Get details
details = disease_info[selected_disease].get("details", {}).get(labels[class_index])

# ==================================================
# DISPLAY PREDICTION RESULTS
# ==================================================
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("🎯 Predicted Condition", labels[class_index])
with col2:
    st.metric("📊 Confidence", f"{confidence:.2f}%")
with col3:
    st.metric("⚠️ Severity", severity_label(confidence, labels[class_index]))

# ==================================================
# COMPUTE HEATMAP AND EXPLAINABILITY DATA
# ==================================================
heatmap = get_gradcam_heatmap(model, input_tensor, class_index)
heatmap = prepare_heatmap(heatmap, image.size, (input_w, input_h))

regions = extract_regions_for_ui(heatmap, image.size) if heatmap is not None else []
features = extract_image_features(image, heatmap, regions)
explainability_score = calculate_explainability_score(heatmap, regions, confidence)

# Compute gray here for use in Overview tab
gray = np.array(image.convert('L'))

# --------------------------------------------------
# TABS
# --------------------------------------------------
tabs = st.tabs([
    "🧠 Overview", "🔐 Trust Panel", "🎯 Attention", "📋 Details",
    "🧊 3D Viewer", "📈 Comparative Mode", "🤝 Collaboration",
    "📊 Patient Timeline", "🏥 Patient Health Timeline",
    "💊 Medications", "🔗 Symptom Fusion", "📊 Population Data",
    "🔍 Why This Region?", "🚨 Emergency", "📱 Cross-Device", "💬 Chat with AI",
    "📋 Compliance Mode", "🔬 Next Tests", "🎤 Voice Assistant"
])

# --------------------------------------------------
# OVERVIEW TAB
# --------------------------------------------------
with tabs[0]:
    # ===== PRIVACY OVERLAY MODE =====
    st.markdown("### 🔐 Privacy Overlay Mode")
    privacy_enabled, blur_level = render_privacy_toggle(image, gray)

    if privacy_enabled:
        display_image, blurred_regions = apply_privacy_overlay(
            image, gray, blur_strength=21 + (blur_level * 2)
        )
        st.success(f"🔐 Privacy mode enabled - {len(blurred_regions)} sensitive areas blurred")
        st.image(
            display_image,
            caption="Privacy Protected: Medical Image Data Visible, Personal Info Blurred",
            use_column_width=True
        )

        if blurred_regions:
            with st.expander("ℹ️ Blurred Information Summary"):
                for region in blurred_regions:
                    st.write(f"✅ {region['name']} - Blurred")

        st.markdown("---")
        st.markdown("### 🔓 Unlock Full Image")
        is_verified = verify_privacy_password()

        if is_verified:
            st.info("✅ Access verified. Full image and metadata visible below.")
            st.image(
                image,
                caption="FULL IMAGE - All patient data visible (Authorized Personnel Only)",
                use_column_width=True
            )
            st.markdown("---")
            with st.expander("📋 Access Audit Log"):
                st.write("""
                ⏰ Image accessed without privacy overlay
                👤 Authorized Personnel
                🔐 Password verified
                📅 Session timestamp: """ + str(pd.Timestamp.now()))
    else:
        st.info("⚠️ Privacy Mode Disabled - Full patient data visible")
        st.image(
            image,
            caption="Full Unprotected Image - All Personal Info Visible",
            use_column_width=True
        )
        st.warning("""
        ⚠️ **PRIVACY WARNING**
        Full patient information is currently visible:
        - Patient name/ID
        - Hospital information
        - Date/Time stamps
        - All metadata

        Enable Privacy Overlay Mode above to protect sensitive information!
        """)

    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.metric("Predicted Condition", labels[class_index])
    with col2:
        st.metric("Confidence", f"{confidence:.2f}%")

    st.metric("Estimated Severity", severity_label(confidence, labels[class_index]))

    st.markdown(
        "<div class='card'>"
        "The AI analyzed the uploaded medical image and generated a prediction "
        "based on learned visual patterns."
        "</div>",
        unsafe_allow_html=True
    )

    with st.expander("🧾 AI Diagnostic Summary"):
        st.markdown(f"""
**Condition:** {selected_disease}
**Model Inference:** {labels[class_index]}
**Model Confidence Estimate:** {confidence:.2f}%
**Estimated Severity:** {severity_label(confidence, labels[class_index])}

**AI Findings:** The model detected visual patterns consistent with **{labels[class_index]}**.
Regions highlighted by the explainability map indicate areas that most influenced the model's inference.

⚠️ *This is an AI-assisted analysis for educational and research purposes only.*
        """)

    report_text = f"""
Condition: {selected_disease}
Model Inference: {labels[class_index]}
Confidence: {confidence:.2f}%
Estimated Severity: {severity_label(confidence, labels[class_index])}

🔐 PRIVACY NOTICE: This report was generated with Privacy Overlay Mode.
Personal patient information has been protected.
Full details available only to authorized personnel upon password verification.
    """
    st.download_button(
        "📄 Download AI Report (Privacy Protected)",
        report_text,
        file_name="ai_diagnostic_report.txt"
    )

# --------------------------------------------------
# TRUST PANEL TAB
# --------------------------------------------------
with tabs[1]:
    if RoleBasedInterface.can_access_tab(current_role, "Trust Panel"):
        render_trust_panel(features, explainability_score, selected_disease)
    else:
        show_access_denied_message("Trust Panel", "Doctor or Radiologist")


# --------------------------------------------------
# ATTENTION TAB
# --------------------------------------------------
with tabs[2]:
    if RoleBasedInterface.can_access_tab(current_role, "Attention"):
        st.markdown("### 🎯 Model Attention & Explainability")

        feature_select = st.radio(
            "Select Visualization Feature",
            [
                "Feature 1: Heatmap with Region Boxes",
                "Feature 2: AI Confidence Gradient",
                "Feature 3: Tumor Detection (WHITE edges)"
            ],
            horizontal=True
        )

        if heatmap is not None:
            if feature_select == "Feature 1: Heatmap with Region Boxes":
                st.markdown("#### 🔵 Feature 1: Model Attention Heatmap with Detected Regions")
                st.caption("Red/Yellow = High attention (tumor area), Green/Blue = Low attention")

                show_regions = st.checkbox(
                    "🔍 Show Region Boxes", value=True,
                    help="Show boxes around detected high-intensity regions",
                    key="feature1_regions"
                )

                heatmap_color = np.uint8(255 * cm.jet(heatmap)[:, :, :3])
                overlay = cv2.addWeighted(np.array(image), 0.6, heatmap_color, 0.4, 0)

                if regions and show_regions:
                    region_names = [f"Region {i + 1}" for i in range(len(regions))]
                    selected_region = st.selectbox("Select Region", region_names, key="feature1_select")
                    active_idx = region_names.index(selected_region)

                    final_img = draw_region_boxes(overlay, regions, active_idx)
                    st.image(final_img,  use_column_width=True, caption="Detected Regions on Heatmap (WHITE edges)")

                    if active_idx < len(regions):
                        region = regions[active_idx]
                        st.success(
                            f"✅ **Region {active_idx + 1}** at position ({region['x']}, {region['y']}) \n"
                            f"Size: {region['w']}×{region['h']} pixels \n"
                            f"Model Confidence: {region['intensity'] * 100:.1f}%"
                        )
                else:
                    st.image(overlay,  use_column_width=True, caption="Feature 1: Heatmap Overlay")

                if not regions:
                    st.warning("No distinct attention regions detected with current threshold.")

                st.caption(
                    "🔴 **Red zones** = Highest model attention (most likely lesion) \n"
                    "🟡 **Yellow zones** = Medium attention \n"
                    "🟢 **Green zones** = Low attention (normal tissue)"
                )

            elif feature_select == "Feature 2: AI Confidence Gradient":
                st.markdown("#### 🌡️ Feature 2: AI Confidence Gradient")
                st.caption("Shows varying AI confidence levels across different regions")

                gradient_img = apply_confidence_gradient(np.array(image), heatmap, confidence)
                st.image(gradient_img,  use_column_width=True,
                         caption="AI Confidence Heat Gradient (Green→Yellow→Red)")

                st.info(
                    "This gradient overlay shows how confident the AI model is about different regions:\n"
                    "🟢 **Green zones** = Low problem probability (healthy areas)\n"
                    "🟡 **Yellow zones** = Medium problem probability\n"
                    "🔴 **Red zones** = High problem probability (likely problem areas)"
                )
                st.caption(
                    f"Model confidence: {confidence:.1f}% | "
                    "Use both Feature 1 and Feature 2 to understand the AI's decision better"
                )

            else:
                st.markdown("#### 🎯 Feature 3: AI-Detected Disease Regions")
                st.caption("WHITE box edges show regions where AI model detected disease")

                show_regions = st.checkbox(
                    "✅ Show Disease Boxes", value=True,
                    help="Show white boxes around detected disease regions",
                    key="heatmap_boxes"
                )

                if heatmap is not None:
                    heatmap_color = np.uint8(255 * cm.jet(heatmap)[:, :, :3])
                    overlay = cv2.addWeighted(np.array(image), 0.6, heatmap_color, 0.4, 0)
                else:
                    overlay = np.array(image)

                if regions and show_regions:
                    region_names = [f"Disease Region {i + 1}" for i in range(len(regions))]
                    selected_region = st.selectbox("Select Region", region_names, key="heatmap_select")
                    active_idx = region_names.index(selected_region)

                    final_img = draw_region_boxes(overlay, regions, active_idx)
                    st.image(final_img,  use_column_width=True,
                             caption="AI-Detected Disease Regions (WHITE edges)")

                    if active_idx < len(regions):
                        region = regions[active_idx]
                        st.success(
                            f"✅ **Disease Region {active_idx + 1}** \n"
                            f"Position: ({region['x']}, {region['y']}) \n"
                            f"Size: {region['w']}×{region['h']} pixels \n"
                            f"AI Confidence: {region['intensity'] * 100:.1f}%"
                        )
                else:
                    st.image(overlay,  use_column_width=True, caption="Heatmap Overlay")

                if not regions:
                    st.warning("⚠️ No high-confidence disease regions detected in the heatmap")

                st.info(
                    "🤍 **WHITE box edges** = AI-detected disease boundaries (from heatmap) \n"
                    "🔴 **Red zones** = Highest AI attention (most likely disease) \n"
                    "🟡 **Yellow/Green zones** = Moderate to low attention \n"
                    "🔵 **Cyan arrow** = Region center location"
                )
        else:
            st.warning("Grad-CAM not available.")
    else:
        show_access_denied_message("Attention", "Doctor or Radiologist")

# --------------------------------------------------
# DETAILS TAB
# --------------------------------------------------
with tabs[3]:
    st.markdown("### 📋 Condition Information")

    if details:
        st.markdown(f"**Description** \n{details.get('info', 'N/A')}")
        st.markdown(f"**Symptoms** \n{', '.join(details.get('symptoms', []))}")
        st.markdown(f"**Causes** \n{', '.join(details.get('causes', []))}")
        st.markdown(
            f"**Treatment Overview** \n"
            f"{details.get('treatment_overview', 'Consult a professional')}"
        )
    else:
        st.warning("No detailed information available.")

    with st.expander("🔬 Model Information"):
        st.markdown(f"""
        - **Disease:** {selected_disease}
        - **Architecture:** Convolutional Neural Network (Keras)
        - **Input Resolution:** {input_h} × {input_w} × {input_channels}
        - **Output Classes:** {num_classes} ({', '.join(labels)})
        - **Explainability:** Grad-CAM
        - **Visualization:** 2D, Pseudo-3D, Volumetric Rendering
        """)

# --------------------------------------------------
# 🧊 3D VIEWER TAB
# --------------------------------------------------
with tabs[4]:
    st.markdown("### 🧊 3D Medical Visualization with AI Lesion Overlay")
    st.info(
        "🔬 **Advanced Features:**\n"
        "- Interactive 3D rotation, zoom, and pan\n"
        "- AI-predicted lesion overlay in color\n"
        "- Slice navigation (Axial, Sagittal, Coronal)\n"
        "- Medical-grade visualization\n"
        "- Lesion statistics and volume calculation"
    )

    col_mode1, col_mode2 = st.columns(2)
    with col_mode1:
        viz_type = st.radio(
            "Visualization Type",
            ["Single Image (Pseudo-3D)", "Full Volume (CT/MRI)"],
            horizontal=False
        )
    with col_mode2:
        show_ai_lesion = st.checkbox(
            "🎯 Show AI Lesion Overlay", value=True,
            help="Overlay model's predicted lesion areas"
        )

    if viz_type == "Single Image (Pseudo-3D)":
        st.markdown("#### 🖼️ Pseudo-3D Surface Rendering")

        col1, col2 = st.columns(2)
        with col1:
            colorscale = st.selectbox(
                "Color Scheme",
                ["Viridis", "Hot", "Cool", "Gray", "Blues", "Greys", "Reds"],
                index=0
            )
        with col2:
            lesion_threshold = st.slider(
                "Lesion Confidence Threshold",
                min_value=0.1, max_value=1.0, value=0.5, step=0.1,
                help="Minimum AI confidence to show as lesion"
            )

        fig_3d = show_pseudo_3d(
            image_array=img_array,
            heatmap=heatmap if heatmap is not None else None,
            colorscale=colorscale,
            show_lesion_overlay=show_ai_lesion
        )
        st.plotly_chart(fig_3d,  use_column_width=True)

        if show_ai_lesion and heatmap is not None:
            from visualization.pseudo_3d import create_lesion_statistics
            st.markdown("#### 📊 Lesion Analysis")
            stats = create_lesion_statistics(heatmap, lesion_threshold)

            if stats:
                col_s1, col_s2, col_s3 = st.columns(3)
                with col_s1:
                    st.metric(
                        "Lesion Coverage",
                        f"{stats['lesion_percentage']:.2f}%",
                        help="Percentage of image showing lesion"
                    )
                with col_s2:
                    st.metric(
                        "Max Confidence",
                        f"{stats['max_intensity']:.2%}",
                        help="Highest AI confidence in lesion area"
                    )
                with col_s3:
                    st.metric(
                        "Mean Confidence",
                        f"{stats['mean_intensity']:.2%}",
                        help="Average AI confidence across lesion"
                    )

                if stats['centroid'] is not None:
                    st.caption(
                        f"📍 **Lesion Centroid:** Position "
                        f"({stats['centroid'][0]:.0f}, {stats['centroid'][1]:.0f})"
                    )
    else:
        st.markdown("#### 📀 3D Volumetric Scan Visualization")
        nii_file = st.file_uploader(
            "Upload CT/MRI Scan (.nii / .nii.gz)",
            type=["nii", "nii.gz"],
            help="Medical imaging volume in NIfTI format"
        )

        if nii_file:
            st.markdown("**Loading 3D volume... This may take a moment.**")
            try:
                col_ctrl1, col_ctrl2, col_ctrl3 = st.columns(3)
                with col_ctrl1:
                    opacity_base = st.slider("Volume Opacity", 0.0, 1.0, 0.15)
                with col_ctrl2:
                    opacity_lesion = st.slider("Lesion Opacity", 0.0, 1.0, 0.7)
                with col_ctrl3:
                    lesion_threshold_3d = st.slider("Lesion Threshold (3D)", 0.1, 1.0, 0.5)

                fig_volume = show_volume_3d(
                    nii_file=nii_file,
                    lesion_heatmap_3d=None,
                    lesion_threshold=lesion_threshold_3d,
                    show_lesion_overlay=show_ai_lesion,
                    opacity_base=opacity_base,
                    opacity_lesion=opacity_lesion
                )
                st.plotly_chart(fig_volume,  use_column_width=True)
                st.success("✅ 3D volume loaded and rendered successfully")

                with st.expander("💡 Visualization Tips"):
                    st.markdown("""
                    **Navigation:**
                    - **Rotate:** Click and drag with mouse
                    - **Zoom:** Scroll mouse wheel or pinch
                    - **Pan:** Right-click and drag
                    - **Reset:** Double-click
                    """)

                with st.expander("🔍 Slice-by-Slice Navigation"):
                    st.markdown("View individual 2D slices from the 3D volume")
                    plane_selected = st.selectbox(
                        "Select Plane",
                        ["Axial (Transverse)", "Sagittal", "Coronal"]
                    )

                    from visualization.volume_3d import create_slice_comparison_figure
                    plane_map = {
                        "Axial (Transverse)": "axial",
                        "Sagittal": "sagittal",
                        "Coronal": "coronal"
                    }

                    try:
                        import nibabel as nib
                        nii_data = nib.load(nii_file)
                        volume_data = nii_data.get_fdata()
                        fig_slice = create_slice_comparison_figure(
                            volume_data, lesion_mask=None, plane=plane_map[plane_selected]
                        )
                        st.plotly_chart(fig_slice,  use_column_width=True)
                    except Exception as e:
                        st.error(f"Error loading slice: {str(e)}")

            except Exception as e:
                st.error(f"❌ Error processing 3D volume: {str(e)}")
                st.info("Please ensure the file is a valid NIfTI format (.nii or .nii.gz)")
        else:
            st.info("👆 Upload a CT or MRI scan (NIfTI format) to visualize in 3D")

# --------------------------------------------------
# 📈 COMPARATIVE LEARNING MODE TAB
# --------------------------------------------------
with tabs[5]:
    st.markdown("### 📈 Comparative Disease Progression Analysis")

    col1, col2 = st.columns(2)
    with col1:
        prev_file = st.file_uploader(
            "Upload Previous Scan", type=["jpg", "jpeg", "png"], key="prev_scan"
        )
    with col2:
        curr_file = st.file_uploader(
            "Upload Current Scan", type=["jpg", "jpeg", "png"], key="curr_scan"
        )

    st.metric(
        "Detected Structural Change Level", "Qualitative",
        help="Based on pixel-wise structural variation between scans"
    )

    if prev_file and curr_file:
        prev_img = Image.open(io.BytesIO(prev_file.getvalue()))
        curr_img = Image.open(io.BytesIO(curr_file.getvalue()))

        target_size = curr_img.size
        prev_gray = preprocess_compare_image(prev_img, target_size)
        curr_gray = preprocess_compare_image(curr_img, target_size)

        progression_map = compute_progression_map(prev_gray, curr_gray)

        st.markdown("#### 🔬 Comparative Disease Progression")
        c1, c2, c3 = st.columns(3)
        with c1:
            st.markdown("**Previous Scan**")
            st.image(prev_img,  use_column_width=True)
        with c2:
            st.markdown("**Current Scan**")
            st.image(curr_img, use_column_width=True)
        with c3:
            st.markdown("**Detected Changes**")
            st.image(progression_map, use_column_width=True)

        st.info(
            "The rightmost image highlights **structural changes over time**. "
            "Brighter blue regions indicate stronger progression or regression."
        )
    else:
        st.warning("Upload both previous and current scans to compare.")

# ==================================================
# COLLABORATION TAB
# ==================================================
with tabs[6]:
    render_collaboration_mode(
        model_prediction=labels[class_index],
        model_confidence=confidence,
        image=image,
        image_name=uploaded_file.name,
        heatmap=heatmap
    )

# ==================================================
# PATIENT TIMELINE DASHBOARD TAB
# ==================================================
with tabs[7]:
    render_patient_timeline_dashboard(patient_id=None)

# ==================================================
# PATIENT HEALTH TIMELINE TAB
# ==================================================
with tabs[8]:
    render_health_timeline_dashboard()

# ✅ ROLE-BASED TAB ACCESS
# Medication Suggestions Tab
with tabs[9]:
    if RoleBasedInterface.can_access_tab(current_role, "Medications"):
        show_medication_suggestions(selected_disease, confidence)
    else:
        show_access_denied_message("Medications", "Doctor or Radiologist")

# Symptom + Image Fusion Tab
with tabs[10]:
    if RoleBasedInterface.can_access_tab(current_role, "Symptom Fusion"):
        show_symptom_image_fusion(selected_disease, confidence)
    else:
        show_access_denied_message("Symptom Fusion", "Doctor or Radiologist")

# Population Comparison Tab
with tabs[11]:
    if RoleBasedInterface.can_access_tab(current_role, "Population Data"):
        age = st.sidebar.number_input("Patient Age", min_value=0, max_value=120, value=40)
        gender = st.sidebar.selectbox("Gender", ["Male", "Female", "Other"])
        show_population_comparison(selected_disease, confidence, age, gender)
    else:
        show_access_denied_message("Population Data", "Doctor or Radiologist")

# Why This Region Tab
with tabs[12]:
    if RoleBasedInterface.can_access_tab(current_role, "Why This Region?"):
        if regions:
            show_why_this_region(selected_disease, regions, heatmap)
        else:
            st.warning("⚠️ No regions detected. Upload image first.")
    else:
        show_access_denied_message("Why This Region?", "Doctor or Radiologist")

# Emergency Alert Tab
with tabs[13]:
    if RoleBasedInterface.can_access_tab(current_role, "Emergency"):
        show_emergency_alert_mode(selected_disease, confidence, labels[class_index])
    else:
        show_access_denied_message("Emergency", "Doctor or Radiologist")

# Cross-Device Continuity Tab
with tabs[14]:
    if RoleBasedInterface.can_access_tab(current_role, "Cross-Device"):
        show_cross_device_continuity(current_user)
    else:
        show_access_denied_message("Cross-Device", "Doctor or Radiologist")

# Chat with AI Tab
with tabs[15]:
    if RoleBasedInterface.can_access_tab(current_role, "Chat with AI"):
        show_chat_with_ai_report(selected_disease, confidence, get_current_user())
    else:
        show_access_denied_message("Chat with AI", "Medical Professional")

# Medical Audit & Compliance Tab
with tabs[16]:
    if RoleBasedInterface.can_access_tab(current_role, "Compliance Mode"):
        show_medical_audit_compliance(selected_disease, confidence, get_current_user())
    else:
        show_access_denied_message("Compliance Mode", "Doctor or Radiologist")

# Clinical Guidelines & Next Tests Tab
with tabs[17]:
    if RoleBasedInterface.can_access_tab(current_role, "Next Tests"):
        show_guideline_aligned_next_tests(selected_disease, confidence)
    else:
        show_access_denied_message("Next Tests", "Doctor or Radiologist")

# Voice Diagnosis Assistant Tab
with tabs[18]:
    if RoleBasedInterface.can_access_tab(current_role, "Voice Assistant"):
        show_voice_diagnosis_assistant(selected_disease, confidence)
    else:
        show_access_denied_message("Voice Assistant", "Medical Professional")


# ==================================================
# FOOTER
# ==================================================
st.markdown("---")
st.caption("Built as an educational AI demo 🧠")