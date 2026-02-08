"""
Patient Health Timeline Dashboard
- Visual timeline of patient diagnoses over time
- Recovery rate tracking
- Medical notes and observations
- Trend analysis and predictions
- Historical diagnosis comparison
- Patient health status tracking
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from enum import Enum


class HealthStatus(Enum):
    """Patient health status levels"""
    CRITICAL = "🔴 Critical"
    SEVERE = "🟠 Severe"
    MODERATE = "🟡 Moderate"
    MILD = "🟢 Mild"
    RECOVERED = "✅ Recovered"


class PatientHealthTimeline:
    """Manages patient health timeline and diagnosis history"""
    
    def __init__(self, timeline_dir="patient_timeline"):
        """
        Initialize patient timeline system
        
        Args:
            timeline_dir: Directory to store timeline data
        """
        self.timeline_dir = Path(timeline_dir)
        self.timeline_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.timeline_dir / "patients").mkdir(exist_ok=True)
        (self.timeline_dir / "diagnoses").mkdir(exist_ok=True)
        (self.timeline_dir / "notes").mkdir(exist_ok=True)
        (self.timeline_dir / "recovery").mkdir(exist_ok=True)
        
        self.patients_file = self.timeline_dir / "patients" / "patients.json"
        self.diagnoses_file = self.timeline_dir / "diagnoses" / "diagnoses.json"
        self.notes_file = self.timeline_dir / "notes" / "notes.json"
        self.recovery_file = self.timeline_dir / "recovery" / "recovery.json"
        
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        if not self.patients_file.exists():
            self._save_json(self.patients_file, {"total": 0, "patients": []})
        
        if not self.diagnoses_file.exists():
            self._save_json(self.diagnoses_file, {"total": 0, "diagnoses": []})
        
        if not self.notes_file.exists():
            self._save_json(self.notes_file, {"total": 0, "notes": []})
        
        if not self.recovery_file.exists():
            self._save_json(self.recovery_file, {"total": 0, "recovery_records": []})
    
    def _load_json(self, filepath):
        """Load JSON file safely"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except:
            return {}
    
    def _save_json(self, filepath, data):
        """Save JSON file safely"""
        try:
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2, default=str)
            return True
        except Exception as e:
            print(f"Error saving JSON: {e}")
            return False
    
    def add_patient(self, patient_id, patient_name, age, gender, medical_history=None):
        """
        Add new patient to system
        
        Args:
            patient_id: Unique patient identifier
            patient_name: Patient's name
            age: Patient's age
            gender: Patient's gender
            medical_history: Optional medical history
        
        Returns:
            Patient record
        """
        
        patient_data = {
            "id": str(patient_id),
            "name": str(patient_name),
            "age": int(age),
            "gender": str(gender),
            "created_date": datetime.now().isoformat(),
            "last_visit": datetime.now().isoformat(),
            "medical_history": medical_history or "",
            "total_diagnoses": 0,
            "current_status": "Active"
        }
        
        # Load existing patients
        data = self._load_json(self.patients_file)
        
        # Check if patient already exists
        existing = [p for p in data.get("patients", []) if p["id"] == str(patient_id)]
        if not existing:
            data["patients"].append(patient_data)
            data["total"] = len(data["patients"])
            self._save_json(self.patients_file, data)
        else:
            patient_data = existing[0]
        
        return patient_data
    
    def add_diagnosis(self, patient_id, diagnosis, confidence, image_name, 
                     severity="Moderate", notes="", ai_prediction=None):
        """
        Record a new diagnosis for patient
        
        Args:
            patient_id: Patient ID
            diagnosis: Diagnosis description
            confidence: AI confidence score (0-100)
            image_name: Name of medical image
            severity: Severity level (Mild, Moderate, Severe, Critical)
            notes: Clinical notes
            ai_prediction: Original AI prediction
        
        Returns:
            Diagnosis record
        """
        
        diagnosis_record = {
            "id": f"DX_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "patient_id": str(patient_id),
            "timestamp": datetime.now().isoformat(),
            "diagnosis": str(diagnosis),
            "confidence": float(confidence),
            "image_name": str(image_name),
            "severity": str(severity),
            "notes": str(notes),
            "ai_prediction": str(ai_prediction) if ai_prediction else "",
            "doctor_verified": False
        }
        
        # Load existing diagnoses
        data = self._load_json(self.diagnoses_file)
        data["diagnoses"].append(diagnosis_record)
        data["total"] = len(data["diagnoses"])
        
        # Update patient record
        patients_data = self._load_json(self.patients_file)
        for patient in patients_data.get("patients", []):
            if patient["id"] == str(patient_id):
                patient["total_diagnoses"] = sum(
                    1 for d in data["diagnoses"] if d["patient_id"] == str(patient_id)
                )
                patient["last_visit"] = datetime.now().isoformat()
        
        self._save_json(self.diagnoses_file, data)
        self._save_json(self.patients_file, patients_data)
        
        return diagnosis_record
    
    def add_medical_note(self, patient_id, note_title, note_content, note_type="General"):
        """
        Add medical note to patient record
        
        Args:
            patient_id: Patient ID
            note_title: Title of note
            note_content: Detailed note content
            note_type: Type of note (General, Follow-up, Observation, Warning)
        
        Returns:
            Note record
        """
        
        note_record = {
            "id": f"NOTE_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "patient_id": str(patient_id),
            "timestamp": datetime.now().isoformat(),
            "title": str(note_title),
            "content": str(note_content),
            "type": str(note_type)
        }
        
        # Load and update notes
        data = self._load_json(self.notes_file)
        data["notes"].append(note_record)
        data["total"] = len(data["notes"])
        
        self._save_json(self.notes_file, data)
        
        return note_record
    
    def add_recovery_update(self, patient_id, recovery_percentage, status, notes=""):
        """
        Record recovery progress for patient
        
        Args:
            patient_id: Patient ID
            recovery_percentage: Recovery progress (0-100%)
            status: Recovery status (Improving, Stable, Declining, Recovered)
            notes: Recovery notes
        
        Returns:
            Recovery record
        """
        
        recovery_record = {
            "id": f"REC_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "patient_id": str(patient_id),
            "timestamp": datetime.now().isoformat(),
            "recovery_percentage": float(recovery_percentage),
            "status": str(status),
            "notes": str(notes)
        }
        
        # Load and update recovery records
        data = self._load_json(self.recovery_file)
        data["recovery_records"].append(recovery_record)
        data["total"] = len(data["recovery_records"])
        
        self._save_json(self.recovery_file, data)
        
        return recovery_record
    
    def get_patient_timeline(self, patient_id):
        """
        Get complete timeline for a patient
        
        Args:
            patient_id: Patient ID
        
        Returns:
            Complete patient timeline data
        """
        
        # Get patient info
        patients_data = self._load_json(self.patients_file)
        patient = next(
            (p for p in patients_data.get("patients", []) if p["id"] == str(patient_id)),
            None
        )
        
        if not patient:
            return None
        
        # Get diagnoses
        diagnoses_data = self._load_json(self.diagnoses_file)
        diagnoses = [
            d for d in diagnoses_data.get("diagnoses", []) 
            if d["patient_id"] == str(patient_id)
        ]
        
        # Get notes
        notes_data = self._load_json(self.notes_file)
        notes = [
            n for n in notes_data.get("notes", []) 
            if n["patient_id"] == str(patient_id)
        ]
        
        # Get recovery records
        recovery_data = self._load_json(self.recovery_file)
        recovery_records = [
            r for r in recovery_data.get("recovery_records", []) 
            if r["patient_id"] == str(patient_id)
        ]
        
        return {
            "patient": patient,
            "diagnoses": sorted(diagnoses, key=lambda x: x["timestamp"]),
            "notes": sorted(notes, key=lambda x: x["timestamp"]),
            "recovery_records": sorted(recovery_records, key=lambda x: x["timestamp"])
        }
    
    def get_all_patients(self):
        """Get all patients"""
        data = self._load_json(self.patients_file)
        return data.get("patients", [])
    
    def calculate_recovery_rate(self, patient_id):
        """Calculate overall recovery rate for patient"""
        recovery_data = self._load_json(self.recovery_file)
        patient_records = [
            r for r in recovery_data.get("recovery_records", [])
            if r["patient_id"] == str(patient_id)
        ]
        
        if not patient_records:
            return 0
        
        # Return average recovery percentage
        return np.mean([r["recovery_percentage"] for r in patient_records])
    
    def get_diagnosis_trend(self, patient_id):
        """Get diagnosis severity trend for patient"""
        diagnoses_data = self._load_json(self.diagnoses_file)
        diagnoses = sorted(
            [d for d in diagnoses_data.get("diagnoses", []) if d["patient_id"] == str(patient_id)],
            key=lambda x: x["timestamp"]
        )
        
        # Map severity to numeric value
        severity_map = {"Mild": 1, "Moderate": 2, "Severe": 3, "Critical": 4}
        
        return [
            {
                "timestamp": d["timestamp"],
                "severity": d["severity"],
                "severity_score": severity_map.get(d["severity"], 2),
                "diagnosis": d["diagnosis"],
                "confidence": d["confidence"]
            }
            for d in diagnoses
        ]
    
    def predict_health_trajectory(self, patient_id):
        """Predict future health trajectory based on historical data"""
        recovery_records = self._load_json(self.recovery_file)
        patient_records = sorted(
            [r for r in recovery_records.get("recovery_records", []) if r["patient_id"] == str(patient_id)],
            key=lambda x: x["timestamp"]
        )
        
        if len(patient_records) < 2:
            return {"trend": "Insufficient data", "prediction": "Cannot predict"}
        
        # Simple linear trend
        recovery_values = [r["recovery_percentage"] for r in patient_records]
        x = np.arange(len(recovery_values))
        
        # Fit polynomial
        z = np.polyfit(x, recovery_values, 1)
        p = np.poly1d(z)
        
        # Predict next 5 days
        future_x = np.arange(len(recovery_values), len(recovery_values) + 5)
        predictions = p(future_x)
        
        # Determine trend
        slope = z[0]
        if slope > 2:
            trend = "📈 Improving Rapidly"
        elif slope > 0.5:
            trend = "📈 Improving"
        elif slope > -0.5:
            trend = "➡️ Stable"
        elif slope > -2:
            trend = "📉 Declining"
        else:
            trend = "📉 Declining Rapidly"
        
        return {
            "trend": trend,
            "slope": float(slope),
            "current_recovery": float(recovery_values[-1]),
            "predicted_recovery": float(np.mean(predictions)),
            "predictions": predictions.tolist()
        }


