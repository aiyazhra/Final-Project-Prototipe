import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import random
import json
import os

_HISTORY_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'history.json')

def load_history():
    if os.path.exists(_HISTORY_FILE):
        try:
            with open(_HISTORY_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            pass
    return []

def save_history(projects):
    try:
        with open(_HISTORY_FILE, 'w') as f:
            json.dump(projects, f)
    except Exception:
        pass


# ─── Custom CSS ───────────────────────────────────────────────────────────────

STYLES = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Inter', sans-serif !important; }
#MainMenu, footer, header[data-testid="stHeader"] { display: none !important; }

/* ── Sidebar ── */
section[data-testid="stSidebar"] {
    background: #3b82f6 !important;
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    flex: 0 0 120px !important;
}
section[data-testid="stSidebar"] > div:first-child {
    width: 120px !important;
    min-width: 120px !important;
    max-width: 120px !important;
    padding: 0 0 16px 0 !important;
    background: #3b82f6 !important;
    overflow-x: hidden !important;
}

[data-testid="stSidebarCollapseButton"],
[data-testid="stSidebarResizeHandle"] { display: none !important; }
[data-testid="collapsedControl"] { display: flex !important; }

section[data-testid="stSidebar"] {
    transform: translateX(0) !important;
    margin-left: 0 !important;
    left: 0 !important;
}

[data-testid="stSidebarNav"],
[data-testid="stSidebarNavContainer"],
[data-testid="stSidebarNavItems"],
[data-testid="stSidebarNavLink"],
[data-testid="stSidebarNavSeparator"],
section[data-testid="stSidebar"] nav,
section[data-testid="stSidebar"] ul { display: none !important; }

section[data-testid="stSidebar"] .element-container,
section[data-testid="stSidebar"] .stMarkdown { margin: 0 !important; padding: 0 !important; }

section[data-testid="stSidebar"] .stButton {
    display: flex !important;
    justify-content: center !important;
}
section[data-testid="stSidebar"] .stButton > button {
    display: flex !important;
    flex-direction: column !important;
    align-items: center !important;
    justify-content: center !important;
    gap: 6px !important;
    width: calc(100% - 16px) !important;
    min-height: 68px !important;
    margin: 2px 8px !important;
    background: transparent !important;
    border: none !important;
    border-radius: 12px !important;
    color: rgba(255,255,255,0.65) !important;
    padding: 10px 6px !important;
    box-shadow: none !important;
    transform: none !important;
    transition: background 0.15s !important;
    font-size: 11px !important;
    font-weight: 600 !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,255,255,0.12) !important;
    color: rgba(255,255,255,0.95) !important;
    transform: none !important;
    box-shadow: none !important;
}
section[data-testid="stSidebar"] .stButton > button p,
section[data-testid="stSidebar"] .stButton > button span {
    font-size: 11px !important;
    color: inherit !important;
    text-align: center !important;
    margin: 0 !important;
    white-space: pre-line !important;
}

section[data-testid="stSidebar"] .tile-inactive {
    pointer-events: none !important;
}

section[data-testid="stSidebar"] .element-container:has(.stPageLink) {
    margin-top: -74px !important;
    height: 70px !important;
    position: relative !important;
    z-index: 10 !important;
    opacity: 0 !important;
}
section[data-testid="stSidebar"] .stPageLink,
section[data-testid="stSidebar"] .stPageLink a {
    display: block !important;
    width: 100% !important;
    height: 70px !important;
    cursor: pointer !important;
}

.stApp, .main { background: white !important; }
.block-container { padding: 20px 28px !important; max-width: 1300px !important; }

