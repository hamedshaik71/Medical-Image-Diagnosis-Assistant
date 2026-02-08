"""
Doctor-AI Collaboration Mode
- Doctors approve/reject AI findings
- Annotate images with corrections
- System learns from feedback (incremental learning)
- Track accuracy improvements over time
- Audit trail of all corrections
"""

import streamlit as st
import json
import os
from datetime import datetime
from pathlib import Path
import numpy as np
import cv2
from PIL import Image
import pandas as pd


class DoctorAICollaborationSystem:
    """Manages doctor feedback and incremental learning"""
    
    def __init__(self, feedback_dir="feedback_system"):
        """
        Initialize collaboration system
        
        Args:
            feedback_dir: Directory to store feedback data
        """
        self.feedback_dir = Path(feedback_dir)
        self.feedback_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.feedback_dir / "corrections").mkdir(exist_ok=True)
        (self.feedback_dir / "annotations").mkdir(exist_ok=True)
        (self.feedback_dir / "learning_log").mkdir(exist_ok=True)
        (self.feedback_dir / "metrics").mkdir(exist_ok=True)
        
        self.corrections_file = self.feedback_dir / "corrections" / "corrections.json"
        self.learning_log_file = self.feedback_dir / "learning_log" / "learning_log.json"
        self.metrics_file = self.feedback_dir / "metrics" / "metrics.json"
        
        # Initialize files if they don't exist
        self._initialize_files()
    
    def _initialize_files(self):
        """Initialize JSON files if they don't exist"""
        if not self.corrections_file.exists():
            self._save_json(self.corrections_file, {"total": 0, "corrections": []})
        
        if not self.learning_log_file.exists():
            self._save_json(self.learning_log_file, {"sessions": [], "total_learned": 0})
        
        if not self.metrics_file.exists():
            self._save_json(self.metrics_file, {
                "accuracy": [],
                "improvement": [],
                "doctor_agreement": []
            })
    
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
    
    def submit_feedback(self, image_name, model_prediction, model_confidence, 
                       doctor_approval, doctor_diagnosis, annotations=None):
        """
        Submit doctor feedback on AI prediction
        
        Args:
            image_name: Name of the image
            model_prediction: AI's prediction
            model_confidence: AI's confidence score
            doctor_approval: Doctor approved (True/False)
            doctor_diagnosis: Doctor's actual diagnosis
            annotations: Optional annotation data
        
        Returns:
            Feedback ID and confirmation
        """
        
        feedback_data = {
            "id": f"FB_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "timestamp": datetime.now().isoformat(),
            "image_name": str(image_name),
            "model_prediction": str(model_prediction),
            "model_confidence": float(model_confidence),
            "doctor_approval": bool(doctor_approval),
            "doctor_diagnosis": str(doctor_diagnosis),
            "agreement": str(model_prediction) == str(doctor_diagnosis),
            "annotations": annotations or {}
        }
        
        # Load existing corrections
        data = self._load_json(self.corrections_file)
        data["corrections"].append(feedback_data)
        data["total"] = len(data["corrections"])
        
        # Save updated corrections
        self._save_json(self.corrections_file, data)
        
        # Log for learning
        self._log_learning_event(feedback_data)
        
        # Update metrics
        self._update_metrics(feedback_data)
        
        return feedback_data["id"], True
    
    def _log_learning_event(self, feedback_data):
        """Log feedback event for learning"""
        log_data = self._load_json(self.learning_log_file)
        
        learning_event = {
            "feedback_id": feedback_data["id"],
            "timestamp": feedback_data["timestamp"],
            "image_name": feedback_data["image_name"],
            "ai_was_correct": feedback_data["agreement"],
            "correction_type": self._determine_correction_type(feedback_data),
            "confidence_delta": 0  # Will be updated with retraining
        }
        
        log_data["sessions"].append(learning_event)
        log_data["total_learned"] = len(log_data["sessions"])
        
        self._save_json(self.learning_log_file, log_data)
    
    def _determine_correction_type(self, feedback_data):
        """Determine type of correction"""
        if feedback_data["agreement"]:
            return "CONFIRMED"
        else:
            return "CORRECTED"
    
    def _update_metrics(self, feedback_data):
        """Update system metrics"""
        metrics = self._load_json(self.metrics_file)
        
        # Calculate accuracy
        corrections = self._load_json(self.corrections_file)["corrections"]
        if corrections:
            correct_count = sum(1 for c in corrections if c["agreement"])
            accuracy = (correct_count / len(corrections)) * 100
            metrics["accuracy"].append({
                "timestamp": datetime.now().isoformat(),
                "accuracy": accuracy,
                "total_feedback": len(corrections)
            })
        
        # Doctor agreement rate
        doctor_agreement = feedback_data["agreement"]
        metrics["doctor_agreement"].append({
            "timestamp": datetime.now().isoformat(),
            "agreement": doctor_agreement
        })
        
        self._save_json(self.metrics_file, metrics)
    
    def get_corrections_summary(self):
        """Get summary of all corrections"""
        data = self._load_json(self.corrections_file)
        
        if not data["corrections"]:
            return None
        
        corrections = data["corrections"]
        total = len(corrections)
        agreed = sum(1 for c in corrections if c["agreement"])
        disagreed = total - agreed
        
        return {
            "total_feedback": total,
            "agreed": agreed,
            "disagreed": disagreed,
            "agreement_rate": (agreed / total * 100) if total > 0 else 0,
            "recent_feedback": corrections[-5:] if corrections else []
        }
    
    def get_learning_summary(self):
        """Get summary of learning progress"""
        log_data = self._load_json(self.learning_log_file)
        
        if not log_data["sessions"]:
            return None
        
        sessions = log_data["sessions"]
        confirmed = sum(1 for s in sessions if s["correction_type"] == "CONFIRMED")
        corrected = sum(1 for s in sessions if s["correction_type"] == "CORRECTED")
        
        return {
            "total_learned": log_data["total_learned"],
            "confirmed": confirmed,
            "corrected": corrected,
            "learning_efficiency": (confirmed / len(sessions) * 100) if sessions else 0
        }
    
    def get_accuracy_metrics(self):
        """Get accuracy improvement metrics"""
        metrics = self._load_json(self.metrics_file)
        
        if not metrics["accuracy"]:
            return None
        
        accuracy_list = metrics["accuracy"]
        
        if len(accuracy_list) >= 2:
            initial = accuracy_list[0]["accuracy"]
            current = accuracy_list[-1]["accuracy"]
            improvement = current - initial
        else:
            improvement = 0
        
        return {
            "current_accuracy": accuracy_list[-1]["accuracy"] if accuracy_list else 0,
            "initial_accuracy": accuracy_list[0]["accuracy"] if accuracy_list else 0,
            "improvement": improvement,
            "history": accuracy_list
        }
    
    def get_doctor_agreement_rate(self):
        """Get doctor agreement rate"""
        metrics = self._load_json(self.metrics_file)
        
        if not metrics["doctor_agreement"]:
            return 0
        
        agreements = [a["agreement"] for a in metrics["doctor_agreement"]]
        return (sum(agreements) / len(agreements)) * 100
    
    def export_learning_data(self):
        """Export all learning data for model retraining"""
        corrections = self._load_json(self.corrections_file).get("corrections", [])
        
        if not corrections:
            # Return None tuple to indicate no data
            return None, None
        
        # Format data for retraining
        training_data = {
            "timestamp": datetime.now().isoformat(),
            "total_samples": len(corrections),
            "corrections": corrections,
            "summary": {
                "total": len(corrections),
                "correct_ai": sum(1 for c in corrections if c["agreement"]),
                "corrected_ai": sum(1 for c in corrections if not c["agreement"])
            }
        }
        
        # Save export
        export_file = self.feedback_dir / "learning_log" / f"export_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        self._save_json(export_file, training_data)
        
        return training_data, export_file
    
    def get_correction_insights(self):
        """Get insights about common correction patterns"""
        corrections = self._load_json(self.corrections_file)["corrections"]
        
        if not corrections:
            return None
        
        # Analyze patterns
        insights = {
            "most_corrected": {},
            "doctor_diagnoses": {},
            "confidence_patterns": []
        }
        
        for correction in corrections:
            # Track which diagnoses are most corrected
            diagnosis = correction["doctor_diagnosis"]
            insights["doctor_diagnoses"][diagnosis] = insights["doctor_diagnoses"].get(diagnosis, 0) + 1
            
            # Track confidence patterns
            if not correction["agreement"]:
                insights["confidence_patterns"].append({
                    "model_confidence": correction["model_confidence"],
                    "ai_prediction": correction["model_prediction"],
                    "correct_diagnosis": correction["doctor_diagnosis"]
                })
        
        return insights


