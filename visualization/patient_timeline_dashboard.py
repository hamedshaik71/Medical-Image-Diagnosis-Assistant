"""
Patient Health Timeline Dashboard
- Visual timeline of diagnoses over time
- Prediction accuracy tracking
- Recovery rate monitoring
- Clinical notes and observations
- Comparative analysis between visits
- Health trend analysis
"""

import streamlit as st
import json
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go
import plotly.express as px
from PIL import Image
import io


class PatientTimelineManager:
    """Manages patient health records and timeline data"""
    
    def __init__(self, timeline_dir="patient_timeline"):
        """
        Initialize timeline manager
        
        Args:
            timeline_dir: Directory to store patient timeline data
        """
        self.timeline_dir = Path(timeline_dir)
        self.timeline_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.timeline_dir / "patients").mkdir(exist_ok=True)
        (self.timeline_dir / "visits").mkdir(exist_ok=True)
        (self.timeline_dir / "analytics").mkdir(exist_ok=True)
        
        self.patients_index = self.timeline_dir / "patients_index.json"
        
        # Initialize index file
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        if not self.patients_index.exists():
            self._save_json(self.patients_index, {"patients": [], "total": 0})
    
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
    
    def create_or_get_patient(self, patient_id, patient_name, age=None, gender=None, medical_history=None):
        """
        Create or retrieve patient record
        
        Args:
            patient_id: Unique patient identifier
            patient_name: Patient's full name
            age: Patient's age
            gender: Patient's gender
            medical_history: Previous medical conditions
        
        Returns:
            Patient record
        """
        
        # Load patients index
        index_data = self._load_json(self.patients_index)
        
        # Check if patient exists
        existing_patient = next((p for p in index_data["patients"] if p["patient_id"] == patient_id), None)
        
        if existing_patient:
            return existing_patient
        
        # Create new patient
        patient_record = {
            "patient_id": str(patient_id),
            "patient_name": str(patient_name),
            "age": age,
            "gender": gender,
            "medical_history": medical_history or [],
            "created_date": datetime.now().isoformat(),
            "total_visits": 0,
            "last_visit": None
        }
        
        # Save patient file
        patient_file = self.timeline_dir / "patients" / f"{patient_id}.json"
        self._save_json(patient_file, {
            "patient": patient_record,
            "visits": []
        })
        
        # Update index
        index_data["patients"].append(patient_record)
        index_data["total"] = len(index_data["patients"])
        self._save_json(self.patients_index, index_data)
        
        return patient_record
    
    def add_visit(self, patient_id, diagnosis, confidence, notes="", 
                  recovery_rate=None, image_path=None, additional_findings=None):
        """
        Add a visit/diagnosis record for patient
        
        Args:
            patient_id: Patient identifier
            diagnosis: AI diagnosis
            confidence: Confidence score (0-100)
            notes: Doctor's clinical notes
            recovery_rate: Recovery percentage (0-100)
            image_path: Path to medical image
            additional_findings: Other findings
        
        Returns:
            Visit record and success status
        """
        
        visit_record = {
            "visit_id": f"V_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "diagnosis": str(diagnosis),
            "confidence": float(confidence),
            "notes": str(notes),
            "recovery_rate": float(recovery_rate) if recovery_rate else 0,
            "image_path": str(image_path) if image_path else None,
            "additional_findings": additional_findings or {},
            "status": self._determine_status(confidence, recovery_rate)
        }
        
        # Load patient file
        patient_file = self.timeline_dir / "patients" / f"{patient_id}.json"
        patient_data = self._load_json(patient_file)
        
        if not patient_data:
            return None, False
        
        # Add visit
        patient_data["visits"].append(visit_record)
        
        # Update patient info
        patient_data["patient"]["total_visits"] = len(patient_data["visits"])
        patient_data["patient"]["last_visit"] = visit_record["timestamp"]
        
        # Save updated patient file
        self._save_json(patient_file, patient_data)
        
        # Update index
        index_data = self._load_json(self.patients_index)
        for p in index_data["patients"]:
            if p["patient_id"] == patient_id:
                p["total_visits"] = len(patient_data["visits"])
                p["last_visit"] = visit_record["timestamp"]
        self._save_json(self.patients_index, index_data)
        
        return visit_record, True
    
    def _determine_status(self, confidence, recovery_rate):
        """Determine visit status based on metrics"""
        if recovery_rate is None or recovery_rate == 0:
            if confidence >= 80:
                return "Active - High Confidence"
            elif confidence >= 60:
                return "Active - Medium Confidence"
            else:
                return "Active - Low Confidence"
        elif recovery_rate >= 80:
            return "Recovered"
        elif recovery_rate >= 50:
            return "Recovering"
        else:
            return "Active Treatment"
    
    def get_patient_timeline(self, patient_id):
        """Get complete timeline for a patient"""
        patient_file = self.timeline_dir / "patients" / f"{patient_id}.json"
        patient_data = self._load_json(patient_file)
        
        if not patient_data:
            return None
        
        return patient_data
    
    def get_all_patients(self):
        """Get list of all patients"""
        index_data = self._load_json(self.patients_index)
        return index_data.get("patients", [])
    
    def calculate_timeline_metrics(self, patient_id):
        """Calculate metrics for patient timeline"""
        patient_data = self.get_patient_timeline(patient_id)
        
        if not patient_data or not patient_data["visits"]:
            return None
        
        visits = patient_data["visits"]
        
        metrics = {
            "total_visits": len(visits),
            "avg_confidence": np.mean([v["confidence"] for v in visits]),
            "avg_recovery_rate": np.mean([v["recovery_rate"] for v in visits]),
            "latest_diagnosis": visits[-1]["diagnosis"] if visits else None,
            "latest_status": visits[-1]["status"] if visits else None,
            "diagnosis_history": [v["diagnosis"] for v in visits],
            "confidence_trend": [v["confidence"] for v in visits],
            "recovery_trend": [v["recovery_rate"] for v in visits],
            "visits_timeline": visits
        }
        
        return metrics
    
    def get_diagnosis_distribution(self, patient_id):
        """Get distribution of diagnoses over time"""
        metrics = self.calculate_timeline_metrics(patient_id)
        
        if not metrics:
            return None
        
        diagnosis_counts = {}
        for diagnosis in metrics["diagnosis_history"]:
            diagnosis_counts[diagnosis] = diagnosis_counts.get(diagnosis, 0) + 1
        
        return diagnosis_counts
    
    def export_patient_report(self, patient_id):
        """Export complete patient report"""
        patient_data = self.get_patient_timeline(patient_id)
        
        if not patient_data:
            return None
        
        # Create report
        report = {
            "generated_date": datetime.now().isoformat(),
            "patient": patient_data["patient"],
            "visits": patient_data["visits"],
            "summary": self.calculate_timeline_metrics(patient_id)
        }
        
        return report


