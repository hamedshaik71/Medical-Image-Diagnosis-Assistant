"""
🎨 Advanced CSS Styles for Authentication System (WITHOUT BALLOON ANIMATIONS)
- Glassmorphism
- Neon Effects
- Animated Gradients
- Particle Backgrounds
"""

# The CSS styles remain the same as before
AUTH_STYLES = """
<style>
    /* ============================================
       🌌 ANIMATED PARTICLE BACKGROUND
       ============================================ */
    @keyframes float {
        0%, 100% { transform: translateY(0) rotate(0deg); opacity: 1; }
        50% { transform: translateY(-20px) rotate(180deg); opacity: 0.5; }
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(0, 212, 170, 0.3); }
        50% { box-shadow: 0 0 40px rgba(0, 212, 170, 0.6), 0 0 60px rgba(0, 255, 136, 0.3); }
    }
    
    @keyframes gradient-shift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    @keyframes border-dance {
        0%, 100% { border-color: #00d4aa; }
        25% { border-color: #00ff88; }
        50% { border-color: #6366f1; }
        75% { border-color: #8b5cf6; }
    }
    
    @keyframes shimmer {
        0% { background-position: -200% 0; }
        100% { background-position: 200% 0; }
    }
    
    @keyframes bounce-in {
        0% { transform: scale(0.3); opacity: 0; }
        50% { transform: scale(1.05); }
        70% { transform: scale(0.9); }
        100% { transform: scale(1); opacity: 1; }
    }
    
    @keyframes slide-up {
        from { transform: translateY(30px); opacity: 0; }
        to { transform: translateY(0); opacity: 1; }
    }
    
    @keyframes typing {
        from { width: 0; }
        to { width: 100%; }
    }
    
    @keyframes blink-caret {
        from, to { border-color: transparent; }
        50% { border-color: #00d4aa; }
    }
    
    @keyframes rotate-gradient {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }
    
    @keyframes neon-flicker {
        0%, 19%, 21%, 23%, 25%, 54%, 56%, 100% {
            text-shadow: 
                0 0 4px #00d4aa,
                0 0 11px #00d4aa,
                0 0 19px #00d4aa,
                0 0 40px #00ff88,
                0 0 80px #00ff88;
        }
        20%, 24%, 55% {
            text-shadow: none;
        }
    }

    /* ============================================
       🎭 PARTICLE BACKGROUND
       ============================================ */
    .particles-container {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        pointer-events: none;
        overflow: hidden;
        z-index: -1;
    }
    
    .particle {
        position: absolute;
        width: 10px;
        height: 10px;
        background: linear-gradient(135deg, #00d4aa, #00ff88);
        border-radius: 50%;
        animation: float 15s infinite;
        opacity: 0.3;
    }
    
    .particle:nth-child(1) { left: 10%; animation-delay: 0s; width: 8px; height: 8px; }
    .particle:nth-child(2) { left: 20%; animation-delay: 2s; width: 12px; height: 12px; }
    .particle:nth-child(3) { left: 30%; animation-delay: 4s; width: 6px; height: 6px; }
    .particle:nth-child(4) { left: 40%; animation-delay: 6s; width: 14px; height: 14px; }
    .particle:nth-child(5) { left: 50%; animation-delay: 8s; width: 10px; height: 10px; }
    .particle:nth-child(6) { left: 60%; animation-delay: 10s; width: 8px; height: 8px; }
    .particle:nth-child(7) { left: 70%; animation-delay: 12s; width: 16px; height: 16px; }
    .particle:nth-child(8) { left: 80%; animation-delay: 14s; width: 6px; height: 6px; }
    .particle:nth-child(9) { left: 90%; animation-delay: 16s; width: 12px; height: 12px; }
    .particle:nth-child(10) { left: 95%; animation-delay: 18s; width: 10px; height: 10px; }

    /* ============================================
       🔮 GLASSMORPHISM MAIN CONTAINER
       ============================================ */
    .auth-glass-container {
        max-width: 520px;
        margin: 1rem auto;
        background: rgba(15, 23, 42, 0.8);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        padding: 2.5rem;
        border-radius: 24px;
        border: 1px solid rgba(0, 212, 170, 0.2);
        box-shadow: 
            0 25px 50px -12px rgba(0, 0, 0, 0.5),
            0 0 0 1px rgba(255, 255, 255, 0.05),
            inset 0 1px 0 rgba(255, 255, 255, 0.1);
        animation: bounce-in 0.6s ease-out;
        position: relative;
        overflow: hidden;
    }
    
    .auth-glass-container::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 200%;
        height: 100%;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.03),
            transparent
        );
        animation: shimmer 8s infinite;
    }
    
    .auth-glass-container::after {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: conic-gradient(
            from 0deg,
            transparent,
            rgba(0, 212, 170, 0.1),
            transparent,
            rgba(99, 102, 241, 0.1),
            transparent
        );
        animation: rotate-gradient 20s linear infinite;
        z-index: -1;
    }

    /* ============================================
       ✨ NEON LOGO & HEADER
       ============================================ */
    .neon-header {
        text-align: center;
        margin-bottom: 2rem;
        animation: slide-up 0.5s ease-out;
    }
    
    .neon-logo {
        font-size: 4rem;
        margin-bottom: 0.5rem;
        animation: float 3s ease-in-out infinite;
        filter: drop-shadow(0 0 20px rgba(0, 212, 170, 0.5));
    }
    
    .neon-title {
        font-size: 2.2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4aa 0%, #00ff88 50%, #6366f1 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: gradient-shift 3s ease infinite;
        margin-bottom: 0.5rem;
        letter-spacing: -1px;
    }
    
    .neon-subtitle {
        color: #9ca3af;
        font-size: 1rem;
        font-weight: 400;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

    /* ============================================
       🎯 ADVANCED INPUT FIELDS
       ============================================ */
    .input-group {
        position: relative;
        margin-bottom: 1.5rem;
        animation: slide-up 0.5s ease-out;
    }
    
    .input-group label {
        display: block;
        color: #9ca3af;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.5rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    .stTextInput > div > div > input {
        background: rgba(15, 23, 42, 0.9) !important;
        border: 2px solid rgba(75, 85, 99, 0.3) !important;
        border-radius: 12px !important;
        padding: 1rem 1.2rem !important;
        color: #e5e7eb !important;
        font-size: 1rem !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        width: 100% !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #00d4aa !important;
        box-shadow: 
            0 0 0 3px rgba(0, 212, 170, 0.1),
            0 0 20px rgba(0, 212, 170, 0.2) !important;
        background: rgba(15, 23, 42, 1) !important;
    }
    
    .stTextInput > div > div > input::placeholder {
        color: #6b7280 !important;
    }

    /* ============================================
       🚀 ANIMATED BUTTONS
       ============================================ */
    .stButton > button {
        background: linear-gradient(135deg, #00d4aa 0%, #00ff88 50%, #00d4aa 100%) !important;
        background-size: 200% auto !important;
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        letter-spacing: 0.5px !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 0.9rem 2rem !important;
        cursor: pointer !important;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1) !important;
        position: relative !important;
        overflow: hidden !important;
        text-transform: uppercase !important;
    }
    
    .stButton > button:hover {
        background-position: right center !important;
        transform: translateY(-2px) !important;
        box-shadow: 
            0 10px 40px rgba(0, 212, 170, 0.4),
            0 0 0 1px rgba(0, 212, 170, 0.2) !important;
    }
    
    .stButton > button:active {
        transform: translateY(0) scale(0.98) !important;
    }
    
    .stButton > button::before {
        content: '' !important;
        position: absolute !important;
        top: 0 !important;
        left: -100% !important;
        width: 100% !important;
        height: 100% !important;
        background: linear-gradient(
            90deg,
            transparent,
            rgba(255, 255, 255, 0.3),
            transparent
        ) !important;
        transition: left 0.5s !important;
    }
    
    .stButton > button:hover::before {
        left: 100% !important;
    }

    /* Secondary Button Style */
    .secondary-btn > button {
        background: transparent !important;
        border: 2px solid rgba(0, 212, 170, 0.5) !important;
        color: #00d4aa !important;
    }
    
    .secondary-btn > button:hover {
        background: rgba(0, 212, 170, 0.1) !important;
        border-color: #00d4aa !important;
    }

    /* ============================================
       🔐 PASSWORD STRENGTH METER
       ============================================ */
    .password-strength-container {
        margin-top: 0.5rem;
        animation: slide-up 0.3s ease-out;
    }
    
    .password-strength-bar {
        height: 6px;
        border-radius: 3px;
        background: #1f2937;
        overflow: hidden;
        margin-bottom: 0.5rem;
    }
    
    .password-strength-fill {
        height: 100%;
        border-radius: 3px;
        transition: all 0.3s ease;
    }
    
    .strength-weak { 
        width: 25%; 
        background: linear-gradient(90deg, #ef4444, #f87171); 
    }
    .strength-fair { 
        width: 50%; 
        background: linear-gradient(90deg, #f59e0b, #fbbf24); 
    }
    .strength-good { 
        width: 75%; 
        background: linear-gradient(90deg, #3b82f6, #60a5fa); 
    }
    .strength-strong { 
        width: 100%; 
        background: linear-gradient(90deg, #10b981, #34d399); 
    }
    
    .strength-text {
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    
    .strength-weak-text { color: #ef4444; }
    .strength-fair-text { color: #f59e0b; }
    .strength-good-text { color: #3b82f6; }
    .strength-strong-text { color: #10b981; }

    /* ============================================
       ✅ PASSWORD REQUIREMENTS CHECKLIST
       ============================================ */
    .requirements-list {
        background: rgba(15, 23, 42, 0.5);
        border-radius: 12px;
        padding: 1rem;
        margin-top: 1rem;
        border: 1px solid rgba(75, 85, 99, 0.2);
    }
    
    .requirement-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.3rem 0;
        font-size: 0.85rem;
        transition: all 0.3s ease;
    }
    
    .requirement-met {
        color: #10b981;
    }
    
    .requirement-unmet {
        color: #6b7280;
    }
    
    .requirement-icon {
        width: 18px;
        height: 18px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        transition: all 0.3s ease;
    }
    
    .requirement-icon-met {
        background: #10b981;
        color: white;
    }
    
    .requirement-icon-unmet {
        background: rgba(75, 85, 99, 0.3);
        color: #6b7280;
    }

    /* ============================================
       📊 PROGRESS STEPPER
       ============================================ */
    .stepper-container {
        display: flex;
        justify-content: center;
        align-items: center;
        margin-bottom: 2rem;
        gap: 0;
    }
    
    .step {
        display: flex;
        flex-direction: column;
        align-items: center;
        position: relative;
    }
    
    .step-circle {
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 700;
        font-size: 0.9rem;
        transition: all 0.3s ease;
        position: relative;
        z-index: 1;
    }
    
    .step-active .step-circle {
        background: linear-gradient(135deg, #00d4aa, #00ff88);
        color: #0f172a;
        box-shadow: 0 0 20px rgba(0, 212, 170, 0.5);
        animation: pulse-glow 2s infinite;
    }
    
    .step-completed .step-circle {
        background: #10b981;
        color: white;
    }
    
    .step-pending .step-circle {
        background: rgba(75, 85, 99, 0.3);
        color: #6b7280;
        border: 2px solid rgba(75, 85, 99, 0.5);
    }
    
    .step-label {
        font-size: 0.75rem;
        color: #9ca3af;
        margin-top: 0.5rem;
        text-align: center;
        max-width: 80px;
    }
    
    .step-connector {
        width: 60px;
        height: 3px;
        background: rgba(75, 85, 99, 0.3);
        margin: 0 0.5rem;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
    }
    
    .step-connector-active {
        background: linear-gradient(90deg, #00d4aa, #00ff88);
    }

    /* ============================================
       🎉 SUCCESS ANIMATION (WITHOUT CONFETTI)
       ============================================ */
    .success-container {
        text-align: center;
        padding: 2rem;
        animation: bounce-in 0.6s ease-out;
    }
    
    .success-icon {
        font-size: 4rem;
        margin-bottom: 1rem;
        animation: float 2s ease-in-out infinite;
        filter: drop-shadow(0 0 30px rgba(16, 185, 129, 0.5));
    }
    
    .success-title {
        font-size: 1.5rem;
        font-weight: 700;
        color: #10b981;
        margin-bottom: 0.5rem;
    }
    
    .success-message {
        color: #9ca3af;
        font-size: 1rem;
    }

    /* ============================================
       ❌ ERROR ANIMATION
       ============================================ */
    .error-shake {
        animation: shake 0.5s ease-in-out;
    }
    
    @keyframes shake {
        0%, 100% { transform: translateX(0); }
        10%, 30%, 50%, 70%, 90% { transform: translateX(-5px); }
        20%, 40%, 60%, 80% { transform: translateX(5px); }
    }
    
    .error-container {
        background: linear-gradient(135deg, rgba(239, 68, 68, 0.1), rgba(220, 38, 38, 0.1));
        border: 1px solid rgba(239, 68, 68, 0.3);
        border-radius: 12px;
        padding: 1rem;
        margin: 1rem 0;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        animation: slide-up 0.3s ease-out;
    }
    
    .error-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
    }
    
    .error-text {
        color: #fca5a5;
        font-size: 0.9rem;
    }

    /* ============================================
       🔄 LOADING SPINNER
       ============================================ */
    .loading-container {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        padding: 2rem;
    }
    
    .loading-spinner {
        width: 50px;
        height: 50px;
        border: 4px solid rgba(0, 212, 170, 0.1);
        border-top-color: #00d4aa;
        border-radius: 50%;
        animation: spin 1s linear infinite;
    }
    
    @keyframes spin {
        to { transform: rotate(360deg); }
    }
    
    .loading-text {
        margin-top: 1rem;
        color: #9ca3af;
        font-size: 0.9rem;
        animation: pulse 1.5s ease-in-out infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 0.5; }
        50% { opacity: 1; }
    }
    
    .loading-dots::after {
        content: '';
        animation: dots 1.5s steps(4, end) infinite;
    }
    
    @keyframes dots {
        0%, 20% { content: ''; }
        40% { content: '.'; }
        60% { content: '..'; }
        80%, 100% { content: '...'; }
    }

    /* ============================================
       📱 SOCIAL LOGIN BUTTONS
       ============================================ */
    .social-container {
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(75, 85, 99, 0.2);
    }
    
    .social-divider {
        text-align: center;
        color: #6b7280;
        font-size: 0.85rem;
        margin-bottom: 1rem;
        position: relative;
    }
    
    .social-divider::before,
    .social-divider::after {
        content: '';
        position: absolute;
        top: 50%;
        width: 30%;
        height: 1px;
        background: rgba(75, 85, 99, 0.3);
    }
    
    .social-divider::before { left: 0; }
    .social-divider::after { right: 0; }
    
    .social-buttons {
        display: flex;
        gap: 1rem;
        justify-content: center;
    }
    
    .social-btn {
        width: 50px;
        height: 50px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.5rem;
        transition: all 0.3s ease;
        cursor: pointer;
        border: 1px solid rgba(75, 85, 99, 0.3);
        background: rgba(15, 23, 42, 0.5);
    }
    
    .social-btn:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
    }
    
    .social-google:hover { 
        background: rgba(234, 67, 53, 0.2); 
        border-color: #ea4335; 
    }
    .social-github:hover { 
        background: rgba(255, 255, 255, 0.1); 
        border-color: #ffffff; 
    }
    .social-microsoft:hover { 
        background: rgba(0, 120, 212, 0.2); 
        border-color: #0078d4; 
    }

    /* ============================================
       🌙 THEME TOGGLE
       ============================================ */
    .theme-toggle {
        position: absolute;
        top: 1rem;
        right: 1rem;
        width: 40px;
        height: 40px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        cursor: pointer;
        background: rgba(75, 85, 99, 0.2);
        border: 1px solid rgba(75, 85, 99, 0.3);
        transition: all 0.3s ease;
        font-size: 1.2rem;
    }
    
    .theme-toggle:hover {
        background: rgba(0, 212, 170, 0.1);
        border-color: #00d4aa;
    }

       /* ============================================
       📋 TAB STYLES - FIXED SPACING
       ============================================ */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;  /* ✅ Added gap between tabs */
        background: rgba(15, 23, 42, 0.5);
        border-radius: 16px;
        padding: 0.75rem;  /* ✅ Increased padding */
        border: 1px solid rgba(75, 85, 99, 0.2);
        margin-bottom: 1.5rem;  /* ✅ Added margin below tabs */
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        min-width: 140px;  /* ✅ Added minimum width */
        border-radius: 12px;
        color: #9ca3af;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.3s ease;
        background: transparent;
        border: none;
        padding: 0 1.5rem;  /* ✅ Added horizontal padding */
        margin: 0 0.25rem;  /* ✅ Added margin between tabs */
        white-space: nowrap;  /* ✅ Prevent text wrapping */
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        color: #e5e7eb;
        background: rgba(0, 212, 170, 0.1);
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #00d4aa, #00ff88) !important;
        color: #0f172a !important;
    }
    
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }
    
    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* ============================================
       🔔 NOTIFICATION BADGE
       ============================================ */
    .notification-badge {
        position: absolute;
        top: -5px;
        right: -5px;
        width: 20px;
        height: 20px;
        background: #ef4444;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.7rem;
        font-weight: 700;
        color: white;
        animation: pulse-glow 2s infinite;
    }

    /* ============================================
       📊 STATS CARDS
       ============================================ */
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 1rem;
        margin: 1.5rem 0;
    }
    
    .stat-card {
        background: rgba(15, 23, 42, 0.6);
        border: 1px solid rgba(75, 85, 99, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: #00d4aa;
        transform: translateY(-3px);
    }
    
    .stat-value {
        font-size: 1.5rem;
        font-weight: 700;
        color: #00d4aa;
    }
    
    .stat-label {
        font-size: 0.75rem;
        color: #6b7280;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* ============================================
       📱 RESPONSIVE DESIGN
       ============================================ */
    @media (max-width: 768px) {
        .auth-glass-container {
            margin: 0.5rem;
            padding: 1.5rem;
        }
        
        .neon-title {
            font-size: 1.8rem;
        }
        
        .stats-grid {
            grid-template-columns: 1fr;
        }
        
        .social-buttons {
            flex-wrap: wrap;
        }
    }

    /* ============================================
       🎭 AVATAR STYLES
       ============================================ */
    .avatar-container {
        width: 100px;
        height: 100px;
        margin: 0 auto 1rem;
        position: relative;
    }
    
    .avatar {
        width: 100%;
        height: 100%;
        border-radius: 50%;
        background: linear-gradient(135deg, #00d4aa, #00ff88);
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 2.5rem;
        color: #0f172a;
        font-weight: 700;
        border: 4px solid rgba(0, 212, 170, 0.3);
        box-shadow: 0 0 30px rgba(0, 212, 170, 0.3);
    }
    
    .avatar-status {
        position: absolute;
        bottom: 5px;
        right: 5px;
        width: 20px;
        height: 20px;
        background: #10b981;
        border-radius: 50%;
        border: 3px solid #0f172a;
    }

    /* ============================================
       🔒 SECURITY BADGE
       ============================================ */
    .security-badge {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 0.5rem;
        padding: 0.5rem 1rem;
        background: rgba(16, 185, 129, 0.1);
        border: 1px solid rgba(16, 185, 129, 0.3);
        border-radius: 20px;
        font-size: 0.8rem;
        color: #10b981;
        margin-top: 1.5rem;
    }
    
    .security-badge-icon {
        font-size: 1rem;
    }

    /* Hide Streamlit Branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Custom Scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: #0f172a;
    }
    
    ::-webkit-scrollbar-thumb {
        background: #00d4aa;
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: #00ff88;
    }
</style>

<!-- Particle Background -->
<div class="particles-container">
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
    <div class="particle"></div>
</div>
"""

# Other style constants remain the same
FORGOT_PASSWORD_STYLES = """<style>...[same as before]...</style>"""

SUCCESS_ANIMATION = """
<div class="success-container">
    <div class="success-icon">✅</div>
    <div class="success-title">{title}</div>
    <div class="success-message">{message}</div>
</div>
"""

ERROR_ANIMATION = """
<div class="error-container error-shake">
    <div class="error-icon">❌</div>
    <div class="error-text">{message}</div>
</div>
"""

LOADING_ANIMATION = """
<div class="loading-container">
    <div class="loading-spinner"></div>
    <div class="loading-text">{message}<span class="loading-dots"></span></div>
</div>
"""