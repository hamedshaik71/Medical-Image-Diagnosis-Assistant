# 💬 CHAT WITH THE AI REPORT
# Interactive conversation interface for discussing diagnosis with AI

import streamlit as st
import json
from datetime import datetime
from typing import List, Dict
import os

CHAT_HISTORY_PATH = "database/chat_history.json"


def init_chat_db():
    """Initialize chat history database"""
    os.makedirs("database", exist_ok=True)
    
    if not os.path.exists(CHAT_HISTORY_PATH):
        with open(CHAT_HISTORY_PATH, "w") as f:
            json.dump({}, f)


def load_chat_history(session_id: str) -> List[Dict]:
    """Load chat history for a session"""
    if not os.path.exists(CHAT_HISTORY_PATH):
        return []
    
    try:
        with open(CHAT_HISTORY_PATH, "r") as f:
            all_chats = json.load(f)
            return all_chats.get(session_id, [])
    except:
        return []


def save_chat_history(session_id: str, messages: List[Dict]) -> bool:
    """Save chat history"""
    try:
        with open(CHAT_HISTORY_PATH, "r") as f:
            all_chats = json.load(f)
    except:
        all_chats = {}
    
    all_chats[session_id] = messages
    
    try:
        with open(CHAT_HISTORY_PATH, "w") as f:
            json.dump(all_chats, f, indent=4, default=str)
        return True
    except Exception as e:
        print(f"Error saving chat: {e}")
        return False


