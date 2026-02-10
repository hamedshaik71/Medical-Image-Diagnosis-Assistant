# **`auth_logic.py` - CLEAN PRODUCTION VERSION**
"""
🔐 Enhanced Authentication Logic
- Advanced security features
- Session management
- Login attempt tracking
- Account lockout
- Password hashing
- LOGIN WITH USERNAME OR EMAIL
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
    """Generic JSON loader with error handling"""
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r") as f:
            data = json.load(f)
            return data if isinstance(data, dict) else {}
    except:
        return {}


def save_json(path: str, data: dict) -> bool:
    """Generic JSON saver"""
    try:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f, indent=4)
        return True
    except Exception as e:
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
    """Hash password with SHA256"""
    if not password:
        return ""
    return hashlib.sha256(password.encode('utf-8')).hexdigest()


def verify_password(password: str, hashed: str) -> bool:
    """Verify password against hash"""
    if not password or not hashed:
        return False
    return hash_password(password) == hashed


def check_password_strength(password: str) -> Dict:
    """
    Check password strength and return detailed analysis
    Returns dict with: strength (0-4), label, class, requirements
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
    if not email:
        return False
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email.strip()))


def validate_username(username: str) -> Tuple[bool, str]:
    """Validate username format"""
    if not username:
        return False, "Username cannot be empty"
    
    username = username.strip()
    
    if len(username) < 3:
        return False, "Username must be at least 3 characters"
    if len(username) > 20:
        return False, "Username must be less than 20 characters"
    if not re.match(r'^[a-zA-Z0-9_]+$', username):
        return False, "Username can only contain letters, numbers, and underscores"
    return True, "Valid"


# ============================================
# 🔍 USER LOOKUP HELPER
# ============================================
def find_user_by_identifier(identifier: str) -> Tuple[Optional[str], Optional[dict]]:
    """
    Find user by username OR email (case-insensitive)
    Returns: (username, user_data) or (None, None) if not found
    """
    if not identifier:
        return None, None
    
    users = load_users()
    if not users:
        return None, None
    
    identifier = identifier.strip()
    identifier_lower = identifier.lower()
    
    # Check for username match (case-insensitive)
    for username, user_data in users.items():
        if username.lower() == identifier_lower:
            return username, user_data
    
    # Check for email match (case-insensitive)
    for username, user_data in users.items():
        user_email = user_data.get("email", "")
        if user_email and user_email.lower() == identifier_lower:
            return username, user_data
    
    return None, None


def get_identifier_type(identifier: str) -> str:
    """Determine if identifier is email or username"""
    if validate_email(identifier):
        return "email"
    return "username"


# ============================================
# 🚫 LOGIN ATTEMPT TRACKING
# ============================================
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = 15  # minutes


def get_login_attempts(identifier: str) -> dict:
    """Get login attempts for a user"""
    if not identifier:
        return {"count": 0, "last_attempt": None, "locked_until": None}
    
    attempts = load_login_attempts()
    identifier_key = identifier.lower().strip()
    return attempts.get(identifier_key, {"count": 0, "last_attempt": None, "locked_until": None})


def record_failed_login(identifier: str):
    """Record a failed login attempt"""
    if not identifier:
        return
    
    attempts = load_login_attempts()
    identifier_key = identifier.lower().strip()
    
    user_attempts = attempts.get(identifier_key, {"count": 0, "last_attempt": None, "locked_until": None})
    user_attempts["count"] = user_attempts.get("count", 0) + 1
    user_attempts["last_attempt"] = datetime.now().isoformat()
    
    if user_attempts["count"] >= MAX_LOGIN_ATTEMPTS:
        user_attempts["locked_until"] = (datetime.now() + timedelta(minutes=LOCKOUT_DURATION)).isoformat()
    
    attempts[identifier_key] = user_attempts
    save_login_attempts(attempts)


def clear_login_attempts(identifier: str):
    """Clear login attempts after successful login"""
    if not identifier:
        return
    
    attempts = load_login_attempts()
    identifier_key = identifier.lower().strip()
    if identifier_key in attempts:
        del attempts[identifier_key]
        save_login_attempts(attempts)