def create_diagnosis_timeline_chart(timeline_data):
    """Create interactive diagnosis timeline chart"""
    
    if not timeline_data or not timeline_data.get("diagnoses"):
        return None
    
    diagnoses = timeline_data["diagnoses"]
    
    # Create figure
    fig = go.Figure()
    
    # Add diagnosis markers
    for diagnosis in diagnoses:
        severity_color = {
            "Mild": "#90EE90",
            "Moderate": "#FFD700",
            "Severe": "#FF8C00",
            "Critical": "#FF0000"
        }
        
        color = severity_color.get(diagnosis["severity"], "#FFD700")
        
        fig.add_trace(go.Scatter(
            x=[diagnosis["timestamp"]],
            y=[diagnosis["confidence"]],
            mode='markers+text',
            marker=dict(
                size=15,
                color=color,
                line=dict(width=2, color="white")
            ),
            text=diagnosis["diagnosis"],
            textposition="top center",
            hovertemplate=f"""
            <b>{diagnosis['diagnosis']}</b><br>
            Date: {diagnosis['timestamp']}<br>
            Confidence: {diagnosis['confidence']:.1f}%<br>
            Severity: {diagnosis['severity']}<br>
            <extra></extra>
            """,
            name=diagnosis["diagnosis"]
        ))
    
    # Update layout
    fig.update_layout(
        title="📊 Patient Diagnosis Timeline",
        xaxis_title="Date",
        yaxis_title="AI Confidence (%)",
        hovermode="x unified",
        height=400,
        template="plotly_dark",
        showlegend=False
    )
    
    return fig


