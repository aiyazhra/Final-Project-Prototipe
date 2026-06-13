import streamlit as st
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Settings — ClusterHub", page_icon="⚙️", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('settings')

st.markdown("## ⚙️ Settings")
st.markdown("Manage your profile and default clustering preferences.")

tab1, tab2, tab3, tab4 = st.tabs(["👤 Profile", "🔧 Default Parameters", "🔔 Notifications", "⚠️ Danger Zone"])

with tab1:
    col_avatar, col_form = st.columns([1, 3])
    with col_avatar:
        username = st.session_state.get('username', 'User')
        initials = ''.join(w[0].upper() for w in username.split()[:2]) or 'U'
        st.markdown(f"""
        <div style="width:90px;height:90px;border-radius:50%;background:linear-gradient(135deg,#3b82f6,#60a5fa);
                    display:flex;align-items:center;justify-content:center;color:white;
                    font-size:30px;font-weight:700;margin:0 auto 12px;">{initials}</div>
        """, unsafe_allow_html=True)
        st.button("Change Photo", use_container_width=True)

    with col_form:
        with st.form("profile_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input("Full Name", value=st.session_state.get('username',''))
                institution = st.text_input("Institution", value="Universitas XYZ")
            with col2:
                email = st.text_input("Email", value="cathaleyazachary@gmail.com")
                role = st.selectbox("Role", ["Researcher","Business Analyst","Student","Academic"], index=0)

            saved = st.form_submit_button("💾 Save Profile", use_container_width=True)
            if saved:
                st.session_state.username = new_name
                st.success("✅ Profile saved successfully!")

with tab2:
    st.markdown("#### Default Clustering Parameters")
    st.markdown("These values will be pre-filled when you start a new clustering session.")

    col1, col2 = st.columns(2)
    with col1:
        default_k = st.number_input("Default K (clusters)", min_value=2, max_value=10,
                                     value=st.session_state.get('k', 4))
        default_thresh = st.select_slider("Default Threshold", [0.2,0.3,0.5,0.7,1.0],
                                          value=st.session_state.get('threshold', 0.5))
    with col2:
        default_norm = st.selectbox("Default Normalization", ["Min-Max Scaling","Z-Score Standardization","Robust Scaling"])
        remove_outliers = st.checkbox("Remove Outliers by Default", value=True)

    st.markdown("#### Default AHP Weights")
    w = st.session_state.get('ahp_weights', [0.637, 0.261, 0.102])
    col_r, col_f, col_m = st.columns(3)
    with col_r: wr = st.number_input("Recency Weight", 0.0, 1.0, round(w[0],3), 0.001)
    with col_f: wf = st.number_input("Frequency Weight", 0.0, 1.0, round(w[1],3), 0.001)
    with col_m: wm = st.number_input("Monetary Weight", 0.0, 1.0, round(w[2],3), 0.001)

    total_w = wr + wf + wm
    if abs(total_w - 1.0) > 0.01:
        st.warning(f"⚠️ Weights sum to {total_w:.3f}. They should sum to 1.0.")

    if st.button("💾 Save Default Parameters", use_container_width=False):
        st.session_state.k = int(default_k)
        st.session_state.threshold = default_thresh
        st.session_state.ahp_weights = [wr, wf, wm]
        st.session_state.outlier_removed = remove_outliers
        st.success("✅ Default parameters saved!")

with tab3:
    st.markdown("#### Notification Preferences")

    notifs = {
        "Clustering Complete": ("Notify when a clustering run finishes", True),
        "Poor Quality Alert": ("Alert when Silhouette Score < 0.4", True),
        "Export Ready": ("Notify when export is ready to download", False),
        "New Data Upload": ("Confirm after successful file upload", True),
    }
    for label, (desc, default) in notifs.items():
        col_n, col_toggle = st.columns([3, 1])
        with col_n:
            st.markdown(f"**{label}**  \n<small style='color:#64748b;'>{desc}</small>", unsafe_allow_html=True)
        with col_toggle:
            st.checkbox("", value=default, key=f"notif_{label.replace(' ','_')}")

    if st.button("💾 Save Notifications"):
        st.success("✅ Notification preferences saved!")

with tab4:
    st.markdown("#### Danger Zone")
    st.error("⚠️ The following actions are permanent and cannot be undone.")

    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown("""
        <div style="background:#fee2e2;border-radius:8px;padding:16px;margin-bottom:12px;">
          <div style="font-weight:600;color:#991b1b;">Clear Current Session Data</div>
          <div style="font-size:12px;color:#b91c1c;margin-top:4px;">Removes uploaded data and results from memory</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️ Clear Session Data", use_container_width=True):
            for key in ['df','rfm_df','rfm_normalized','labels','pca_coords',
                        'silhouette_score','davies_bouldin','cluster_summary']:
                st.session_state[key] = None
            st.success("Session data cleared.")

    with col_b:
        st.markdown("""
        <div style="background:#fee2e2;border-radius:8px;padding:16px;margin-bottom:12px;">
          <div style="font-weight:600;color:#991b1b;">Delete All Saved Projects</div>
          <div style="font-size:12px;color:#b91c1c;margin-top:4px;">Permanently removes all project history</div>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🗑️ Delete All Projects", use_container_width=True):
            st.session_state.projects = []
            st.success("All projects deleted.")

    st.markdown("---")
    st.markdown("""
    <div style="background:#fee2e2;border-radius:8px;padding:16px;">
      <div style="font-weight:600;color:#991b1b;">Logout & End Session</div>
      <div style="font-size:12px;color:#b91c1c;margin-top:4px;">Returns to login page. Session state is preserved.</div>
    </div>
    """, unsafe_allow_html=True)
    if st.button("🚪 Logout Now", use_container_width=False):
        st.session_state.logged_in = False
        st.switch_page('app.py')