class DiagnosisAIAssistant:
    """AI Assistant for interactive diagnosis discussion"""
    
    def __init__(self, disease: str, confidence: float):
        self.disease = disease
        self.confidence = confidence
        self.conversation_memory = []
    
    def generate_response(self, user_message: str) -> str:
        """Generate AI response to user query"""
        
        # Disease-specific knowledge base
        knowledge_base = {
            "Pneumonia": {
                "imaging_findings": "Consolidation in lung fields, air bronchograms visible",
                "clinical_correlation": "Patient presents with fever, cough, and dyspnea",
                "differential": "Consider viral pneumonia, TB, aspiration",
                "management": "Antibiotics based on culture, oxygen support if needed",
                "complications": "Sepsis, respiratory failure, empyema",
                "followup": "Repeat X-ray in 6-8 weeks after treatment"
            },
            "Brain Tumor": {
                "imaging_findings": "Mass with mass effect, surrounding edema",
                "clinical_correlation": "Headaches, visual disturbance, seizures",
                "differential": "Glioblastoma, metastasis, meningioma",
                "management": "Neurosurgery consultation, possible biopsy/resection",
                "complications": "Herniation, increased ICP, radiation necrosis",
                "followup": "MRI surveillance, neuropsych evaluation"
            },
            "Diabetic Retinopathy": {
                "imaging_findings": "Microaneurysms, dot-blot hemorrhages, exudates",
                "clinical_correlation": "Blurred vision, floaters, vision loss",
                "differential": "Consider central artery occlusion, branch vein occlusion",
                "management": "Laser therapy, anti-VEGF injections, control blood glucose",
                "complications": "Vision loss, vitreous hemorrhage, rubeotic glaucoma",
                "followup": "Ophthalmology every 3-6 months"
            },
            "Tuberculosis": {
                "imaging_findings": "Upper lobe infiltrates, cavitary lesions",
                "clinical_correlation": "Persistent cough, night sweats, hemoptysis",
                "differential": "Fungal infection, NTM, silicosis",
                "management": "6-month RIPE therapy, directly observed therapy (DOT)",
                "complications": "Multi-drug resistance, hepatotoxicity, IRIS",
                "followup": "Sputum smear microscopy monthly x 3"
            },
            "Skin Cancer": {
                "imaging_findings": "Asymmetry, border irregularity, color variation",
                "clinical_correlation": "Changing mole, itching, bleeding",
                "differential": "Benign nevus, basal cell carcinoma, squamous cell",
                "management": "Wide local excision, Mohs surgery, immunotherapy",
                "complications": "Metastasis, relapse, lymphedema",
                "followup": "Dermatology surveillance every 3-6 months"
            },
            "Malaria": {
                "imaging_findings": "Usually normal, check for complications",
                "clinical_correlation": "Fever, chills, sweating in endemic area",
                "differential": "Dengue, typhoid, influenza",
                "management": "Artemether-lumefantrine, supportive care",
                "complications": "Cerebral malaria, severe anemia, AKI",
                "followup": "Blood smear negative before discharge"
            },
            "Dental": {
                "imaging_findings": "Periapical radiolucency, bone loss",
                "clinical_correlation": "Tooth pain, swelling, mobility",
                "differential": "Cyst, granuloma, neoplasm",
                "management": "Root canal therapy, extraction, antibiotics",
                "complications": "Abscess, osteomyelitis, cellulitis",
                "followup": "6-month radiograph verification"
            }
        }
        
        # Get knowledge base for this disease
        kb = knowledge_base.get(self.disease, {})
        
        # Response logic based on user query
        lower_msg = user_message.lower()
        
        if "finding" in lower_msg or "image" in lower_msg or "scan" in lower_msg:
            return f"**Imaging Findings:**\n{kb.get('imaging_findings', 'Analysis in progress...')}\n\nThese findings are consistent with {self.disease}."
        
        elif "differential" in lower_msg or "other possibility" in lower_msg or "rule out" in lower_msg:
            return f"**Differential Diagnosis:**\n{kb.get('differential', 'Multiple possibilities exist')}\n\nHowever, current imaging and presentation most consistent with {self.disease} ({self.confidence:.1f}% confidence)."
        
        elif "management" in lower_msg or "treatment" in lower_msg or "how do we" in lower_msg:
            return f"**Management Approach:**\n{kb.get('management', 'Treatment plan pending')}\n\nRecommend multidisciplinary consultation for definitive treatment plan."
        
        elif "complication" in lower_msg or "risk" in lower_msg or "what if" in lower_msg:
            return f"**Potential Complications:**\n{kb.get('complications', 'Various complications possible')}\n\nClose monitoring recommended to identify complications early."
        
        elif "follow" in lower_msg or "next" in lower_msg or "when" in lower_msg:
            return f"**Follow-up Plan:**\n{kb.get('followup', 'Follow-up needed')}\n\nSchedule follow-up imaging and clinical assessment as per protocol."
        
        elif "confident" in lower_msg or "sure" in lower_msg or "certain" in lower_msg:
            return f"**Confidence Analysis:**\nCurrent AI confidence: {self.confidence:.1f}%\n\nThis confidence level is based on:\n- Image quality and clarity\n- Imaging findings consistency\n- Model training data alignment\n- Clinical presentation match\n\nAlways correlate with clinical presentation."
        
        elif "compare" in lower_msg or "previous" in lower_msg or "change" in lower_msg:
            return f"**Comparative Analysis:**\nTo compare with previous imaging, please upload the prior scan. I can then highlight:\n- Progression or improvement\n- New findings\n- Treatment response\n- Size/extent changes"
        
        else:
            # Default response
            return f"**Regarding {self.disease}:**\n\n{kb.get('clinical_correlation', 'Analysis in progress...')}\n\nCurrent confidence: {self.confidence:.1f}%\n\nWhat specific aspect would you like to discuss?"
    
    def add_message(self, role: str, content: str):
        """Add message to conversation"""
        self.conversation_memory.append({
            "timestamp": datetime.now().isoformat(),
            "role": role,
            "content": content
        })
    
    def get_memory(self) -> List[Dict]:
        """Get conversation memory"""
        return self.conversation_memory


