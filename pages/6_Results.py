import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Results — ClusterHub", page_icon="📋", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('results')

st.markdown("## 📋 Clustering Results")

if st.session_state.get('labels') is None:
    st.warning("⚠️ No clustering results yet. Please run clustering first.")
    if st.button("Go to Clustering"):
        st.switch_page('pages/5_Clustering.py')
    st.stop()

labels     = np.array(st.session_state.labels)
pca        = np.array(st.session_state.pca_coords)
sil        = st.session_state.silhouette_score   or 0.0
db         = st.session_state.davies_bouldin      or 0.0
ch         = st.session_state.get('calinski_harabasz') or 0.0
summary    = pd.DataFrame(st.session_state.cluster_summary)
rfm        = st.session_state.rfm_df.copy()
algo       = st.session_state.get('algo_used', 'BIRCH')
n_clusters = len(summary)
ahp_w      = st.session_state.get('ahp_weights', [1/3, 1/3, 1/3])
w_r, w_f, w_m = float(ahp_w[0]), float(ahp_w[1]), float(ahp_w[2])

# ── Recompute cluster-level CLV using AHP weights ─────────────────────────────
# Normalize avg R/F/M across clusters (min-max), then apply the weighted formula
def _minmax_series(s):
    lo, hi = s.min(), s.max()
    return (s - lo) / (hi - lo) if hi != lo else pd.Series(0.0, index=s.index)

summary = summary.copy()
summary['R_norm_clv'] = _minmax_series(summary['Avg_Recency'])
summary['F_norm_clv'] = _minmax_series(summary['Avg_Frequency'])
summary['M_norm_clv'] = _minmax_series(summary['Avg_Monetary'])
# Recency is negative (lower recency days = more recent = better)
summary['Avg_CLV'] = (
    - w_r * summary['R_norm_clv']
    + w_f * summary['F_norm_clv']
    + w_m * summary['M_norm_clv']
)

# ── Per-customer CLV using same formula (individual-level normalization) ───────
rfm = rfm.reset_index(drop=True)
rfm['Cluster'] = labels
rfm['Segment'] = [f'Cluster {l}' if l != -1 else 'Noise' for l in labels]

def _minmax(col):
    lo, hi = col.min(), col.max()
    return (col - lo) / (hi - lo + 1e-12)

rfm['R_norm_clv'] = _minmax(rfm['Recency'])
rfm['F_norm_clv'] = _minmax(rfm['Frequency'])
rfm['M_norm_clv'] = _minmax(rfm['Monetary'])
rfm['CLV'] = (
    - w_r * rfm['R_norm_clv']
    + w_f * rfm['F_norm_clv']
    + w_m * rfm['M_norm_clv']
).round(4)

# ─── Header row ───────────────────────────────────────────────────────────────
col_title, col_btns = st.columns([2, 1])
with col_title:
    st.markdown(
        f"**Algorithm:** {algo} &nbsp;·&nbsp; "
        f"**Clusters:** {n_clusters} &nbsp;·&nbsp; "
        f"**Customers:** {len(rfm):,}"
    )
with col_btns:
    ca, cb = st.columns(2)
    with ca:
        if st.button("💾 Save Result", use_container_width=True):
            project = {
                'name': f'Clustering #{len(st.session_state.projects)+1}',
                'date': pd.Timestamp.now().strftime('%b %d, %Y'),
                'algorithm': algo, 'k': n_clusters,
                'customers': len(rfm),
                'silhouette': round(sil, 4),
                'status': 'Completed',
            }
            if project not in st.session_state.projects:
                st.session_state.projects.append(project)
            st.success("Saved!")
    with cb:
        export_cols = ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'Cluster', 'Segment', 'CLV']
        export_cols = [c for c in export_cols if c in rfm.columns]
        csv = rfm[export_cols].to_csv(index=False)
        st.download_button("📥 Export CSV", csv, "clustering_results.csv",
                           "text/csv", use_container_width=True)

# ─── 5 metric cards ───────────────────────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.metric("Total Customers", f"{len(rfm):,}")
with m2:
    st.metric("Clusters", str(n_clusters), algo)
with m3:
    q = "Excellent ✓" if sil > 0.7 else ("Good ✓" if sil > 0.5 else ("Fair" if sil > 0.25 else "Poor ✗"))
    st.metric("Silhouette Score", f"{sil:.4f}", q)
with m4:
    dq = "Good ✓" if db < 1.0 else ("Fair" if db < 2.0 else "Poor ✗")
    st.metric("Davies-Bouldin", f"{db:.4f}", dq + " (↓ better)")
with m5:
    cq = "Good ✓" if ch > 100 else ("Fair" if ch > 50 else "Weak ✗")
    st.metric("Calinski-Harabasz", f"{ch:.1f}", cq + " (↑ better)")

