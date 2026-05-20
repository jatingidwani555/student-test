import streamlit as st

def inject_custom_css():
    """Inject beautiful, custom premium-grade dark/glassmorphic CSS styles into the Streamlit app."""
    css = """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700;800&family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    /* Global Overrides */
    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', 'Outfit', sans-serif;
    }

    /* Main Container Padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }

    /* Gradient Text Header */
    .gradient-text {
        background: linear-gradient(135deg, #FF6B6B 0%, #FF8E53 50%, #4D96FF 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 800;
        font-size: 3rem;
        letter-spacing: -1.5px;
        margin-bottom: 0.5rem;
    }
    
    .gradient-text-sub {
        background: linear-gradient(135deg, #4D96FF 0%, #6BCB77 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700;
        font-size: 2.2rem;
        letter-spacing: -1px;
    }

    /* Modern Glassmorphic Cards */
    .glass-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 16px;
        padding: 24px;
        backdrop-filter: blur(16px);
        -webkit-backdrop-filter: blur(16px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.2);
        margin-bottom: 20px;
        transition: transform 0.3s ease, border-color 0.3s ease;
    }
    .glass-card:hover {
        transform: translateY(-2px);
        border-color: rgba(255, 255, 255, 0.15);
    }
    
    .glass-card-header {
        font-size: 1.3rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 12px;
        border-bottom: 1px solid rgba(255, 255, 255, 0.1);
        padding-bottom: 8px;
    }

    /* Interactive Exam Header/Timer Component */
    .exam-timer-box {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.1) 0%, rgba(255, 142, 83, 0.1) 100%);
        border: 1px solid rgba(255, 107, 107, 0.2);
        border-radius: 12px;
        padding: 16px;
        text-align: center;
        margin-bottom: 24px;
    }
    
    .timer-text {
        font-size: 2rem;
        font-weight: 800;
        color: #FF6B6B;
        font-family: monospace;
        letter-spacing: 2px;
    }

    /* Custom Metric Display */
    .metric-container {
        display: flex;
        justify-content: space-between;
        gap: 16px;
        margin-bottom: 24px;
    }
    
    .metric-box {
        flex: 1;
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 12px;
        padding: 20px;
        text-align: center;
    }
    .metric-box-label {
        font-size: 0.85rem;
        color: #a0aec0;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 6px;
    }
    .metric-box-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #ffffff;
    }

    /* Question Navigation Grid Button Custom Stylings */
    .q-grid-btn {
        display: inline-block;
        width: 36px;
        height: 36px;
        line-height: 34px;
        text-align: center;
        border-radius: 8px;
        margin: 4px;
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    .q-grid-btn-unattempted {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        color: #ffffff;
    }
    .q-grid-btn-attempted {
        background: rgba(77, 150, 255, 0.2);
        border: 1px solid rgba(77, 150, 255, 0.6);
        color: #4D96FF;
    }
    .q-grid-btn-current {
        background: #ffffff;
        border: 1px solid #ffffff;
        color: #0e1117;
        box-shadow: 0 0 12px rgba(255, 255, 255, 0.4);
    }

    /* Question Card Styling */
    .question-card {
        background: rgba(255, 255, 255, 0.03);
        border-left: 4px solid #4D96FF;
        padding: 20px;
        border-radius: 4px 12px 12px 4px;
        margin-bottom: 24px;
    }
    
    .question-title {
        font-size: 1.2rem;
        font-weight: 600;
        color: #ffffff;
        margin-bottom: 8px;
    }

    /* Premium Form Inputs Custom Styling */
    div[data-baseweb="input"] {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }
    
    div[data-baseweb="select"] > div {
        background-color: rgba(255, 255, 255, 0.03) !important;
        border: 1px solid rgba(255, 255, 255, 0.08) !important;
        border-radius: 8px !important;
    }

    /* Sidebar Glassmorphic Elements */
    section[data-testid="stSidebar"] {
        background-color: rgba(14, 17, 23, 0.95) !important;
        border-right: 1px solid rgba(255, 255, 255, 0.05);
    }
    
    /* Elegant scrollbars */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    ::-webkit-scrollbar-track {
        background: rgba(255, 255, 255, 0.02);
    }
    ::-webkit-scrollbar-thumb {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 4px;
    }
    ::-webkit-scrollbar-thumb:hover {
        background: rgba(255, 255, 255, 0.2);
    }

    /* Success/Error/Info Glowing Banners */
    .stAlert {
        border-radius: 12px !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        background-color: rgba(255, 255, 255, 0.03) !important;
        backdrop-filter: blur(10px);
    }
    
    /* Custom Badge elements */
    .custom-badge {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 50px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    
    .badge-primary {
        background-color: rgba(77, 150, 255, 0.15);
        color: #4D96FF;
        border: 1px solid rgba(77, 150, 255, 0.3);
    }
    
    .badge-success {
        background-color: rgba(107, 203, 119, 0.15);
        color: #6BCB77;
        border: 1px solid rgba(107, 203, 119, 0.3);
    }

    .badge-danger {
        background-color: rgba(255, 107, 107, 0.15);
        color: #FF6B6B;
        border: 1px solid rgba(255, 107, 107, 0.3);
    }
    
    /* Login layout styles */
    .login-container {
        max-width: 450px;
        margin: 0 auto;
        padding: 40px;
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        box-shadow: 0 15px 35px rgba(0, 0, 0, 0.4);
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)
