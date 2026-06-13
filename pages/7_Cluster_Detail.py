import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Cluster Detail — ClusterViz", page_icon="🔍", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('results')

st.markdown("## 🔍 Cluster Detail")

if st.session_state.get('labels') is None:
    st.warning("⚠️ No clustering results yet.")
    if st.button("Go to Results"):
        st.switch_page('pages/6_Results.py')
    st.stop()

labels   = np.array(st.session_state.labels)
rfm      = st.session_state.rfm_df.copy()
rfm['Cluster'] = labels
summary  = pd.DataFrame(st.session_state.cluster_summary)
k        = st.session_state.k

# ─── Cluster selector ─────────────────────────────────────────────────────────
col_hdr, col_sel = st.columns([2, 1])
with col_sel:
    cluster_ids = sorted(summary['Cluster'].unique().tolist())
    cluster_options = [f"Cluster {int(c)}" for c in cluster_ids]
    sel_idx = st.selectbox("Select Cluster", range(len(cluster_options)),
                           format_func=lambda i: cluster_options[i])
    sel_cluster = cluster_ids[sel_idx]

row = summary[summary['Cluster'] == sel_cluster].iloc[0]
color = CLUSTER_COLORS[int(sel_idx) % len(CLUSTER_COLORS)]

with col_hdr:
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{color},{color}bb);border-radius:12px;
                padding:16px 22px;color:white;display:flex;align-items:center;justify-content:space-between;">
      <div>
        <div style="font-size:11px;opacity:0.8;text-transform:uppercase;letter-spacing:1px;">Selected Cluster</div>
        <div style="font-size:20px;font-weight:800;">Cluster {int(sel_cluster)}</div>
      </div>
      <div style="text-align:right;">
        <div style="font-size:36px;font-weight:800;line-height:1;">{int(row.Customers):,}</div>
        <div style="font-size:12px;opacity:0.8;">Total Customers</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ─── Metric cards ─────────────────────────────────────────────────────────────
c1, c2, c3, c4 = st.columns(4)
with c1: st.metric("Avg Recency", f"{row.Avg_Recency:.1f} days", "Since last purchase")
with c2: st.metric("Avg Frequency", f"{row.Avg_Frequency:.1f} orders", "Number of orders")
with c3: st.metric("Avg Monetary", f"Rp {row.Avg_Monetary:,.0f}", "Total spending")
with c4: st.metric("CLV Score", f"{row.Avg_CLV:.4f}", "Lifetime value score")

# ─── Main content ─────────────────────────────────────────────────────────────
col_table, col_right = st.columns([1.6, 1])

with col_table:
    st.markdown("#### Customer List")
    cluster_df = rfm[rfm['Cluster'] == sel_cluster].copy()
    if 'rfm_normalized' in st.session_state and st.session_state.rfm_normalized is not None:
        norm = st.session_state.rfm_normalized[['CustomerID','R_norm','F_norm','M_norm']]
        cluster_df = cluster_df.merge(norm, on='CustomerID', how='left')

    # Search
    search = st.text_input("🔍 Search customer ID", placeholder="e.g. C1001")
    if search:
        cluster_df = cluster_df[cluster_df['CustomerID'].str.contains(search, case=False)]

    display_cols = ['CustomerID','Recency','Frequency','Monetary']
    if 'R_norm' in cluster_df.columns:
        display_cols += ['R_norm','F_norm','M_norm']

    show_df = cluster_df[display_cols].copy()
    show_df = show_df.rename(columns={'R_norm':'R(norm)','F_norm':'F(norm)','M_norm':'M(norm)'})
    for col_name in ['R(norm)','F(norm)','M(norm)']:
        if col_name in show_df.columns:
            show_df[col_name] = show_df[col_name].round(4)

    st.dataframe(show_df.head(50), use_container_width=True, hide_index=True)
    st.caption(f"Showing up to 50 of {len(cluster_df):,} customers in this cluster")

    # Export this cluster
    csv_data = cluster_df[display_cols].to_csv(index=False)
    st.download_button(
        f"📥 Export Cluster {int(sel_cluster)} CSV",
        csv_data,
        f"cluster_{int(sel_cluster)}_customers.csv",
        "text/csv"
    )

with col_right:
    # Radar chart
    st.markdown("#### Cluster Profile (Radar)")
    cats   = ['Recency\n(inv)', 'Frequency', 'Monetary', 'CLV', 'Cohesion']
    r_inv  = 1 - row.get('Avg_R_norm', 0.5)
    vals   = [
        float(row.get('Avg_R_norm', 0.5)),
        float(row.get('Avg_F_norm', 0.5)),
        float(row.get('Avg_M_norm', 0.5)),
        float(min(row.Avg_CLV / (rfm['Monetary'].max() * 5 + 1), 1.0)),
        float(1 - row.Avg_Recency / (rfm['Recency'].max() + 1)),
    ]
    fig = make_radar(['Recency', 'Frequency', 'Monetary', 'CLV', 'Cohesion'], vals, color=color)
    st.plotly_chart(fig, use_container_width=True)

    # Centroid
    st.markdown("#### Centroid (Normalized)")
    r_n = float(row.get('Avg_R_norm', 0))
    f_n = float(row.get('Avg_F_norm', 0))
    m_n = float(row.get('Avg_M_norm', 0))
    st.markdown(f"""
    <div style="background:#f8fafc;border-radius:8px;padding:14px;font-family:monospace;font-size:13px;
                border:1px solid #e2e8f0;">
      [R: {r_n:.4f},&nbsp; F: {f_n:.4f},&nbsp; M: {m_n:.4f}]
    </div>
    """, unsafe_allow_html=True)
    st.caption("Min-Max normalized + AHP-weighted centroid")

    # Cluster label
    st.markdown("#### Cluster")
    st.markdown(f"""
    <div style="background:{color}22;color:{color};border-radius:8px;padding:12px 16px;
                font-size:15px;font-weight:700;text-align:center;margin-bottom:12px;">
      Cluster {int(sel_cluster)}
    </div>
    """, unsafe_allow_html=True)
    st.info("Explore the R/F/M profile above to determine the best strategy for this cluster.")

    if st.button("← Back to All Results", use_container_width=True):
        st.switch_page('pages/6_Results.py')