def create_recovery_trend_chart(recovery_records):
    """Create recovery progress trend chart"""
    
    if not recovery_records:
        return None
    
    df = pd.DataFrame(recovery_records)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    fig = go.Figure()
    
    # Add recovery progress line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["recovery_percentage"],
        mode='lines+markers',
        name='Recovery Progress',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=8),
        fill='tozeroy',
        fillcolor='rgba(0, 212, 170, 0.2)',
        hovertemplate="<b>Recovery Progress</b><br>Date: %{x}<br>Progress: %{y:.1f}%<extra></extra>"
    ))
    
    # Add status annotations
    for idx, row in df.iterrows():
        fig.add_annotation(
            x=row["timestamp"],
            y=row["recovery_percentage"],
            text=row["status"],
            showarrow=True,
            arrowhead=2,
            arrowsize=1,
            arrowwidth=2,
            arrowcolor="white",
            font=dict(size=9, color="white")
        )
    
    # Update layout
    fig.update_layout(
        title="📈 Recovery Progress Over Time",
        xaxis_title="Date",
        yaxis_title="Recovery Progress (%)",
        hovermode="x unified",
        height=400,
        template="plotly_dark",
        yaxis=dict(range=[0, 105])
    )
    
    return fig


def create_severity_distribution_chart(diagnoses):
    """Create severity distribution pie chart"""
    
    if not diagnoses:
        return None
    
    severity_counts = {}
    for diagnosis in diagnoses:
        severity = diagnosis["severity"]
        severity_counts[severity] = severity_counts.get(severity, 0) + 1
    
    colors = {
        "Mild": "#90EE90",
        "Moderate": "#FFD700",
        "Severe": "#FF8C00",
        "Critical": "#FF0000"
    }
    
    fig = go.Figure(data=[go.Pie(
        labels=list(severity_counts.keys()),
        values=list(severity_counts.values()),
        marker=dict(colors=[colors.get(k, "#FFD700") for k in severity_counts.keys()]),
        hovertemplate="<b>%{label}</b><br>Count: %{value}<extra></extra>"
    )])
    
    fig.update_layout(
        title="📊 Diagnosis Severity Distribution",
        height=400,
        template="plotly_dark"
    )
    
    return fig