def create_annotation_canvas(image, image_name):
    """
    Create simple annotation interface for doctors
    
    Args:
        image: PIL Image object
        image_name: Name of the image
    
    Returns:
        Annotation data
    """
    st.markdown("### 🎨 Annotate Image")
    st.info("Use the tools below to mark areas of concern or corrections")
    
    annotation_cols = st.columns(2)
    
    with annotation_cols[0]:
        annotation_type = st.selectbox(
            "Annotation Type",
            [
                "Point (Mark specific area)",
                "Circle (Mark lesion area)",
                "Rectangle (Mark region)",
                "Arrow (Indicate direction)",
                "Text Note"
            ]
        )
    
    with annotation_cols[1]:
        annotation_severity = st.select_slider(
            "Severity/Importance",
            options=["Low", "Medium", "High", "Critical"],
            value="Medium"
        )
    
    annotation_notes = st.text_area(
        "Annotation Notes",
        placeholder="Describe the annotation, findings, or corrections...",
        height=100
    )
    
    annotation_data = {
        "image_name": str(image_name),
        "type": annotation_type,
        "severity": annotation_severity,
        "notes": annotation_notes,
        "timestamp": datetime.now().isoformat()
    }
    
    return annotation_data


def render_collaboration_mode(model_prediction, model_confidence, image, image_name, heatmap=None):
    """
    Main function to render Doctor-AI Collaboration Mode
    
    Args:
        model_prediction: AI's prediction
        model_confidence: AI's confidence
        image: Image object
        image_name: Name of image
        heatmap: Optional grad-CAM heatmap
    """
    
    # Initialize collaboration system
    collab_system = DoctorAICollaborationSystem(
        feedback_dir="feedback_system"
    )
    
    st.markdown("---")
    st.markdown("## 👨‍⚕️ Doctor-AI Collaboration Mode")
    
    st.info(
        "🤝 **Work together with AI**: Review the AI prediction below, provide your expertise, "
        "and help the system learn from your feedback. Each correction improves the AI!"
    )
    
    # Create tabs for different modes
    collab_tabs = st.tabs([
        "📋 Review & Feedback",
        "📊 Learning Dashboard",
        "📈 Performance Metrics",
        "💾 Data Export"
    ])
    
    # ===== TAB 1: REVIEW & FEEDBACK =====
    with collab_tabs[0]:
        st.markdown("### 🔍 AI Prediction Review")
        
        col_pred1, col_pred2 = st.columns(2)
        
        with col_pred1:
            st.metric("AI Prediction", str(model_prediction))
        with col_pred2:
            st.metric("Confidence", f"{model_confidence:.1f}%")
        
        st.markdown("---")
        
        # Doctor feedback section
        st.markdown("### ✍️ Your Expert Diagnosis")
        
        feedback_cols = st.columns(2)
        
        with feedback_cols[0]:
            doctor_approval = st.radio(
                "Do you agree with AI's prediction?",
                ["✅ Agree", "❌ Disagree", "🤔 Partially Agree"],
                horizontal=True
            )
        
        with feedback_cols[1]:
            doctor_diagnosis = st.text_input(
                "Your Diagnosis",
                value=str(model_prediction),
                help="Enter your correct diagnosis or finding"
            )
        
        st.markdown("---")
        
        # Annotation section
        st.markdown("### 🎨 Image Annotation & Notes")
        
        annotation_data = create_annotation_canvas(image, image_name)
        
        additional_notes = st.text_area(
            "Additional Medical Notes",
            placeholder="Any additional observations, concerns, or clinical notes...",
            height=120
        )
        
        st.markdown("---")
        
        # Confidence assessment
        st.markdown("### 📊 Assessment Details")
        
        assess_cols = st.columns(3)
        
        with assess_cols[0]:
            ai_reliability = st.slider(
                "AI Reliability (this case)",
                0, 100, 50,
                help="How reliable was the AI for this specific case?"
            )
        
        with assess_cols[1]:
            confidence_alignment = st.slider(
                "Confidence Alignment",
                0, 100, 50,
                help="Does AI confidence match actual correctness?"
            )
        
        with assess_cols[2]:
            difficulty_level = st.select_slider(
                "Case Difficulty",
                options=["Easy", "Medium", "Hard", "Very Hard"]
            )
        
        st.markdown("---")
        
        # Submit feedback
        col_submit1, col_submit2 = st.columns([3, 1])
        
        with col_submit1:
            st.markdown(
                "### 💾 Save Your Feedback\n"
                "Your feedback will be used to improve the AI system"
            )
        
        with col_submit2:
            if st.button("🚀 Submit Feedback", key="submit_feedback_btn", use_container_width=True):
                # Parse approval
                approval_map = {
                    "✅ Agree": True,
                    "❌ Disagree": False,
                    "🤔 Partially Agree": "partial"
                }
                
                try:
                    feedback_id, success = collab_system.submit_feedback(
                        image_name=image_name,
                        model_prediction=model_prediction,
                        model_confidence=model_confidence,
                        doctor_approval=approval_map[doctor_approval],
                        doctor_diagnosis=doctor_diagnosis,
                        annotations={
                            **annotation_data,
                            "additional_notes": additional_notes,
                            "ai_reliability": ai_reliability,
                            "confidence_alignment": confidence_alignment,
                            "difficulty_level": difficulty_level
                        }
                    )
                    
                    if success:
                        st.success(
                            f"✅ **Feedback Submitted!**\n\n"
                            f"Feedback ID: `{feedback_id}`\n\n"
                            f"Thank you! Your feedback helps improve the AI system. "
                            f"This case will be used for incremental learning.",
                            icon="🎉"
                        )
                    else:
                        st.error("Failed to submit feedback. Please try again.")
                
                except Exception as e:
                    st.error(f"Error submitting feedback: {str(e)}")
    
    # ===== TAB 2: LEARNING DASHBOARD =====
    with collab_tabs[1]:
        st.markdown("### 📚 Learning Progress Dashboard")
        
        learning_summary = collab_system.get_learning_summary()
        
        if learning_summary:
            metric_cols = st.columns(4)
            
            with metric_cols[0]:
                st.metric(
                    "Total Learned Cases",
                    learning_summary["total_learned"],
                    help="Number of cases the system has learned from"
                )
            
            with metric_cols[1]:
                st.metric(
                    "Confirmed Cases",
                    learning_summary["confirmed"],
                    f"{learning_summary['learning_efficiency']:.1f}%",
                    help="Cases where AI was correct"
                )
            
            with metric_cols[2]:
                st.metric(
                    "Corrected Cases",
                    learning_summary["corrected"],
                    help="Cases where AI needed correction"
                )
            
            with metric_cols[3]:
                st.metric(
                    "Learning Efficiency",
                    f"{learning_summary['learning_efficiency']:.1f}%",
                    help="Ratio of correct predictions to corrections"
                )
            
            st.markdown("---")
            
            # Learning timeline
            st.markdown("### 📅 Recent Learning Events")
            
            log_data = collab_system._load_json(collab_system.learning_log_file)
            if log_data["sessions"]:
                # Create DataFrame
                sessions = log_data["sessions"][-10:]  # Last 10
                df = pd.DataFrame(sessions)
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df[["timestamp", "image_name", "correction_type", "ai_was_correct"]]
                df.columns = ["Timestamp", "Image", "Type", "AI Correct"]
                
                st.dataframe(df, use_container_width=True)
        else:
            st.info("📊 No learning data yet. Submit feedback to start the learning process!")
    
    # ===== TAB 3: PERFORMANCE METRICS =====
    with collab_tabs[2]:
        st.markdown("### 📈 System Performance Metrics")
        
        corrections_summary = collab_system.get_corrections_summary()
        
        if corrections_summary:
            perf_cols = st.columns(4)
            
            with perf_cols[0]:
                st.metric(
                    "Total Feedback",
                    corrections_summary["total_feedback"]
                )
            
            with perf_cols[1]:
                st.metric(
                    "Agreement Rate",
                    f"{corrections_summary['agreement_rate']:.1f}%",
                    help="% of cases where AI was correct"
                )
            
            with perf_cols[2]:
                st.metric(
                    "Agreed Cases",
                    corrections_summary["agreed"]
                )
            
            with perf_cols[3]:
                st.metric(
                    "Corrected Cases",
                    corrections_summary["disagreed"]
                )
            
            st.markdown("---")
            
            # Accuracy over time
            accuracy_metrics = collab_system.get_accuracy_metrics()
            if accuracy_metrics and accuracy_metrics["history"]:
                st.markdown("### 📊 Accuracy Trend")
                
                import plotly.graph_objects as go
                
                history = accuracy_metrics["history"]
                fig = go.Figure()
                
                fig.add_trace(go.Scatter(
                    x=[h["timestamp"] for h in history],
                    y=[h["accuracy"] for h in history],
                    mode='lines+markers',
                    name='Accuracy',
                    line=dict(color='#00d4aa', width=3),
                    marker=dict(size=8)
                ))
                
                fig.update_layout(
                    title="AI Accuracy Over Time",
                    xaxis_title="Time",
                    yaxis_title="Accuracy (%)",
                    hovermode="x unified",
                    height=400,
                    template="plotly_dark"
                )
                
                st.plotly_chart(fig, use_container_width=True)
                
                st.markdown("---")
                
                st.markdown("### 📊 Performance Summary")
                col_s1, col_s2, col_s3 = st.columns(3)
                
                with col_s1:
                    st.metric(
                        "Current Accuracy",
                        f"{accuracy_metrics['current_accuracy']:.1f}%"
                    )
                
                with col_s2:
                    st.metric(
                        "Initial Accuracy",
                        f"{accuracy_metrics['initial_accuracy']:.1f}%"
                    )
                
                with col_s3:
                    improvement = accuracy_metrics["improvement"]
                    delta_str = f"+{improvement:.1f}%" if improvement >= 0 else f"{improvement:.1f}%"
                    st.metric(
                        "Improvement",
                        delta_str
                    )
        else:
            st.info("📊 No performance data yet. Performance metrics will appear as feedback is collected.")
    
    # ===== TAB 4: DATA EXPORT =====
    with collab_tabs[3]:
        st.markdown("### 💾 Export Learning Data")
        
        st.info(
            "🔄 **Incremental Learning**: Export this data to retrain or fine-tune your AI model "
            "with the corrections and feedback from doctors."
        )
        
        export_data, export_file = collab_system.export_learning_data()
        
        if export_data is not None and export_file is not None:
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                st.markdown("### 📊 Export Summary")
                st.markdown(f"""
                - **Total Samples**: {export_data['summary']['total']}
                - **AI Correct**: {export_data['summary']['correct_ai']}
                - **AI Incorrect**: {export_data['summary']['corrected_ai']}
                - **Accuracy**: {(export_data['summary']['correct_ai'] / export_data['summary']['total'] * 100):.1f}%
                """)
            
            with col_exp2:
                st.markdown("### 💾 Download Options")
                
                # JSON export
                json_str = json.dumps(export_data, indent=2, default=str)
                st.download_button(
                    "📥 Download as JSON",
                    json_str,
                    f"learning_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    "application/json"
                )
                
                # CSV export
                corrections_df = pd.DataFrame(export_data["corrections"])
                csv_str = corrections_df.to_csv(index=False)
                st.download_button(
                    "📊 Download as CSV",
                    csv_str,
                    f"corrections_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    "text/csv"
                )
            
            st.markdown("---")
            
            st.markdown("### 📋 Recent Corrections")
            corrections_df = pd.DataFrame(export_data["corrections"][-10:])
            st.dataframe(
                corrections_df[["timestamp", "image_name", "model_prediction", "doctor_diagnosis", "agreement"]],
                use_container_width=True
            )
        
        else:
            st.info("💾 No data to export yet. Submit feedback to generate learning data.")
        
        st.markdown("---")
        
        st.markdown("### 🔄 Retraining Instructions")
        st.markdown("""
        **How to use this data for incremental learning:**
        
        1. **Export** the learning data (JSON or CSV format)
        2. **Prepare** the data for your training pipeline
        3. **Augment** your existing training dataset with corrections
        4. **Fine-tune** your model using transfer learning
        5. **Evaluate** on a validation set
        6. **Deploy** the improved model
        
        **Benefits:**
        - Continuously improve model accuracy
        - Learn from domain expert corrections
        - Adapt to specific clinical patterns
        - Build a feedback loop for learning
        """)


if __name__ == "__main__":
    # Test the system
    test_system = DoctorAICollaborationSystem()
    summary = test_system.get_corrections_summary()
    print("Collaboration System initialized successfully!")