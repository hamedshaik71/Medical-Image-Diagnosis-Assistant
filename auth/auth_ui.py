"""
🎨 Ultimate Authentication UI
- Glassmorphism Design
- Animated Components
- Password Strength Meter
- Social Login Options
- Progressive Registration
"""

import streamlit as st
import time
from auth.auth_logic import (
    authenticate_user,
    register_user,
    init_auth_state,
    get_current_user,
    get_current_role,
    get_user_avatar,
    get_user_stats,
    logout_user,
    check_password_strength,
    validate_email,
    validate_username,
    check_username_availability,
    check_email_availability,
    show_loading_animation
)
from auth.forgot_password import show_forgot_password_modal
from auth.styles import AUTH_STYLES, SUCCESS_ANIMATION, ERROR_ANIMATION


def render_particles():
    """Render animated particle background"""
    st.markdown(AUTH_STYLES, unsafe_allow_html=True)


def render_password_strength(password: str):
    """Render password strength meter"""
    if not password:
        return
    
    strength = check_password_strength(password)
    
    st.markdown(
        f"""
        <div class="password-strength-container">
            <div class="password-strength-bar">
                <div class="password-strength-fill strength-{strength['class']}"></div>
            </div>
            <div class="strength-text strength-{strength['class']}-text">
                🔐 Password Strength: {strength['label']}
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Requirements checklist
    reqs = strength['requirements']
    
    st.markdown(
        f"""
        <div class="requirements-list">
            <div class="requirement-item {'requirement-met' if reqs['length'] else 'requirement-unmet'}">
                <span class="requirement-icon {'requirement-icon-met' if reqs['length'] else 'requirement-icon-unmet'}">
                    {'✓' if reqs['length'] else '○'}
                </span>
                At least 8 characters
            </div>
            <div class="requirement-item {'requirement-met' if reqs['uppercase'] else 'requirement-unmet'}">
                <span class="requirement-icon {'requirement-icon-met' if reqs['uppercase'] else 'requirement-icon-unmet'}">
                    {'✓' if reqs['uppercase'] else '○'}
                </span>
                One uppercase letter
            </div>
            <div class="requirement-item {'requirement-met' if reqs['lowercase'] else 'requirement-unmet'}">
                <span class="requirement-icon {'requirement-icon-met' if reqs['lowercase'] else 'requirement-icon-unmet'}">
                    {'✓' if reqs['lowercase'] else '○'}
                </span>
                One lowercase letter
            </div>
            <div class="requirement-item {'requirement-met' if reqs['digit'] else 'requirement-unmet'}">
                <span class="requirement-icon {'requirement-icon-met' if reqs['digit'] else 'requirement-icon-unmet'}">
                    {'✓' if reqs['digit'] else '○'}
                </span>
                One number
            </div>
            <div class="requirement-item {'requirement-met' if reqs['special'] else 'requirement-unmet'}">
                <span class="requirement-icon {'requirement-icon-met' if reqs['special'] else 'requirement-icon-unmet'}">
                    {'✓' if reqs['special'] else '○'}
                </span>
                One special character (!@#$%^&*)
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_social_login():
    """Render social login options"""
    st.markdown(
        """
        <div class="social-container">
            <div class="social-divider">or continue with</div>
            <div class="social-buttons">
                <div class="social-btn social-google" title="Google">🔴</div>
                <div class="social-btn social-github" title="GitHub">⚫</div>
                <div class="social-btn social-microsoft" title="Microsoft">🔵</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    st.caption("*Social login coming soon*")


def render_security_badge():
    """Render security badge"""
    st.markdown(
        """
        <div class="security-badge">
            <span class="security-badge-icon">🔒</span>
            <span>256-bit SSL Encrypted</span>
        </div>
        """,
        unsafe_allow_html=True
    )


def show_auth_ui():
    """Display main authentication UI"""
    
    init_auth_state()
    
    # Already authenticated
    if st.session_state.authenticated:
        return
    
    # Render styles and particles
    render_particles()
    
    # Check for forgot password modal
    if st.session_state.get("show_forgot_password", False):
        show_forgot_password_modal()
        return
    
    # Main container header
    st.markdown(
        """
        <div class="auth-glass-container">
            <div class="neon-header">
                <div class="neon-logo">🏥</div>
                <div class="neon-title">MediAI Platform</div>
                <div class="neon-subtitle">Secure Medical Intelligence</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Tabs
    tab1, tab2 = st.tabs(["🔑 Sign In", "✨ Create Account"])
    
    # ==========================================
    # 🔑 LOGIN TAB
    # ==========================================
    with tab1:
        st.markdown("#### Welcome Back!")
        st.caption("Enter your credentials to access your account")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Username input
        username = st.text_input(
            "👤 Username",
            placeholder="Enter your username",
            key="login_username",
            help="Your unique username"
        )
        
        # Password input
        password = st.text_input(
            "🔒 Password",
            type="password",
            placeholder="Enter your password",
            key="login_password",
            help="Your secure password"
        )
        
        # Remember me & Forgot password row
        col1, col2 = st.columns(2)
        
        with col1:
            remember = st.checkbox("Remember me", key="remember_me_check")
        
        with col2:
            if st.button("Forgot Password?", key="forgot_btn", type="secondary"):
                st.session_state.show_forgot_password = True
                st.rerun()
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Login button
        if st.button("🚀 Sign In", use_container_width=True, key="login_submit", type="primary"):
            if not username or not password:
                st.markdown(
                    ERROR_ANIMATION.format(message="Please enter both username and password"),
                    unsafe_allow_html=True
                )
            else:
                # Loading animation
                with st.spinner("🔐 Authenticating..."):
                    time.sleep(1)
                    success, message = authenticate_user(username, password)
                
                if success:
                    st.markdown(
                        SUCCESS_ANIMATION.format(
                            title="Login Successful!",
                            message="Redirecting to dashboard..."
                        ),
                        unsafe_allow_html=True
                    )
                    time.sleep(1.5)
                    st.rerun()
                else:
                    st.markdown(
                        ERROR_ANIMATION.format(message=message),
                        unsafe_allow_html=True
                    )
        
        render_social_login()
        render_security_badge()
    
    # ==========================================
    # ✨ REGISTER TAB
    # ==========================================
    with tab2:
        st.markdown("#### Create Your Account")
        st.caption("Join thousands of healthcare professionals")
        
        # Progress stepper
        step = st.session_state.get("registration_step", 1)
        
        st.markdown(
            f"""
            <div class="stepper-container">
                <div class="step {'step-completed' if step > 1 else 'step-active' if step == 1 else 'step-pending'}">
                    <div class="step-circle">{'✓' if step > 1 else '1'}</div>
                    <div class="step-label">Account</div>
                </div>
                <div class="step-connector {'step-connector-active' if step > 1 else ''}"></div>
                <div class="step {'step-completed' if step > 2 else 'step-active' if step == 2 else 'step-pending'}">
                    <div class="step-circle">{'✓' if step > 2 else '2'}</div>
                    <div class="step-label">Profile</div>
                </div>
                <div class="step-connector {'step-connector-active' if step > 2 else ''}"></div>
                <div class="step {'step-active' if step == 3 else 'step-pending'}">
                    <div class="step-circle">3</div>
                    <div class="step-label">Complete</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        if step == 1:
            # Step 1: Basic Account Info
            st.markdown("##### Step 1: Account Information")
            
            new_username = st.text_input(
                "👤 Username",
                placeholder="Choose a unique username",
                key="reg_username",
                help="3-20 characters, letters, numbers, underscores"
            )
            
            # Real-time username validation
            if new_username:
                valid, msg = validate_username(new_username)
                if valid:
                    if check_username_availability(new_username):
                        st.success("✅ Username available!")
                    else:
                        st.error("❌ Username already taken")
                else:
                    st.warning(f"⚠️ {msg}")
            
            new_email = st.text_input(
                "📧 Email Address",
                placeholder="your@email.com",
                key="reg_email",
                help="We'll send verification to this email"
            )
            
            # Real-time email validation
            if new_email:
                if validate_email(new_email):
                    if check_email_availability(new_email):
                        st.success("✅ Email available!")
                    else:
                        st.error("❌ Email already registered")
                else:
                    st.warning("⚠️ Invalid email format")
            
            col1, col2 = st.columns(2)
            with col2:
                if st.button("Next →", use_container_width=True, type="primary"):
                    if not new_username or not new_email:
                        st.error("Please fill all fields")
                    elif not validate_username(new_username)[0]:
                        st.error("Invalid username format")
                    elif not validate_email(new_email):
                        st.error("Invalid email format")
                    elif not check_username_availability(new_username):
                        st.error("Username already taken")
                    elif not check_email_availability(new_email):
                        st.error("Email already registered")
                    else:
                        st.session_state.reg_username_temp = new_username
                        st.session_state.reg_email_temp = new_email
                        st.session_state.registration_step = 2
                        st.rerun()
        
        elif step == 2:
            # Step 2: Password & Role
            st.markdown("##### Step 2: Security & Profile")
            
            new_password = st.text_input(
                "🔒 Password",
                type="password",
                placeholder="Create a strong password",
                key="reg_password"
            )
            
            # Password strength meter
            if new_password:
                render_password_strength(new_password)
            
            confirm_password = st.text_input(
                "🔒 Confirm Password",
                type="password",
                placeholder="Re-enter your password",
                key="reg_confirm_password"
            )
            
            if confirm_password and new_password != confirm_password:
                st.error("❌ Passwords don't match")
            
            role = st.selectbox(
                "👨‍⚕️ Your Role",
                ["Doctor", "Radiologist", "Nurse", "Researcher", "Patient", "Admin"],
                key="reg_role",
                help="Select your primary role"
            )
            
            full_name = st.text_input(
                "📝 Full Name (Optional)",
                placeholder="Dr. John Smith",
                key="reg_fullname"
            )
            
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("← Back", use_container_width=True):
                    st.session_state.registration_step = 1
                    st.rerun()
            
            with col2:
                if st.button("Create Account ✨", use_container_width=True, type="primary"):
                    if not new_password:
                        st.error("Please enter a password")
                    elif len(new_password) < 6:
                        st.error("Password must be at least 6 characters")
                    elif new_password != confirm_password:
                        st.error("Passwords don't match")
                    else:
                        strength = check_password_strength(new_password)
                        if strength["strength"] < 2:
                            st.warning("Password is weak. Consider adding uppercase, numbers, or special characters.")
                        
                        with st.spinner("✨ Creating your account..."):
                            time.sleep(1.5)
                            success, message = register_user(
                                username=st.session_state.reg_username_temp,
                                password=new_password,
                                email=st.session_state.reg_email_temp,
                                role=role,
                                full_name=full_name
                            )
                        
                        if success:
                            st.session_state.registration_step = 3
                            st.rerun()
                        else:
                            st.error(f"❌ {message}")
        
        elif step == 3:
            # Step 3: Success
            st.markdown(
                f"""
                <div class="success-container">
                    <div class="success-icon">🎉</div>
                    <div class="success-title">Account Created Successfully!</div>
                    <div class="success-message">
                        Welcome to MediAI Platform, {st.session_state.get('reg_username_temp', 'User')}!<br>
                        <small>You can now sign in with your credentials.</small>
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            
            
            if st.button("🔑 Go to Sign In", use_container_width=True, type="primary"):
                st.session_state.registration_step = 1
                # Clean up temp data
                for key in ["reg_username_temp", "reg_email_temp"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        render_security_badge()


def show_user_panel():
    """Show user info panel in sidebar"""
    if not st.session_state.get("authenticated", False):
        return
    
    user = get_current_user()
    role = get_current_role()
    avatar = get_user_avatar()
    stats = get_user_stats(user)
    
    with st.sidebar:
        st.markdown("---")
        
        # User avatar and info
        st.markdown(
            f"""
            <div style="text-align: center; padding: 1rem;">
                <div class="avatar-container" style="width: 80px; height: 80px; margin: 0 auto 1rem;">
                    <div class="avatar" style="width: 80px; height: 80px; font-size: 2rem;">
                        {avatar}
                    </div>
                    <div class="avatar-status"></div>
                </div>
                <div style="font-size: 1.2rem; font-weight: 700; color: #e5e7eb;">
                    {user}
                </div>
                <div style="font-size: 0.85rem; color: #9ca3af; margin-top: 0.25rem;">
                    {role}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Quick stats
        st.markdown(
            f"""
            <div class="stats-grid" style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 0.5rem; margin: 1rem 0;">
                <div class="stat-card" style="text-align: center; padding: 0.5rem; background: rgba(15, 23, 42, 0.6); border-radius: 8px;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #00d4aa;">{stats['login_count']}</div>
                    <div style="font-size: 0.65rem; color: #6b7280;">LOGINS</div>
                </div>
                <div class="stat-card" style="text-align: center; padding: 0.5rem; background: rgba(15, 23, 42, 0.6); border-radius: 8px;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #6366f1;">{stats['days_member']}</div>
                    <div style="font-size: 0.65rem; color: #6b7280;">DAYS</div>
                </div>
                <div class="stat-card" style="text-align: center; padding: 0.5rem; background: rgba(15, 23, 42, 0.6); border-radius: 8px;">
                    <div style="font-size: 1.2rem; font-weight: 700; color: #10b981;">{'✓' if stats['verified'] else '○'}</div>
                    <div style="font-size: 0.65rem; color: #6b7280;">VERIFIED</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        # Logout button
        if st.button("🚪 Sign Out", use_container_width=True, key="logout_btn"):
            with st.spinner("Signing out..."):
                time.sleep(1)
                logout_user()
            st.rerun()
        
        st.caption("🔐 Secure Session Active")