def create_timeline_chart(patient_data, metrics):
    """
    Create interactive timeline chart
    
    Args:
        patient_data: Patient information
        metrics: Timeline metrics
    
    Returns:
        Plotly figure
    """
    
    visits = metrics["visits_timeline"]
    
    if not visits:
        return None
    
    # Extract data
    timestamps = [datetime.fromisoformat(v["timestamp"]) for v in visits]
    diagnoses = [v["diagnosis"] for v in visits]
    confidences = [v["confidence"] for v in visits]
    recovery_rates = [v["recovery_rate"] for v in visits]
    status_list = [v["status"] for v in visits]
    
    # Get patient name safely
    patient_name = patient_data.get("patient", {}).get("patient_name", "Unknown Patient")
    if not patient_name:
        patient_name = "Unknown Patient"
    
    # Create figure with secondary y-axis
    fig = go.Figure()
    
    # Add confidence line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=confidences,
        mode='lines+markers',
        name='AI Confidence',
        line=dict(color='#00d4aa', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Confidence: %{y:.1f}%<extra></extra>'
    ))
    
    # Add recovery rate line
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=recovery_rates,
        mode='lines+markers',
        name='Recovery Rate',
        line=dict(color='#ff9500', width=3),
        marker=dict(size=10),
        yaxis='y2',
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Recovery: %{y:.1f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        title=f"<b>Health Timeline: {patient_name}</b>",
        xaxis_title="Date",
        yaxis_title="AI Confidence (%)",
        yaxis2=dict(
            title="Recovery Rate (%)",
            overlaying='y',
            side='right',
            range=[0, 100]
        ),
        yaxis=dict(range=[0, 100]),
        hovermode='x unified',
        height=500,
        template='plotly_dark',
        margin=dict(l=50, r=100, b=50, t=80)
    )
    
    return fig