def is_account_locked(identifier: str) -> Tuple[bool, Optional[int]]:
    """Check if account is locked, return remaining lockout time"""
    if not identifier:
        return False, None
    
    user_attempts = get_login_attempts(identifier)
    
    if user_attempts.get("locked_until"):
        locked_until = datetime.fromisoformat(user_attempts["locked_until"])
        if datetime.now() < locked_until:
            remaining = int((locked_until - datetime.now()).total_seconds() / 60) + 1
            return True, remaining
        else:
            clear_login_attempts(identifier)
    
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
        return True
    except:
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
    
    if attempts >= 5:
        del otp_data[email]
        save_otp_data(otp_data)
        return False, "Too many failed attempts. Please request a new OTP."
    
    if datetime.now() - timestamp > timedelta(minutes=5):
        del otp_data[email]
        save_otp_data(otp_data)
        return False, "OTP expired. Please request a new one."
    
    if stored_otp != str(otp_input):
        otp_data[email]["attempts"] = attempts + 1
        save_otp_data(otp_data)
        remaining = 5 - attempts - 1
        return False, f"Invalid OTP. {remaining} attempts remaining."
    
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
    """Check if username is available (case-insensitive)"""
    if not username:
        return False
    
    users = load_users()
    username_lower = username.strip().lower()
    
    for existing_username in users.keys():
        if existing_username.lower() == username_lower:
            return False
    
    return True


def check_email_availability(email: str) -> bool:
    """Check if email is available (case-insensitive)"""
    if not email:
        return False
    
    users = load_users()
    email_lower = email.strip().lower()
    
    for user_data in users.values():
        if user_data.get("email", "").lower() == email_lower:
            return False
    
    return True


def register_user(
    username: str, 
    password: str, 
    email: str, 
    role: str = "User",
    full_name: str = "",
    otp_verified: bool = False
) -> Tuple[bool, str]:
    """Register a new user with comprehensive validation"""
    
    username = username.strip()
    email = email.strip().lower()
    password = password.strip()
    
    valid, msg = validate_username(username)
    if not valid:
        return False, msg
    
    if not validate_email(email):
        return False, "Invalid email format"
    
    if len(password) < 6:
        return False, "Password must be at least 6 characters"
    
    strength = check_password_strength(password)
    if strength["strength"] < 2:
        return False, "Password is too weak. Add uppercase, numbers, or special characters."
    
    if not check_username_availability(username):
        return False, "Username already taken"
    
    if not check_email_availability(email):
        return False, "Email already registered"
    
    users = load_users()
    
    users[username] = {
        "password": hash_password(password),
        "email": email,
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
def authenticate_user(identifier: str, password: str) -> Tuple[bool, str]:
    """
    Authenticate user with USERNAME or EMAIL
    
    Args:
        identifier: Username or email address
        password: User's password
        
    Returns:
        (success, message) tuple
    """
    
    if not identifier or not password:
        return False, "❌ Please enter both username/email and password"
    
    identifier = identifier.strip()
    password = password.strip()
    
    locked, remaining = is_account_locked(identifier)
    if locked:
        return False, f"🔒 Account locked. Try again in {remaining} minutes."
    
    username, user = find_user_by_identifier(identifier)
    
    if not user or not username:
        record_failed_login(identifier)
        return False, "❌ Invalid username/email or password"
    
    stored_password_hash = user.get("password", "")
    
    if not stored_password_hash:
        return False, "❌ Account configuration error. Please contact support."
    
    if not verify_password(password, stored_password_hash):
        record_failed_login(identifier)
        attempts = get_login_attempts(identifier)
        remaining = MAX_LOGIN_ATTEMPTS - attempts["count"]
        
        if remaining <= 0:
            return False, f"🔒 Account locked for {LOCKOUT_DURATION} minutes due to too many failed attempts"
        elif remaining <= 2:
            return False, f"❌ Invalid password. ⚠️ {remaining} attempts remaining before lockout!"
        else:
            return False, "❌ Invalid username/email or password"
    
    clear_login_attempts(identifier)
    clear_login_attempts(username)
    if user.get("email"):
        clear_login_attempts(user["email"])
    
    st.session_state.authenticated = True
    st.session_state.current_user = username
    st.session_state.current_role = user.get("role", "User")
    st.session_state.current_email = user.get("email", "")
    st.session_state.user_avatar = user.get("avatar", username[0].upper())
    st.session_state.login_time = datetime.now().isoformat()
    
    users = load_users()
    if username in users:
        users[username]["last_login"] = datetime.now().isoformat()
        users[username]["login_count"] = users[username].get("login_count", 0) + 1
        save_users(users)
    
    login_method = get_identifier_type(identifier)
    if login_method == "email":
        return True, f"✅ Welcome back, {username}! 🎉 (Logged in via email)"
    else:
        return True, f"✅ Welcome back, {username}! 🎉"


def logout_user():
    """Logout current user and clear session"""
    keys_to_clear = [
        "authenticated",
        "current_user",
        "current_role",
        "current_email",
        "user_avatar",
        "login_time",
        "loading",
        "show_forgot_password",
        "reset_step",
        "reset_email"
    ]
    
    for key in keys_to_clear:
        if key in st.session_state:
            st.session_state[key] = None
    
    st.session_state.authenticated = False


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
        try:
            created_date = datetime.fromisoformat(created)
            days_member = (datetime.now() - created_date).days
        except:
            days_member = 0
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