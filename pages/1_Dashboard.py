import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Dashboard — ClusterViz", page_icon="📊", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('dashboard')

# ─── Header ──────────────────────────────────────────────────────────────────

name = st.session_state.get('username', 'User')
st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;
            background:#3b82f6;
            border-radius:16px;padding:20px 28px;margin-bottom:20px;color:white;">
  <div>
    <div style="font-size:20px;font-weight:700;">Hello, {name}! 👋</div>
    <div style="font-size:13px;opacity:0.8;margin-top:3px;">Here's your clustering project summary</div>
  </div>
  <div style="display:flex;gap:10px;">
    <a href="History" style="background:rgba(255,255,255,0.15);color:white;padding:8px 16px;
       border-radius:8px;font-size:13px;font-weight:600;text-decoration:none;">📁 Saved Results</a>
  </div>
</div>
""", unsafe_allow_html=True)

# ─── Stat Cards ──────────────────────────────────────────────────────────────

has_results = st.session_state.get('labels') is not None
has_data    = st.session_state.get('df') is not None
n_projects  = len(st.session_state.get('projects', []))
sil = st.session_state.get('silhouette_score')
n_customers = len(st.session_state['rfm_df']) if st.session_state.get('rfm_df') is not None else (
              len(st.session_state['df']['CustomerID'].unique()) if has_data else 0)

c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Total Customers", f"{n_customers:,}" if n_customers else "—", "Ready for clustering" if has_data else "Upload data first")
with c2:
    n_tx = len(st.session_state['df']) if has_data else 0
    st.metric("Total Transactions", f"{n_tx:,}" if n_tx else "—", "Rows in dataset" if has_data else "No data yet")
with c3:
    st.metric("Clustering Projects", str(n_projects), f"{n_projects} saved" if n_projects else "Run first clustering")

st.markdown("<div style='margin-top:4px;'></div>", unsafe_allow_html=True)

# ─── Charts Row ──────────────────────────────────────────────────────────────

col_chart, col_right = st.columns([2.2, 1])

with col_chart:
    st.markdown("### Cluster Visualization")
    if has_results:
        pca_coords = np.array(st.session_state['pca_coords'])
        labels     = np.array(st.session_state['labels'])
        fig = make_pca_scatter(pca_coords, labels, height=420)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:60px;text-align:center;
                    border:2px dashed #e2e8f0;height:510px;display:flex;flex-direction:column;
                    align-items:center;justify-content:center;">
          <div style="font-size:48px;margin-bottom:12px;">📊</div>
          <div style="font-size:15px;font-weight:600;color:#1e293b;">No clustering results yet</div>
          <div style="font-size:13px;color:#64748b;margin-top:6px;">
            Upload data and run clustering to see visualization here
          </div>
        </div>
        """, unsafe_allow_html=True)

with col_right:
    st.markdown("### Evaluation")
    sil_pct = int((sil or 0) * 100)
    sil_color = "#10b981" if (sil or 0) > 0.5 else ("#f59e0b" if (sil or 0) > 0.25 else "#ef4444")
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:20px;box-shadow:0 2px 10px rgba(0,0,0,0.07);text-align:center;margin-bottom:12px;">
      <div style="font-size:12px;color:#64748b;margin-bottom:4px;">Silhouette Score</div>
      <div style="font-size:40px;font-weight:800;color:{sil_color};">{f"{sil:.3f}" if sil else "—"}</div>
      <div style="font-size:12px;color:#64748b;margin-bottom:10px;">{'Good clustering quality' if sil and sil>0.5 else 'Run clustering first'}</div>
      <div style="background:#f1f5f9;border-radius:20px;height:8px;overflow:hidden;">
        <div style="width:{sil_pct}%;height:100%;background:{sil_color};border-radius:20px;transition:width 0.5s;"></div>
      </div>
      <div style="display:flex;justify-content:space-between;font-size:10px;color:#94a3b8;margin-top:4px;"><span>0</span><span>1.0</span></div>
    </div>
    """, unsafe_allow_html=True)

    db = st.session_state.get('davies_bouldin')
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,0.07);text-align:center;margin-bottom:12px;">
      <div style="font-size:12px;color:#64748b;margin-bottom:4px;">Davies-Bouldin Index</div>
      <div style="font-size:32px;font-weight:800;color:#f59e0b;">{f"{db:.3f}" if db else "—"}</div>
      <div style="font-size:11px;color:#94a3b8;">Lower = better</div>
    </div>
    """, unsafe_allow_html=True)

    ch = st.session_state.get('calinski_harabasz')
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:16px;box-shadow:0 2px 10px rgba(0,0,0,0.07);text-align:center;margin-bottom:12px;">
      <div style="font-size:12px;color:#64748b;margin-bottom:4px;">Calinski-Harabasz Index</div>
      <div style="font-size:32px;font-weight:800;color:#3b82f6;">{f"{ch:.1f}" if ch else "—"}</div>
      <div style="font-size:11px;color:#94a3b8;">Higher = better</div>
    </div>
    """, unsafe_allow_html=True)

    if has_results:
        if st.button("📋 View Results", use_container_width=True):
            st.switch_page('pages/6_Results.py')

# ─── Recent Projects Table ────────────────────────────────────────────────────

st.markdown("---")
st.markdown("### Recent Clustering Projects")
projects = st.session_state.get('projects', [])

if projects:
    df_proj = pd.DataFrame(projects)
    df_proj = df_proj.rename(columns={
        'name':'Project Name', 'date':'Date', 'algorithm':'Algorithm',
        'k':'K', 'customers':'Customers', 'silhouette':'Silhouette', 'status':'Status'
    })
    st.dataframe(df_proj, use_container_width=True, hide_index=True)
else:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:32px;text-align:center;
                border:1px solid #e2e8f0;">
      <div style="font-size:32px;margin-bottom:8px;">🗂️</div>
      <div style="font-size:14px;font-weight:600;color:#1e293b;">No saved projects yet</div>
      <div style="font-size:12px;color:#64748b;margin-top:4px;">
        After you run clustering and save the result, it will appear here.
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:12px;'></div>", unsafe_allow_html=True)
    if st.button("➕ Start New Clustering", use_container_width=False):
        st.switch_page('pages/2_Data_Upload.py')

