import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="AHP Weighting — ClusterViz", page_icon="⚖️", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('data')

st.markdown("## ⚖️ AHP Pairwise Comparison")
st.markdown("Set RFM criteria weights using the Analytic Hierarchy Process.")

criteria = ['Recency', 'Frequency', 'Monetary']
colors   = ['#3b82f6', '#0d9488', '#f59e0b']

# Saaty scale labels
SAATY = {1:"Equal",2:"Weak",3:"Moderate",4:"Moderate–Strong",5:"Strong",
         6:"Strong–Very Strong",7:"Very Strong",8:"Very–Extreme",9:"Extreme"}

col_left, col_right = st.columns([1.5, 1])

with col_left:
    st.markdown("#### Pairwise Comparisons")
    st.markdown(
        "<div style='font-size:12px;color:#64748b;margin-bottom:14px;'>"
        "For each pair, choose which criterion is more important, then set the intensity (Saaty 1–9)."
        "</div>", unsafe_allow_html=True
    )

    # ── 3 pair cards ──────────────────────────────────────────────────────────
    pairs = [(0,1,"Recency","Frequency"), (0,2,"Recency","Monetary"), (1,2,"Frequency","Monetary")]

    # Load existing matrix to derive saved direction + intensity
    saved = st.session_state.get('ahp_matrix', [[1,3,5],[1/3,1,3],[1/5,1/3,1]])

    def val_to_dir_int(v):
        """Convert matrix upper-triangle value to (direction_idx, intensity)."""
        if abs(v - 1.0) < 1e-9:
            return 1, 1          # Equal
        elif v > 1:
            return 0, round(v)   # First criterion
        else:
            return 2, round(1/v) # Second criterion

    new_vals = {}  # (i,j) → matrix value

    for i, j, a, b in pairs:
        v0 = saved[i][j]
        dir_idx0, int0 = val_to_dir_int(v0)

        st.markdown(f"""
        <div style="background:white;border-radius:12px;padding:18px 20px;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);margin-bottom:12px;">
          <div style="font-size:13px;font-weight:700;color:#1e293b;margin-bottom:12px;">
            {a} &nbsp;vs&nbsp; {b}
          </div>
        """, unsafe_allow_html=True)

        direction = st.radio(
            f"Which is more important? ({a} vs {b})",
            [f"✦ {a}", "Equal (1:1)", f"✦ {b}"],
            index=dir_idx0,
            horizontal=True,
            key=f"dir_{i}_{j}",
            label_visibility="collapsed"
        )

        if "Equal" in direction:
            intensity = 1
            st.markdown(
                "<div style='font-size:12px;color:#64748b;margin-top:8px;padding:6px 0;'>"
                "Both criteria carry equal weight.</div>",
                unsafe_allow_html=True
            )
            matrix_val = 1.0
        else:
            intensity = st.slider(
                f"Intensity ({a} vs {b})",
                min_value=1, max_value=9,
                value=int0 if int0 >= 1 else 1,
                key=f"int_{i}_{j}",
                label_visibility="collapsed"
            )
            dominant = a if direction.endswith(a) else b
            meaning  = SAATY.get(intensity, "")
            st.markdown(
                f"<div style='font-size:12px;color:#3b82f6;margin-top:4px;'>"
                f"<strong>{dominant}</strong> is <strong>{meaning.lower()}</strong> more important "
                f"({intensity}× on Saaty scale)</div>",
                unsafe_allow_html=True
            )
            matrix_val = float(intensity) if direction.endswith(a) else 1.0 / intensity

        st.markdown("</div>", unsafe_allow_html=True)
        new_vals[(i, j)] = matrix_val

    # ── Build full 3×3 matrix ─────────────────────────────────────────────────
    matrix = [[1.0]*3 for _ in range(3)]
    for (i, j), v in new_vals.items():
        matrix[i][j] = v
        matrix[j][i] = 1.0 / v

    st.session_state.ahp_matrix = matrix
    weights, cr, lambda_max = calculate_ahp(matrix)
    st.session_state.ahp_weights = weights
    st.session_state.ahp_cr      = cr

    # ── Full matrix preview ───────────────────────────────────────────────────
    st.markdown("#### Resulting Pairwise Matrix")

    def fmt(v):
        if abs(v - round(v)) < 0.01:
            return str(int(round(v)))
        # Show as fraction if reciprocal
        for d in range(2, 10):
            if abs(v - 1/d) < 0.01:
                return f"1/{d}"
        return f"{v:.3f}"

    header = "<tr><th style='padding:8px 12px;background:#f8fafc;'></th>" + \
             "".join(f"<th style='padding:8px 12px;background:#f8fafc;color:#374151;'>{c}</th>" for c in criteria) + "</tr>"
    rows_html = ""
    for ri, row in enumerate(matrix):
        cells = f"<td style='padding:8px 12px;font-weight:600;color:#374151;background:#f8fafc;'>{criteria[ri]}</td>"
        for ci, v in enumerate(row):
            if ri == ci:
                bg, fw = "#e0f2fe", "700"
            elif ci > ri:
                bg, fw = "#fef9ec", "600"
            else:
                bg, fw = "#f9fafb", "400"
            clr = "#1e293b" if ri != ci else "#0369a1"
            cells += f"<td style='padding:8px 12px;text-align:center;background:{bg};font-weight:{fw};color:{clr};'>{fmt(v)}</td>"
        rows_html += f"<tr>{cells}</tr>"

    st.markdown(
        f"<div style='background:white;border-radius:12px;overflow:hidden;"
        f"box-shadow:0 2px 10px rgba(0,0,0,0.07);'>"
        f"<table style='width:100%;border-collapse:collapse;'>{header}{rows_html}</table>"
        f"<div style='font-size:11px;color:#94a3b8;padding:8px 14px;'>"
        f"Blue diagonal = 1 (self) · Yellow = upper triangle (your input) · Grey = auto-reciprocal</div></div>",
        unsafe_allow_html=True
    )

    with st.expander("📖 Saaty Scale Reference"):
        ref = pd.DataFrame({'Intensity': list(SAATY.keys()), 'Meaning': list(SAATY.values())})
        st.dataframe(ref, hide_index=True, use_container_width=True)

