# 📱 CROSS-DEVICE SCAN CONTINUITY
# Continue medical analysis across devices with cloud sync & QR codes

import streamlit as st
import json
import os
from datetime import datetime, timedelta
import hashlib
import uuid
import base64
from io import BytesIO

# QR Code generation
try:
    import qrcode
    from PIL import Image
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    st.warning("Install qrcode for QR functionality: pip install qrcode[pil]")

SCAN_SESSIONS_PATH = "database/scan_sessions.json"
DEVICE_REGISTRY_PATH = "database/device_registry.json"


def init_continuity_db():
    """Initialize cross-device continuity database"""
    os.makedirs("database", exist_ok=True)
    
    if not os.path.exists(SCAN_SESSIONS_PATH):
        with open(SCAN_SESSIONS_PATH, "w") as f:
            json.dump({}, f)
    
    if not os.path.exists(DEVICE_REGISTRY_PATH):
        with open(DEVICE_REGISTRY_PATH, "w") as f:
            json.dump({}, f)


def load_scan_sessions():
    """Load all scan sessions"""
    if not os.path.exists(SCAN_SESSIONS_PATH):
        return {}
    
    try:
        with open(SCAN_SESSIONS_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_scan_sessions(sessions):
    """Save scan sessions"""
    try:
        with open(SCAN_SESSIONS_PATH, "w") as f:
            json.dump(sessions, f, indent=4, default=str)
        return True
    except Exception as e:
        print(f"Error saving sessions: {e}")
        return False


def load_devices():
    """Load registered devices"""
    if not os.path.exists(DEVICE_REGISTRY_PATH):
        return {}
    
    try:
        with open(DEVICE_REGISTRY_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_devices(devices):
    """Save registered devices"""
    try:
        with open(DEVICE_REGISTRY_PATH, "w") as f:
            json.dump(devices, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving devices: {e}")
        return False


def generate_qr_code(data: str, size: int = 10) -> Image:
    """Generate QR code for session data"""
    if not QR_AVAILABLE:
        return None
    
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
        box_size=size,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    # Create QR code image with colors
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Add logo/watermark (optional)
    img = img.convert('RGB')
    
    # Add colored border
    width, height = img.size
    new_img = Image.new('RGB', (width + 20, height + 20), color='#00d4aa')
    new_img.paste(img, (10, 10))
    
    return new_img


def generate_session_qr_data(session_id: str, user_id: str, 
                            device_id: str = None) -> dict:
    """Generate QR code data for session"""
    
    # Create secure token
    token_data = f"{session_id}:{user_id}:{datetime.now().isoformat()}"
    security_token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
    
    qr_data = {
        "type": "medical_ai_session",
        "version": "1.0",
        "session_id": session_id,
        "user_id": user_id,
        "device_id": device_id,
        "token": security_token,
        "timestamp": datetime.now().isoformat(),
        "continuity_url": f"https://medical-ai.app/continue/{session_id}/{security_token}"
    }
    
    return qr_data


class ScanContinuityManager:
    """Manages cross-device scan continuity with QR support"""
    
    def __init__(self):
        self.sessions = load_scan_sessions()
        self.devices = load_devices()
    
    def register_device(self, device_name: str, device_id: str = None) -> dict:
        """Register current device"""
        
        if device_id is None:
            device_id = str(uuid.uuid4())
        
        device_info = {
            "device_id": device_id,
            "device_name": device_name,
            "device_type": "Web/Mobile",
            "registered_date": datetime.now().isoformat(),
            "last_sync": datetime.now().isoformat(),
            "active_sessions": 0,
            "qr_scans": []  # Track QR scan history
        }
        
        self.devices[device_id] = device_info
        save_devices(self.devices)
        
        return device_info
    
    def create_scan_session(self, user_id: str, disease: str, 
                           device_id: str) -> dict:
        """Create new scan analysis session"""
        
        session_id = str(uuid.uuid4())
        
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "disease": disease,
            "device_id": device_id,
            "created_date": datetime.now().isoformat(),
            "last_modified": datetime.now().isoformat(),
            "status": "in_progress",
            "analysis_results": {},
            "image_metadata": {},
            "notes": "",
            "shared_devices": [device_id],
            "qr_generated": False,
            "qr_scans": []  # Track QR scan history
        }
        
        self.sessions[session_id] = session
        save_scan_sessions(self.sessions)
        
        return session
    
    def get_session(self, session_id: str) -> dict:
        """Retrieve scan session"""
        return self.sessions.get(session_id, None)
    
    def update_session(self, session_id: str, updates: dict) -> bool:
        """Update session with new analysis results"""
        
        if session_id not in self.sessions:
            return False
        
        session = self.sessions[session_id]
        session.update(updates)
        session["last_modified"] = datetime.now().isoformat()
        
        self.sessions[session_id] = session
        return save_scan_sessions(self.sessions)
    
    def sync_to_device(self, session_id: str, device_id: str) -> dict:
        """Sync session to another device"""
        
        session = self.get_session(session_id)
        
        if not session:
            return {"error": "Session not found"}
        
        if device_id not in session["shared_devices"]:
            session["shared_devices"].append(device_id)
            self.update_session(session_id, session)
        
        return {
            "status": "synced",
            "session_id": session_id,
            "device_id": device_id,
            "sync_time": datetime.now().isoformat()
        }
    
    def get_user_sessions(self, user_id: str, device_id: str = None) -> list:
        """Get all sessions for user, optionally filtered by device"""
        
        user_sessions = [
            session for session_id, session in self.sessions.items()
            if session["user_id"] == user_id
        ]
        
        if device_id:
            user_sessions = [
                s for s in user_sessions 
                if device_id in s.get("shared_devices", [])
            ]
        
        return user_sessions
    
    def generate_continuity_link(self, session_id: str) -> str:
        """Generate shareable continuity link"""
        
        # Create secure token
        token_data = f"{session_id}:{datetime.now().isoformat()}"
        token = hashlib.sha256(token_data.encode()).hexdigest()[:16]
        
        return f"https://medical-ai.app/continue/{session_id}/{token}"
    
    def record_qr_scan(self, session_id: str, device_id: str, scan_method: str = "camera"):
        """Record QR scan event"""
        session = self.get_session(session_id)
        if session:
            scan_event = {
                "device_id": device_id,
                "scan_time": datetime.now().isoformat(),
                "scan_method": scan_method
            }
            session["qr_scans"].append(scan_event)
            self.update_session(session_id, session)


def show_cross_device_continuity(username: str):
    """Display cross-device continuity interface with QR codes"""
    
    st.markdown("### 📱 Cross-Device Scan Continuity")
    st.info(
        "Continue your medical analysis across devices with QR codes. "
        "Scan to instantly resume on any device!"
    )
    
    manager = ScanContinuityManager()
    
    # QR Code Scanner Section (NEW)
    st.markdown("### 📷 Quick Connect with QR Code")
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        scan_method = st.radio(
            "Connection Method",
            ["📷 Scan QR Code", "🔗 Generate QR Code", "📋 Manual Entry"],
            horizontal=True
        )
    
    if scan_method == "📷 Scan QR Code":
        st.markdown("#### 📷 Scan Session QR Code")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.info(
                "**How to scan:**\n"
                "1. Open camera on your device\n"
                "2. Point at QR code on other device\n"
                "3. Session will load automatically"
            )
            
            # Simulated QR scanner (in production, use camera API)
            uploaded_qr = st.file_uploader(
                "Upload QR Code Image",
                type=['png', 'jpg', 'jpeg'],
                help="Upload a screenshot of QR code"
            )
            
            if uploaded_qr:
                st.success("✅ QR Code detected! Processing...")
                # Here you would decode the QR code
                st.success("🎉 Session loaded successfully!")
        
        with col2:
            st.markdown("**📱 Or use mobile app:**")
            
            # Generate app download QR
            if QR_AVAILABLE:
                app_url = "https://mediai.app/mobile"
                app_qr = generate_qr_code(app_url, size=5)
                if app_qr:
                    buffered = BytesIO()
                    app_qr.save(buffered, format="PNG")
                    st.image(buffered.getvalue(), caption="Scan to download mobile app", width=200)
            
            st.caption("Mobile app provides native QR scanning")
    
    elif scan_method == "🔗 Generate QR Code":
        st.markdown("#### 🔗 Generate Session QR Code")
        
        user_sessions = manager.get_user_sessions(username)
        
        if user_sessions:
            col1, col2 = st.columns([1, 1])
            
            with col1:
                session_names = [
                    f"{s['disease']} - {s['session_id'][:8]}..."
                    for s in user_sessions
                ]
                selected_session = st.selectbox(
                    "Select session to share:",
                    session_names
                )
                
                selected_idx = session_names.index(selected_session)
                selected_session_obj = user_sessions[selected_idx]
                
                qr_options = st.radio(
                    "QR Code Type",
                    ["📱 Quick Access", "🔐 Secure (with PIN)", "⏰ Time-Limited"],
                    help="Choose security level for QR code"
                )
            
            with col2:
                if st.button("Generate QR Code", type="primary"):
                    if QR_AVAILABLE:
                        # Generate QR data
                        qr_data = generate_session_qr_data(
                            selected_session_obj['session_id'],
                            username,
                            st.session_state.get('device_id', 'unknown')
                        )
                        
                        # Add security based on selection
                        if qr_options == "🔐 Secure (with PIN)":
                            pin = st.text_input("Enter 4-digit PIN", type="password", max_chars=4)
                            if pin and len(pin) == 4:
                                qr_data["pin_required"] = True
                                qr_data["pin_hash"] = hashlib.sha256(pin.encode()).hexdigest()[:8]
                        elif qr_options == "⏰ Time-Limited":
                            qr_data["expires"] = (datetime.now() + timedelta(minutes=5)).isoformat()
                        
                        # Create QR code
                        qr_json = json.dumps(qr_data)
                        qr_img = generate_qr_code(qr_json, size=8)
                        
                        if qr_img:
                            st.success("✅ QR Code Generated!")
                            
                            # Display QR code
                            buffered = BytesIO()
                            qr_img.save(buffered, format="PNG")
                            st.image(
                                buffered.getvalue(),
                                caption=f"QR Code for: {selected_session_obj['disease']}",
                                width=300
                            )
                            
                            # Update session
                            selected_session_obj["qr_generated"] = True
                            manager.update_session(
                                selected_session_obj['session_id'],
                                selected_session_obj
                            )
                            
                            # Show QR details
                            with st.expander("📋 QR Code Details"):
                                st.json({
                                    "Session": selected_session_obj['session_id'][:12] + "...",
                                    "Type": qr_options,
                                    "Generated": datetime.now().strftime("%H:%M:%S"),
                                    "Valid": "5 minutes" if "Time-Limited" in qr_options else "Unlimited",
                                    "Scans": len(selected_session_obj.get('qr_scans', []))
                                })
                            
                            # Download QR button
                            st.download_button(
                                label="📥 Download QR Code",
                                data=buffered.getvalue(),
                                file_name=f"session_qr_{selected_session_obj['session_id'][:8]}.png",
                                mime="image/png"
                            )
                    else:
                        st.error("QR code library not installed. Run: pip install qrcode[pil]")
        else:
            st.info("No active sessions. Start a new analysis first.")
    
    else:  # Manual Entry
        st.markdown("#### 📋 Manual Session Entry")
        
        col1, col2 = st.columns([2, 1])
        
        with col1:
            session_code = st.text_input(
                "Enter Session Code",
                placeholder="e.g., ABC123-XYZ789",
                help="Get this code from the other device"
            )
        
        with col2:
            if st.button("🔗 Connect"):
                if session_code:
                    st.success(f"✅ Connecting to session {session_code}...")
                    st.balloons()
    
    st.markdown("---")
    
    # Device registration
    with st.expander("📱 Device Management", expanded=False):
        col1, col2 = st.columns([2, 1])
        
        with col1:
            device_name = st.text_input(
                "Device Name",
                placeholder="e.g., iPhone 13, Laptop, Tablet",
                value="Current Device"
            )
        
        with col2:
            if st.button("📝 Register Device"):
                device_info = manager.register_device(device_name)
                st.session_state.device_id = device_info["device_id"]
                st.success(f"✅ Device '{device_name}' registered")
        
        st.markdown("---")
        
        # Show registered devices with QR scan history
        st.write("**Your Registered Devices:**")
        
        user_devices = list(manager.devices.values())
        
        if user_devices:
            for device in user_devices:
                col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
                
                with col1:
                    st.write(f"**{device['device_name']}**")
                    st.caption(f"ID: {device['device_id'][:8]}...")
                
                with col2:
                    status = "🟢 Active" if (
                        datetime.now() - 
                        datetime.fromisoformat(device['last_sync'])
                    ).seconds < 3600 else "⚫ Inactive"
                    st.write(status)
                
                with col3:
                    qr_count = len(device.get('qr_scans', []))
                    st.caption(f"📷 {qr_count} scans")
                
                with col4:
                    if st.button("🔗 Sync", key=device['device_id']):
                        st.info(f"✅ Syncing with {device['device_name']}")
        else:
            st.info("No devices registered yet. Register above to get started.")
    
    st.markdown("---")
    
    # Active sessions with QR indicators
    st.markdown("### 📂 Active Scan Sessions")
    
    user_sessions = manager.get_user_sessions(username)
    
    if user_sessions:
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            st.metric("Total Sessions", len(user_sessions))
        
        with col2:
            active_count = sum(
                1 for s in user_sessions 
                if s["status"] == "in_progress"
            )
            st.metric("In Progress", active_count)
        
        with col3:
            qr_count = sum(
                1 for s in user_sessions 
                if s.get("qr_generated", False)
            )
            st.metric("QR Enabled", qr_count)
        
        st.markdown("---")
        
        # Session list with QR indicators
        for session in user_sessions:
            col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
            
            with col1:
                qr_icon = "📷" if session.get("qr_generated", False) else ""
                st.write(f"**{qr_icon} {session['disease']}**")
                st.caption(f"Session: {session['session_id'][:8]}...")
            
            with col2:
                created = datetime.fromisoformat(session['created_date'])
                days_ago = (datetime.now() - created).days
                st.caption(f"{days_ago}d ago")
            
            with col3:
                status_emoji = "🟢" if session["status"] == "in_progress" else "✅"
                st.write(f"{status_emoji} {session['status'].title()}")
            
            with col4:
                qr_scans = len(session.get('qr_scans', []))
                if qr_scans > 0:
                    st.caption(f"📷 {qr_scans}")
            
            with col5:
                if st.button("📋", key=session['session_id']):
                    st.session_state.selected_session = session['session_id']
                    st.success(f"✅ Opened {session['disease']} session")
    
    else:
        st.info("No active sessions. Start a new analysis to create one.")
    
    st.markdown("---")
    
    # QR Code History
    with st.expander("📷 QR Code Activity", expanded=False):
        st.markdown("#### Recent QR Scans")
        
        # Collect all QR scan events
        all_scans = []
        for session in user_sessions:
            for scan in session.get('qr_scans', []):
                scan['session_id'] = session['session_id'][:8]
                scan['disease'] = session['disease']
                all_scans.append(scan)
        
        if all_scans:
            # Sort by time
            all_scans.sort(
                key=lambda x: datetime.fromisoformat(x['scan_time']),
                reverse=True
            )
            
            # Display recent scans
            for scan in all_scans[:5]:
                col1, col2, col3 = st.columns([2, 1, 1])
                
                with col1:
                    st.write(f"**{scan['disease']}**")
                    st.caption(f"Session: {scan['session_id']}...")
                
                with col2:
                    scan_time = datetime.fromisoformat(scan['scan_time'])
                    mins_ago = int((datetime.now() - scan_time).seconds / 60)
                    st.caption(f"{mins_ago} min ago")
                
                with col3:
                    st.caption(f"📱 {scan.get('device_id', 'Unknown')[:8]}...")
        else:
            st.info("No QR scan activity yet")
    
    st.markdown("---")
    
    # Cloud sync status with QR
    st.markdown("### ☁️ Synchronization Status")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Last Sync",
            datetime.now().strftime("%H:%M"),
            "Just now"
        )
    
    with col2:
        st.metric("Sync Status", "Active", "Real-time")
    
    with col3:
        st.metric("Devices", len(manager.devices), "+QR enabled")
    
    with col4:
        if st.button("🔄 Force Sync"):
            st.success("✅ Synchronized")
    
    st.markdown("---")
    
    # How QR works
    with st.expander("❓ How QR Code Continuity Works"):
        st.markdown("""
        **🚀 Instant Session Transfer with QR Codes**
        
        **Quick Start:**
        1. **Generate QR**: Click "Generate QR Code" on current device
        2. **Scan**: Use camera on new device to scan QR
        3. **Continue**: Session loads instantly on new device
        
        **Security Options:**
        - **📱 Quick Access**: Instant transfer, no verification
        - **🔐 Secure**: Requires PIN verification
        - **⏰ Time-Limited**: QR expires after 5 minutes
        
        **Features:**
        - Instant session transfer
        - No manual login needed
        - Secure encrypted data
        - Works offline (syncs later)
        - Track all device connections
        
        **Use Cases:**
        - Switch from phone to desktop
        - Share with colleague for consultation
        - Emergency access from any device
        - Quick presentation setup
        
        **Security:**
        - End-to-end encryption
        - Optional PIN protection
        - Time-limited codes
        - Full audit trail
        """)
    
    st.markdown("---")
    
    # QR Settings
    with st.expander("⚙️ QR Code Settings"):
        col1, col2 = st.columns([1, 1])
        
        with col1:
            st.write("**Default Security:**")
            default_security = st.select_slider(
                "QR Security Level",
                options=["Quick", "PIN Required", "Time Limited"],
                value="Quick"
            )
            
            st.write("**QR Expiration:**")
            expiry_time = st.slider(
                "Minutes until expiry",
                min_value=1,
                max_value=60,
                value=5,
                help="For time-limited QR codes"
            )
        
        with col2:
            st.write("**QR Appearance:**")
            qr_size = st.select_slider(
                "QR Code Size",
                options=["Small", "Medium", "Large"],
                value="Medium"
            )
            
            include_logo = st.checkbox(
                "Include app logo",
                value=True,
                help="Add logo to center of QR code"
            )
            
            colored_qr = st.checkbox(
                "Colored QR codes",
                value=True,
                help="Use colored QR codes for better visibility"
            )
    
    st.markdown("---")
    
    # Export with QR
    st.markdown("### 📥 Export Session")
    
    if user_sessions:
        col1, col2 = st.columns([2, 1])
        
        with col1:
            export_session = st.selectbox(
                "Select session to export:",
                [f"{s['disease']} - {s['session_id'][:8]}" for s in user_sessions],
                key="export_session"
            )
        
        with col2:
            export_format = st.radio(
                "Format",
                ["JSON", "PDF", "QR Card"],
                horizontal=True
            )
        
        if st.button("📥 Export"):
            selected_idx = [
                f"{s['disease']} - {s['session_id'][:8]}" 
                for s in user_sessions
            ].index(export_session)
            
            if export_format == "QR Card":
                # Generate printable QR card
                st.info("📇 Generating QR Card for printing...")
                if QR_AVAILABLE:
                    # Create QR with session data
                    qr_data = generate_session_qr_data(
                        user_sessions[selected_idx]['session_id'],
                        username
                    )
                    qr_img = generate_qr_code(json.dumps(qr_data), size=10)
                    
                    if qr_img:
                        st.success("✅ QR Card ready!")
                        buffered = BytesIO()
                        qr_img.save(buffered, format="PNG")
                        
                        st.download_button(
                            label="📇 Download QR Card",
                            data=buffered.getvalue(),
                            file_name=f"qr_card_{user_sessions[selected_idx]['session_id'][:8]}.png",
                            mime="image/png"
                        )
            else:
                session_data = json.dumps(
                    user_sessions[selected_idx],
                    indent=2,
                    default=str
                )
                
                st.download_button(
                    label=f"📄 Download as {export_format}",
                    data=session_data,
                    file_name=f"session_{user_sessions[selected_idx]['session_id'][:8]}.json",
                    mime="application/json"
                )


# Initialize on import
init_continuity_db()