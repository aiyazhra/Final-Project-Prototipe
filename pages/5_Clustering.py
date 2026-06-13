import streamlit as st
import pandas as pd
import numpy as np
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Clustering — ClusterHub", page_icon="🔵", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('cluster')

st.markdown("## 🔵 Clustering Parameters")
st.markdown("Choose an algorithm, configure its parameters, then run clustering.")

if st.session_state.get('rfm_normalized') is None:
    st.warning("⚠️ RFM data not computed yet. Please complete RFM Analysis first.")
    if st.button("Go to RFM Analysis"):
        st.switch_page('pages/3_RFM_Analysis.py')
    st.stop()

rfm_norm = st.session_state.rfm_normalized
weights  = st.session_state.ahp_weights
k_range  = list(range(2, 9))

col_params, col_right = st.columns([1.4, 1])

# ── Algorithm recommendation (cached per rfm hash) ────────────────────────────
rfm_hash = str(len(rfm_norm)) + str(round(float(rfm_norm['R_norm'].mean()), 4))
if st.session_state.get('_algo_rec_hash') != rfm_hash:
    with st.spinner("Evaluating algorithms…"):
        rec = compute_algo_recommendations(rfm_norm, weights)
        st.session_state['_algo_recs']     = rec
        st.session_state['_algo_rec_hash'] = rfm_hash
algo_recs = st.session_state.get('_algo_recs', [])
best_algo = max(algo_recs, key=lambda r: r['sil'])['algo'] if algo_recs else 'BIRCH'