# ─── PCA chart + Evaluation metrics ───────────────────────────────────────────
st.markdown("---")
col_chart, col_eval = st.columns([2, 1])

with col_chart:
    st.markdown("#### PCA 2D Cluster Visualization")
    fig = make_pca_scatter(pca, labels, height=420)
    st.plotly_chart(fig, use_container_width=True)

with col_eval:
    st.markdown("#### Evaluation Metrics")

    def _eval_card(label, value_str, pct, color, note):
        pct = max(0, min(100, pct))
        return f"""
        <div style="background:white;border-radius:12px;padding:16px 18px;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
            <span style="font-size:12px;color:#64748b;font-weight:500;">{label}</span>
            <span style="font-size:22px;font-weight:800;color:{color};">{value_str}</span>
          </div>
          <div style="background:#f1f5f9;border-radius:20px;height:7px;overflow:hidden;">
            <div style="width:{pct:.0f}%;height:100%;background:{color};border-radius:20px;"></div>
          </div>
          <div style="font-size:11px;color:#94a3b8;margin-top:5px;">{note}</div>
        </div>"""

    sil_c  = "#10b981" if sil > 0.5 else ("#f59e0b" if sil > 0.25 else "#ef4444")
    sil_lbl = "Excellent — very well separated" if sil > 0.7 else \
              ("Good — clusters are distinct" if sil > 0.5 else \
              ("Fair — some overlap exists" if sil > 0.25 else "Poor — clusters overlap heavily"))

    db_c   = "#10b981" if db < 1.0 else ("#f59e0b" if db < 2.0 else "#ef4444")
    db_pct = max(0, 100 - db * 30)
    db_lbl = "Good separation" if db < 1.0 else ("Moderate separation" if db < 2.0 else "Poor separation")

    ch_c   = "#10b981" if ch > 100 else ("#f59e0b" if ch > 50 else "#ef4444")
    ch_pct = min(100, ch / 5)
    ch_lbl = "Compact & well-separated clusters" if ch > 100 else \
             ("Moderate cluster structure" if ch > 50 else "Weak cluster structure")

    st.markdown(
        _eval_card("Silhouette Score (range: −1 to 1)",
                   f"{sil:.4f}", sil * 100, sil_c, sil_lbl) +
        _eval_card("Davies-Bouldin Index (lower = better)",
                   f"{db:.4f}", db_pct, db_c, db_lbl) +
        _eval_card("Calinski-Harabasz Index (higher = better)",
                   f"{ch:.1f}", ch_pct, ch_c, ch_lbl),
        unsafe_allow_html=True
    )

# ─── Cluster summary cards ─────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Cluster Summary")

summary_sorted = summary.sort_values('Cluster').reset_index(drop=True)
cluster_cols = st.columns(len(summary_sorted))

