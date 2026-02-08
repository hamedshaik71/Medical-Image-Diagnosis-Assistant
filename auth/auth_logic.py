"""
🔐 Enhanced Authentication Logic
- Advanced security features
- Session management
- Login attempt tracking
- Account lockout
- Password hashing (demo)
"""

import streamlit as st
import json
import os
import time
import random
import hashlib
import re
from datetime import datetime, timedelta
from typing import Tuple, Optional, Dict

# ============================================
# 📁 DATABASE PATHS
# ============================================
DB_PATH = "database/users.json"
OTP_DB_PATH = "database/otp_verification.json"
LOGIN_ATTEMPTS_PATH = "database/login_attempts.json"
SESSIONS_PATH = "database/sessions.json"


# ============================================
# 🔧 DATABASE INITIALIZATION
# ============================================
def init_db():
    """Initialize all database files"""
    os.makedirs("database", exist_ok=True)
    
    files = [DB_PATH, OTP_DB_PATH, LOGIN_ATTEMPTS_PATH, SESSIONS_PATH]
    
    for file_path in files:
        if not os.path.exists(file_path):
            with open(file_path, "w") as f:
                json.dump({}, f)


def load_json(path: str) -> dict:
    """Generic JSON loader"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            return json.load(f)
    except:
        return {}


def save_json(path: str, data: dict) -> bool:
    """Generic JSON saver"""
    try:
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
        print(f"Error saving {path}: {e}")
        return False


# Convenience functions
def load_users() -> dict:
    return load_json(DB_PATH)

def save_users(users: dict) -> bool:
    return save_json(DB_PATH, users)

def load_otp_data() -> dict:
    return load_json(OTP_DB_PATH)

def save_otp_data(data: dict) -> bool:
    return save_json(OTP_DB_PATH, data)

def load_login_attempts() -> dict:
    return load_json(LOGIN_ATTEMPTS_PATH)

def save_login_attempts(data: dict) -> bool:
    return save_json(LOGIN_ATTEMPTS_PATH, data)


# ============================================
# 🔒 PASSWORD SECURITY
# ============================================
def hash_password(password: str) -> str:
    """Hash password with SHA256 (use bcrypt in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    return hash_password(password) == hashed


def check_password_strength(password: str) -> Dict:
    """
    Check password strength and return detailed analysis
    Returns dict with: strength (0-4), label, color, requirements
    """
    requirements = {
        "length": len(password) >= 8,
        "uppercase": bool(re.search(r'[A-Z]', password)),
        "lowercase": bool(re.search(r'[a-z]', password)),
        "digit": bool(re.search(r'\d', password)),
        "special": bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password)),
    }
    
    score = sum(requirements.values())
    
    if score <= 1:
        return {"strength": 0, "label": "Very Weak", "class": "weak", "requirements": requirements}
    elif score == 2:
        return {"strength": 1, "label": "Weak", "class": "weak", "requirements": requirements}
    elif score == 3:
        return {"strength": 2, "label": "Fair", "class": "fair", "requirements": requirements}
    elif score == 4:
        return {"strength": 3, "label": "Good", "class": "good", "requirements": requirements}
    else:
        return {"strength": 4, "label": "Strong", "class": "strong", "requirements": requirements}