[data-testid="stMetric"] { background: white; border-radius: 12px; padding: 16px 18px !important; box-shadow: 0 2px 10px rgba(0,0,0,0.07); }
[data-testid="stMetricLabel"] p { font-size: 12px !important; color: #64748b !important; font-weight: 500 !important; }
[data-testid="stMetricValue"] { font-size: 26px !important; font-weight: 800 !important; color: #1e293b !important; }
[data-testid="stMetricDelta"] { font-size: 12px !important; }

.main .stButton > button { background: #3b82f6 !important; color: white !important; border: none !important; border-radius: 8px !important; padding: 8px 18px !important; font-weight: 600 !important; font-size: 13px !important; transition: all 0.2s !important; }
.main .stButton > button:hover { background: #2563eb !important; transform: translateY(-1px) !important; box-shadow: 0 4px 12px rgba(59,130,246,0.35) !important; }
.main .stButton > button[kind="secondary"] { background: white !important; color: #1e293b !important; border: 1.5px solid #e2e8f0 !important; }
.main .stButton > button[kind="secondary"]:hover { background: #f8fafc !important; transform: none !important; box-shadow: none !important; }

[data-testid="stDataFrame"] { border-radius: 12px !important; overflow: hidden !important; border: 1px solid #e2e8f0 !important; }

.stTextInput > div > div, .stNumberInput > div > div { border-radius: 8px !important; background: white !important; }
.stTextInput input { padding-top: 2px !important; padding-bottom: 18px !important; }
.stSelectbox > div > div { border-radius: 8px !important; background: white !important; }
.stSlider { background: transparent !important; }

.stTabs [data-baseweb="tab-list"] { background: #f1f5f9 !important; border-radius: 8px; padding: 4px; gap: 2px; border: 1px solid #e2e8f0; }
.stTabs [data-baseweb="tab"] { border-radius: 6px !important; font-weight: 600 !important; font-size: 13px !important; color: #64748b !important; }
.stTabs [aria-selected="true"] { background: white !important; color: #3b82f6 !important; box-shadow: 0 1px 3px rgba(0,0,0,0.08) !important; }

.stAlert { border-radius: 8px !important; }
[data-testid="stInfo"] { background: #dbeafe !important; border-left-color: #3b82f6 !important; }
[data-testid="stSuccess"] { background: #d1fae5 !important; }
[data-testid="stWarning"] { background: #fef3c7 !important; }

.stProgress > div > div > div { background: #3b82f6 !important; border-radius: 10px !important; }

.streamlit-expanderHeader { background: white !important; border-radius: 8px !important; font-weight: 600 !important; }

[data-testid="stFileUploader"] { background: white; border-radius: 12px; padding: 8px; border: 2px dashed #e2e8f0; }

.stRadio > div { background: white; border-radius: 8px; padding: 12px; }
.stCheckbox label { font-size: 13px !important; }

hr { border-color: #e2e8f0 !important; }
</style>
"""

# ─── Sidebar nav ──────────────────────────────────────────────────────────────

_NAV_ITEMS = [
    ('dashboard', 'Dashboard',   'pages/1_Dashboard.py',   '/Dashboard'),
    ('data',      'Data Upload', 'pages/2_Data_Upload.py', '/Data_Upload'),
    ('cluster',   'Clustering',  'pages/5_Clustering.py',  '/Clustering'),
    ('results',   'Results',     'pages/6_Results.py',     '/Results'),
    ('history',   'History',     'pages/8_History.py',     '/History'),
    ('settings',  'Settings',    'pages/9_Settings.py',    '/Settings'),
]

_SVG_ICONS = {
    'dashboard': (
        '<rect x="3" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="3" width="7" height="7" rx="1.5"/>'
        '<rect x="3" y="14" width="7" height="7" rx="1.5"/>'
        '<rect x="14" y="14" width="7" height="7" rx="1.5"/>'
    ),
    'data': (
        '<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/>'
        '<polyline points="17 8 12 3 7 8"/>'
        '<line x1="12" y1="3" x2="12" y2="15"/>'
    ),
    'cluster': (
        '<path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>'
        '<circle cx="9" cy="7" r="4"/>'
        '<path d="M23 21v-2a4 4 0 0 0-3-3.87"/>'
        '<path d="M16 3.13a4 4 0 0 1 0 7.75"/>'
    ),
    'results': (
        '<line x1="18" y1="20" x2="18" y2="10"/>'
        '<line x1="12" y1="20" x2="12" y2="4"/>'
        '<line x1="6" y1="20" x2="6" y2="14"/>'
        '<line x1="2" y1="20" x2="22" y2="20"/>'
    ),
    'history': (
        '<circle cx="12" cy="12" r="9"/>'
        '<polyline points="12 6 12 12 16 14"/>'
    ),
    'settings': (
        '<circle cx="12" cy="12" r="3"/>'
        '<path d="M12 2v3m0 14v3M4.22 4.22l2.12 2.12m11.32 11.32 2.12 2.12'
        'M2 12h3m14 0h3M4.22 19.78l2.12-2.12M17.66 6.34l2.12-2.12"/>'
    ),
}


def _nav_icon_html(key, size=24):
    paths = _SVG_ICONS.get(key, '')
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="white" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">'
        f'{paths}</svg>'
    )


_TILE_ACTIVE = (
    "display:flex;flex-direction:column;align-items:center;justify-content:center;"
    "gap:7px;margin:2px 8px;padding:12px 6px;border-radius:12px;"
    "background:rgba(255,255,255,0.22);border:1px solid rgba(255,255,255,0.28);"
    "position:relative;cursor:default;"
)
_TILE_INACTIVE = (
    "display:flex;flex-direction:column;align-items:center;justify-content:center;"
    "gap:7px;margin:2px 8px;padding:12px 6px;border-radius:12px;"
    "background:transparent;text-decoration:none;cursor:pointer;"
    "transition:background 0.15s;"
)


def render_nav(current='dashboard'):
    with st.sidebar:
        st.markdown("""
        <div style="text-align:center;padding:18px 8px 14px;">
          <div style="display:inline-flex;align-items:center;justify-content:center;
                      background:white;border-radius:12px;padding:9px;
                      box-shadow:0 3px 10px rgba(0,0,0,0.25);">
            <svg width="28" height="28" viewBox="0 0 34 34" fill="none">
              <rect x="1" y="1" width="14" height="14" rx="2.5" fill="#3b82f6"/>
              <rect x="19" y="1" width="14" height="14" rx="2.5" fill="#2563eb"/>
              <rect x="1" y="19" width="14" height="14" rx="2.5" fill="#60a5fa"/>
              <rect x="19" y="19" width="14" height="14" rx="2.5" fill="#3b82f6"/>
            </svg>
          </div>
          <div style="color:rgba(255,255,255,0.5);font-size:9px;font-weight:600;
                      letter-spacing:1.2px;margin-top:6px;text-transform:uppercase;">ClusterHub</div>
        </div>
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:0 10px 6px;">
        """, unsafe_allow_html=True)

        for key, label, page, href in _NAV_ITEMS:
            active = current == key
            icon   = _nav_icon_html(key, size=26)

            if active:
                arrow = ('<div style="position:absolute;right:-7px;top:50%;'
                         'transform:translateY(-50%);width:0;height:0;'
                         'border-top:7px solid transparent;'
                         'border-bottom:7px solid transparent;'
                         'border-left:7px solid rgba(255,255,255,0.35);"></div>')
                st.markdown(
                    f'<div class="tile-active" style="{_TILE_ACTIVE}">'
                    f'  {icon}'
                    f'  <span style="font-size:10px;color:white;font-weight:700;'
                    f'               text-align:center;letter-spacing:0.2px;">{label}</span>'
                    f'  {arrow}'
                    f'</div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="tile-inactive" style="{_TILE_INACTIVE}">'
                    f'  {icon}'
                    f'  <span style="font-size:10px;color:rgba(255,255,255,0.72);'
                    f'               font-weight:600;text-align:center;">{label}</span>'
                    f'</div>',
                    unsafe_allow_html=True
                )
                st.page_link(page, label=label)

        st.markdown("""
        <hr style="border:none;border-top:1px solid rgba(255,255,255,0.12);margin:6px 10px 4px;">
        """, unsafe_allow_html=True)
        if st.button("🚪  Logout", key="nav_logout", use_container_width=True, help="Logout"):
            st.session_state.logged_in = False
            st.rerun()


def apply_styles():
    st.markdown(STYLES, unsafe_allow_html=True)


# ─── Session State ────────────────────────────────────────────────────────────

def init_session():
    defaults = {
        'logged_in':        False,
        'username':         'Ayak',
        'df':               None,
        'file_name':        None,
        'rfm_df':           None,
        'rfm_normalized':   None,
        'outlier_removed':  True,
        'ahp_matrix':       [[1.0, 3.0, 5.0], [1/3, 1.0, 3.0], [1/5, 1/3, 1.0]],
        'ahp_weights':      [0.637, 0.261, 0.102],
        'ahp_cr':           0.037,
        'k':                4,
        'threshold':        0.5,
        'labels':           None,
        'pca_coords':       None,
        'silhouette_score': None,
        'davies_bouldin':   None,
        'calinski_harabasz':None,
        'cluster_summary':  None,
        'projects': load_history(),
        'col_map':          {},
    }
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def require_login():
    init_session()
    if not st.session_state.get('logged_in'):
        st.rerun()


# ─── Sample Data ──────────────────────────────────────────────────────────────

def generate_sample_data(n_customers=1200, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    customers  = [f'C{i:04d}' for i in range(1001, 1001 + n_customers)]
    records    = []
    end_date   = datetime(2024, 12, 31)
    start_date = datetime(2024, 1, 1)

    for cid in customers:
        ctype = np.random.choice(['loyal', 'potential', 'at_risk', 'lost'],
                                 p=[0.27, 0.23, 0.29, 0.21])
        if ctype == 'loyal':
            n_trans, recency = np.random.randint(12, 50), np.random.randint(1, 30)
            price_range = (30000, 250000)
        elif ctype == 'potential':
            n_trans, recency = np.random.randint(4, 14), np.random.randint(20, 90)
            price_range = (10000, 80000)
        elif ctype == 'at_risk':
            n_trans, recency = np.random.randint(2, 6), np.random.randint(60, 200)
            price_range = (5000, 30000)
        else:
            n_trans, recency = np.random.randint(1, 3), np.random.randint(180, 365)
            price_range = (2000, 12000)

        last_date = end_date - timedelta(days=recency)
        for _ in range(n_trans):
            inv_date = last_date - timedelta(days=random.randint(0, 280))
            inv_date = max(inv_date, start_date)
            qty   = np.random.randint(1, 20)
            price = round(np.random.uniform(*price_range), 0)
            records.append({
                'CustomerID':  cid,
                'InvoiceNo':   f'INV-{random.randint(10000, 99999)}',
                'InvoiceDate': inv_date.strftime('%Y-%m-%d'),
                'Quantity':    qty,
                'UnitPrice':   price,
                'TotalAmount': round(qty * price, 0),
                'Country':     'Indonesia',
            })

    df      = pd.DataFrame(records)
    idx_miss = np.random.choice(len(df), 23, replace=False)
    df.loc[idx_miss[:12], 'Quantity']  = np.nan
    df.loc[idx_miss[12:], 'UnitPrice'] = np.nan
    dups = df.sample(11, random_state=seed)
    df   = pd.concat([df, dups], ignore_index=True)
    return df.sample(frac=1, random_state=seed).reset_index(drop=True)


# ─── RFM ─────────────────────────────────────────────────────────────────────

def calculate_rfm(df):
    d = df.copy()
    d['InvoiceDate'] = pd.to_datetime(d['InvoiceDate'], errors='coerce')
    d['TotalAmount'] = pd.to_numeric(d.get('TotalAmount', pd.Series(dtype=float)), errors='coerce')
    d = d.dropna(subset=['CustomerID', 'InvoiceDate', 'TotalAmount'])
    d = d[d['TotalAmount'] > 0]
    d = d.drop_duplicates()
    ref = d['InvoiceDate'].max()
    if 'InvoiceNo' in d.columns:
        freq_series = d.groupby('CustomerID')['InvoiceNo'].nunique()
    else:
        freq_series = d.groupby('CustomerID')['InvoiceDate'].count()
    rfm = d.groupby('CustomerID').agg(
        Recency=('InvoiceDate', lambda x: (ref - x.max()).days),
        Monetary=('TotalAmount', 'sum'),
    ).reset_index()
    rfm['Frequency'] = rfm['CustomerID'].map(freq_series)
    return rfm


def normalize_rfm(rfm_df):
    from sklearn.preprocessing import MinMaxScaler
    scaler = MinMaxScaler()
    r = rfm_df.copy()
    r[['R_norm', 'F_norm', 'M_norm']] = scaler.fit_transform(r[['Recency', 'Frequency', 'Monetary']])
    r['R_norm'] = 1 - r['R_norm']
    return r


# ─── AHP ─────────────────────────────────────────────────────────────────────

def calculate_ahp(matrix):
    m        = np.array(matrix, dtype=float)
    n        = m.shape[0]
    col_sums = m.sum(axis=0)
    norm     = m / col_sums
    weights  = norm.mean(axis=1)
    ws       = m @ weights
    lambda_max = float(np.mean(ws / weights))
    ci       = (lambda_max - n) / (n - 1)
    ri_table = {1: 0, 2: 0, 3: 0.58, 4: 0.9, 5: 1.12}
    ri       = ri_table.get(n, 1.12)
    cr       = float(ci / ri) if ri > 0 else 0.0
    return weights.tolist(), cr, lambda_max


# ─── Clustering ───────────────────────────────────────────────────────────────

def _cluster_metrics(X, labels):
    from sklearn.metrics import silhouette_score, davies_bouldin_score, calinski_harabasz_score
    valid = labels != -1
    u     = set(labels[valid])
    if len(u) < 2 or valid.sum() < len(u) + 1:
        return 0.0, 99.0, 0.0
    sil = float(silhouette_score(X[valid], labels[valid]))
    db  = float(davies_bouldin_score(X[valid], labels[valid]))
    ch  = float(calinski_harabasz_score(X[valid], labels[valid]))
    return sil, db, ch


def run_clustering(rfm_norm, k=4, threshold=0.5, algorithm='BIRCH',
                   eps=0.5, min_pts=6, cov_type='full'):
    from sklearn.decomposition import PCA

    X = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values

    if algorithm == 'K-Means':
        from sklearn.cluster import KMeans
        labels = KMeans(n_clusters=k, random_state=42).fit_predict(X) + 1

    elif algorithm == 'DBSCAN':
        from sklearn.cluster import DBSCAN
        from sklearn.metrics import silhouette_score as _sf
        from sklearn.metrics import davies_bouldin_score as _df
        from sklearn.metrics import calinski_harabasz_score as _cf
        labels = DBSCAN(eps=eps, min_samples=min_pts).fit_predict(X)
        try:
            if len(set(labels)) >= 2:
                sil = float(_sf(X, labels))
                db  = float(_df(X, labels))
                ch  = float(_cf(X, labels))
            else:
                sil, db, ch = 0.0, 99.0, 0.0
        except Exception:
            sil, db, ch = 0.0, 99.0, 0.0
        coords = PCA(n_components=2, random_state=42).fit_transform(X)
        return labels, sil, db, ch, coords

    elif algorithm == 'BIRCH':
        from sklearn.cluster import Birch
        labels = Birch(n_clusters=k, threshold=threshold).fit_predict(X) + 1

    elif algorithm == 'Spectral':
        from sklearn.cluster import SpectralClustering
        labels = SpectralClustering(n_clusters=k, random_state=42).fit_predict(X) + 1

    elif algorithm == 'GMM':
        from sklearn.mixture import GaussianMixture
        labels = GaussianMixture(n_components=k, covariance_type=cov_type,
                                 random_state=42).fit_predict(X) + 1
    else:
        raise ValueError(f"Unknown algorithm: {algorithm}")

    sil, db, ch = _cluster_metrics(X, labels)
    coords = PCA(n_components=2, random_state=42).fit_transform(X)
    return labels, sil, db, ch, coords


# ─── Diagnostic charts ────────────────────────────────────────────────────────

def make_birch_silhouette_chart(rfm_norm, k_range=range(2, 11), threshold_range=None):
    if threshold_range is None:
        threshold_range = [0.1, 0.2, 0.3, 0.5, 0.7, 1.0]
    from sklearn.cluster import Birch
    from sklearn.metrics import silhouette_score as _sil

    X       = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values
    records = []
    for thr in threshold_range:
        for k in k_range:
            try:
                lbl = Birch(n_clusters=k, threshold=thr).fit_predict(X)
                s   = float(_sil(X, lbl)) if len(set(lbl)) >= 2 else 0.0
            except Exception:
                s = 0.0
            records.append({'threshold': thr, 'k': k, 'silhouette': s})

    results_df = pd.DataFrame(records)
    best_row   = results_df.loc[results_df['silhouette'].idxmax()]
    best_thr   = best_row['threshold']
    best_k     = int(best_row['k'])

    colors = ['#3b82f6', '#0d9488', '#f59e0b', '#7c3aed', '#ef4444', '#10b981']
    fig    = go.Figure()
    for i, thr in enumerate(threshold_range):
        temp    = results_df[results_df['threshold'] == thr]
        is_best = thr == best_thr
        fig.add_trace(go.Scatter(
            x=temp['k'].tolist(), y=temp['silhouette'].tolist(),
            mode='lines+markers', name=f'th={thr}',
            line=dict(color=colors[i % len(colors)],
                      width=3 if is_best else 1.5,
                      dash='solid' if is_best else 'dot'),
            marker=dict(size=8 if is_best else 5, color=colors[i % len(colors)])
        ))

    fig.add_annotation(
        x=best_k, y=float(best_row['silhouette']),
        text=f'Best: th={best_thr}, K={best_k}',
        showarrow=True, arrowhead=2, arrowcolor='#ef4444',
        font=dict(color='#ef4444', size=11),
        bgcolor='white', bordercolor='#ef4444', borderwidth=1
    )
    fig.update_layout(
        title='BIRCH Silhouette Score for Different Thresholds',
        xaxis=dict(title='Number of Clusters (K)', dtick=1, gridcolor='#f1f5f9'),
        yaxis=dict(title='Silhouette Score', gridcolor='#f1f5f9'),
        height=320, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(t=50, b=30, l=40, r=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font_family='Inter'
    )
    return fig, best_thr, best_k, results_df


def make_spectral_silhouette_chart(rfm_norm, k_range=range(2, 11)):
    from sklearn.cluster import SpectralClustering
    from sklearn.metrics import silhouette_score as _sil

    X          = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values
    sil_scores = []
    for k in k_range:
        try:
            lbl = SpectralClustering(n_clusters=k, random_state=42).fit_predict(X)
            s   = float(_sil(X, lbl)) if len(set(lbl)) >= 2 else 0.0
        except Exception:
            s = 0.0
        sil_scores.append(s)

    best_idx = sil_scores.index(max(sil_scores))
    best_k   = list(k_range)[best_idx]
    best_sil = sil_scores[best_idx]

    marker_colors = ['#ef4444' if k == best_k else '#7c3aed' for k in k_range]
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=list(k_range), y=sil_scores,
        mode='lines+markers',
        line=dict(color='#7c3aed', width=2.5),
        marker=dict(size=9, color=marker_colors),
        name='Silhouette'
    ))
    fig.add_annotation(
        x=best_k, y=best_sil,
        text=f'Best K={best_k} (sil={best_sil:.4f})',
        showarrow=True, arrowhead=2, arrowcolor='#ef4444',
        font=dict(color='#ef4444', size=11),
        bgcolor='white', bordercolor='#ef4444', borderwidth=1, ay=-40
    )
    fig.update_layout(
        title='Identify Number of Clusters — Silhouette Score',
        xaxis=dict(title='Number of Clusters (K)', dtick=1, gridcolor='#f1f5f9'),
        yaxis=dict(title='Silhouette Score', gridcolor='#f1f5f9'),
        height=300, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(t=50, b=30, l=40, r=20), font_family='Inter'
    )
    return fig, best_k, sil_scores


def make_bic_chart(rfm_norm, k_range=range(2, 11)):
    from sklearn.mixture import GaussianMixture

    X        = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values
    cov_list = ['full', 'tied', 'diag', 'spherical']
    colors   = ['#3b82f6', '#0d9488', '#f59e0b', '#7c3aed']

    all_bics   = {}
    best_bic   = float('inf')
    best_k_out = 2
    best_cov   = 'full'

    for cov in cov_list:
        bics = []
        for k in k_range:
            try:
                gmm = GaussianMixture(n_components=k, covariance_type=cov, random_state=42)
                gmm.fit(X)
                bics.append(gmm.bic(X))
            except Exception:
                bics.append(float('nan'))
        all_bics[cov] = bics
        valid = [(v, k) for v, k in zip(bics, k_range) if not np.isnan(v)]
        if valid:
            min_bic, min_k = min(valid, key=lambda x: x[0])
            if min_bic < best_bic:
                best_bic   = min_bic
                best_k_out = min_k
                best_cov   = cov

    fig = go.Figure()
    for i, cov in enumerate(cov_list):
        is_best = cov == best_cov
        fig.add_trace(go.Scatter(
            x=list(k_range), y=all_bics[cov],
            mode='lines+markers', name=cov,
            line=dict(color=colors[i], width=3 if is_best else 1.5,
                      dash='solid' if is_best else 'dot'),
            marker=dict(size=8 if is_best else 5, color=colors[i])
        ))

    fig.add_annotation(
        x=best_k_out, y=best_bic,
        text=f'Best: {best_cov}, K={best_k_out}',
        showarrow=True, arrowhead=2, arrowcolor='#ef4444',
        font=dict(color='#ef4444', size=11),
        bgcolor='white', bordercolor='#ef4444', borderwidth=1, ay=-40
    )
    fig.update_layout(
        title='GMM BIC Score — All Covariance Types (lower = better)',
        xaxis=dict(title='Number of Components (K)', dtick=1, gridcolor='#f1f5f9'),
        yaxis=dict(title='BIC Score', gridcolor='#f1f5f9'),
        height=320, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(t=50, b=30, l=40, r=20),
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1),
        font_family='Inter'
    )
    return fig, best_k_out, best_cov


def make_knn_distance_chart(rfm_norm, weights, min_pts):
    from sklearn.neighbors import NearestNeighbors

    X    = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values
    nbrs = NearestNeighbors(n_neighbors=min_pts).fit(X)
    distances, _ = nbrs.kneighbors(X)
    k_dist = np.sort(distances[:, min_pts - 1])

    if len(k_dist) > 3:
        d2        = np.diff(np.diff(k_dist))
        elbow_idx = int(np.argmax(d2)) + 1
    else:
        elbow_idx = len(k_dist) // 2

    suggested_eps = round(float(k_dist[elbow_idx]), 4)

    fig = go.Figure()
    fig.add_trace(go.Scatter(y=k_dist.tolist(), mode='lines',
                             line=dict(color='#3b82f6', width=2), name='k-dist'))
    fig.add_hline(y=suggested_eps, line_dash='dash', line_color='#ef4444',
                  annotation_text=f'eps ≈ {suggested_eps}', annotation_position='top right')
    fig.update_layout(
        title=f'{min_pts}-NN Distance Plot (sorted asc)',
        xaxis_title='Points (sorted)', yaxis_title=f'{min_pts}-th NN Distance',
        height=280, plot_bgcolor='white', paper_bgcolor='white',
        margin=dict(t=40, b=30, l=40, r=20)
    )
    return fig, suggested_eps


def compute_algo_recommendations(rfm_norm, weights):
    from sklearn.metrics import silhouette_score as _sil

    X       = rfm_norm[['R_norm', 'F_norm', 'M_norm']].values
    k_range = range(2, 7)
    results = []

    def best_k_sil(labels_fn):
        best_s, best_k = 0.0, 2
        for k in k_range:
            try:
                lbl   = labels_fn(k)
                valid = lbl != -1
                if len(set(lbl[valid])) >= 2:
                    s = float(_sil(X[valid], lbl[valid]))
                    if s > best_s:
                        best_s, best_k = s, k
            except Exception:
                pass
        return round(best_s, 4), best_k

    try:
        from sklearn.cluster import KMeans
        s, k = best_k_sil(lambda k: KMeans(n_clusters=k, random_state=42).fit_predict(X) + 1)
        results.append({'algo': 'K-Means', 'sil': s, 'rec_k': str(k),
                        'note': 'General purpose, spherical clusters'})
    except Exception:
        pass

    try:
        from sklearn.cluster import Birch
        best_s_b, best_k_b = 0.0, 2
        for thr in [0.1, 0.2, 0.3, 0.5, 0.7]:
            bs, bk = best_k_sil(lambda k, t=thr: Birch(n_clusters=k, threshold=t).fit_predict(X) + 1)
            if bs > best_s_b:
                best_s_b, best_k_b = bs, bk
        results.append({'algo': 'BIRCH', 'sil': round(best_s_b, 4), 'rec_k': str(best_k_b),
                        'note': 'Efficient for large datasets'})
    except Exception:
        pass

    try:
        from sklearn.cluster import SpectralClustering
        s, k = best_k_sil(lambda k: SpectralClustering(n_clusters=k, random_state=42).fit_predict(X) + 1)
        results.append({'algo': 'Spectral', 'sil': s, 'rec_k': str(k),
                        'note': 'Non-convex / complex shapes'})
    except Exception:
        pass

    try:
        from sklearn.mixture import GaussianMixture
        best_s_g, best_k_g = 0.0, 2
        for cov in ['full', 'tied', 'diag', 'spherical']:
            bs, bk = best_k_sil(
                lambda k, c=cov: GaussianMixture(n_components=k,
                    covariance_type=c, random_state=42).fit_predict(X) + 1)
            if bs > best_s_g:
                best_s_g, best_k_g = bs, bk
        results.append({'algo': 'GMM', 'sil': round(best_s_g, 4), 'rec_k': str(best_k_g),
                        'note': 'Probabilistic / soft clusters'})
    except Exception:
        pass

    try:
        from sklearn.cluster import DBSCAN
        from sklearn.neighbors import NearestNeighbors
        min_pts_db = 2 * 3
        nbrs       = NearestNeighbors(n_neighbors=min_pts_db).fit(X)
        dist, _    = nbrs.kneighbors(X)
        k_dist_asc = np.sort(dist[:, min_pts_db - 1])
        d2         = np.diff(np.diff(k_dist_asc))
        eps        = round(float(k_dist_asc[int(np.argmax(d2)) + 1]), 4)
        lbl        = DBSCAN(eps=eps, min_samples=min_pts_db).fit_predict(X)
        noise      = int((lbl == -1).sum())
        n_cl       = len(set(lbl)) - (1 if -1 in lbl else 0)
        s          = float(_sil(X, lbl)) if len(set(lbl)) >= 2 else 0.0
        results.append({'algo': 'DBSCAN', 'sil': round(s, 4),
                        'rec_k': f'{n_cl} (+{noise} noise)',
                        'note': 'Auto-detects shape & noise'})
    except Exception:
        pass

    return results


def build_cluster_summary(rfm_norm, labels):
    df = rfm_norm.copy()
    df['Cluster'] = labels
    summary = df.groupby('Cluster').agg(
        Customers=('CustomerID',  'count'),
        Avg_Recency=('Recency',   'mean'),
        Avg_Frequency=('Frequency','mean'),
        Avg_Monetary=('Monetary', 'mean'),
        Avg_R_norm=('R_norm',     'mean'),
        Avg_F_norm=('F_norm',     'mean'),
        Avg_M_norm=('M_norm',     'mean'),
    ).reset_index()
    summary['Avg_CLV'] = (
        summary['Avg_Monetary']
        * np.log1p(summary['Avg_Frequency'])
        * (1 / np.log1p(summary['Avg_Recency'] + 1))
        * 5
    )
    summary['Segment'] = summary['Cluster'].apply(lambda c: f'Cluster {c}')
    return summary


# ─── Colors ──────────────────────────────────────────────────────────────────

CLUSTER_COLORS = ['#3b82f6', '#0d9488', '#f59e0b', '#7c3aed', '#ef4444', '#10b981']


# ─── Charts ──────────────────────────────────────────────────────────────────

def make_pca_scatter(pca_coords, labels, height=380):
    df_plot = pd.DataFrame(pca_coords, columns=['PC1', 'PC2'])
    df_plot['Cluster'] = labels
    df_plot['Label']   = df_plot['Cluster'].apply(
        lambda c: 'Noise' if c == -1 else f'Cluster {c}'
    )
    fig = px.scatter(
        df_plot, x='PC1', y='PC2', color='Label',
        color_discrete_sequence=CLUSTER_COLORS, height=height,
        template='plotly_white',
        labels={'PC1': 'Principal Component 1', 'PC2': 'Principal Component 2'}
    )
    fig.update_traces(marker=dict(size=5, opacity=0.72))
    fig.update_layout(
        legend=dict(orientation='h', yanchor='bottom', y=1.01,
                    xanchor='right', x=1, font=dict(size=11)),
        margin=dict(l=10, r=10, t=40, b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        font_family='Inter',
    )
    return fig


def make_histogram(series, title, color='#3b82f6', height=220):
    fig = px.histogram(series.dropna(), nbins=12, template='plotly_white',
                       height=height, color_discrete_sequence=[color])
    fig.update_layout(
        title=dict(text=title, font=dict(size=13), x=0),
        showlegend=False,
        margin=dict(l=10, r=10, t=36, b=10),
        paper_bgcolor='white', plot_bgcolor='white',
        font_family='Inter',
        xaxis=dict(gridcolor='#f1f5f9'),
        yaxis=dict(title='Count', gridcolor='#f1f5f9'),
    )
    fig.update_traces(marker_line_width=0)
    return fig


def make_radar(categories, values, color='#3b82f6', height=280):
    vals      = list(values) + [values[0]]
    cats      = list(categories) + [categories[0]]
    fill_color = 'rgba(59,130,246,0.15)' if color == '#3b82f6' else color + '26'
    fig = go.Figure(go.Scatterpolar(
        r=vals, theta=cats, fill='toself',
        fillcolor=fill_color,
        line=dict(color=color, width=2),
        marker=dict(size=4),
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 1], tickfont=dict(size=9)),
            angularaxis=dict(tickfont=dict(size=11)),
        ),
        showlegend=False, height=height,
        margin=dict(l=30, r=30, t=30, b=20),
        paper_bgcolor='white', font_family='Inter',
    )
    return fig


def make_sse_chart(k_values, sse_values, height=260):
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=k_values, y=sse_values,
        mode='lines+markers',
        line=dict(color='#3b82f6', width=2.5),
        marker=dict(size=7, color='#3b82f6', symbol='circle'),
        fill='tozeroy', fillcolor='rgba(37,99,235,0.07)',
    ))
    fig.update_layout(
        xaxis=dict(title='Number of Clusters K', gridcolor='#f1f5f9', dtick=1),
        yaxis=dict(title='SSE', gridcolor='#f1f5f9'),
        template='plotly_white', height=height,
        margin=dict(l=20, r=20, t=20, b=40),
        paper_bgcolor='white', font_family='Inter',
    )
    return fig


def make_weight_bar(labels, weights, colors=None, height=180):
    if colors is None:
        colors = ['#3b82f6', '#0d9488', '#f59e0b']
    fig = go.Figure(go.Bar(
        x=weights, y=labels, orientation='h',
        marker=dict(color=colors[:len(labels)]),
        text=[f'{v:.1%}' for v in weights],
        textposition='outside',
    ))
    fig.update_layout(
        xaxis=dict(range=[0, max(weights) * 1.25], tickformat='.0%', gridcolor='#f1f5f9'),
        template='plotly_white', height=height,
        margin=dict(l=10, r=60, t=10, b=10),
        paper_bgcolor='white', font_family='Inter', showlegend=False,
    )
    return fig


def make_donut(labels, values, colors, height=200):
    fig = go.Figure(go.Pie(
        labels=labels, values=values,
        marker=dict(colors=colors), hole=0.55,
        textinfo='percent', textfont=dict(size=11)
    ))
    fig.update_layout(
        showlegend=True,
        legend=dict(font=dict(size=10), orientation='h', y=-0.1),
        height=height, margin=dict(l=10, r=10, t=10, b=10),
        paper_bgcolor='white', font_family='Inter',
    )
    return fig
