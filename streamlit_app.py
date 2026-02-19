import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime

# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="YoY Entry Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ─────────────────────────────────────────────
# CUSTOM CSS
# ─────────────────────────────────────────────
st.markdown(
    """
    <style>
        /* ── Global ── */
        [data-testid="stAppViewContainer"] { background: #0f1923; }
        [data-testid="stHeader"] { background: transparent; }
        section[data-testid="stSidebar"] { background: #0f1923; }

        /* ── Header banner ── */
        .dash-header {
            background: linear-gradient(135deg, #1a2e45 0%, #0d2137 60%, #0a1a2e 100%);
            border: 1px solid #1e4060;
            border-radius: 12px;
            padding: 28px 36px 20px;
            margin-bottom: 28px;
        }
        .dash-header h1 {
            color: #e8f4fd;
            font-size: 1.85rem;
            font-weight: 700;
            margin: 0 0 4px 0;
            letter-spacing: -0.5px;
        }
        .dash-header p {
            color: #6b9ab8;
            font-size: 0.9rem;
            margin: 0;
        }

        /* ── Filter row card ── */
        .filter-card {
            background: #132030;
            border: 1px solid #1e3a55;
            border-radius: 10px;
            padding: 18px 24px 8px;
            margin-bottom: 32px;
        }
        .filter-label {
            color: #4da3d4;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 1.2px;
            text-transform: uppercase;
            margin-bottom: 6px;
        }

        /* ── Section titles ── */
        .section-title {
            color: #c9e0f0;
            font-size: 1.05rem;
            font-weight: 700;
            letter-spacing: 0.4px;
            padding: 6px 0 14px;
            border-bottom: 1px solid #1e3a55;
            margin-bottom: 20px;
        }
        .section-badge {
            display: inline-block;
            background: #1a3d5c;
            color: #4da3d4;
            font-size: 0.68rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            padding: 3px 10px;
            border-radius: 20px;
            margin-right: 10px;
            border: 1px solid #2a5580;
            vertical-align: middle;
        }

        /* ── KPI metric card ── */
        .kpi-card {
            background: #132030;
            border: 1px solid #1e3a55;
            border-radius: 10px;
            padding: 20px 22px 16px;
            text-align: center;
            height: 100%;
            transition: border-color 0.2s;
        }
        .kpi-card:hover { border-color: #2e6090; }
        .kpi-label {
            color: #5a8fad;
            font-size: 0.72rem;
            font-weight: 700;
            letter-spacing: 1.1px;
            text-transform: uppercase;
            margin-bottom: 8px;
        }
        .kpi-value {
            color: #e8f4fd;
            font-size: 2.0rem;
            font-weight: 800;
            line-height: 1.1;
            margin-bottom: 6px;
            font-variant-numeric: tabular-nums;
        }
        .kpi-value.year1 { color: #4da3d4; }
        .kpi-value.year2 { color: #f5a623; }
        .kpi-sub {
            color: #4a7a96;
            font-size: 0.72rem;
            margin-top: 4px;
        }

        /* ── Category breakdown card ── */
        .cat-card {
            background: #132030;
            border: 1px solid #1e3a55;
            border-radius: 10px;
            padding: 20px 20px 16px;
        }
        .cat-title {
            font-size: 0.78rem;
            font-weight: 700;
            letter-spacing: 1px;
            text-transform: uppercase;
            margin-bottom: 14px;
            padding-bottom: 10px;
            border-bottom: 1px solid #1e3a55;
        }
        .cat-title.ped  { color: #6bcfb0; }
        .cat-title.car  { color: #7abde0; }
        .cat-title.taxi { color: #f0c96b; }
        .cat-row {
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 7px 0;
            border-bottom: 1px solid #0d1f30;
        }
        .cat-row-label { color: #7aaccb; font-size: 0.8rem; }
        .cat-row-val   { color: #d0eaf8; font-size: 0.92rem; font-weight: 700;
                         font-variant-numeric: tabular-nums; }

        /* ── Local filter bar ── */
        .local-filter-bar {
            background: #0d1f30;
            border: 1px solid #1a3450;
            border-radius: 8px;
            padding: 12px 16px 4px;
            margin-bottom: 20px;
        }

        /* ── Chart container ── */
        .chart-wrap {
            background: #132030;
            border: 1px solid #1e3a55;
            border-radius: 10px;
            padding: 20px 16px 8px;
        }

        /* ── Divider ── */
        .section-divider {
            border: none;
            border-top: 1px solid #1a3050;
            margin: 36px 0 32px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# CONSTANTS & SYNTHETIC DATA
# ─────────────────────────────────────────────
MONTH_NAMES = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun",
              "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
ACCESS_POINTS = [
    "Main Gate", "North Entrance", "South Entrance", "East Gate", "West Gate",
]
ENTRY_TYPES = ["Pedestrian", "Car", "Taxi"]
YEARS = [2021, 2022, 2023, 2024, 2025]

COLOR_Y1 = "#4da3d4"   # blue  – Year 1
COLOR_Y2 = "#f5a623"   # amber – Year 2

PLOTLY_BASE = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="#7aaccb", family="sans-serif", size=12),
    margin=dict(l=10, r=10, t=46, b=10),
    legend=dict(
        bgcolor="rgba(13,31,48,0.85)",
        bordercolor="#1e3a55",
        borderwidth=1,
        font=dict(color="#a0c8e0", size=11),
    ),
    xaxis=dict(gridcolor="#1a3050", linecolor="#1a3050",
               tickcolor="#1a3050", zerolinecolor="#1a3050"),
    yaxis=dict(gridcolor="#1a3050", linecolor="#1a3050",
               tickcolor="#1a3050", zerolinecolor="#1a3050"),
)


@st.cache_data
def generate_data() -> pd.DataFrame:
    rng = np.random.default_rng(42)
    base = {"Pedestrian": 1_400, "Car": 920, "Taxi": 380}
    ap_mult = {
        "Main Gate":      2.10,
        "North Entrance": 1.55,
        "South Entrance": 1.25,
        "East Gate":      0.95,
        "West Gate":      0.70,
    }
    y_growth = {2021: 1.00, 2022: 1.07, 2023: 1.15, 2024: 1.24, 2025: 1.33}
    seasonal = [
        0.84, 0.87, 0.94, 1.00, 1.06, 1.11,
        1.14, 1.10, 1.04, 0.97, 0.91, 1.22,
    ]
    records = []
    for year in YEARS:
        for month in range(1, 13):
            for ap in ACCESS_POINTS:
                for et in ENTRY_TYPES:
                    v = (base[et] * ap_mult[ap]
                         * y_growth[year] * seasonal[month - 1]
                         * rng.normal(1.0, 0.055))
                    records.append({
                        "year": year,
                        "month": month,
                        "month_abbr": MONTH_ABBR[month - 1],
                        "access_point": ap,
                        "entry_type": et,
                        "entries": max(0, int(v)),
                    })
    return pd.DataFrame(records)


df = generate_data()


# ─────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────
def fmt(n: int) -> str:
    return f"{int(n):,}"


def pct_delta(v1: int, v2: int) -> float:
    return (v2 - v1) / v1 * 100 if v1 else 0.0


def delta_color(d: float) -> str:
    return "#3ecf8e" if d >= 0 else "#e05c5c"


def delta_arrow(d: float) -> str:
    return "▲" if d >= 0 else "▼"


# ─────────────────────────────────────────────
# HEADER
# ─────────────────────────────────────────────
st.markdown(
    """
    <div class="dash-header">
        <h1>📊 Year-over-Year Entry Comparison Dashboard</h1>
        <p>
            Analyze entry volumes across access points, transport modes, and time
            periods — select a reference month and two comparison years below.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
# GLOBAL FILTERS
# ─────────────────────────────────────────────
st.markdown('<div class="filter-card">', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#4da3d4;font-size:0.72rem;font-weight:700;'
    'letter-spacing:1.2px;text-transform:uppercase;margin-bottom:12px;">'
    "🎚&nbsp; Global Filters</p>",
    unsafe_allow_html=True,
)
fc1, fc2, fc3 = st.columns(3)

with fc1:
    st.markdown('<div class="filter-label">Filter 1 — Reference Month</div>',
                unsafe_allow_html=True)
    selected_month_name: str = st.selectbox(
        "month_sel", MONTH_NAMES, index=5, label_visibility="collapsed"
    )
    selected_month: int = MONTH_NAMES.index(selected_month_name) + 1

with fc2:
    st.markdown('<div class="filter-label">Filter 2 — Year 1 (Baseline)</div>',
                unsafe_allow_html=True)
    year1: int = st.selectbox(
        "year1_sel", YEARS, index=2, label_visibility="collapsed"
    )

with fc3:
    st.markdown('<div class="filter-label">Filter 3 — Year 2 (Comparison)</div>',
                unsafe_allow_html=True)
    year2: int = st.selectbox(
        "year2_sel", YEARS, index=3, label_visibility="collapsed"
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Derived slices ────────────────────────────
ytd_y1 = df[(df["year"] == year1) & (df["month"] <= selected_month)]
ytd_y2 = df[(df["year"] == year2) & (df["month"] <= selected_month)]
mon_y1 = df[(df["year"] == year1) & (df["month"] == selected_month)]
mon_y2 = df[(df["year"] == year2) & (df["month"] == selected_month)]

ytd_tot_y1 = int(ytd_y1["entries"].sum())
ytd_tot_y2 = int(ytd_y2["entries"].sum())
mon_tot_y1 = int(mon_y1["entries"].sum())
mon_tot_y2 = int(mon_y2["entries"].sum())


# ═════════════════════════════════════════════
# SECTION 1 — YTD ENTRIES
# ═════════════════════════════════════════════
st.markdown(
    f'<div class="section-title">'
    f'<span class="section-badge">01</span>'
    f'Year-to-Date Entries &nbsp;·&nbsp; Jan – {selected_month_name}'
    f'</div>',
    unsafe_allow_html=True,
)

s1a, s1b, s1c = st.columns(3)

ytd_diff  = ytd_tot_y2 - ytd_tot_y1
ytd_pct   = pct_delta(ytd_tot_y1, ytd_tot_y2)
ytd_color = delta_color(ytd_pct)
ytd_arrow = delta_arrow(ytd_pct)

with s1a:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">YTD Total &mdash; {year1}</div>
            <div class="kpi-value year1">{fmt(ytd_tot_y1)}</div>
            <div class="kpi-sub">Jan &ndash; {selected_month_name} {year1}</div>
        </div>
        """, unsafe_allow_html=True)

with s1b:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">YTD Total &mdash; {year2}</div>
            <div class="kpi-value year2">{fmt(ytd_tot_y2)}</div>
            <div class="kpi-sub">Jan &ndash; {selected_month_name} {year2}</div>
        </div>
        """, unsafe_allow_html=True)

with s1c:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">YoY Change (YTD)</div>
            <div class="kpi-value" style="color:{ytd_color};font-size:1.75rem;">
                {ytd_arrow} {abs(ytd_pct):.1f}%
            </div>
            <div class="kpi-sub" style="color:{ytd_color};">
                {("+" if ytd_diff >= 0 else "")}{fmt(ytd_diff)} entries
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# SECTION 2 — MONTHLY ENTRIES COMPARISON
# ═════════════════════════════════════════════
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">'
    f'<span class="section-badge">02</span>'
    f'Monthly Entries Comparison &nbsp;·&nbsp; {selected_month_name} Only'
    f'</div>',
    unsafe_allow_html=True,
)