def create_diagnosis_distribution(patient_id, metrics):
    """Create pie chart of diagnosis distribution"""
    
    diagnosis_dist = {}
    for v in metrics["visits_timeline"]:
        diagnosis = v["diagnosis"]
        diagnosis_dist[diagnosis] = diagnosis_dist.get(diagnosis, 0) + 1
    
    fig = go.Figure(data=[go.Pie(
        labels=list(diagnosis_dist.keys()),
        values=list(diagnosis_dist.values()),
        hovertemplate='<b>%{label}</b><br>Count: %{value}<extra></extra>'
    )])
    
    fig.update_layout(
        title="Diagnosis Distribution Over Time",
        height=400,
        template='plotly_dark'
    )
    
    return fig


def create_recovery_progress_chart(metrics):
    """Create recovery progress visualization"""
    
    visits = metrics["visits_timeline"]
    timestamps = [datetime.fromisoformat(v["timestamp"]) for v in visits]
    recovery_rates = [v["recovery_rate"] for v in visits]
    
    fig = go.Figure()
    
    # Recovery progress bar
    fig.add_trace(go.Scatter(
        x=timestamps,
        y=recovery_rates,
        fill='tozeroy',
        name='Recovery Rate',
        line=dict(color='#00ff88', width=3),
        marker=dict(size=10),
        hovertemplate='<b>%{x|%Y-%m-%d}</b><br>Recovery: %{y:.1f}%<extra></extra>'
    ))
    
    # Add recovery milestones
    fig.add_hline(y=50, line_dash="dash", line_color="orange", 
                  annotation_text="50% Recovery", annotation_position="right")
    fig.add_hline(y=80, line_dash="dash", line_color="green", 
                  annotation_text="80% Recovery (Clinical Target)", annotation_position="right")
    
    fig.update_layout(
        title="Recovery Progress Over Time",
        xaxis_title="Date",
        yaxis_title="Recovery Rate (%)",
        yaxis=dict(range=[0, 100]),
        height=400,
        template='plotly_dark',
        hovermode='x unified'
    )
    
    return fig