with col_params:
    st.markdown("#### Algorithm & Parameters")

    ALGOS = ['K-Means', 'DBSCAN', 'BIRCH', 'Spectral Clustering', 'GMM']
    algo_key = st.selectbox("Clustering Algorithm", ALGOS,
                            index=ALGOS.index('BIRCH'), key='algo_select')

    if algo_key == 'K-Means':
        k = st.slider("Number of Clusters (K)", 2, 8,
                      st.session_state.get('k', 4), key='k_km')
        st.session_state.k = k
        st.markdown("#### SSE Elbow Method")
        from sklearn.cluster import KMeans as _KM
        X_raw = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values
        sse_vals = [_KM(n_clusters=ki, random_state=42).fit(X_raw).inertia_
                    for ki in k_range]
        fig_sse = make_sse_chart(k_range, sse_vals)
        fig_sse.add_vline(x=k, line_dash='dash', line_color='#ef4444',
                          annotation_text=f'K={k}', annotation_position='top right')
        st.plotly_chart(fig_sse, use_container_width=True)
        run_params = dict(algorithm='K-Means', k=k, threshold=0.5)

    elif algo_key == 'DBSCAN':
        min_pts = st.slider("MinPts (min. samples)", 2, 20, 6, key='dbscan_minpts',
                            help="Rule of thumb: 2 × number of features = 6")
        st.markdown("#### KNN Distance Plot")
        st.caption("Elbow of the curve (sorted ascending) suggests a good eps value. Uses raw R/F/M.")
        fig_knn, suggested_eps = make_knn_distance_chart(rfm_norm, weights, min_pts)
        st.plotly_chart(fig_knn, use_container_width=True)
        _step = max(0.001, round(suggested_eps / 100, 4))
        _max  = max(suggested_eps * 10, 1000.0)
        eps = st.number_input("Eps (neighborhood radius)", min_value=0.0001,
                              max_value=float(_max), value=float(suggested_eps),
                              step=float(_step), format="%.4f", key='dbscan_eps')
        run_params = dict(algorithm='DBSCAN', k=2, threshold=0.5, eps=eps, min_pts=min_pts)

    elif algo_key == 'BIRCH':
        BIRCH_K_RANGE    = list(range(2, 11))          # k 2–10
        BIRCH_THRESHOLDS = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]

        k = st.slider("Number of Clusters (K)", 2, 10,
                      st.session_state.get('k', 4), key='k_birch')
        st.session_state.k = k
        threshold = st.select_slider("Threshold", BIRCH_THRESHOLDS,
                                     st.session_state.get('threshold', 0.2), key='thr_birch')
        st.session_state.threshold = threshold

        st.markdown("#### Silhouette Score vs K (Multiple Thresholds)")
        fig_sil, best_thr_birch, best_k_birch, _ = make_birch_silhouette_chart(
            rfm_norm, k_range=BIRCH_K_RANGE, threshold_range=BIRCH_THRESHOLDS)
        fig_sil.add_vline(x=k, line_dash='dot', line_color='#7c3aed',
                          annotation_text=f'Selected K={k}', annotation_position='bottom right')
        st.plotly_chart(fig_sil, use_container_width=True)
        st.caption(f"Best from chart: threshold={best_thr_birch}, K={best_k_birch} · Uses raw R/F/M")
        run_params = dict(algorithm='BIRCH', k=k, threshold=threshold)

    elif algo_key == 'Spectral Clustering':
        SPECTRAL_K_RANGE = list(range(2, 11))   # k 2–10

        st.markdown("#### Silhouette Score vs K")
        fig_sil, best_k_spec, sil_scores_spec = make_spectral_silhouette_chart(
            rfm_norm, k_range=SPECTRAL_K_RANGE)
        st.plotly_chart(fig_sil, use_container_width=True)

        # Recommendation box
        best_sil_spec = sil_scores_spec[SPECTRAL_K_RANGE.index(best_k_spec)]
        q_spec = "Excellent" if best_sil_spec > 0.7 else ("Good" if best_sil_spec > 0.5 else "Fair")
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#7c3aed,#a855f7);border-radius:10px;
                    padding:10px 16px;margin-bottom:10px;color:white;">
          <div style="font-size:12px;opacity:.85;margin-bottom:2px;">Recommended clusters</div>
          <div style="font-size:20px;font-weight:800;">K = {best_k_spec}
            <span style="font-size:12px;font-weight:400;opacity:.85;margin-left:8px;">
              Silhouette {best_sil_spec:.4f} · {q_spec}
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        k = st.slider("Number of Clusters (K)", 2, 10,
                      best_k_spec, key='k_spec')
        st.session_state.k = k
        run_params = dict(algorithm='Spectral', k=k, threshold=0.5)

    elif algo_key == 'GMM':
        GMM_K_RANGE  = list(range(2, 11))   # k 2–10
        COV_TYPES    = ['full', 'tied', 'diag', 'spherical']

        st.markdown("#### BIC Score vs K — All Covariance Types")
        fig_bic, best_k_gmm, best_cov_gmm = make_bic_chart(rfm_norm, k_range=GMM_K_RANGE)
        st.plotly_chart(fig_bic, use_container_width=True)

        # Recommendation box
        st.markdown(f"""
        <div style="background:linear-gradient(135deg,#f59e0b,#fbbf24);border-radius:10px;
                    padding:10px 16px;margin-bottom:10px;color:white;">
          <div style="font-size:12px;opacity:.85;margin-bottom:2px;">Recommended (lowest BIC)</div>
          <div style="font-size:20px;font-weight:800;">K = {best_k_gmm}
            <span style="font-size:12px;font-weight:400;opacity:.85;margin-left:8px;">
              covariance_type = '{best_cov_gmm}'
            </span>
          </div>
        </div>
        """, unsafe_allow_html=True)

        k = st.slider("Number of Components (K)", 2, 10, best_k_gmm, key='k_gmm')
        st.session_state.k = k
        cov_type = st.selectbox("Covariance Type", COV_TYPES,
                                index=COV_TYPES.index(best_cov_gmm),
                                help="full=general, tied=shared, diag=axis-aligned, spherical=isotropic",
                                key='gmm_cov')
        run_params = dict(algorithm='GMM', k=k, threshold=0.5, cov_type=cov_type)

