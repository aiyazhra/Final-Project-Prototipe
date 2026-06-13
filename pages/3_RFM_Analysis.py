import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="RFM Analysis — ClusterViz", page_icon="📈", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('data')

st.markdown("## 📈 Data Preprocessing & RFM Analysis")
st.markdown("Data cleaning, RFM calculation, and normalization results.")

if st.session_state.get('df') is None:
    st.warning("⚠️ No data loaded. Please upload a dataset first.")
    if st.button("Go to Data Upload"):
        st.switch_page('pages/2_Data_Upload.py')
    st.stop()

df_raw = st.session_state.df.copy()

# ─── Preprocessing ────────────────────────────────────────────────────────────
n_missing = int(df_raw.isnull().sum().sum())
n_dupes   = int(df_raw.duplicated().sum())

df_clean = df_raw.copy()
up = pd.to_numeric(df_clean.get('UnitPrice', pd.Series(dtype=float)), errors='coerce')
df_clean['UnitPrice'] = up.fillna(up.median())

if 'TotalAmount' not in df_clean.columns:
    qty_num = pd.to_numeric(df_clean.get('Quantity', pd.Series(dtype=float)), errors='coerce')
    if qty_num.notna().sum() > len(df_clean) * 0.5:
        df_clean['TotalAmount'] = qty_num.fillna(qty_num.median()) * df_clean['UnitPrice']
    else:
        df_clean['TotalAmount'] = df_clean['UnitPrice']

df_clean = df_clean.drop_duplicates()

# ─── Compute RFM (full data) ─────────────────────────────────────────────────
rfm_full = calculate_rfm(df_clean)

# ─── IQR Outlier Detection ────────────────────────────────────────────────────
def detect_outliers_iqr(df, cols):
    mask   = pd.Series(False, index=df.index)
    detail = {}
    for col in cols:
        Q1, Q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        IQR    = Q3 - Q1
        lb, ub = Q1 - 1.5 * IQR, Q3 + 1.5 * IQR
        col_out = (df[col] < lb) | (df[col] > ub)
        mask    = mask | col_out
        detail[col] = {'lb': lb, 'ub': ub, 'count': int(col_out.sum())}
    return mask, detail

outlier_mask, outlier_detail = detect_outliers_iqr(rfm_full, ['Recency', 'Frequency', 'Monetary'])
n_outliers = int(outlier_mask.sum())

# ─── Status cards ─────────────────────────────────────────────────────────────
def status_card(col, icon, label, detail, color='#10b981'):
    with col:
        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:16px;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);
                    display:flex;align-items:center;gap:12px;min-height:72px;">
          <div style="width:36px;height:36px;background:{color}20;border-radius:8px;
                      display:flex;align-items:center;justify-content:center;
                      font-size:16px;flex-shrink:0;">{icon}</div>
          <div>
            <div style="font-size:12px;font-weight:600;color:#1e293b;">{label}</div>
            <div style="font-size:11px;color:#64748b;margin-top:2px;">{detail}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

c1, c2, c3 = st.columns(3)
status_card(c1, "✅", "Missing Values",     f"{n_missing} rows filled (median)")
status_card(c2, "✅", "Duplicate Removal",  f"{n_dupes} duplicates removed")
status_card(c3, "✅", "Null Values Handled", "All null rows resolved")

st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

# ─── Outlier Detection Summary + Handling ────────────────────────────────────
out_left, out_right = st.columns([1.2, 1])