m_diff  = mon_tot_y2 - mon_tot_y1
m_pct   = pct_delta(mon_tot_y1, mon_tot_y2)
m_color = delta_color(m_pct)
m_arrow = delta_arrow(m_pct)

s2a, s2b, s2c, s2d = st.columns(4)

with s2a:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{selected_month_name} {year1}</div>
            <div class="kpi-value year1">{fmt(mon_tot_y1)}</div>
            <div class="kpi-sub">Total entries</div>
        </div>
        """, unsafe_allow_html=True)

with s2b:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">{selected_month_name} {year2}</div>
            <div class="kpi-value year2">{fmt(mon_tot_y2)}</div>
            <div class="kpi-sub">Total entries</div>
        </div>
        """, unsafe_allow_html=True)

with s2c:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">Absolute Change</div>
            <div class="kpi-value" style="color:{m_color};font-size:1.75rem;">
                {("+" if m_diff >= 0 else "")}{fmt(m_diff)}
            </div>
            <div class="kpi-sub">{year2} vs {year1}</div>
        </div>
        """, unsafe_allow_html=True)

with s2d:
    st.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-label">% Change</div>
            <div class="kpi-value" style="color:{m_color};font-size:1.75rem;">
                {m_arrow} {abs(m_pct):.1f}%
            </div>
            <div class="kpi-sub">{year2} vs {year1}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# SECTION 3 — YTD CATEGORY BREAKDOWN
# ═════════════════════════════════════════════
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">'
    f'<span class="section-badge">03</span>'
    f'YTD Category Breakdown &nbsp;·&nbsp; Pedestrian · Car · Taxi'
    f'</div>',
    unsafe_allow_html=True,
)

cat_configs = [
    ("Pedestrian", "ped",  "🚶"),
    ("Car",        "car",  "🚗"),
    ("Taxi",       "taxi", "🚕"),
]

cat_cols = st.columns(3)
for col, (etype, css_cls, icon) in zip(cat_cols, cat_configs):
    v1 = int(ytd_y1[ytd_y1["entry_type"] == etype]["entries"].sum())
    v2 = int(ytd_y2[ytd_y2["entry_type"] == etype]["entries"].sum())
    diff   = v2 - v1
    pct    = pct_delta(v1, v2)
    dc     = delta_color(pct)
    da     = delta_arrow(pct)
    sh_y1  = (v1 / ytd_tot_y1 * 100) if ytd_tot_y1 else 0
    sh_y2  = (v2 / ytd_tot_y2 * 100) if ytd_tot_y2 else 0

    with col:
        st.markdown(
            f"""
            <div class="cat-card">
                <div class="cat-title {css_cls}">{icon}&nbsp;&nbsp;{etype}</div>

                <div class="cat-row">
                    <span class="cat-row-label">{year1} &nbsp;(YTD)</span>
                    <span class="cat-row-val">{fmt(v1)}</span>
                </div>
                <div class="cat-row">
                    <span class="cat-row-label">{year2} &nbsp;(YTD)</span>
                    <span class="cat-row-val">{fmt(v2)}</span>
                </div>
                <div class="cat-row">
                    <span class="cat-row-label">YoY Change</span>
                    <span class="cat-row-val" style="color:{dc};">
                        {da} {abs(pct):.1f}%
                        <small style="font-weight:400;font-size:0.74rem;opacity:0.85;">
                            &nbsp;({("+" if diff >= 0 else "")}{fmt(diff)})
                        </small>
                    </span>
                </div>
                <div class="cat-row" style="border:none;padding-top:10px;">
                    <span class="cat-row-label">Mix share {year1}</span>
                    <span class="cat-row-val">{sh_y1:.1f}%</span>
                </div>
                <div class="cat-row" style="border:none;">
                    <span class="cat-row-label">Mix share {year2}</span>
                    <span class="cat-row-val">{sh_y2:.1f}%</span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# SECTION 4 — ENTRIES BY ACCESS POINT