def create_confidence_trend_chart(diagnoses):
    """Create AI confidence trend over time"""
    
    if not diagnoses:
        return None
    
    df = pd.DataFrame(diagnoses)
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df = df.sort_values("timestamp")
    
    fig = go.Figure()
    
    # Add confidence line
    fig.add_trace(go.Scatter(
        x=df["timestamp"],
        y=df["confidence"],
        mode='lines+markers',
        name='AI Confidence',
        line=dict(color='#FF6B9D', width=2),
        marker=dict(size=6),
        hovertemplate="<b>AI Confidence</b><br>Date: %{x}<br>Confidence: %{y:.1f}%<extra></extra>"
    ))
    
    # Add average line
    avg_confidence = df["confidence"].mean()
    fig.add_hline(
        y=avg_confidence,
        line_dash="dash",
        line_color="white",
        annotation_text=f"Average: {avg_confidence:.1f}%",
        annotation_position="right"
    )
    
    fig.update_layout(
        title="🎯 AI Prediction Confidence Trend",
        xaxis_title="Date",
        yaxis_title="Confidence (%)",
        hovermode="x unified",
        height=400,
        template="plotly_dark",
        yaxis=dict(range=[0, 105])
    )
    
    return fig


def render_health_timeline_dashboard():
    """Main function to render Patient Health Timeline Dashboard"""
    
    # Initialize timeline system
    timeline_system = PatientHealthTimeline(timeline_dir="patient_timeline")
    
    st.markdown("---")
    st.markdown("## 🏥 Patient Health Timeline Dashboard")
    
    st.info(
        "📊 **Track Patient Health**: View complete diagnosis history, recovery progress, "
        "medical notes, and health trajectory predictions for each patient."
    )
    
    # Create tabs for different views
    timeline_tabs = st.tabs([
        "👥 Patient Search",
        "📅 Timeline View",
        "📈 Analytics",
        "📝 Medical Notes",
        "🔮 Predictions"
    ])
    
    # ===== TAB 1: PATIENT SEARCH =====
    with timeline_tabs[0]:
        st.markdown("### 👥 Search & Select Patient")
        
        search_cols = st.columns(2)
        
        with search_cols[0]:
            search_type = st.radio(
                "Search by:",
                ["Patient ID", "Patient Name"],
                horizontal=True
            )
        
        with search_cols[1]:
            if search_type == "Patient ID":
                patient_id = st.text_input(
                    "Enter Patient ID",
                    placeholder="e.g., P001, PAT-2024-001"
                )
            else:
                patient_name = st.text_input(
                    "Enter Patient Name",
                    placeholder="e.g., John Doe"
                )
        
        st.markdown("---")
        
        # Add new patient option
        with st.expander("➕ Add New Patient"):
            col_new1, col_new2 = st.columns(2)
            
            with col_new1:
                new_patient_id = st.text_input("Patient ID", key="health_new_patient_id")
                new_patient_age = st.number_input("Age", min_value=0, max_value=150, value=30, key="health_new_patient_age")
            
            with col_new2:
                new_patient_name = st.text_input("Patient Name", key="health_new_patient_name")
                new_patient_gender = st.selectbox("Gender", ["Male", "Female", "Other"], key="health_new_patient_gender")
            
            new_patient_history = st.text_area(
                "Medical History",
                placeholder="Any relevant medical history...",
                height=80,
                key="health_new_patient_history"
            )
            
            if st.button("➕ Add Patient", use_container_width=True):
                if new_patient_id and new_patient_name:
                    timeline_system.add_patient(
                        new_patient_id,
                        new_patient_name,
                        new_patient_age,
                        new_patient_gender,
                        new_patient_history
                    )
                    st.success(f"✅ Patient {new_patient_name} added successfully!")
                    st.rerun()
                else:
                    st.error("❌ Please enter Patient ID and Name")
        
        st.markdown("---")
        
        # Display existing patients
        st.markdown("### 📋 All Patients")
        all_patients = timeline_system.get_all_patients()
        
        if all_patients:
            patients_df = pd.DataFrame([
                {
                    "ID": p["id"],
                    "Name": p["name"],
                    "Age": p["age"],
                    "Gender": p["gender"],
                    "Diagnoses": p["total_diagnoses"],
                    "Last Visit": p["last_visit"][:10]
                }
                for p in all_patients
            ])
            st.dataframe(patients_df, use_container_width=True, hide_index=True)
        else:
            st.info("ℹ️ No patients registered yet. Add a new patient above.")
    
    # ===== TAB 2: TIMELINE VIEW =====
    with timeline_tabs[1]:
        st.markdown("### 📅 Patient Diagnosis Timeline")
        
        # Patient selector
        all_patients = timeline_system.get_all_patients()
        if all_patients:
            selected_patient = st.selectbox(
                "Select Patient",
                options=[p["id"] for p in all_patients],
                format_func=lambda x: next((f"{p['name']} ({p['id']})" for p in all_patients if p["id"] == x), x)
            )
            
            timeline_data = timeline_system.get_patient_timeline(selected_patient)
            
            if timeline_data:
                patient = timeline_data["patient"]
                diagnoses = timeline_data["diagnoses"]
                
                # Patient info
                col_info1, col_info2, col_info3, col_info4 = st.columns(4)
                
                with col_info1:
                    st.metric("Patient Name", patient["name"])
                with col_info2:
                    st.metric("Age", patient["age"])
                with col_info3:
                    st.metric("Total Diagnoses", patient["total_diagnoses"])
                with col_info4:
                    recovery_rate = timeline_system.calculate_recovery_rate(selected_patient)
                    st.metric("Recovery Rate", f"{recovery_rate:.1f}%")
                
                st.markdown("---")
                
                # Timeline chart
                timeline_chart = create_diagnosis_timeline_chart(timeline_data)
                if timeline_chart:
                    st.plotly_chart(timeline_chart, use_container_width=True)
                
                st.markdown("---")
                
                # Diagnosis list
                st.markdown("### 📋 Diagnosis History")
                
                if diagnoses:
                    for diagnosis in reversed(diagnoses):
                        severity_emoji = {
                            "Mild": "🟢",
                            "Moderate": "🟡",
                            "Severe": "🟠",
                            "Critical": "🔴"
                        }
                        
                        with st.expander(
                            f"{severity_emoji.get(diagnosis['severity'], '📋')} "
                            f"{diagnosis['diagnosis']} - {diagnosis['timestamp'][:10]}"
                        ):
                            col_d1, col_d2 = st.columns(2)
                            
                            with col_d1:
                                st.write(f"**Confidence:** {diagnosis['confidence']:.1f}%")
                                st.write(f"**Severity:** {diagnosis['severity']}")
                                st.write(f"**Image:** {diagnosis['image_name']}")
                            
                            with col_d2:
                                st.write(f"**Timestamp:** {diagnosis['timestamp']}")
                                st.write(f"**Verified:** {'✅ Yes' if diagnosis['doctor_verified'] else '❌ No'}")
                                if diagnosis['ai_prediction']:
                                    st.write(f"**AI Prediction:** {diagnosis['ai_prediction']}")
                            
                            if diagnosis['notes']:
                                st.write(f"**Notes:** {diagnosis['notes']}")
                else:
                    st.info("ℹ️ No diagnoses recorded for this patient yet.")
        else:
            st.info("ℹ️ No patients available. Please add a patient first.")
    
    # ===== TAB 3: ANALYTICS =====
    with timeline_tabs[2]:
        st.markdown("### 📈 Patient Analytics")
        
        all_patients = timeline_system.get_all_patients()
        if all_patients:
            selected_patient = st.selectbox(
                "Select Patient for Analytics",
                options=[p["id"] for p in all_patients],
                format_func=lambda x: next((f"{p['name']} ({p['id']})" for p in all_patients if p["id"] == x), x),
                key="analytics_patient"
            )
            
            timeline_data = timeline_system.get_patient_timeline(selected_patient)
            
            if timeline_data:
                diagnoses = timeline_data["diagnoses"]
                recovery_records = timeline_data["recovery_records"]
                
                # Recovery trend
                if recovery_records:
                    st.markdown("#### 📊 Recovery Progress")
                    recovery_chart = create_recovery_trend_chart(recovery_records)
                    if recovery_chart:
                        st.plotly_chart(recovery_chart, use_container_width=True)
                
                # Severity distribution
                if diagnoses:
                    st.markdown("#### 🎯 Severity Distribution")
                    severity_chart = create_severity_distribution_chart(diagnoses)
                    if severity_chart:
                        st.plotly_chart(severity_chart, use_container_width=True)
                
                # Confidence trend
                if diagnoses:
                    st.markdown("#### 🔍 AI Confidence Trend")
                    confidence_chart = create_confidence_trend_chart(diagnoses)
                    if confidence_chart:
                        st.plotly_chart(confidence_chart, use_container_width=True)
        else:
            st.info("ℹ️ No patients available for analytics.")
    
    # ===== TAB 4: MEDICAL NOTES =====
    with timeline_tabs[3]:
        st.markdown("### 📝 Medical Notes & Observations")
        
        all_patients = timeline_system.get_all_patients()
        if all_patients:
            selected_patient = st.selectbox(
                "Select Patient",
                options=[p["id"] for p in all_patients],
                format_func=lambda x: next((f"{p['name']} ({p['id']})" for p in all_patients if p["id"] == x), x),
                key="notes_patient"
            )
            
            st.markdown("---")
            
            # Add new note
            with st.expander("➕ Add New Medical Note"):
                col_note1, col_note2 = st.columns(2)
                
                with col_note1:
                    note_title = st.text_input("Note Title")
                    note_type = st.selectbox(
                        "Note Type",
                        ["General", "Follow-up", "Observation", "Warning", "Recommendation"]
                    )
                
                with col_note2:
                    note_content = st.text_area(
                        "Note Content",
                        placeholder="Enter detailed medical notes...",
                        height=100
                    )
                
                if st.button("💾 Save Note", use_container_width=True):
                    if note_title and note_content:
                        timeline_system.add_medical_note(
                            selected_patient,
                            note_title,
                            note_content,
                            note_type
                        )
                        st.success("✅ Medical note saved successfully!")
                        st.rerun()
                    else:
                        st.error("❌ Please fill in all fields")
            
            st.markdown("---")
            
            # Display notes
            st.markdown("### 📋 Patient Notes History")
            timeline_data = timeline_system.get_patient_timeline(selected_patient)
            
            if timeline_data and timeline_data["notes"]:
                notes = timeline_data["notes"]
                
                for note in reversed(notes):
                    note_type_emoji = {
                        "General": "📝",
                        "Follow-up": "🔄",
                        "Observation": "👁️",
                        "Warning": "⚠️",
                        "Recommendation": "💡"
                    }
                    
                    with st.expander(
                        f"{note_type_emoji.get(note['type'], '📝')} "
                        f"{note['title']} - {note['timestamp'][:10]}"
                    ):
                        st.write(f"**Type:** {note['type']}")
                        st.write(f"**Content:** {note['content']}")
                        st.caption(f"Created: {note['timestamp']}")
            else:
                st.info("ℹ️ No medical notes for this patient yet.")
        else:
            st.info("ℹ️ No patients available.")
    
    # ===== TAB 5: PREDICTIONS =====
    with timeline_tabs[4]:
        st.markdown("### 🔮 Health Trajectory Predictions")
        
        all_patients = timeline_system.get_all_patients()
        if all_patients:
            selected_patient = st.selectbox(
                "Select Patient",
                options=[p["id"] for p in all_patients],
                format_func=lambda x: next((f"{p['name']} ({p['id']})" for p in all_patients if p["id"] == x), x),
                key="prediction_patient"
            )
            
            trajectory = timeline_system.predict_health_trajectory(selected_patient)
            
            if trajectory and trajectory["trend"] != "Insufficient data":
                col_pred1, col_pred2, col_pred3 = st.columns(3)
                
                with col_pred1:
                    st.metric("Health Trend", trajectory["trend"])
                
                with col_pred2:
                    st.metric(
                        "Current Recovery",
                        f"{trajectory['current_recovery']:.1f}%"
                    )
                
                with col_pred3:
                    st.metric(
                        "Predicted Recovery (5 days)",
                        f"{trajectory['predicted_recovery']:.1f}%"
                    )
                
                st.markdown("---")
                
                st.markdown("#### 📊 Recovery Projection")
                
                # Create projection chart
                timeline_data = timeline_system.get_patient_timeline(selected_patient)
                recovery_records = timeline_data["recovery_records"]
                
                if recovery_records:
                    df = pd.DataFrame(recovery_records)
                    df["timestamp"] = pd.to_datetime(df["timestamp"])
                    df = df.sort_values("timestamp")
                    
                    # Historical data
                    historical_x = np.arange(len(df))
                    historical_y = df["recovery_percentage"].values
                    
                    # Projection
                    z = np.polyfit(historical_x, historical_y, 1)
                    p = np.poly1d(z)
                    future_x = np.arange(len(df), len(df) + 5)
                    predictions = p(future_x)
                    
                    fig = go.Figure()
                    
                    # Historical
                    fig.add_trace(go.Scatter(
                        x=df["timestamp"],
                        y=historical_y,
                        mode='lines+markers',
                        name='Historical Recovery',
                        line=dict(color='#00d4aa', width=3),
                        marker=dict(size=8)
                    ))
                    
                    # Projection
                    future_dates = [
                        df["timestamp"].max() + timedelta(days=i) 
                        for i in range(1, 6)
                    ]
                    fig.add_trace(go.Scatter(
                        x=future_dates,
                        y=predictions,
                        mode='lines+markers',
                        name='Projected Recovery',
                        line=dict(color='#FF6B9D', width=3, dash='dash'),
                        marker=dict(size=8)
                    ))
                    
                    fig.update_layout(
                        title="🔮 Recovery Trajectory Projection",
                        xaxis_title="Date",
                        yaxis_title="Recovery (%)",
                        hovermode="x unified",
                        height=400,
                        template="plotly_dark",
                        yaxis=dict(range=[0, 105])
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Insufficient data for predictions. Need at least 2 recovery records.")
        else:
            st.info("ℹ️ No patients available.")


if __name__ == "__main__":
    # Test the system
    test_system = PatientHealthTimeline()
    print("Patient Health Timeline initialized successfully!")