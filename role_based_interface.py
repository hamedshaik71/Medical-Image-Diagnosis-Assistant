# 👥 ROLE-BASED INTERFACE MODULE
# Different UI/features based on user role (Doctor, Patient, Radiologist, Admin)

import streamlit as st
from auth.auth_logic import get_current_user, get_current_role


class RoleBasedInterface:
    """Manages role-specific features and UI customization"""
    
    ROLE_CONFIGS = {
        "Doctor": {
            "icon": "👨‍⚕️",
            "color": "#00d4aa",
            "features": [
                "patient_management",
                "diagnosis_analysis",
                "prescription_management",
                "patient_history",
                "report_generation",
                "collaboration_tools"
            ],
            "dashboard_widgets": [
                "patient_list",
                "pending_diagnosis",
                "today_appointments",
                "patient_reports",
                "team_collaboration"
            ],
            "can_view": ["patient_data", "medical_history", "all_reports"],
            "can_edit": ["patient_notes", "prescriptions", "diagnosis"],
            "can_delete": False,
            # Define which tabs are accessible for each role
            "accessible_tabs": [
                "Overview", "Trust Panel", "Attention", "Details", "3D Viewer",
                "Comparative Mode", "Collaboration", "Patient Timeline",
                "Patient Health Timeline", "Medications", "Symptom Fusion",
                "Population Data", "Why This Region?", "Emergency",
                "Cross-Device", "Chat with AI", "Compliance Mode",
                "Next Tests", "Voice Assistant"
            ]
        },
        "Patient": {
            "icon": "👤",
            "color": "#00ff88",
            "features": [
                "view_reports",
                "appointment_booking",
                "health_records",
                "message_doctor",
                "medication_tracker",
                "health_insights"
            ],
            "dashboard_widgets": [
                "my_reports",
                "upcoming_appointments",
                "health_summary",
                "medication_schedule",
                "doctor_messages"
            ],
            "can_view": ["own_data", "own_reports", "own_appointments"],
            "can_edit": ["profile", "health_info"],
            "can_delete": False,
            # Patients have limited access
            "accessible_tabs": [
                "Overview", "Details", "Patient Health Timeline",
                "Chat with AI", "Voice Assistant"
            ]
        },
        "Radiologist": {
            "icon": "🔍",
            "color": "#ff6b6b",
            "features": [
                "image_analysis",
                "diagnosis_analysis",
                "report_generation",
                "quality_control",
                "team_collaboration",
                "image_archive"
            ],
            "dashboard_widgets": [
                "pending_scans",
                "analysis_queue",
                "completed_reports",
                "quality_metrics",
                "workflow_stats"
            ],
            "can_view": ["all_imaging", "reports", "patient_history"],
            "can_edit": ["radiology_reports", "diagnoses"],
            "can_delete": False,
            "accessible_tabs": [
                "Overview", "Trust Panel", "Attention", "Details", "3D Viewer",
                "Comparative Mode", "Collaboration", "Patient Timeline",
                "Medications", "Symptom Fusion", "Population Data",
                "Why This Region?", "Emergency", "Cross-Device",
                "Chat with AI", "Compliance Mode", "Next Tests", "Voice Assistant"
            ]
        },
        "Admin": {
            "icon": "⚙️",
            "color": "#ff9500",
            "features": [
                "user_management",
                "system_settings",
                "access_control",
                "audit_logs",
                "database_management",
                "security_settings"
            ],
            "dashboard_widgets": [
                "system_health",
                "user_activity",
                "system_logs",
                "security_alerts",
                "performance_metrics"
            ],
            "can_view": ["all_data", "system_logs", "user_activity"],
            "can_edit": ["system_settings", "user_permissions"],
            "can_delete": True,
            # Admin has access to everything
            "accessible_tabs": [
                "Overview", "Trust Panel", "Attention", "Details", "3D Viewer",
                "Comparative Mode", "Collaboration", "Patient Timeline",
                "Patient Health Timeline", "Medications", "Symptom Fusion",
                "Population Data", "Why This Region?", "Emergency",
                "Cross-Device", "Chat with AI", "Compliance Mode",
                "Next Tests", "Voice Assistant", "Admin Panel"
            ]
        }
    }
    
    @staticmethod
    def get_role_config(role):
        """Get configuration for a specific role"""
        return RoleBasedInterface.ROLE_CONFIGS.get(role, RoleBasedInterface.ROLE_CONFIGS["Patient"])
    
    @staticmethod
    def has_feature(role, feature):
        """Check if role has access to a feature"""
        config = RoleBasedInterface.get_role_config(role)
        return feature in config["features"]
    
    @staticmethod
    def can_view(role, data_type):
        """Check if role can view specific data type"""
        config = RoleBasedInterface.get_role_config(role)
        return data_type in config["can_view"]
    
    @staticmethod
    def can_edit(role, data_type):
        """Check if role can edit specific data type"""
        config = RoleBasedInterface.get_role_config(role)
        return data_type in config["can_edit"]
    
    @staticmethod
    def can_delete(role):
        """Check if role can delete"""
        config = RoleBasedInterface.get_role_config(role)
        return config.get("can_delete", False)
    
    @staticmethod
    def can_access_tab(role, tab_name):
        """Check if role can access a specific tab"""
        config = RoleBasedInterface.get_role_config(role)
        accessible_tabs = config.get("accessible_tabs", [])
        return tab_name in accessible_tabs
    
    @staticmethod
    def get_accessible_tabs(role):
        """Get list of tabs accessible for a role"""
        config = RoleBasedInterface.get_role_config(role)
        return config.get("accessible_tabs", [])


