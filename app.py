import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from utils.helpers import init_session

init_session()

if not st.session_state.get('logged_in'):
    # ─── Login page ───────────────────────────────────────────────────────────
    st.set_page_config(
        page_title="ClusterViz — Login",
        page_icon="🔵",
        layout="centered",
        initial_sidebar_state="collapsed",
    )
    st.markdown("""
<style>
html,body,[class*="css"]{font-family:'Inter',sans-serif!important;}
#MainMenu,footer,header[data-testid="stHeader"]{display:none!important;}
section[data-testid="stSidebar"]{display:none!important;}
.stApp{background:transparent!important;min-height:100vh;}
/* White card */
.block-container,
[data-testid="stMainBlockContainer"] {
    background:white!important;
    border-radius:16px!important;
    box-shadow:0 4px 32px rgba(0,0,0,0.12)!important;
    max-width:460px!important;
    padding:36px 44px 20px!important;
    margin:70px auto 0!important;
}
/* ── Input fields ── */
[data-testid="stTextInput"] label{
    font-weight:600!important;
    color:#374151!important;
    font-size:13.5px!important;
    margin-bottom:2px!important;
}
[data-testid="stTextInput"]>div>div{
    border:1.5px solid #d1d5db!important;
    border-radius:8px!important;
    background:white!important;
    overflow:hidden!important;
}
[data-testid="stTextInput"] input{
    padding-left:42px!important;
    height:46px!important;
    background-color:white!important;
    background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='none' stroke='%239ca3af' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Crect x='3' y='11' width='18' height='11' rx='2'/%3E%3Cpath d='M7 11V7a5 5 0 0 1 10 0v4'/%3E%3C/svg%3E")!important;
    background-repeat:no-repeat!important;
    background-position:12px center!important;
    background-size:18px 18px!important;
    font-size:14px!important;
    color:#111827!important;
    border:none!important;
}
[data-testid="stTextInput"] input::placeholder{color:#9ca3af!important;}
[data-testid="stTextInput"] input:focus{outline:none!important;}
/* ── Submit button ── */
[data-testid="stFormSubmitButton"]>button{
    background:#2563eb!important;
    color:white!important;
    border:none!important;
    border-radius:8px!important;
    height:48px!important;
    font-size:15px!important;
    font-weight:600!important;
    width:100%!important;
    margin-top:6px!important;
    letter-spacing:0.3px!important;
}
[data-testid="stFormSubmitButton"]>button:hover{
    background:#1d4ed8!important;
    box-shadow:0 4px 14px rgba(37,99,235,0.4)!important;
}
/* ── Checkbox & link ── */
.stCheckbox label p{color:#6b7280!important;font-size:13px!important;}
/* ── Remove Streamlit form border ── */
[data-testid="stForm"] {
    border:none!important;
    padding:0!important;
    background:transparent!important;
}
/* ── Hide heading anchor link ── */
[data-testid="stMarkdown"] h2 a,
[data-testid="stMarkdown"] h2 .anchor-link,
[data-testid="stMarkdown"] h2 svg { display:none!important; }
/* ── Full-width markdown so heading truly centers ── */
[data-testid="stMarkdown"],
[data-testid="stMarkdown"] > div { width:100%!important; }
[data-testid="stMarkdown"] h2,
[data-testid="stMarkdown"] p { text-align:center!important; }
</style>

<div style="position:fixed;inset:0;z-index:-1;overflow:hidden;pointer-events:none;">
  <svg viewBox="0 0 1440 900" xmlns="http://www.w3.org/2000/svg"
       preserveAspectRatio="xMidYMid slice"
       style="width:100%;height:100%;position:absolute;top:0;left:0;">
    <defs>
      <pattern id="grid" width="50" height="50" patternUnits="userSpaceOnUse">
        <path d="M 50 0 L 0 0 0 50" fill="none" stroke="#90bde0" stroke-width="0.6"/>
      </pattern>
    </defs>
    <rect width="1440" height="900" fill="#c8e0f4"/>
    <rect width="1440" height="900" fill="url(#grid)" opacity="0.45"/>
    <g stroke="#7ab2e0" stroke-width="1.5" fill="none" opacity="0.65">
      <line x1="0" y1="80" x2="160" y2="80"/>
      <line x1="160" y1="80" x2="160" y2="160"/>
      <line x1="160" y1="160" x2="320" y2="160"/>
      <line x1="240" y1="80" x2="400" y2="80"/>
      <line x1="400" y1="0" x2="400" y2="80"/>
      <line x1="480" y1="80" x2="640" y2="80"/>
      <line x1="560" y1="0" x2="560" y2="80"/>
      <line x1="640" y1="80" x2="640" y2="160"/>
      <line x1="640" y1="160" x2="760" y2="160"/>
      <line x1="880" y1="0" x2="880" y2="120"/>
      <line x1="880" y1="120" x2="1000" y2="120"/>
      <line x1="1000" y1="0" x2="1000" y2="120"/>
      <line x1="1000" y1="120" x2="1000" y2="200"/>
      <line x1="1000" y1="200" x2="1140" y2="200"/>
      <line x1="1140" y1="80" x2="1140" y2="200"/>
      <line x1="1140" y1="80" x2="1300" y2="80"/>
      <line x1="1200" y1="0" x2="1200" y2="80"/>
      <line x1="1300" y1="0" x2="1300" y2="80"/>
      <line x1="1300" y1="80" x2="1440" y2="80"/>
      <line x1="0" y1="260" x2="120" y2="260"/>
      <line x1="120" y1="260" x2="120" y2="320"/>
      <line x1="120" y1="320" x2="280" y2="320"/>
      <line x1="280" y1="160" x2="280" y2="320"/>
      <line x1="280" y1="240" x2="440" y2="240"/>
      <line x1="440" y1="160" x2="440" y2="320"/>
      <line x1="440" y1="320" x2="600" y2="320"/>
      <line x1="600" y1="240" x2="760" y2="240"/>
      <line x1="760" y1="160" x2="760" y2="320"/>
      <line x1="1060" y1="200" x2="1060" y2="280"/>
      <line x1="1060" y1="280" x2="1220" y2="280"/>
      <line x1="1220" y1="200" x2="1220" y2="360"/>
      <line x1="1220" y1="360" x2="1440" y2="360"/>
      <line x1="0" y1="440" x2="180" y2="440"/>
      <line x1="180" y1="440" x2="180" y2="500"/>
      <line x1="180" y1="500" x2="360" y2="500"/>
      <line x1="360" y1="440" x2="360" y2="500"/>
      <line x1="360" y1="440" x2="540" y2="440"/>
      <line x1="540" y1="360" x2="540" y2="440"/>
      <line x1="540" y1="360" x2="700" y2="360"/>
      <line x1="700" y1="360" x2="700" y2="440"/>
      <line x1="700" y1="440" x2="880" y2="440"/>
      <line x1="880" y1="360" x2="880" y2="440"/>
      <line x1="880" y1="360" x2="1040" y2="360"/>
      <line x1="1040" y1="360" x2="1040" y2="440"/>
      <line x1="1040" y1="440" x2="1220" y2="440"/>
      <line x1="1220" y1="440" x2="1440" y2="440"/>
      <line x1="0" y1="660" x2="160" y2="660"/>
      <line x1="160" y1="660" x2="160" y2="720"/>
      <line x1="160" y1="720" x2="340" y2="720"/>
      <line x1="340" y1="660" x2="340" y2="800"/>
      <line x1="340" y1="800" x2="520" y2="800"/>
      <line x1="520" y1="720" x2="520" y2="800"/>
      <line x1="520" y1="720" x2="700" y2="720"/>
      <line x1="700" y1="640" x2="700" y2="800"/>
      <line x1="700" y1="800" x2="880" y2="800"/>
      <line x1="880" y1="720" x2="880" y2="800"/>
      <line x1="880" y1="720" x2="1060" y2="720"/>
      <line x1="1060" y1="640" x2="1060" y2="800"/>
      <line x1="1060" y1="800" x2="1240" y2="800"/>
      <line x1="1240" y1="720" x2="1240" y2="800"/>
      <line x1="1240" y1="720" x2="1440" y2="720"/>
      <line x1="160" y1="720" x2="160" y2="900"/>
      <line x1="700" y1="800" x2="700" y2="900"/>
      <line x1="1240" y1="800" x2="1240" y2="900"/>
    </g>
    <g fill="#5296c8" opacity="0.8">
      <circle cx="160" cy="80" r="4.5"/><circle cx="160" cy="160" r="4.5"/>
      <circle cx="240" cy="80" r="4.5"/><circle cx="400" cy="80" r="4.5"/>
      <circle cx="480" cy="80" r="4.5"/><circle cx="560" cy="80" r="4.5"/>
      <circle cx="640" cy="80" r="4.5"/><circle cx="640" cy="160" r="4.5"/>
      <circle cx="760" cy="160" r="4.5"/>
      <circle cx="880" cy="120" r="4.5"/><circle cx="1000" cy="120" r="4.5"/>
      <circle cx="1000" cy="200" r="4.5"/><circle cx="1140" cy="200" r="4.5"/>
      <circle cx="1140" cy="80" r="4.5"/><circle cx="1300" cy="80" r="4.5"/>
      <circle cx="1200" cy="80" r="4.5"/>
      <circle cx="280" cy="160" r="4.5"/><circle cx="280" cy="240" r="4.5"/>
      <circle cx="280" cy="320" r="4.5"/><circle cx="120" cy="260" r="4.5"/>
      <circle cx="120" cy="320" r="4.5"/><circle cx="440" cy="160" r="4.5"/>
      <circle cx="440" cy="240" r="4.5"/><circle cx="440" cy="320" r="4.5"/>
      <circle cx="600" cy="240" r="4.5"/><circle cx="600" cy="320" r="4.5"/>
      <circle cx="760" cy="240" r="4.5"/><circle cx="760" cy="320" r="4.5"/>
      <circle cx="1060" cy="200" r="4.5"/><circle cx="1060" cy="280" r="4.5"/>
      <circle cx="1220" cy="200" r="4.5"/><circle cx="1220" cy="280" r="4.5"/>
      <circle cx="1220" cy="360" r="4.5"/>
      <circle cx="180" cy="440" r="4.5"/><circle cx="180" cy="500" r="4.5"/>
      <circle cx="360" cy="440" r="4.5"/><circle cx="360" cy="500" r="4.5"/>
      <circle cx="540" cy="440" r="4.5"/><circle cx="540" cy="360" r="4.5"/>
      <circle cx="700" cy="360" r="4.5"/><circle cx="700" cy="440" r="4.5"/>
      <circle cx="880" cy="440" r="4.5"/><circle cx="880" cy="360" r="4.5"/>
      <circle cx="1040" cy="360" r="4.5"/><circle cx="1040" cy="440" r="4.5"/>
      <circle cx="1220" cy="440" r="4.5"/>
      <circle cx="160" cy="660" r="4.5"/><circle cx="160" cy="720" r="4.5"/>
      <circle cx="340" cy="660" r="4.5"/><circle cx="340" cy="720" r="4.5"/>
      <circle cx="340" cy="800" r="4.5"/><circle cx="520" cy="720" r="4.5"/>
      <circle cx="520" cy="800" r="4.5"/><circle cx="700" cy="640" r="4.5"/>
      <circle cx="700" cy="720" r="4.5"/><circle cx="700" cy="800" r="4.5"/>
      <circle cx="880" cy="720" r="4.5"/><circle cx="880" cy="800" r="4.5"/>
      <circle cx="1060" cy="640" r="4.5"/><circle cx="1060" cy="720" r="4.5"/>
      <circle cx="1060" cy="800" r="4.5"/><circle cx="1240" cy="720" r="4.5"/>
      <circle cx="1240" cy="800" r="4.5"/>
    </g>
  </svg>
  <div style="position:absolute;bottom:-130px;left:-130px;width:430px;height:430px;
              border-radius:50%;background:radial-gradient(circle at 38% 38%,#60a5fa,#2563eb);
              opacity:0.88;"></div>
  <div style="position:absolute;top:-100px;right:-100px;width:360px;height:360px;
              border-radius:50%;background:radial-gradient(circle at 38% 38%,#93c5fd,#3b82f6);
              opacity:0.82;"></div>
</div>
""", unsafe_allow_html=True)

    st.markdown("""
    <div style="text-align:center;margin-bottom:20px;">
      <div style="display:inline-flex;align-items:center;gap:10px;">
        <svg width="34" height="34" viewBox="0 0 34 34" fill="none" xmlns="http://www.w3.org/2000/svg">
          <rect x="1" y="1" width="14" height="14" rx="2.5" fill="#3b82f6"/>
          <rect x="19" y="1" width="14" height="14" rx="2.5" fill="#2563eb"/>
          <rect x="1" y="19" width="14" height="14" rx="2.5" fill="#60a5fa"/>
          <rect x="19" y="19" width="14" height="14" rx="2.5" fill="#3b82f6"/>
        </svg>
        <span style="font-size:20px;font-weight:700;color:#1e3a8a;letter-spacing:-0.3px;">ClusterHub</span>
      </div>
    </div>
    <h2 style="font-size:28px;font-weight:800;color:#111827;margin:0 0 6px;text-align:center;width:100%;display:block;">Welcome Back!</h2>
    <p style="color:#9ca3af;font-size:13px;margin:0 0 28px;text-align:center;width:100%;display:block;">Sign in to your account</p>
    """, unsafe_allow_html=True)

    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="Enter your password")

        col_r, col_f = st.columns([1, 1])
        with col_r:
            st.checkbox("Remember me")
        with col_f:
            st.markdown(
                "<div style='text-align:right;padding-top:4px;'>"
                "<a href='#' style='font-size:12px;color:#2563eb;'>Forgot password?</a></div>",
                unsafe_allow_html=True,
            )

        submitted = st.form_submit_button("Sign In", use_container_width=True)
        if submitted:
            if username.strip() and password.strip():
                st.session_state.logged_in = True
                st.session_state.username = username.strip()
                st.rerun()
            else:
                st.error("Please enter username and password.")

    st.markdown("""
    <div style="text-align:center;margin-top:16px;padding-bottom:4px;font-size:11px;color:#9ca3af;">
      ClusterHub Analytics Platform 2026
    </div>
    """, unsafe_allow_html=True)

else:
    # ─── Authenticated app with hidden auto-nav ────────────────────────────────
    st.set_page_config(
        page_title="ClusterViz",
        page_icon="🔵",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    pg = st.navigation(
        [
            st.Page("pages/1_Dashboard.py",      title="Dashboard",      icon="📊"),
            st.Page("pages/2_Data_Upload.py",     title="Data",           icon="📁"),
            st.Page("pages/3_RFM_Analysis.py",    title="RFM Analysis",   icon="📈"),
            st.Page("pages/4_AHP_Weighting.py",   title="AHP",            icon="⚖️"),
            st.Page("pages/5_Clustering.py",      title="Clustering",     icon="🔵"),
            st.Page("pages/6_Results.py",         title="Results",        icon="📋"),
            st.Page("pages/7_Cluster_Detail.py",  title="Cluster Detail", icon="🔍"),
            st.Page("pages/8_History.py",         title="History",        icon="📂"),
            st.Page("pages/9_Settings.py",        title="Settings",       icon="⚙️"),
        ],
        position="hidden",   # kills Streamlit's built-in sidebar nav
    )
    pg.run()