# ═════════════════════════════════════════════
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">'
    f'<span class="section-badge">04</span>'
    f'Entries by Access Point &nbsp;·&nbsp; YTD Jan – {selected_month_name}'
    f'</div>',
    unsafe_allow_html=True,
)

# ── Local filters ─────────────────────────────
st.markdown('<div class="local-filter-bar">', unsafe_allow_html=True)
st.markdown(
    '<p style="color:#4da3d4;font-size:0.68rem;font-weight:700;'
    'letter-spacing:1.1px;text-transform:uppercase;margin-bottom:10px;">'
    "⚙&nbsp; Local Filters</p>",
    unsafe_allow_html=True,
)
lf1, lf2 = st.columns(2)
with lf1:
    sel_ap = st.multiselect(
        "Access Point",
        ACCESS_POINTS,
        default=ACCESS_POINTS,
        key="lf_ap",
    )
with lf2:
    sel_et = st.multiselect(
        "Entry Type",
        ENTRY_TYPES,
        default=ENTRY_TYPES,
        key="lf_et",
    )
st.markdown("</div>", unsafe_allow_html=True)

ap_f = sel_ap if sel_ap else ACCESS_POINTS
et_f = sel_et if sel_et else ENTRY_TYPES

def ap_totals(base_df, aps, ets):
    filtered = base_df[
        base_df["access_point"].isin(aps) & base_df["entry_type"].isin(ets)
    ]
    return (
        filtered.groupby("access_point")["entries"]
        .sum()
        .reindex(aps, fill_value=0)
    )