def render_patient_timeline_dashboard(patient_id=None):
    """
    Main function to render Patient Health Timeline Dashboard
    
    Args:
        patient_id: Optional patient ID to load
    """
    
    # Initialize timeline manager
    timeline_manager = PatientTimelineManager(timeline_dir="patient_timeline")
    
    st.markdown("---")
    st.markdown("## 📊 Patient Health Timeline Dashboard")
    
    st.info(
        "📈 **Track Patient Progress**: Monitor diagnosis history, recovery rates, "
        "AI prediction accuracy, and clinical notes over time."
    )
    
    # Create tabs
    timeline_tabs = st.tabs([
        "👤 Patient Selection",
        "📅 Timeline View",
        "📈 Progress Analysis",
        "📊 Statistics",
        "📋 Clinical Notes",
        "📥 Export Report"
    ])
    
    # ===== TAB 1: PATIENT SELECTION =====
    with timeline_tabs[0]:
        st.markdown("### 👤 Select or Create Patient Record")
        
        # Get all patients
        all_patients = timeline_manager.get_all_patients()
        
        col_select1, col_select2 = st.columns(2)
        
        with col_select1:
            if all_patients:
                patient_options = {p["patient_name"]: p["patient_id"] for p in all_patients}
                selected_patient_name = st.selectbox(
                    "Existing Patients",
                    list(patient_options.keys()),
                    key="patient_select"
                )
                selected_patient_id = patient_options[selected_patient_name]
            else:
                selected_patient_id = None
                st.info("No patients found. Create a new patient record below.")
        
        st.markdown("---")
        st.markdown("### ➕ Add New Patient or Add Visit")
        
        if selected_patient_id:
            st.success(f"✅ Selected Patient: {selected_patient_name}")
            
            # Get patient data
            patient_data = timeline_manager.get_patient_timeline(selected_patient_id)
            
            st.markdown("#### 📝 Add New Visit Record")
            
            visit_cols = st.columns(2)
            
            with visit_cols[0]:
                visit_diagnosis = st.text_input(
                    "Diagnosis",
                    placeholder="e.g., Brain Tumor, Pneumonia"
                )
                visit_confidence = st.slider(
                    "AI Confidence (%)",
                    0, 100, 75
                )
            
            with visit_cols[1]:
                visit_recovery = st.slider(
                    "Recovery Rate (%)",
                    0, 100, 0,
                    help="Patient's recovery progress (0% = no improvement, 100% = fully recovered)"
                )
                visit_status = st.selectbox(
                    "Treatment Status",
                    ["Active Treatment", "Recovering", "Recovered", "Monitoring"]
                )
            
            visit_notes = st.text_area(
                "Clinical Notes",
                placeholder="Doctor's observations, treatment plan, follow-up recommendations...",
                height=100
            )
            
            additional_findings = st.text_area(
                "Additional Findings",
                placeholder="Secondary findings, comorbidities, risk factors...",
                height=80
            )
            
            if st.button("💾 Save Visit Record", use_container_width=True):
                visit_record, success = timeline_manager.add_visit(
                    patient_id=selected_patient_id,
                    diagnosis=visit_diagnosis,
                    confidence=visit_confidence,
                    notes=visit_notes,
                    recovery_rate=visit_recovery,
                    additional_findings=additional_findings
                )
                
                if success:
                    st.success(
                        f"✅ **Visit Recorded!**\n\n"
                        f"Visit ID: `{visit_record['visit_id']}`\n"
                        f"Diagnosis: **{visit_diagnosis}**\n"
                        f"Recovery: **{visit_recovery}%**",
                        icon="🎉"
                    )
                    st.rerun()
                else:
                    st.error("Failed to save visit record.")
        
        else:
            st.markdown("#### 🆕 Create New Patient")
            
            new_patient_cols = st.columns(2)
            
            with new_patient_cols[0]:
                new_patient_id = st.text_input(
                    "Patient ID",
                    placeholder="e.g., P001, P123",
                    key="new_patient_id"
                )
                new_patient_name = st.text_input(
                    "Patient Name",
                    placeholder="Full name",
                    key="new_patient_name"
                )
                new_patient_age = st.number_input(
                    "Age",
                    min_value=1,
                    max_value=120,
                    value=50,
                    key="new_patient_age"
                )
            
            with new_patient_cols[1]:
                new_patient_gender = st.selectbox(
                    "Gender",
                    ["Male", "Female", "Other"],
                    key="new_patient_gender"
                )
                new_patient_history = st.text_area(
                    "Medical History",
                    placeholder="Previous conditions, allergies, surgeries...",
                    height=80,
                    key="new_patient_history"
                )
            
            if st.button("🆕 Create Patient Record", use_container_width=True):
                if new_patient_id and new_patient_name:
                    patient_record = timeline_manager.create_or_get_patient(
                        patient_id=new_patient_id,
                        patient_name=new_patient_name,
                        age=new_patient_age,
                        gender=new_patient_gender,
                        medical_history=new_patient_history.split(",") if new_patient_history else []
                    )
                    
                    st.success(
                        f"✅ **Patient Created!**\n\n"
                        f"Patient ID: `{patient_record['patient_id']}`\n"
                        f"Name: **{patient_record['patient_name']}**",
                        icon="🎉"
                    )
                    st.rerun()
                else:
                    st.error("Please fill in Patient ID and Name.")
    
    # ===== TAB 2: TIMELINE VIEW =====
    with timeline_tabs[1]:
        st.markdown("### 📅 Patient Timeline Visualization")
        
        # Get all patients for selection
        all_patients = timeline_manager.get_all_patients()
        
        if all_patients:
            patient_options = {p["patient_name"]: p["patient_id"] for p in all_patients}
            selected_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                key="timeline_patient"
            )
            
            selected_id = patient_options[selected_name]
            patient_data = timeline_manager.get_patient_timeline(selected_id)
            
            if patient_data and patient_data["visits"]:
                metrics = timeline_manager.calculate_timeline_metrics(selected_id)
                
                # Patient info
                st.markdown(f"### 👤 {patient_data['patient']['patient_name']}")
                
                info_cols = st.columns(4)
                with info_cols[0]:
                    st.metric("Total Visits", metrics["total_visits"])
                with info_cols[1]:
                    st.metric("Avg Confidence", f"{metrics['avg_confidence']:.1f}%")
                with info_cols[2]:
                    st.metric("Avg Recovery", f"{metrics['avg_recovery_rate']:.1f}%")
                with info_cols[3]:
                    st.metric("Latest Status", metrics["latest_status"])
                
                st.markdown("---")
                
                # Timeline chart
                fig = create_timeline_chart(patient_data, metrics)
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("No visit records for this patient yet.")
        else:
            st.info("No patients found. Create a patient record first.")
    
    # ===== TAB 3: PROGRESS ANALYSIS =====
    with timeline_tabs[2]:
        st.markdown("### 📈 Progress Analysis")
        
        all_patients = timeline_manager.get_all_patients()
        
        if all_patients:
            patient_options = {p["patient_name"]: p["patient_id"] for p in all_patients}
            selected_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                key="progress_patient"
            )
            
            selected_id = patient_options[selected_name]
            patient_data = timeline_manager.get_patient_timeline(selected_id)
            
            if patient_data and patient_data["visits"]:
                metrics = timeline_manager.calculate_timeline_metrics(selected_id)
                
                col_ana1, col_ana2 = st.columns(2)
                
                with col_ana1:
                    # Recovery progress
                    fig_recovery = create_recovery_progress_chart(metrics)
                    st.plotly_chart(fig_recovery, use_container_width=True)
                
                with col_ana2:
                    # Diagnosis distribution
                    fig_dist = create_diagnosis_distribution(selected_id, metrics)
                    st.plotly_chart(fig_dist, use_container_width=True)
            else:
                st.info("No visit records for this patient.")
        else:
            st.info("No patients found.")
    
    # ===== TAB 4: STATISTICS =====
    with timeline_tabs[3]:
        st.markdown("### 📊 Detailed Statistics")
        
        all_patients = timeline_manager.get_all_patients()
        
        if all_patients:
            patient_options = {p["patient_name"]: p["patient_id"] for p in all_patients}
            selected_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                key="stats_patient"
            )
            
            selected_id = patient_options[selected_name]
            patient_data = timeline_manager.get_patient_timeline(selected_id)
            
            if patient_data and patient_data["visits"]:
                visits = patient_data["visits"]
                
                # Create DataFrame
                df = pd.DataFrame(visits)[["timestamp", "diagnosis", "confidence", "recovery_rate", "status"]]
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp")
                df.columns = ["Date", "Diagnosis", "Confidence (%)", "Recovery (%)", "Status"]
                
                st.markdown("#### 📋 Visit History")
                st.dataframe(df, use_container_width=True)
                
                st.markdown("---")
                
                # Summary statistics
                st.markdown("#### 📊 Summary Statistics")
                
                stat_cols = st.columns(4)
                
                with stat_cols[0]:
                    st.metric(
                        "Avg Confidence",
                        f"{np.mean([v['confidence'] for v in visits]):.1f}%"
                    )
                
                with stat_cols[1]:
                    st.metric(
                        "Max Confidence",
                        f"{max([v['confidence'] for v in visits]):.1f}%"
                    )
                
                with stat_cols[2]:
                    st.metric(
                        "Avg Recovery",
                        f"{np.mean([v['recovery_rate'] for v in visits]):.1f}%"
                    )
                
                with stat_cols[3]:
                    st.metric(
                        "Max Recovery",
                        f"{max([v['recovery_rate'] for v in visits]):.1f}%"
                    )
            else:
                st.info("No visit records for this patient.")
        else:
            st.info("No patients found.")
    
    # ===== TAB 5: CLINICAL NOTES =====
    with timeline_tabs[4]:
        st.markdown("### 📋 Clinical Notes & Observations")
        
        all_patients = timeline_manager.get_all_patients()
        
        if all_patients:
            patient_options = {p["patient_name"]: p["patient_id"] for p in all_patients}
            selected_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                key="notes_patient"
            )
            
            selected_id = patient_options[selected_name]
            patient_data = timeline_manager.get_patient_timeline(selected_id)
            
            if patient_data and patient_data["visits"]:
                visits = patient_data["visits"]
                
                # Display notes for each visit
                for i, visit in enumerate(reversed(visits), 1):
                    with st.expander(
                        f"📅 Visit {len(visits)-i+1}: {visit['diagnosis']} - "
                        f"{datetime.fromisoformat(visit['timestamp']).strftime('%Y-%m-%d')}",
                        expanded=(i == 1)
                    ):
                        col_note1, col_note2 = st.columns(2)
                        
                        with col_note1:
                            st.markdown(f"**Diagnosis:** {visit['diagnosis']}")
                            st.markdown(f"**Confidence:** {visit['confidence']:.1f}%")
                            st.markdown(f"**Recovery:** {visit['recovery_rate']:.1f}%")
                            st.markdown(f"**Status:** {visit['status']}")
                        
                        with col_note2:
                            st.markdown("**Clinical Notes:**")
                            st.markdown(visit['notes'] if visit['notes'] else "No notes")
                        
                        if visit.get('additional_findings'):
                            st.markdown("**Additional Findings:**")
                            st.markdown(str(visit['additional_findings']))
            else:
                st.info("No visit records for this patient.")
        else:
            st.info("No patients found.")
    
    # ===== TAB 6: EXPORT REPORT =====
    with timeline_tabs[5]:
        st.markdown("### 📥 Export Patient Report")
        
        all_patients = timeline_manager.get_all_patients()
        
        if all_patients:
            patient_options = {p["patient_name"]: p["patient_id"] for p in all_patients}
            selected_name = st.selectbox(
                "Select Patient",
                list(patient_options.keys()),
                key="export_patient"
            )
            
            selected_id = patient_options[selected_name]
            report = timeline_manager.export_patient_report(selected_id)
            
            if report:
                # Display report summary
                st.markdown("#### 📄 Report Summary")
                
                st.markdown(f"""
                **Patient:** {report['patient']['patient_name']}  
                **Patient ID:** {report['patient']['patient_id']}  
                **Age:** {report['patient']['age']}  
                **Gender:** {report['patient']['gender']}  
                **Total Visits:** {len(report['visits'])}  
                **Report Generated:** {report['generated_date']}
                """)
                
                st.markdown("---")
                
                # Download options
                st.markdown("#### 💾 Download Options")
                
                col_exp1, col_exp2 = st.columns(2)
                
                with col_exp1:
                    # JSON export
                    json_str = json.dumps(report, indent=2, default=str)
                    st.download_button(
                        "📥 Download as JSON",
                        json_str,
                        f"patient_{selected_id}_{datetime.now().strftime('%Y%m%d')}.json",
                        "application/json"
                    )
                
                with col_exp2:
                    # CSV export
                    visits_df = pd.DataFrame(report["visits"])
                    csv_str = visits_df.to_csv(index=False)
                    st.download_button(
                        "📊 Download as CSV",
                        csv_str,
                        f"patient_{selected_id}_visits_{datetime.now().strftime('%Y%m%d')}.csv",
                        "text/csv"
                    )
                
                st.markdown("---")
                
                # Full report preview
                st.markdown("#### 📋 Full Report Preview")
                st.json(report)
        else:
            st.info("No patients found.")


if __name__ == "__main__":
    timeline_manager = PatientTimelineManager()
    print("Timeline Dashboard initialized successfully!")