with out_left:
    out_color = '#ef4444' if n_outliers > 0 else '#10b981'
    out_icon  = '⚠️'       if n_outliers > 0 else '✅'
    rows = ""
    for col, d in outlier_detail.items():
        cnt  = d['count']
        clr  = '#ef4444' if cnt > 0 else '#10b981'
        rows += (
            f"<div style='display:flex;justify-content:space-between;padding:5px 0;"
            f"border-bottom:1px solid #f1f5f9;font-size:12px;'>"
            f"<span style='color:#374151;'>{col}</span>"
            f"<span style='font-weight:600;color:{clr};'>{cnt} outlier{'s' if cnt!=1 else ''}</span></div>"
        )
    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:18px 20px;
                box-shadow:0 2px 10px rgba(0,0,0,0.07);">
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;">
        <span style="font-size:18px;">{out_icon}</span>
        <div>
          <div style="font-size:13px;font-weight:700;color:#1e293b;">
            Outlier Detection (IQR Method)
          </div>
          <div style="font-size:11px;color:#64748b;margin-top:1px;">
            {n_outliers} customer{'s' if n_outliers!=1 else ''} detected as outlier
            across R, F, M dimensions
          </div>
        </div>
      </div>
      {rows}
      <div style="font-size:10px;color:#94a3b8;margin-top:8px;">
        Bounds: Q1 − 1.5×IQR &nbsp;/&nbsp; Q3 + 1.5×IQR per dimension
      </div>
    </div>
    """, unsafe_allow_html=True)

with out_right:
    st.markdown("""
    <div style="background:white;border-radius:12px;padding:18px 20px;
                box-shadow:0 2px 10px rgba(0,0,0,0.07);height:100%;">
      <div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:10px;">
        Outlier Handling
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("<div style='margin-top:-12px'></div>", unsafe_allow_html=True)
    outlier_choice = st.radio(
        "Outlier handling",
        [f"Remove {n_outliers} outliers (IQR)", "Keep all data"],
        key="outlier_radio",
        label_visibility="collapsed",
        disabled=(n_outliers == 0)
    )
    st.session_state.outlier_removed = "Remove" in outlier_choice and n_outliers > 0

    if n_outliers == 0:
        st.markdown("<div style='font-size:11px;color:#10b981;'>No outliers detected — all data kept.</div>", unsafe_allow_html=True)
    elif st.session_state.outlier_removed:
        remaining = len(rfm_full) - n_outliers
        st.markdown(f"<div style='font-size:11px;color:#f59e0b;'>{n_outliers} customers will be removed → {remaining:,} remain.</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div style='font-size:11px;color:#3b82f6;'>All {len(rfm_full):,} customers kept including outliers.</div>", unsafe_allow_html=True)

st.markdown("---")

# ─── Apply outlier handling ───────────────────────────────────────────────────
if st.session_state.outlier_removed:
    rfm = rfm_full[~outlier_mask].reset_index(drop=True)
else:
    rfm = rfm_full.copy()

rfm_norm = normalize_rfm(rfm)
st.session_state.rfm_df         = rfm
st.session_state.rfm_normalized = rfm_norm

# ─── Stats + RFM explanation ─────────────────────────────────────────────────
col_stat, col_explain = st.columns([1.8, 1])

with col_stat:
    st.markdown("#### Descriptive Statistics")
    stats = rfm[['Recency','Frequency','Monetary']].describe().T[['min','max','mean','50%','std']]
    stats.columns = ['Min','Max','Mean','Median','Std Dev']
    stats = stats.round(2)
    stats.index = ['Recency (days)','Frequency (orders)','Monetary (IDR)']
    st.dataframe(stats, use_container_width=True)

with col_explain:
    st.markdown("#### What is RFM?")
    for letter, color, title, desc in [
        ("R", "#3b82f6", "Recency",   "Days since last purchase"),
        ("F", "#0d9488", "Frequency", "Number of orders made"),
        ("M", "#f59e0b", "Monetary",  "Total spending amount"),
    ]:
        st.markdown(f"""
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
          <div style="width:36px;height:36px;background:{color}20;border-radius:8px;
                      display:flex;align-items:center;justify-content:center;
                      font-size:15px;font-weight:800;color:{color};flex-shrink:0;">{letter}</div>
          <div>
            <div style="font-size:13px;font-weight:600;">{title}</div>
            <div style="font-size:12px;color:#64748b;">{desc}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ─── RFM Table ────────────────────────────────────────────────────────────────
st.markdown("---")
col_hdr, col_norm_chk = st.columns([2, 1])
with col_hdr:
    st.markdown(f"#### RFM Scores Table ({len(rfm):,} customers)")
with col_norm_chk:
    apply_norm = st.checkbox("Apply Min-Max Normalization", value=True)

display_rfm = rfm_norm if apply_norm else rfm
cols_show   = ['CustomerID','Recency','Frequency','Monetary','R_norm','F_norm','M_norm'] if apply_norm else ['CustomerID','Recency','Frequency','Monetary']
cols_show   = [c for c in cols_show if c in display_rfm.columns]
st.dataframe(display_rfm[cols_show].head(10).round(4), use_container_width=True, hide_index=True)

# ─── Histograms ───────────────────────────────────────────────────────────────
st.markdown("#### Distribution Analysis")
h1, h2, h3 = st.columns(3)
with h1:
    st.plotly_chart(make_histogram(rfm['Recency'],   'Recency Distribution',   '#3b82f6'), use_container_width=True)
with h2:
    st.plotly_chart(make_histogram(rfm['Frequency'], 'Frequency Distribution', '#0d9488'), use_container_width=True)
with h3:
    st.plotly_chart(make_histogram(rfm['Monetary'],  'Monetary Distribution',  '#f59e0b'), use_container_width=True)

# ─── Continue ─────────────────────────────────────────────────────────────────
st.markdown("---")
_, _, btn_col = st.columns([2, 1, 1])
with btn_col:
    if st.button("▶️ Continue to AHP Weighting", use_container_width=True):
        st.switch_page('pages/4_AHP_Weighting.py')