def show_role_based_sidebar():
    """Display role-specific sidebar content"""
    current_user = get_current_user()
    current_role = get_current_role()
    
    if not current_role:
        return
    
    config = RoleBasedInterface.get_role_config(current_role)
    
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"### {config['icon']} {current_role} Panel")
    
    st.sidebar.write(f"**User:** {current_user}")
    st.sidebar.write(f"**Role:** {current_role}")
    
    # Role-specific color indicator
    st.sidebar.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {config['color']}22 0%, {config['color']}11 100%);
            border-left: 4px solid {config['color']};
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        ">
            <span style="color: {config['color']}; font-weight: 600;">
                {config['icon']} {current_role} Access Level
            </span>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    with st.sidebar.expander("🎯 Available Features"):
        for feature in config["features"]:
            feature_name = feature.replace("_", " ").title()
            st.write(f"✓ {feature_name}")
    
    with st.sidebar.expander("📊 Dashboard Widgets"):
        for widget in config["dashboard_widgets"]:
            widget_name = widget.replace("_", " ").title()
            st.write(f"📌 {widget_name}")
    
    with st.sidebar.expander("🔐 Permissions"):
        st.write("**Can View:**")
        for item in config["can_view"]:
            st.write(f"  👁️ {item.replace('_', ' ').title()}")
        st.write("**Can Edit:**")
        for item in config["can_edit"]:
            st.write(f"  ✏️ {item.replace('_', ' ').title()}")
        st.write(f"**Can Delete:** {'✅ Yes' if config['can_delete'] else '❌ No'}")


def show_role_header(current_role):
    """Display role-specific header"""
    config = RoleBasedInterface.get_role_config(current_role)
    
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, {config['color']}22 0%, {config['color']}11 100%);
            border-left: 4px solid {config['color']};
            padding: 1rem;
            border-radius: 12px;
            margin-bottom: 1rem;
        ">
            <span style="color: {config['color']}; font-size: 1.5rem; font-weight: 700;">
                {config['icon']} Welcome, {current_role}
            </span>
            <p style="color: #888; margin: 0.5rem 0 0 0;">
                You have access to {current_role.lower()}-specific features and tools.
            </p>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_access_denied_message(feature_name, required_role=None):
    """Show access denied message for restricted features"""
    st.warning(
        f"""
        ⚠️ **Access Restricted**
        
        The feature **{feature_name}** is not available for your role.
        
        {f"This feature requires **{required_role}** access." if required_role else "Please contact an administrator for access."}
        """
    )