with col_right:
    weights = st.session_state.get('ahp_weights', [0.637, 0.261, 0.102])
    cr      = st.session_state.get('ahp_cr', 0.037)

    cr_ok    = cr < 0.1
    cr_color = "#10b981" if cr_ok else "#ef4444"
    cr_label = "✅ Consistent" if cr_ok else "❌ Inconsistent — Revise"

    st.markdown(f"""
    <div style="background:white;border-radius:12px;padding:20px;
                box-shadow:0 2px 10px rgba(0,0,0,0.07);text-align:center;margin-bottom:14px;">
      <div style="font-size:12px;color:#64748b;margin-bottom:6px;">Consistency Ratio (CR)</div>
      <div style="font-size:44px;font-weight:800;color:{cr_color};line-height:1;">{cr:.4f}</div>
      <div style="margin-top:10px;display:inline-block;background:{cr_color}20;color:{cr_color};
                  padding:5px 14px;border-radius:20px;font-size:12px;font-weight:600;">{cr_label}</div>
      <div style="font-size:11px;color:#94a3b8;margin-top:10px;">CR &lt; 0.1 is acceptable</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("#### Criteria Weights")
    for i, (crit, w) in enumerate(zip(criteria, weights)):
        pct = w * 100
        st.markdown(f"""
        <div style="margin-bottom:12px;">
          <div style="display:flex;justify-content:space-between;margin-bottom:5px;font-size:13px;font-weight:500;">
            <span style="display:flex;align-items:center;gap:6px;">
              <span style="width:8px;height:8px;border-radius:50%;background:{colors[i]};display:inline-block;"></span>
              {crit}
            </span>
            <strong style="color:{colors[i]};">{pct:.1f}%</strong>
          </div>
          <div style="background:#f1f5f9;border-radius:20px;height:10px;overflow:hidden;">
            <div style="width:{pct:.1f}%;height:100%;background:{colors[i]};border-radius:20px;"></div>
          </div>
        </div>
        """, unsafe_allow_html=True)

    fig = make_weight_bar(criteria[::-1], weights[::-1], colors[::-1])
    st.plotly_chart(fig, use_container_width=True)

    fig2 = make_donut(criteria, weights, colors)
    st.plotly_chart(fig2, use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)
    if cr_ok:
        if st.button("▶️ Proceed to Clustering", use_container_width=True):
            st.switch_page('pages/5_Clustering.py')
    else:
        st.error("Adjust comparisons until CR < 0.1 before proceeding.")
