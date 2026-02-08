"""
🔐 Enhanced Forgot Password Module
- Animated OTP Input
- Timer Display
- Step-by-step Process
"""

import streamlit as st
import json
import os
import time
import random
from datetime import datetime, timedelta
from auth.auth_logic import load_users, save_users, hash_password
from auth.styles import FORGOT_PASSWORD_STYLES, SUCCESS_ANIMATION, ERROR_ANIMATION

RESET_DB_PATH = "database/password_resets.json"


def init_reset_db():
    """Initialize password reset database"""
    os.makedirs("database", exist_ok=True)
    if not os.path.exists(RESET_DB_PATH):
        with open(RESET_DB_PATH, "w") as f:
            json.dump({}, f)


def load_reset_data():
    if not os.path.exists(RESET_DB_PATH):
        return {}
    try:
        with open(RESET_DB_PATH, "r") as f:
            return json.load(f)
    except:
        return {}


def save_reset_data(data):
    try:
        with open(RESET_DB_PATH, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except:
        return False


def generate_otp():
    return str(random.randint(100000, 999999))


def initiate_password_reset(email):
    """Start password reset process"""
    users = load_users()
    
    # Find user by email
    username = None
    for user, data in users.items():
        if data.get("email", "").lower() == email.lower():
            username = user
            break
    
    if not username:
        return False, "Email not found in our database"
    
    otp = generate_otp()
    
    reset_data = load_reset_data()
    reset_data[email.lower()] = {
        "otp": otp,
        "username": username,
        "timestamp": datetime.now().isoformat(),
        "verified": False,
        "attempts": 0
    }
    
    if save_reset_data(reset_data):
        print(f"🔐 PASSWORD RESET OTP for {email}: {otp}")
        return True, f"OTP sent to {email}"
    
    return False, "Error initiating reset"


def verify_reset_otp(email, otp_input):
    """Verify OTP for password reset"""
    reset_data = load_reset_data()
    email = email.lower()
    
    if email not in reset_data:
        return False, "No reset request found"
    
    request = reset_data[email]
    timestamp = datetime.fromisoformat(request.get("timestamp"))
    attempts = request.get("attempts", 0)
    
    if attempts >= 5:
        return False, "Too many attempts. Request new OTP."
    
    if datetime.now() - timestamp > timedelta(minutes=10):
        del reset_data[email]
        save_reset_data(reset_data)
        return False, "OTP expired"
    
    if request.get("otp") != str(otp_input):
        reset_data[email]["attempts"] = attempts + 1
        save_reset_data(reset_data)
        return False, f"Invalid OTP. {4 - attempts} attempts left."
    
    reset_data[email]["verified"] = True
    save_reset_data(reset_data)
    
    return True, "OTP verified!"


def reset_password(email, new_password, confirm_password):
    """Reset the password"""
    if not new_password or not confirm_password:
        return False, "Please fill both fields"
    
    if new_password != confirm_password:
        return False, "Passwords don't match"
    
    if len(new_password) < 6:
        return False, "Password must be at least 6 characters"
    
    email = email.lower()
    reset_data = load_reset_data()
    
    if email not in reset_data:
        return False, "No reset request found"
    
    if not reset_data[email].get("verified"):
        return False, "Please verify OTP first"
    
    username = reset_data[email].get("username")
    users = load_users()
    
    if username not in users:
        return False, "User not found"
    
    users[username]["password"] = hash_password(new_password)
    users[username]["password_reset_date"] = datetime.now().isoformat()
    
    if save_users(users):
        del reset_data[email]
        save_reset_data(reset_data)
        return True, "Password reset successfully!"
    
    return False, "Error updating password"


def show_forgot_password_modal():
    """Display forgot password interface"""
    
    st.markdown(FORGOT_PASSWORD_STYLES, unsafe_allow_html=True)
    
    # Initialize state
    if "reset_step" not in st.session_state:
        st.session_state.reset_step = "email"
    if "reset_email" not in st.session_state:
        st.session_state.reset_email = None
    
    # Header
    st.markdown(
        """
        <div class="reset-glass-container">
            <div class="reset-header">
                <div class="reset-icon">🔐</div>
                <div class="reset-title">Reset Password</div>
                <div class="reset-subtitle">We'll help you get back in</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Progress indicator
    step_num = {"email": 1, "otp": 2, "newpassword": 3}.get(st.session_state.reset_step, 1)
    
    st.markdown(
        f"""
        <div class="stepper-container">
            <div class="step {'step-completed' if step_num > 1 else 'step-active'}">
                <div class="step-circle">{'✓' if step_num > 1 else '1'}</div>
                <div class="step-label">Email</div>
            </div>
            <div class="step-connector {'step-connector-active' if step_num > 1 else ''}"></div>
            <div class="step {'step-completed' if step_num > 2 else 'step-active' if step_num == 2 else 'step-pending'}">
                <div class="step-circle">{'✓' if step_num > 2 else '2'}</div>
                <div class="step-label">Verify</div>
            </div>
            <div class="step-connector {'step-connector-active' if step_num > 2 else ''}"></div>
            <div class="step {'step-active' if step_num == 3 else 'step-pending'}">
                <div class="step-circle">3</div>
                <div class="step-label">Reset</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # ==========================================
    # STEP 1: EMAIL
    # ==========================================
    if st.session_state.reset_step == "email":
        st.markdown("#### 📧 Enter Your Email")
        st.caption("We'll send a verification code to your email")
        
        email_input = st.text_input(
            "Email Address",
            placeholder="your@email.com",
            key="reset_email_input"
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Back to Login", use_container_width=True):
                st.session_state.show_forgot_password = False
                st.session_state.reset_step = "email"
                st.rerun()
        
        with col2:
            if st.button("Send OTP →", use_container_width=True, type="primary"):
                if not email_input:
                    st.error("Please enter your email")
                else:
                    with st.spinner("📧 Sending OTP..."):
                        time.sleep(1)
                        success, message = initiate_password_reset(email_input)
                    
                    if success:
                        st.session_state.reset_email = email_input
                        st.session_state.reset_step = "otp"
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # ==========================================
    # STEP 2: OTP VERIFICATION
    # ==========================================
    elif st.session_state.reset_step == "otp":
        st.markdown("#### 🔢 Enter Verification Code")
        st.info(f"📧 OTP sent to: **{st.session_state.reset_email}**")
        
        otp_input = st.text_input(
            "6-Digit OTP",
            placeholder="000000",
            key="reset_otp_input",
            max_chars=6
        )
        
        # Timer warning
        st.markdown(
            """
            <div class="timer-container">
                <span class="timer-icon">⏱️</span>
                <span class="timer-text">OTP expires in 10 minutes</span>
            </div>
            """,
            unsafe_allow_html=True
        )
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("← Back", use_container_width=True):
                st.session_state.reset_step = "email"
                st.rerun()
        
        with col2:
            if st.button("🔄 Resend", use_container_width=True):
                with st.spinner("Resending..."):
                    time.sleep(1)
                    success, message = initiate_password_reset(st.session_state.reset_email)
                st.success("New OTP sent!" if success else message)
        
        with col3:
            if st.button("Verify →", use_container_width=True, type="primary"):
                if not otp_input or len(otp_input) != 6:
                    st.error("Enter 6-digit OTP")
                else:
                    with st.spinner("Verifying..."):
                        time.sleep(0.5)
                        success, message = verify_reset_otp(
                            st.session_state.reset_email,
                            otp_input
                        )
                    
                    if success:
                        st.session_state.reset_step = "newpassword"
                        st.success(message)
                        time.sleep(1)
                        st.rerun()
                    else:
                        st.error(f"❌ {message}")
    
    # ==========================================
    # STEP 3: NEW PASSWORD
    # ==========================================
    elif st.session_state.reset_step == "newpassword":
        st.markdown("#### 🔑 Create New Password")
        
        new_pass = st.text_input(
            "New Password",
            type="password",
            placeholder="Enter new password",
            key="new_password_input"
        )
        
        confirm_pass = st.text_input(
            "Confirm Password",
            type="password",
            placeholder="Confirm new password",
            key="confirm_password_input"
        )
        
        # Password match indicator
        if new_pass and confirm_pass:
            if new_pass == confirm_pass:
                st.success("✅ Passwords match!")
            else:
                st.error("❌ Passwords don't match")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("← Cancel", use_container_width=True):
                st.session_state.show_forgot_password = False
                st.session_state.reset_step = "email"
                st.session_state.reset_email = None
                st.rerun()
        
        with col2:
            if st.button("🔐 Reset Password", use_container_width=True, type="primary"):
                with st.spinner("Resetting password..."):
                    time.sleep(1)
                    success, message = reset_password(
                        st.session_state.reset_email,
                        new_pass,
                        confirm_pass
                    )
                
                if success:
                    st.markdown(
                        SUCCESS_ANIMATION.format(
                            title="Password Reset!",
                            message="You can now login with your new password"
                        ),
                        unsafe_allow_html=True
                    )
                    st.balloons()
                    time.sleep(2)
                    
                    # Clean up
                    st.session_state.show_forgot_password = False
                    st.session_state.reset_step = "email"
                    st.session_state.reset_email = None
                    st.rerun()
                else:
                    st.error(f"❌ {message}")


# Initialize on import
init_reset_db()