def show_doctor_interface():
    """Display doctor-specific interface"""
    st.markdown(
        """
        <style>
            .doctor-header {
                background: linear-gradient(135deg, #1a3a3a 0%, #0f2626 100%);
                border-left: 4px solid #00d4aa;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
            }
            .doctor-header h1 {
                color: #00d4aa;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="doctor-header">
            <h1>👨‍⚕️ Doctor Dashboard</h1>
            <p>Manage patients, analyze diagnoses, and generate reports</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Doctor-specific tabs
    doctor_tabs = st.tabs([
        "📋 Patient Management",
        "🔍 Diagnosis Analysis",
        "📝 Prescriptions",
        "📊 Reports",
        "🤝 Collaboration",
        "📈 Analytics"
    ])
    
    with doctor_tabs[0]:
        st.markdown("## Patient Management")
        st.info("👥 View and manage your patients")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Patients", 45, "+3 this month")
        with col2:
            st.metric("Active Cases", 12, "-2 resolved")
        with col3:
            st.metric("Appointments Today", 8, "+1 scheduled")
        
        st.markdown("---")
        
        if st.checkbox("Show patient list"):
            st.write("Patient search and management would go here")
    
    with doctor_tabs[1]:
        st.markdown("## Diagnosis Analysis")
        st.info("🔍 AI-powered diagnosis assistance")
        
        st.write("""
        - Upload medical images for analysis
        - Get AI-powered suggestions
        - Review Grad-CAM heatmaps
        - Compare with similar cases
        """)
    
    with doctor_tabs[2]:
        st.markdown("## Prescription Management")
        st.info("💊 Create and manage prescriptions")
        
        col1, col2 = st.columns(2)
        with col1:
            st.text_input("Drug name")
        with col2:
            st.text_input("Dosage")
    
    with doctor_tabs[3]:
        st.markdown("## Generate Reports")
        st.info("📄 Create detailed medical reports")
        
        if st.button("📋 New Report"):
            st.success("Report template loaded")
    
    with doctor_tabs[4]:
        st.markdown("## Team Collaboration")
        st.info("🤝 Collaborate with other healthcare professionals")
        
        st.write("Pending collaborations: 3")
    
    with doctor_tabs[5]:
        st.markdown("## Analytics Dashboard")
        st.info("📊 View your performance metrics")


def show_patient_interface():
    """Display patient-specific interface"""
    st.markdown(
        """
        <style>
            .patient-header {
                background: linear-gradient(135deg, #1a3a1a 0%, #0f260f 100%);
                border-left: 4px solid #00ff88;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
            }
            .patient-header h1 {
                color: #00ff88;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="patient-header">
            <h1>👤 Patient Portal</h1>
            <p>Manage your health, view reports, and communicate with doctors</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Patient-specific tabs
    patient_tabs = st.tabs([
        "📄 My Reports",
        "📅 Appointments",
        "💊 Medications",
        "❤️ Health Summary",
        "💬 Messages",
        "📊 Health Insights"
    ])
    
    with patient_tabs[0]:
        st.markdown("## My Medical Reports")
        st.info("📋 View your medical reports and test results")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Reports", 8, "2 pending")
        with col2:
            st.metric("Last Updated", "2 days ago")
        
        st.markdown("---")
        
        st.write("Your recent reports:")
        # Sample report list
        reports = [
            {"name": "Blood Test", "date": "2024-01-15", "status": "✓ Done"},
            {"name": "X-Ray", "date": "2024-01-10", "status": "✓ Done"},
            {"name": "MRI Scan", "date": "2024-01-05", "status": "⏳ Pending"}
        ]
        
        for report in reports:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.write(f"**{report['name']}**")
            with col2:
                st.caption(report['date'])
            with col3:
                st.caption(report['status'])
    
    with patient_tabs[1]:
        st.markdown("## My Appointments")
        st.info("📅 Schedule and manage your appointments")
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Upcoming", 2, "Next: Tomorrow")
        with col2:
            st.metric("Completed", 15)
        
        st.markdown("---")
        
        if st.button("📅 Schedule Appointment"):
            st.success("Appointment booking form would open here")
    
    with patient_tabs[2]:
        st.markdown("## Medication Tracker")
        st.info("💊 Track your medications and doses")
        
        st.write("Current Medications:")
        meds = [
            {"name": "Aspirin", "dose": "100mg", "time": "Morning & Evening"},
            {"name": "Vitamin D", "dose": "1000 IU", "time": "Morning"},
            {"name": "Blood Pressure Med", "dose": "50mg", "time": "Evening"}
        ]
        
        for med in meds:
            col1, col2, col3 = st.columns([2, 1, 2])
            with col1:
                st.write(f"**{med['name']}**")
            with col2:
                st.caption(med['dose'])
            with col3:
                st.caption(med['time'])
    
    with patient_tabs[3]:
        st.markdown("## Health Summary")
        st.info("❤️ Your overall health status")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Blood Pressure", "120/80", "Normal ✓")
        with col2:
            st.metric("BMI", "22.5", "Healthy ✓")
        with col3:
            st.metric("Heart Rate", "72 bpm", "Normal ✓")
    
    with patient_tabs[4]:
        st.markdown("## Message Your Doctor")
        st.info("💬 Send messages to your healthcare provider")
        
        col1, col2 = st.columns([3, 1])
        with col1:
            st.text_area("Your message", placeholder="Type your message here...")
        with col2:
            st.write("")
            if st.button("📤 Send"):
                st.success("Message sent!")
    
    with patient_tabs[5]:
        st.markdown("## Health Insights")
        st.info("📊 AI-powered health insights and recommendations")
        
        st.write("📌 **Recommendations:**")
        recommendations = [
            "Increase daily water intake to 8 glasses",
            "Exercise 30 minutes daily for better health",
            "Schedule eye checkup (annual due)",
            "Maintain consistent sleep schedule"
        ]
        
        for rec in recommendations:
            st.write(f"✓ {rec}")


def show_radiologist_interface():
    """Display radiologist-specific interface"""
    st.markdown(
        """
        <style>
            .radiologist-header {
                background: linear-gradient(135deg, #3a1a1a 0%, #2a0f0f 100%);
                border-left: 4px solid #ff6b6b;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
            }
            .radiologist-header h1 {
                color: #ff6b6b;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="radiologist-header">
            <h1>🔍 Radiologist Workstation</h1>
            <p>Advanced image analysis and diagnostic support</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Radiologist-specific tabs
    rad_tabs = st.tabs([
        "📸 Imaging Queue",
        "🎯 AI Analysis",
        "📋 Reports",
        "✅ QA Review",
        "📊 Workflow",
        "🔧 Tools"
    ])
    
    with rad_tabs[0]:
        st.markdown("## Imaging Queue")
        st.info("📸 Pending images for analysis")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Pending", 12, "⏳ High priority: 3")
        with col2:
            st.metric("In Progress", 4)
        with col3:
            st.metric("Completed Today", 23)
    
    with rad_tabs[1]:
        st.markdown("## AI-Powered Analysis")
        st.info("🤖 Get AI suggestions for image analysis")
    
    with rad_tabs[2]:
        st.markdown("## Generate Reports")
        st.info("📄 Create detailed radiology reports")
    
    with rad_tabs[3]:
        st.markdown("## Quality Assurance")
        st.info("✅ Review and validate analyses")
    
    with rad_tabs[4]:
        st.markdown("## Workflow Statistics")
        st.info("📊 Track your workflow efficiency")
    
    with rad_tabs[5]:
        st.markdown("## Advanced Tools")
        st.info("🔧 Specialized imaging tools and utilities")


def show_admin_interface():
    """Display admin-specific interface"""
    st.markdown(
        """
        <style>
            .admin-header {
                background: linear-gradient(135deg, #3a2a1a 0%, #2a1a0f 100%);
                border-left: 4px solid #ff9500;
                padding: 1.5rem;
                border-radius: 12px;
                margin-bottom: 2rem;
            }
            .admin-header h1 {
                color: #ff9500;
                margin: 0;
            }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown(
        """
        <div class="admin-header">
            <h1>⚙️ Admin Control Panel</h1>
            <p>System management, user control, and security settings</p>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Admin-specific tabs
    admin_tabs = st.tabs([
        "👥 User Management",
        "🔐 Security",
        "⚙️ Settings",
        "📊 System Health",
        "📋 Audit Logs",
        "🔔 Alerts"
    ])
    
    with admin_tabs[0]:
        st.markdown("## User Management")
        st.info("👥 Manage system users and permissions")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Users", 156, "+5 this week")
        with col2:
            st.metric("Active", 142)
        with col3:
            st.metric("Pending", 3)
        with col4:
            st.metric("Disabled", 11)
    
    with admin_tabs[1]:
        st.markdown("## Security Settings")
        st.info("🔐 System security and access control")
        
        st.checkbox("Enable two-factor authentication")
        st.checkbox("Require password change every 90 days")
        st.checkbox("Log all admin actions")
    
    with admin_tabs[2]:
        st.markdown("## System Settings")
        st.info("⚙️ Configure system parameters")
    
    with admin_tabs[3]:
        st.markdown("## System Health")
        st.info("📊 Monitor system performance")
    
    with admin_tabs[4]:
        st.markdown("## Audit Logs")
        st.info("📋 Review system activity and changes")
    
    with admin_tabs[5]:
        st.markdown("## Security Alerts")
        st.info("🔔 Active security alerts and notifications")


def show_role_based_interface():
    """Main function to display role-based interface"""
    current_role = get_current_role()
    
    if not current_role:
        st.error("❌ Role not determined. Please log in again.")
        return
    
    # Show role-specific sidebar
    show_role_based_sidebar()
    
    # Show role header
    show_role_header(current_role)
    
    # Route to appropriate interface
    if current_role == "Doctor":
        show_doctor_interface()
    elif current_role == "Patient":
        show_patient_interface()
    elif current_role == "Radiologist":
        show_radiologist_interface()
    elif current_role == "Admin":
        show_admin_interface()
    else:
        st.warning(f"⚠️ Unknown role: {current_role}")


def check_tab_access(tab_name, current_role):
    """Check if current role can access a tab and show message if not"""
    if RoleBasedInterface.can_access_tab(current_role, tab_name):
        return True
    else:
        show_access_denied_message(tab_name, "Doctor or Radiologist")
        return False


def get_tabs_for_role(current_role):
    """Get the list of tabs that should be shown for a role"""
    all_tabs = [
        ("🧠 Overview", "Overview"),
        ("🔐 Trust Panel", "Trust Panel"),
        ("🎯 Attention", "Attention"),
        ("📋 Details", "Details"),
        ("🧊 3D Viewer", "3D Viewer"),
        ("📈 Comparative Mode", "Comparative Mode"),
        ("🤝 Collaboration", "Collaboration"),
        ("📊 Patient Timeline", "Patient Timeline"),
        ("🏥 Patient Health Timeline", "Patient Health Timeline"),
        ("💊 Medications", "Medications"),
        ("🔗 Symptom Fusion", "Symptom Fusion"),
        ("📊 Population Data", "Population Data"),
        ("🔍 Why This Region?", "Why This Region?"),
        ("🚨 Emergency", "Emergency"),
        ("📱 Cross-Device", "Cross-Device"),
        ("💬 Chat with AI", "Chat with AI"),
        ("📋 Compliance Mode", "Compliance Mode"),
        ("🔬 Next Tests", "Next Tests"),
        ("🎤 Voice Assistant", "Voice Assistant")
    ]
    
    accessible_tabs = RoleBasedInterface.get_accessible_tabs(current_role)
    
    filtered_tabs = []
    for tab_display, tab_name in all_tabs:
        if tab_name in accessible_tabs:
            filtered_tabs.append((tab_display, tab_name))
    
    return filtered_tabs