def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format"""
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Valid"


# ============================================
# 🚫 LOGIN ATTEMPT TRACKING
# ============================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15  # minutes


def get_login_attempts(username: str) -> dict:
    """Get login attempts for a user"""
    attempts = load_login_attempts()
    return attempts.get(username, {"count": 0, "last_attempt": None, "locked_until": None})


def record_failed_login(username: str):
    """Record a failed login attempt"""
    attempts = load_login_attempts()
    
    user_attempts = attempts.get(username, {"count": 0, "last_attempt": None, "locked_until": None})
    user_attempts["count"] = user_attempts.get("count", 0) + 1
    user_attempts["last_attempt"] = datetime.now().isoformat()
    
    # Lock account if too many attempts
    if user_attempts["count"] >= MAX_LOGIN_ATTEMPTS:
        user_attempts["locked_until"] = (datetime.now() + timedelta(minutes=LOCKOUT_DURATION)).isoformat()
    
    attempts[username] = user_attempts
    save_login_attempts(attempts)


def clear_login_attempts(username: str):
    """Clear login attempts after successful login"""
    attempts = load_login_attempts()
    if username in attempts:
        del attempts[username]
        save_login_attempts(attempts)


def is_account_locked(username: str) -> Tuple[bool, Optional[int]]:
    """Check if account is locked, return remaining lockout time"""
    user_attempts = get_login_attempts(username)
    
    if user_attempts.get("locked_until"):
        locked_until = datetime.fromisoformat(user_attempts["locked_until"])
        if datetime.now() < locked_until:
            remaining = int((locked_until - datetime.now()).total_seconds() / 60)
            return True, remaining
        else:
            # Lockout expired, clear attempts
            clear_login_attempts(username)
    
    return False, None


# ============================================
# 🔐 OTP GENERATION & VERIFICATION
# ============================================
def generate_otp() -> str:
    """Generate a 6-digit OTP"""
    return str(random.randint(100000, 999999))


def send_otp_email(email: str, otp: str, purpose: str = "verification") -> bool:
    """
    Send OTP via email (mock implementation)
    In production, integrate with email service (SendGrid, AWS SES, etc.)
    """
    try:
        otp_data = load_otp_data()
        otp_data[email] = {
            "otp": otp,
            "purpose": purpose,
            "timestamp": datetime.now().isoformat(),
            "verified": False,
            "attempts": 0
        }
        save_otp_data(otp_data)
        
        # Mock email sending - print to console
        print(f"📧 OTP for {email} ({purpose}): {otp}")
        
        return True
    except Exception as e:
        print(f"Error in OTP process: {e}")
        return False


def verify_otp(email: str, otp_input: str) -> Tuple[bool, str]:
    """Verify OTP for email"""
    otp_data = load_otp_data()
    
    if email not in otp_data:
        return False, "No OTP found. Please request a new one."
    
    stored_data = otp_data[email]
    stored_otp = stored_data.get("otp")
    timestamp = datetime.fromisoformat(stored_data.get("timestamp", datetime.now().isoformat()))
    attempts = stored_data.get("attempts", 0)
    
    # Check max attempts
    if attempts >= 5:
        del otp_data[email]
        save_otp_data(otp_data)
        return False, "Too many failed attempts. Please request a new OTP."
    
    # Check if OTP expired (5 minutes)
    if datetime.now() - timestamp > timedelta(minutes=5):
        del otp_data[email]
        save_otp_data(otp_data)
        return False, "OTP expired. Please request a new one."
    
    if stored_otp != str(otp_input):
        otp_data[email]["attempts"] = attempts + 1
        save_otp_data(otp_data)
        remaining = 5 - attempts - 1
        return False, f"Invalid OTP. {remaining} attempts remaining."
    
    # Mark as verified
    otp_data[email]["verified"] = True
    save_otp_data(otp_data)
    
    return True, "OTP verified successfully!"


def request_otp(email: str, purpose: str = "verification") -> Tuple[bool, str]:
    """Request a new OTP"""
    otp = generate_otp()
    success = send_otp_email(email, otp, purpose)
    
    if success:
        return True, f"OTP sent to {email}"
    else:
        return False, "Failed to send OTP. Please try again."


# ============================================
# 🔄 SESSION STATE MANAGEMENT
# ============================================
def init_auth_state():
    """Initialize authentication state"""
    defaults = {
        "authenticated": False,
        "current_user": None,
        "current_role": None,
        "current_email": None,
        "user_avatar": None,
        "login_time": None,
        "loading": False,
        "otp_verified": {},
        "show_forgot_password": False,
        "reset_step": "email",
        "reset_email": None,
        "registration_step": 1,
        "remember_me": False,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def show_loading_animation(message: str, duration: float = 2):
    """Show loading animation"""
    st.session_state.loading = True
    
    placeholder = st.empty()
    
    frames = ["🔄", "⏳", "⚙️", "✨", "🔐", "🚀"]
    
    steps = int(duration * 5)
    for i in range(steps):
        with placeholder.container():
            st.markdown(
                f"""
                <div class="loading-container">
                    <div style="font-size: 2rem; animation: float 1s ease-in-out infinite;">{frames[i % len(frames)]}</div>
                    <div class="loading-text">{message}<span class="loading-dots"></span></div>
                </div>
                """,
                unsafe_allow_html=True
            )
            time.sleep(0.2)
    
    placeholder.empty()
    st.session_state.loading = False


# ============================================
# 👤 USER REGISTRATION
# ============================================
def check_username_availability(username: str) -> bool:
    """Check if username is available"""
    users = load_users()
    return username.lower() not in [u.lower() for u in users.keys()]


def check_email_availability(email: str) -> bool:
    """Check if email is available"""
    users = load_users()
    for user_data in users.values():
        if user_data.get("email", "").lower() == email.lower():
            return False
    return True


def register_user(
    username: str, 
    password: str, 
    email: str, 
    role: str,
    full_name: str = "",
    otp_verified: bool = False
) -> Tuple[bool, str]:
    """Register a new user with comprehensive validation"""
    
    # Validate username
    valid, msg = validate_username(username)
    if not valid:
        return False, msg
    
    # Validate email
    if not validate_email(email):
        return False, "Invalid email format"
    
    # Validate password
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    strength = check_password_strength(password)
    if strength["strength"] < 2:
        return False, "Password is too weak. Add uppercase, numbers, or special characters."
    
    users = load_users()
    
    # Check username availability
    if not check_username_availability(username):
        return False, "Username already taken"
    
    # Check email availability
    if not check_email_availability(email):
        return False, "Email already registered"
    
    # Create user
    users[username] = {
        "password": hash_password(password),
        "email": email.lower(),
        "role": role,
        "full_name": full_name,
        "created_date": datetime.now().isoformat(),
        "verified": otp_verified,
        "avatar": username[0].upper(),
        "last_login": None,
        "login_count": 0,
        "settings": {
            "theme": "dark",
            "notifications": True,
            "two_factor": False
        }
    }
    
    if save_users(users):
        return True, "Account created successfully! 🎉"
    else:
        return False, "Error creating account. Please try again."


# ============================================
# 🔑 USER AUTHENTICATION
# ============================================
def authenticate_user(username: str, password: str) -> Tuple[bool, str]:
    """Authenticate user with security checks"""
    
    # Check if account is locked
    locked, remaining = is_account_locked(username)
    if locked:
        return False, f"Account locked. Try again in {remaining} minutes."
    
    users = load_users()
    user = users.get(username)
    
    if not user:
        record_failed_login(username)
        return False, "Invalid username or password"
    
    # Verify password
    if not verify_password(password, user.get("password", "")):
        record_failed_login(username)
        attempts = get_login_attempts(username)
        remaining = MAX_LOGIN_ATTEMPTS - attempts["count"]
        
        if remaining <= 0:
            return False, f"Account locked for {LOCKOUT_DURATION} minutes"
        elif remaining <= 2:
            return False, f"Invalid password. {remaining} attempts remaining before lockout."
        else:
            return False, "Invalid username or password"
    
    # Successful login
    clear_login_attempts(username)
    
    # Update session state
    st.session_state.authenticated = True
    st.session_state.current_user = username
    st.session_state.current_role = user.get("role", "User")
    st.session_state.current_email = user.get("email", "")
    st.session_state.user_avatar = user.get("avatar", username[0].upper())
    st.session_state.login_time = datetime.now().isoformat()
    
    # Update user stats
    users[username]["last_login"] = datetime.now().isoformat()
    users[username]["login_count"] = users[username].get("login_count", 0) + 1
    save_users(users)
    
    return True, f"Welcome back, {username}! 🎉"


def logout_user():
    """Logout current user"""
    st.session_state.authenticated = False
    st.session_state.current_user = None
    st.session_state.current_role = None
    st.session_state.current_email = None
    st.session_state.user_avatar = None
    st.session_state.login_time = None


# ============================================
# 🔍 USER INFO GETTERS
# ============================================
def is_authenticated() -> bool:
    return st.session_state.get("authenticated", False)

def get_current_user() -> Optional[str]:
    return st.session_state.get("current_user")

def get_current_role() -> Optional[str]:
    return st.session_state.get("current_role")

def get_current_email() -> Optional[str]:
    return st.session_state.get("current_email")

def get_user_avatar() -> str:
    return st.session_state.get("user_avatar", "U")

def get_login_time() -> Optional[str]:
    return st.session_state.get("login_time")


def get_user_stats(username: str) -> dict:
    """Get user statistics"""
    users = load_users()
    user = users.get(username, {})
    
    created = user.get("created_date")
    if created:
        created_date = datetime.fromisoformat(created)
        days_member = (datetime.now() - created_date).days
    else:
        days_member = 0
    
    return {
        "login_count": user.get("login_count", 0),
        "days_member": days_member,
        "role": user.get("role", "User"),
        "verified": user.get("verified", False)
    }


def reset_session():
    """Reset authentication session"""
    logout_user()
    st.session_state.show_forgot_password = False
    st.session_state.reset_step = "email"
    st.session_state.reset_email = None


# Initialize database on import
init_db()