ap_vals_y1 = ap_totals(ytd_y1, ap_f, et_f)
ap_vals_y2 = ap_totals(ytd_y2, ap_f, et_f)

fig_ap = go.Figure()
fig_ap.add_trace(go.Bar(
    name=str(year1),
    x=ap_f,
    y=ap_vals_y1.values,
    marker_color=COLOR_Y1,
    marker_line_color="rgba(0,0,0,0)",
    text=[fmt(v) for v in ap_vals_y1.values],
    textposition="outside",
    textfont=dict(color=COLOR_Y1, size=11),
))
fig_ap.add_trace(go.Bar(
    name=str(year2),
    x=ap_f,
    y=ap_vals_y2.values,
    marker_color=COLOR_Y2,
    marker_line_color="rgba(0,0,0,0)",
    text=[fmt(v) for v in ap_vals_y2.values],
    textposition="outside",
    textfont=dict(color=COLOR_Y2, size=11),
))
fig_ap.update_layout(
    **PLOTLY_BASE,
    barmode="group",
    bargap=0.22,
    bargroupgap=0.06,
    height=400,
    yaxis_title="Total Entries (YTD)",
    title=dict(
        text=(
            f"YTD Entries by Access Point"
            f"  ·  Entry types: {', '.join(et_f) if et_f else 'All'}"
        ),
        font=dict(color="#a0c8e0", size=13),
        x=0,
    ),
)

