import streamlit as st
import pandas as pd
import numpy as np
import io, sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="History — ClusterHub", page_icon="📁", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('history')

st.markdown("## 📁 History & Export")
st.markdown("Manage your saved clustering projects and export results.")

projects = st.session_state.get('projects', [])

# ─── Stats row ────────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Total Projects", len(projects))
with c2: st.metric("Completed", len([p for p in projects if p.get('status')=='Completed']))
with c3:
    avg_sil = np.mean([p['silhouette'] for p in projects]) if projects else 0
    st.metric("Avg Silhouette", f"{avg_sil:.3f}" if projects else "—")
with c4:
    max_c = max([p['customers'] for p in projects], default=0)
    st.metric("Largest Dataset", f"{max_c:,}" if projects else "—")

st.markdown("---")

# ─── Project table ────────────────────────────────────────────────────────────
col_hdr, col_new = st.columns([3, 1])
with col_hdr:
    st.markdown("#### Saved Projects")
with col_new:
    if st.button("➕ New Clustering", use_container_width=True):
        st.switch_page('pages/2_Data_Upload.py')

if projects:
    search = st.text_input("🔍 Search projects", placeholder="Project name...")
    filtered = [p for p in projects if not search or search.lower() in p.get('name','').lower()]

    if filtered:
        df_proj = pd.DataFrame(filtered)
        df_proj.index = range(1, len(df_proj)+1)
        df_show = df_proj.rename(columns={
            'name':'Project Name','date':'Date','algorithm':'Algorithm',
            'k':'K','customers':'Customers','silhouette':'Silhouette Score','status':'Status'
        })
        st.dataframe(df_show, use_container_width=True)

        st.markdown("**Actions for selected project:**")
        sel_name = st.selectbox("Select project", [p['name'] for p in filtered])
        sel_p = next((p for p in filtered if p['name']==sel_name), None)

        if sel_p:
            act1, act2, act3 = st.columns(3)
            with act1:
                if st.button("👁️ View Results", use_container_width=True):
                    st.switch_page('pages/6_Results.py')
            with act2:
                if st.button("📥 Download CSV", use_container_width=True):
                    if st.session_state.get('rfm_df') is not None and st.session_state.get('labels') is not None:
                        rfm = st.session_state.rfm_df.copy()
                        rfm['Cluster'] = st.session_state.labels
                        rfm['Segment'] = [f'Cluster {l}' if l != -1 else 'Noise' for l in rfm['Cluster']]
                        csv = rfm.to_csv(index=False)
                        st.download_button("Save CSV", csv, f"{sel_name.replace(' ','_')}.csv", "text/csv")
                    else:
                        st.info("Run a clustering session to download data.")
            with act3:
                if st.button("🗑️ Delete", use_container_width=True):
                    st.session_state.projects = [p for p in st.session_state.projects if p['name']!=sel_name]
                    save_history(st.session_state.projects)
                    st.success(f"Deleted '{sel_name}'")
                    st.rerun()
    else:
        st.info("No projects match your search.")
else:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:48px;text-align:center;border:1px solid #e2e8f0;">
      <div style="font-size:48px;margin-bottom:12px;">🗂️</div>
      <div style="font-size:16px;font-weight:600;color:#1e293b;margin-bottom:6px;">No saved projects</div>
      <div style="font-size:13px;color:#64748b;">
        After running clustering and saving, projects appear here.
      </div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─── Export Options ───────────────────────────────────────────────────────────
st.markdown("#### Export Options")

col_sel, col_fmt = st.columns(2)
with col_sel:
    st.markdown("**Select data to export:**")
    exp_segmentation = st.checkbox("Customer Segmentation", value=True)
    exp_rfm          = st.checkbox("RFM Scores", value=True)
    exp_clv          = st.checkbox("CLV Results", value=False)
    exp_stats        = st.checkbox("Cluster Statistics", value=True)
    exp_ahp          = st.checkbox("AHP Weights", value=False)

with col_fmt:
    st.markdown("**Export format:**")
    fmt = st.radio("Format", ["CSV (.csv)", "Excel (.xlsx)"], label_visibility="collapsed")

    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("📥 Download Export", use_container_width=True):
        if st.session_state.get('rfm_df') is None:
            st.warning("No data to export. Please run clustering first.")
        else:
            rfm   = st.session_state.rfm_df.copy()
            labels = st.session_state.get('labels')
            weights = st.session_state.get('ahp_weights', [0.637, 0.261, 0.102])
            summary = pd.DataFrame(st.session_state.get('cluster_summary', []))

            if labels is not None:
                rfm['Cluster'] = labels
                rfm['Segment'] = [f'Cluster {l}' if l != -1 else 'Noise' for l in labels]

            if 'xlsx' in fmt:
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    if exp_segmentation and labels is not None:
                        rfm[['CustomerID','Cluster','Segment']].to_excel(writer, sheet_name='Segmentation', index=False)
                    if exp_rfm:
                        rfm[['CustomerID','Recency','Frequency','Monetary']].to_excel(writer, sheet_name='RFM', index=False)
                    if exp_stats and not summary.empty:
                        summary.to_excel(writer, sheet_name='Cluster Stats', index=False)
                    if exp_ahp:
                        w_df = pd.DataFrame({'Criterion':['Recency','Frequency','Monetary'],'Weight':weights})
                        w_df.to_excel(writer, sheet_name='AHP Weights', index=False)
                buffer.seek(0)
                st.download_button("💾 Save Excel", buffer, "clusterviz_export.xlsx",
                                   "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            else:
                parts = []
                if exp_segmentation and labels is not None:
                    parts.append(("# Customer Segmentation\n", rfm[['CustomerID','Cluster','Segment']]))
                if exp_rfm:
                    parts.append(("# RFM Scores\n", rfm[['CustomerID','Recency','Frequency','Monetary']]))
                if exp_stats and not summary.empty:
                    parts.append(("# Cluster Statistics\n", summary))
                combined = ""
                for header, df_part in parts:
                    combined += header + df_part.to_csv(index=False) + "\n"
                st.download_button("💾 Save CSV", combined, "clusterviz_export.csv", "text/csv")