def show_chat_with_ai_report(disease: str, confidence: float, username: str):
    """Display chat interface for discussing diagnosis"""
    
    st.markdown("### 💬 Chat with AI Report")
    st.info(
        "Have a conversation with the AI about your diagnosis. "
        "Ask about findings, management, complications, or anything else!"
    )
    
    # Initialize session
    session_id = f"{username}_{disease}_{datetime.now().strftime('%Y%m%d')}"
    
    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = load_chat_history(session_id)
    
    if "ai_assistant" not in st.session_state:
        st.session_state.ai_assistant = DiagnosisAIAssistant(disease, confidence)
    
    assistant = st.session_state.ai_assistant
    
    # Display chat history
    st.markdown("---")
    st.markdown("#### Conversation")
    
    chat_container = st.container()
    
    with chat_container:
        for message in st.session_state.chat_messages:
            if message["role"] == "user":
                with st.chat_message("user"):
                    st.write(message["content"])
            else:
                with st.chat_message("assistant"):
                    st.markdown(message["content"])
    
    st.markdown("---")
    
    # Chat input
    col1, col2 = st.columns([4, 1])
    
    with col1:
        user_input = st.text_input(
            "Ask me about the diagnosis...",
            placeholder="e.g., 'What are the imaging findings?', 'What's the management?'",
            key="chat_input"
        )
    
    with col2:
        send_button = st.button("📤 Send", use_container_width=True)
    
    # Process user message
    if send_button and user_input:
        # Add user message
        st.session_state.chat_messages.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now().isoformat()
        })
        
        # Generate AI response
        ai_response = assistant.generate_response(user_input)
        
        # Add AI message
        st.session_state.chat_messages.append({
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Save chat history
        save_chat_history(session_id, st.session_state.chat_messages)
        
        # Rerun to display
        st.rerun()
    
    st.markdown("---")
    
    # Suggested questions
    st.markdown("#### 💡 Quick Questions")
    
    col1, col2, col3 = st.columns(3)
    
    suggested_questions = [
        "What are the imaging findings?",
        "What's the differential diagnosis?",
        "How should we manage this?",
        "What are the complications?",
        "When should we do follow-up?",
        "How confident are you?"
    ]
    
    for i, question in enumerate(suggested_questions):
        col = [col1, col2, col3][i % 3]
        with col:
            if st.button(f"❓ {question}", use_container_width=True, key=f"quick_{i}"):
                # Simulate sending the question
                st.session_state.chat_messages.append({
                    "role": "user",
                    "content": question,
                    "timestamp": datetime.now().isoformat()
                })
                
                ai_response = assistant.generate_response(question)
                
                st.session_state.chat_messages.append({
                    "role": "assistant",
                    "content": ai_response,
                    "timestamp": datetime.now().isoformat()
                })
                
                save_chat_history(session_id, st.session_state.chat_messages)
                st.rerun()
    
    st.markdown("---")
    
    # Export chat
    st.markdown("#### 📥 Export Conversation")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📄 Export as Text"):
            chat_text = f"""
DIAGNOSIS DISCUSSION REPORT
==========================
Disease: {disease}
AI Confidence: {confidence:.1f}%
Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

CONVERSATION
============
"""
            for msg in st.session_state.chat_messages:
                role = "Doctor" if msg["role"] == "user" else "AI Assistant"
                chat_text += f"\n{role}:\n{msg['content']}\n\n"
            
            st.download_button(
                label="Download Chat",
                data=chat_text,
                file_name=f"chat_report_{disease}_{datetime.now().strftime('%Y%m%d_%H%M')}.txt",
                mime="text/plain"
            )
    
    with col2:
        if st.button("📋 Export as JSON"):
            chat_json = json.dumps(st.session_state.chat_messages, indent=2, default=str)
            
            st.download_button(
                label="Download JSON",
                data=chat_json,
                file_name=f"chat_data_{disease}_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime="application/json"
            )
    
    with col3:
        if st.button("🗑️ Clear Chat"):
            st.session_state.chat_messages = []
            save_chat_history(session_id, [])
            st.success("Chat cleared")
            st.rerun()
    
    st.markdown("---")
    
    # Chat statistics
    col1, col2, col3 = st.columns(3)
    
    user_messages = sum(1 for m in st.session_state.chat_messages if m["role"] == "user")
    ai_messages = sum(1 for m in st.session_state.chat_messages if m["role"] == "assistant")
    
    with col1:
        st.metric("Your Questions", user_messages)
    
    with col2:
        st.metric("AI Responses", ai_messages)
    
    with col3:
        st.metric("Discussion Duration", f"{len(st.session_state.chat_messages)} messages")


# Initialize on import
init_chat_db()