st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
st.plotly_chart(fig_ap, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)


# ═════════════════════════════════════════════
# SECTION 5 — TREND ANALYSIS LINE CHART
# ═════════════════════════════════════════════
st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
st.markdown(
    f'<div class="section-title">'
    f'<span class="section-badge">05</span>'
    f'Trend Analysis &nbsp;·&nbsp; Monthly Entries {year1} vs {year2}'
    f'</div>',
    unsafe_allow_html=True,
)

trend_y1 = (
    df[df["year"] == year1]
    .groupby("month")["entries"].sum()
    .reindex(range(1, 13), fill_value=0)
)
trend_y2 = (
    df[df["year"] == year2]
    .groupby("month")["entries"].sum()
    .reindex(range(1, 13), fill_value=0)
)

fig_trend = go.Figure()

# Year 1 line
fig_trend.add_trace(go.Scatter(
    x=MONTH_ABBR,
    y=trend_y1.values,
    mode="lines+markers",
    name=str(year1),
    line=dict(color=COLOR_Y1, width=2.8),
    marker=dict(
        color=COLOR_Y1,
        size=[11 if m == selected_month else 6 for m in range(1, 13)],
        symbol=["diamond" if m == selected_month else "circle" for m in range(1, 13)],
        line=dict(color="#0f1923", width=2),
    ),
    fill="tozeroy",
    fillcolor="rgba(77,163,212,0.08)",
    hovertemplate=(
        f"<b>{year1}</b> · %{{x}}"
        "<br>Entries: <b>%{y:,}</b><extra></extra>"
    ),
))

# Year 2 line
fig_trend.add_trace(go.Scatter(
    x=MONTH_ABBR,
    y=trend_y2.values,
    mode="lines+markers",
    name=str(year2),
    line=dict(color=COLOR_Y2, width=2.8),
    marker=dict(
        color=COLOR_Y2,
        size=[11 if m == selected_month else 6 for m in range(1, 13)],
        symbol=["diamond" if m == selected_month else "circle" for m in range(1, 13)],
        line=dict(color="#0f1923", width=2),
    ),
    fill="tozeroy",
    fillcolor="rgba(245,166,35,0.08)",
    hovertemplate=(
        f"<b>{year2}</b> · %{{x}}"
        "<br>Entries: <b>%{y:,}</b><extra></extra>"
    ),
))

# Reference-month vertical dashed line
fig_trend.add_vline(
    x=MONTH_ABBR[selected_month - 1],
    line_width=1.5,
    line_dash="dot",
    line_color="#3a6080",
    annotation_text=f"  {selected_month_name[:3]}",
    annotation_font=dict(color="#5a9abf", size=11),
    annotation_position="top",
)

fig_trend.update_layout(
    **PLOTLY_BASE,
    height=430,
    hovermode="x unified",
    yaxis_title="Total Monthly Entries",
    xaxis_title="Month",
    title=dict(
        text=(
            f"Full-Year Monthly Trend  ·  {year1} vs {year2}"
            f"  ·  ◆ = {selected_month_name} (reference month)"
        ),
        font=dict(color="#a0c8e0", size=13),
        x=0,
    ),
)

st.markdown('<div class="chart-wrap">', unsafe_allow_html=True)
st.plotly_chart(fig_trend, use_container_width=True)
st.markdown("</div>", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# FOOTER
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown(
    f"""
    <div style="text-align:center;color:#1e3a55;font-size:0.72rem;
                padding:12px 0 8px;border-top:1px solid #132030;">
        YoY Entry Dashboard &nbsp;·&nbsp;
        Showing data for Jan–{selected_month_name} (YTD) &amp; full-year trend
        &nbsp;·&nbsp; Comparing <strong style="color:#2a5580;">{year1}</strong>
        vs <strong style="color:#2a5580;">{year2}</strong>
    </div>
    """,
    unsafe_allow_html=True,
)
