import streamlit as st
import pandas as pd
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from utils.helpers import *

st.set_page_config(page_title="Data Upload — ClusterHub", page_icon="📤", layout="wide", initial_sidebar_state="expanded")
apply_styles()
require_login()
render_nav('data')

st.markdown("## 📤 Data Upload")
st.markdown("Upload your transaction CSV file to begin the analysis pipeline.")
st.markdown("<div style='margin-bottom:12px'></div>", unsafe_allow_html=True)

# ── Upload controls (full width, above both columns) ──────────────────────────
up_left, up_right = st.columns([2, 1])
with up_left:
    uploaded = st.file_uploader(
        "Drag & drop your CSV file here, or click Browse",
        type=['csv'], help="Upload a CSV with transaction data",
        label_visibility="visible"
    )
with up_right:
    st.markdown("<div style='margin-top:28px'></div>", unsafe_allow_html=True)
    use_demo = st.button("🎲 Use Demo Dataset", use_container_width=True)

if use_demo and st.session_state.get('df') is None:
    with st.spinner("Generating demo dataset..."):
        df = generate_sample_data()
        st.session_state.df = df
        st.session_state.file_name = "demo_transactions.csv"
        st.session_state.col_map = {
            'CustomerID': 'CustomerID', 'InvoiceDate': 'InvoiceDate',
            'InvoiceNo': 'InvoiceNo', 'UnitPrice': 'UnitPrice'
        }
    st.success("Demo dataset loaded! 1,200 unique customers.")

if uploaded is not None:
    try:
        df = pd.read_csv(uploaded)
        st.session_state.df = df
        st.session_state.file_name = uploaded.name
        if 'col_map' not in st.session_state:
            st.session_state.col_map = {}
        st.success(f"✅ **{uploaded.name}** uploaded — {len(df):,} rows, {df.shape[1]} columns")
    except Exception as e:
        st.error(f"Error reading file: {e}")

st.markdown("<div style='margin-bottom:16px'></div>", unsafe_allow_html=True)

# ── Two equal columns — content only ──────────────────────────────────────────
col_up, col_val = st.columns([1, 1])