for i, row in summary_sorted.iterrows():
    with cluster_cols[i]:
        cid = int(row.Cluster)
        bg  = CLUSTER_COLORS[i % len(CLUSTER_COLORS)]
        n_mem = int(row.Customers)
        st.markdown(f"""
        <div style="background:white;border-radius:12px;overflow:hidden;
                    box-shadow:0 2px 10px rgba(0,0,0,0.08);">
          <div style="background:{bg};padding:10px 14px;">
            <div style="color:white;font-size:13px;font-weight:700;">Cluster {cid}</div>
            <div style="color:rgba(255,255,255,0.8);font-size:11px;">{n_mem:,} customers</div>
          </div>
          <div style="padding:12px 14px;">
            <div style="font-size:12px;color:#475569;">
              <div style="display:flex;justify-content:space-between;padding:4px 0;
                          border-bottom:1px solid #f8fafc;">
                <span>Avg Recency</span>
                <strong>{row.Avg_Recency:.0f} days</strong>
              </div>
              <div style="display:flex;justify-content:space-between;padding:4px 0;
                          border-bottom:1px solid #f8fafc;">
                <span>Avg Frequency</span>
                <strong>{row.Avg_Frequency:.1f} orders</strong>
              </div>
              <div style="display:flex;justify-content:space-between;padding:4px 0;
                          border-bottom:1px solid #f8fafc;">
                <span>Avg Monetary</span>
                <strong>Rp {row.Avg_Monetary:,.0f}</strong>
              </div>
              <div style="display:flex;justify-content:space-between;padding:6px 0 2px;
                          margin-top:2px;">
                <span style="color:#3b82f6;font-weight:600;">CLV Score</span>
                <strong style="color:#3b82f6;">{row.Avg_CLV:.4f}</strong>
              </div>
            </div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─── CLV formula note ─────────────────────────────────────────────────────────
st.markdown(
    f"<div style='font-size:11px;color:#94a3b8;margin-top:8px;'>"
    f"CLV Score = −(W_R × R_norm) + (W_F × F_norm) + (W_M × M_norm) &nbsp;|&nbsp; "
    f"AHP Weights: R={w_r:.3f}, F={w_f:.3f}, M={w_m:.3f} &nbsp;|&nbsp; "
    f"R/F/M normalized (min-max) across cluster averages</div>",
    unsafe_allow_html=True
)

# ─── Summary table ─────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Summary Table")
disp_cols = ['Cluster', 'Segment', 'Customers',
             'Avg_Recency', 'Avg_Frequency', 'Avg_Monetary', 'Avg_CLV']
disp_cols = [c for c in disp_cols if c in summary.columns]
disp = summary_sorted[disp_cols].copy()
disp['Avg_Recency']   = disp['Avg_Recency'].round(1).astype(str) + ' days'
disp['Avg_Frequency'] = disp['Avg_Frequency'].round(1)
disp['Avg_Monetary']  = 'Rp ' + disp['Avg_Monetary'].apply(lambda x: f'{x:,.0f}')
disp['Avg_CLV']       = disp['Avg_CLV'].round(4)
disp = disp.rename(columns={
    'Avg_Recency': 'Avg Recency', 'Avg_Frequency': 'Avg Frequency',
    'Avg_Monetary': 'Avg Monetary', 'Avg_CLV': 'CLV Score'
})
st.dataframe(disp, use_container_width=True, hide_index=True)

# ─── Cluster member explorer ───────────────────────────────────────────────────
st.markdown("---")
st.markdown("#### Cluster Members")
st.caption(
    f"Sorted by CLV score (highest first). "
)

valid_cluster_ids = sorted([c for c in summary['Cluster'].unique() if c != -1])
tab_labels = []
for cid in valid_cluster_ids:
    n_mem = int((labels == cid).sum())
    tab_labels.append(f"Cluster {cid}  ·  {n_mem:,} members")

has_noise = -1 in labels
if has_noise:
    valid_cluster_ids.append(-1)
    tab_labels.append(f"Noise  ·  {int((labels == -1).sum())} points")

tabs = st.tabs(tab_labels)
member_cols = [c for c in ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'CLV'] if c in rfm.columns]

for tab, cid in zip(tabs, valid_cluster_ids):
    with tab:
        members = rfm[rfm['Cluster'] == cid][member_cols].copy()
        members = members.sort_values('CLV', ascending=False).reset_index(drop=True)
        members.index = members.index + 1

        # Format for display
        members_disp = members.copy()
        if 'Recency' in members_disp.columns:
            members_disp['Recency'] = members_disp['Recency'].round(0).astype(int).astype(str) + ' days'
        if 'Frequency' in members_disp.columns:
            members_disp['Frequency'] = members_disp['Frequency'].round(0).astype(int)
        if 'Monetary' in members_disp.columns:
            members_disp['Monetary'] = members_disp['Monetary'].apply(lambda x: f'Rp {x:,.0f}')
        if 'CLV' in members_disp.columns:
            members_disp = members_disp.rename(columns={'CLV': 'CLV Score'})

        col_info, col_tbl = st.columns([1, 3])
        with col_info:
            if cid != -1:
                row = summary[summary['Cluster'] == cid].iloc[0]
                clv_avg_ind = rfm[rfm['Cluster'] == cid]['CLV'].mean()
                st.markdown(f"""
                <div style="background:white;border-radius:12px;padding:16px;
                            box-shadow:0 2px 8px rgba(0,0,0,0.07);">
                  <div style="font-size:11px;color:#64748b;margin-bottom:4px;">Cluster CLV Score</div>
                  <div style="font-size:28px;font-weight:800;color:#3b82f6;margin-bottom:10px;">
                    {row.Avg_CLV:.4f}
                  </div>
                  <div style="font-size:12px;color:#475569;">
                    <div style="display:flex;justify-content:space-between;padding:3px 0;">
                      <span>Members</span><strong>{int(row.Customers):,}</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:3px 0;">
                      <span>Avg Recency</span><strong>{row.Avg_Recency:.0f} days</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:3px 0;">
                      <span>Avg Frequency</span><strong>{row.Avg_Frequency:.1f} orders</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:3px 0;">
                      <span>Avg Monetary</span><strong>Rp {row.Avg_Monetary:,.0f}</strong>
                    </div>
                    <div style="display:flex;justify-content:space-between;padding:3px 0;
                                border-top:1px solid #f1f5f9;margin-top:4px;padding-top:6px;">
                      <span style="color:#64748b;">Avg Member CLV</span>
                      <strong style="color:#3b82f6;">{clv_avg_ind:.4f}</strong>
                    </div>
                  </div>
                </div>
                """, unsafe_allow_html=True)
        with col_tbl:
            st.dataframe(members_disp, use_container_width=True)