with col_right:
    # ── Algorithm comparison ───────────────────────────────────────────────────
    st.markdown("#### Algorithm Recommendation")
    if algo_recs:
        best_sil_val = max(r['sil'] for r in algo_recs)
        for r in sorted(algo_recs, key=lambda x: -x['sil']):
            is_best = r['sil'] == best_sil_val
            bg    = 'linear-gradient(135deg,#3b82f6,#60a5fa)' if is_best else 'white'
            tc    = 'white' if is_best else '#1e293b'
            sc    = 'white' if is_best else '#3b82f6'
            badge = '⭐ BEST' if is_best else ''
            badge_html = (f'<span style="font-size:10px;background:rgba(255,255,255,0.25);'
                          f'padding:1px 6px;border-radius:8px;margin-left:6px;">{badge}</span>'
                          if badge else '')
            st.markdown(f"""
            <div style="background:{bg};border-radius:10px;padding:10px 14px;
                        margin-bottom:8px;box-shadow:0 2px 8px rgba(0,0,0,0.07);">
              <div style="display:flex;justify-content:space-between;align-items:center;">
                <span style="font-size:13px;font-weight:700;color:{tc};">
                  {r['algo']}{badge_html}
                </span>
                <span style="font-size:16px;font-weight:800;color:{sc};">{r['sil']:.4f}</span>
              </div>
              <div style="display:flex;justify-content:space-between;margin-top:4px;">
                <span style="font-size:11px;color:{'rgba(255,255,255,0.8)' if is_best else '#64748b'};">
                  {r['note']}
                </span>
                <span style="font-size:11px;color:{'rgba(255,255,255,0.9)' if is_best else '#374151'};
                             font-weight:600;">K={r['rec_k']}</span>
              </div>
            </div>
            """, unsafe_allow_html=True)
        st.caption("Silhouette with optimal K (2–8) per algorithm.")

    st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)

    # ── Current configuration ──────────────────────────────────────────────────
    st.markdown("#### Current Configuration")
    cfg = {"Algorithm": algo_key,
           "Dataset Size": f"{len(rfm_norm):,} customers",
           "Features": "R, F, M (3)",
           "AHP Weights": f"R:{weights[0]:.2f} F:{weights[1]:.2f} M:{weights[2]:.2f}"}
    if algo_key != 'DBSCAN':
        cfg["Clusters (K)"] = run_params.get('k', '—')
    if algo_key == 'BIRCH':
        cfg["Threshold"] = run_params.get('threshold')
    if algo_key == 'DBSCAN':
        cfg["MinPts"] = run_params.get('min_pts')
        cfg["Eps"]    = run_params.get('eps')
    if algo_key == 'GMM':
        cfg["Cov. Type"] = run_params.get('cov_type')

    for label, val in cfg.items():
        st.markdown(f"""
        <div style="display:flex;justify-content:space-between;padding:7px 0;
                    border-bottom:1px solid #f1f5f9;font-size:13px;">
          <span style="color:#64748b;">{label}</span><strong>{val}</strong>
        </div>""", unsafe_allow_html=True)

    algo_info = {
        'K-Means':             "Partitions data into K spherical clusters minimising SSE. Fast and simple.",
        'DBSCAN':              "Density-based, finds arbitrary-shaped clusters and marks outliers as noise. K is auto-detected.",
        'BIRCH':               "Hierarchical CF-tree. Memory-efficient for large datasets.",
        'Spectral Clustering': "Graph-based eigenvector method. Excellent for non-convex cluster shapes.",
        'GMM':                 "Probabilistic mixture model. Allows soft/overlapping cluster membership.",
    }
    with st.expander(f"ℹ️ About {algo_key}"):
        st.markdown(algo_info.get(algo_key, ""))

    st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
    run_clicked = st.button(f"🚀 Run {algo_key}", use_container_width=True)

    if run_clicked:
        with st.spinner(f"Running {algo_key}…"):
            import time
            prog = st.progress(0, text="Preparing…")
            time.sleep(0.3); prog.progress(40, text="Fitting model…")
            labels, sil, db, ch, pca_coords = run_clustering(rfm_norm, **run_params)
            prog.progress(75, text="Building summary…")
            cluster_summary = build_cluster_summary(rfm_norm, labels)
            prog.progress(100, text="Done!"); time.sleep(0.3); prog.empty()

        st.session_state.labels            = labels.tolist()
        st.session_state.pca_coords        = pca_coords.tolist()
        st.session_state.silhouette_score  = sil
        st.session_state.davies_bouldin    = db
        st.session_state.calinski_harabasz = ch
        st.session_state.cluster_summary   = cluster_summary.to_dict('records')
        st.session_state.algo_used         = algo_key

        n_clusters = len(set(labels) - {-1})
        noise      = int((np.array(labels) == -1).sum())

        # Auto-save to history
        st.session_state.projects.append({
            'name':       f'Run #{len(st.session_state.projects)+1}',
            'date':       pd.Timestamp.now().strftime('%b %d, %Y'),
            'algorithm':  algo_key,
            'k':          n_clusters,
            'customers':  len(rfm_norm),
            'silhouette': round(sil, 4),
            'status':     'Completed',
        })

        # Store summary for persistent display
        noise_str = f" · {noise} noise pts" if noise > 0 else ""
        st.session_state['_run_summary'] = (
            f"✅ {n_clusters} clusters{noise_str} · "
            f"Silhouette: **{sil:.4f}** · DB: **{db:.4f}** · Saved to history"
        )
        # Navigate directly to Results
        st.switch_page('pages/6_Results.py')

    # Show persistent result summary + View Results button if previous run exists
    elif st.session_state.get('_run_summary') and st.session_state.get('labels') is not None:
        st.success(st.session_state['_run_summary'])
        if st.button("📋 View Results", use_container_width=True):
            st.switch_page('pages/6_Results.py')