with col_up:
    st.markdown("#### Dataset Preview")
    if st.session_state.get('df') is not None:
        df = st.session_state.df
        st.markdown(
            f"<div style='font-size:12px;color:#64748b;margin-bottom:8px;'>"
            f"Showing first 5 rows of <strong>{st.session_state.file_name}</strong></div>",
            unsafe_allow_html=True
        )
        st.dataframe(df.head(5), use_container_width=True, hide_index=True)
    else:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:60px 20px;text-align:center;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:2px dashed #e2e8f0;">
          <div style="font-size:40px;margin-bottom:10px;">📂</div>
          <div style="font-size:14px;font-weight:600;color:#1e293b;">No file uploaded yet</div>
          <div style="font-size:12px;color:#64748b;margin-top:4px;">Upload a CSV above to preview it here.</div>
        </div>
        """, unsafe_allow_html=True)

with col_val:
    st.markdown("#### Data Validation")

    if st.session_state.get('df') is not None:
        df   = st.session_state.df
        cols = df.columns.tolist()

        # ── Auto-detect columns from names ────────────────────────────────────
        col_map = st.session_state.get('col_map', {})

        def _detect(preferred, hints):
            if preferred and preferred in cols:
                return preferred
            for c in cols:
                if c.lower().replace(' ', '').replace('_', '') in hints:
                    return c
            return ''

        cid_col  = _detect(col_map.get('CustomerID', ''),  ['customerid','custid','customer','idcustomer'])
        date_col = _detect(col_map.get('InvoiceDate', ''), ['invoicedate','tanggal','tglpesan','tgl','date','orderdate'])

        # ── Stats ─────────────────────────────────────────────────────────────
        n_rows    = len(df)
        n_missing = int(df.isnull().sum().sum())
        n_dupes   = int(df.duplicated().sum())
        n_cols    = df.shape[1]
        n_customers = df[cid_col].nunique() if cid_col in df.columns else 0

        if date_col in df.columns:
            dates = pd.to_datetime(df[date_col], errors='coerce').dropna()
            date_range = f"{dates.min().strftime('%b %Y')} – {dates.max().strftime('%b %Y')}" if len(dates) else "N/A"
        else:
            date_range = "N/A"
            for c in cols:
                try:
                    parsed = pd.to_datetime(df[c], errors='coerce')
                    if parsed.notna().sum() > len(df) * 0.5:
                        date_range = f"{parsed.min().strftime('%b %Y')} – {parsed.max().strftime('%b %Y')}"
                        break
                except Exception:
                    pass

        def stat_row(label, value, dot='#10b981', color='#1e293b'):
            return (
                f"<div style='display:flex;align-items:center;justify-content:space-between;"
                f"padding:9px 0;border-bottom:1px solid #f1f5f9;'>"
                f"<span style='display:flex;align-items:center;gap:8px;font-size:13px;color:#374151;'>"
                f"<span style='width:8px;height:8px;border-radius:50%;background:{dot};"
                f"flex-shrink:0;display:inline-block;'></span>{label}</span>"
                f"<strong style='font-size:13px;color:{color};'>{value}</strong></div>"
            )

        miss_dot = '#f59e0b' if n_missing > 0 else '#10b981'
        dupe_dot = '#f59e0b' if n_dupes   > 0 else '#10b981'

        stats_html = "".join([
            stat_row("Total Records",     f"{n_rows:,}"),
            stat_row("Unique Customers",  f"{n_customers:,}" if n_customers else "—"),
            stat_row("Missing Values",    f"{n_missing:,}", miss_dot, miss_dot),
            stat_row("Duplicate Records", f"{n_dupes:,}",   dupe_dot, dupe_dot),
            stat_row("Columns Detected",  str(n_cols)),
            stat_row("Date Range",        date_range),
        ])
        st.markdown(
            f"<div style='background:white;border-radius:12px;padding:16px 18px;"
            f"box-shadow:0 2px 10px rgba(0,0,0,0.07);'>{stats_html}</div>",
            unsafe_allow_html=True
        )

        # ── Null values per column ─────────────────────────────────────────────
        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
        st.markdown("#### Null Values per Column")
        null_counts = df.isnull().sum()
        null_rows = ""
        for col_name in df.columns:
            cnt = int(null_counts[col_name])
            dot = '#ef4444' if cnt > 0 else '#10b981'
            clr = '#ef4444' if cnt > 0 else '#10b981'
            null_rows += (
                f"<div style='display:flex;align-items:center;justify-content:space-between;"
                f"padding:6px 0;border-bottom:1px solid #f8fafc;font-size:12px;'>"
                f"<span style='display:flex;align-items:center;gap:7px;color:#374151;'>"
                f"<span style='width:7px;height:7px;border-radius:50%;background:{dot};"
                f"flex-shrink:0;display:inline-block;'></span>{col_name}</span>"
                f"<strong style='color:{clr};'>{cnt:,} null</strong></div>"
            )
        st.markdown(
            f"<div style='background:white;border-radius:12px;padding:12px 16px;"
            f"box-shadow:0 2px 10px rgba(0,0,0,0.07);'>{null_rows}</div>",
            unsafe_allow_html=True
        )

        # ── Column Mapping ─────────────────────────────────────────────────────
        st.markdown("<div style='margin-top:18px'></div>", unsafe_allow_html=True)
        st.markdown("#### Column Mapping")
        st.markdown(
            "<div style='font-size:12px;color:#64748b;margin-bottom:10px;'>"
            "Map your CSV columns to the required fields.</div>",
            unsafe_allow_html=True
        )

        options = ["— select —"] + cols

        def pick(label, key, hints):
            saved = col_map.get(key, '')
            idx   = options.index(saved) if saved in options else 0
            if idx == 0:
                for c in cols:
                    if c.lower().replace(' ', '').replace('_', '') in hints:
                        idx = options.index(c)
                        break
            chosen = st.selectbox(label, options, index=idx, key=f"colmap_{key}")
            if chosen != "— select —":
                st.session_state.col_map[key] = chosen
            return chosen

        cid    = pick("🪪 Customer ID column",        'CustomerID',  ['customerid','custid','customer','idcustomer'])
        idate  = pick("📅 Invoice Date column",       'InvoiceDate', ['invoicedate','tanggal','tglpesan','tgl','date','orderdate'])
        inv_no = pick("🔢 Transaction ID column",     'InvoiceNo',   ['nopesanan','invoiceno','invoiceid','orderid','transactionid','pesanan','orderno','no.pesanan'])
        price  = pick("💰 Total Transactions column", 'UnitPrice',   ['totalharga','totalamount','unitprice','price','harga','amount','total'])

        # ── Mapping status ────────────────────────────────────────────────────
        st.markdown("<div style='margin-top:16px'></div>", unsafe_allow_html=True)
        mapping = {'CustomerID': cid, 'InvoiceDate': idate, 'InvoiceNo': inv_no, 'UnitPrice': price}
        all_mapped   = all(v != "— select —" and v in cols for v in mapping.values())

        status_rows = ""
        for req, chosen in mapping.items():
            ok    = chosen != "— select —" and chosen in cols
            icon  = "✅" if ok else "❌"
            clr   = "#10b981" if ok else "#ef4444"
            label = chosen if ok else "not mapped"
            status_rows += (
                f"<div style='font-size:12px;padding:4px 0;color:{clr};'>"
                f"{icon} <strong>{req}</strong> "
                f"→ <span style='color:#374151;'>{label}</span></div>"
            )
        st.markdown(status_rows, unsafe_allow_html=True)

        if n_missing > 0 or n_dupes > 0:
            st.warning(f"⚠️ {n_missing} missing + {n_dupes} duplicates will be auto-cleaned.")

        st.markdown("<div style='margin-top:14px'></div>", unsafe_allow_html=True)
        if st.button("▶️ Continue to Preprocessing", use_container_width=True, disabled=not all_mapped):
            df_mapped = st.session_state.df.rename(
                columns={v: k for k, v in mapping.items() if v in st.session_state.df.columns}
            )
            st.session_state.df = df_mapped
            st.switch_page('pages/3_RFM_Analysis.py')

        if not all_mapped:
            st.caption("Map all 4 columns above to continue.")

        # Quick navigation
        st.markdown("<div style='margin-top:10px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='font-size:12px;color:#94a3b8;margin-bottom:6px;'>Quick navigation</div>", unsafe_allow_html=True)
        nav1, nav2 = st.columns(2)
        with nav1:
            if st.button("📈 RFM Analysis", use_container_width=True, disabled=not all_mapped):
                df_mapped = st.session_state.df.rename(
                    columns={v: k for k, v in mapping.items() if v in st.session_state.df.columns}
                )
                st.session_state.df = df_mapped
                st.switch_page('pages/3_RFM_Analysis.py')
        with nav2:
            if st.button("⚖️ AHP Weighting", use_container_width=True,
                         disabled=st.session_state.get('rfm_normalized') is None):
                st.switch_page('pages/4_AHP_Weighting.py')
        if st.session_state.get('rfm_normalized') is None:
            st.caption("Complete RFM Analysis first to unlock AHP Weighting.")

    else:
        st.markdown("""
        <div style="background:white;border-radius:12px;padding:60px 20px;text-align:center;
                    box-shadow:0 2px 10px rgba(0,0,0,0.07);border:2px dashed #e2e8f0;">
          <div style="font-size:40px;margin-bottom:10px;">📋</div>
          <div style="font-size:14px;font-weight:600;color:#1e293b;">Awaiting data</div>
          <div style="font-size:12px;color:#64748b;margin-top:4px;">Upload a CSV above to see validation.</div>
        </div>
        """, unsafe_allow_html=True)
