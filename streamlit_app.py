"""
YoY Visitor Entry Flow Dashboard — Streamlit
Tema claro, diseño moderno con datos sintéticos.
Run: streamlit run streamlit_app.py
"""

import math
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots

# ── Page config ───────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Visitor Entry Flow · YoY",
    page_icon="🏬",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── Global CSS ────────────────────────────────────────────────────────────
st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap');

  html, body, [class*="css"] {
    font-family: 'Inter', sans-serif !important;
  }
  .stApp { background: #F5F6FA; }

  /* Hide Streamlit chrome */
  #MainMenu, footer, header { visibility: hidden; }
  .block-container { padding: 0 !important; max-width: 100% !important; }

  /* Gradient top accent bar */
  .top-bar {
    height: 4px;
    background: linear-gradient(90deg, #2563EB 0%, #818CF8 55%, #F59E0B 100%);
    width: 100%;
  }

  /* Header */
  .dash-header {
    background: #FFFFFF;
    border-bottom: 1px solid #E8EAF0;
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 1px 3px rgba(17,24,39,0.05);
  }

  /* Cards */
  .metric-card {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(17,24,39,0.06), 0 4px 16px rgba(17,24,39,0.04);
  }
  .metric-card.accent { border-left: 4px solid #2563EB; }

  .cat-card {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(17,24,39,0.06), 0 4px 16px rgba(17,24,39,0.04);
  }

  .chart-card {
    background: #FFFFFF;
    border: 1px solid #E8EAF0;
    border-radius: 14px;
    padding: 20px 24px;
    box-shadow: 0 1px 3px rgba(17,24,39,0.06), 0 4px 16px rgba(17,24,39,0.04);
  }

  /* Pills */
  .pill-pos {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;
    background: #ECFDF5; color: #059669; border: 1px solid #A7F3D0;
  }
  .pill-neg {
    display: inline-flex; align-items: center; gap: 4px;
    padding: 3px 10px; border-radius: 20px; font-size: 12px; font-weight: 700;
    background: #FEF2F2; color: #DC2626; border: 1px solid #FECACA;
  }
  .yr1-tag {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700;
    background: #EFF6FF; color: #2563EB; text-transform: uppercase;
  }
  .yr2-tag {
    display: inline-flex; align-items: center; gap: 5px;
    padding: 2px 9px; border-radius: 20px; font-size: 9px; font-weight: 700;
    background: #FFFBEB; color: #B45309; text-transform: uppercase;
  }

  /* Section headers */
  .section-label {
    font-size: 10px; font-weight: 700; color: #6B7280;
    text-transform: uppercase; letter-spacing: 0.1em;
    display: flex; align-items: center; gap: 8px; margin-bottom: 12px;
  }
  .section-line { flex: 1; height: 1px; background: #E8EAF0; }

  /* Big numbers */
  .big-num { font-size: 30px; font-weight: 800; letter-spacing: -0.03em; line-height: 1; }
  .big-num-muted { font-size: 30px; font-weight: 800; letter-spacing: -0.03em; line-height: 1; color: #9CA3AF; }
  .label-sm { font-size: 10px; font-weight: 700; color: #9CA3AF; text-transform: uppercase; letter-spacing: 0.07em; margin-bottom: 10px; }

  /* Streamlit selectbox overrides */
  div[data-baseweb="select"] {
    border-radius: 8px !important;
  }
  div[data-baseweb="select"] > div {
    background: #FFFFFF !important;
    border: 1px solid #E8EAF0 !important;
    border-radius: 8px !important;
    font-size: 13px !important;
    font-weight: 600 !important;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05) !important;
  }
  label[data-testid="stWidgetLabel"] p {
    font-size: 9px !important;
    font-weight: 700 !important;
    color: #9CA3AF !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
  }
</style>
""", unsafe_allow_html=True)


# ── Synthetic Data ────────────────────────────────────────────────────────
MONTHS = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
ACCESS_POINTS = ["Gate 1","Gate 3","Plaza Vea","Gate 7","Gate 9"]
YEARS = [2022, 2023, 2024, 2025, 2026]

def _s(n):
    x = math.sin(n * 9301 + 49297) * 233280
    return x - math.floor(x)

def _rng(base, variance, seed):
    return round(base + (_s(seed) - 0.5) * variance * 2)

@st.cache_data
def build_raw():
    raw = {}
    for yr in YEARS:
        raw[yr] = {}
        for mi, m in enumerate(MONTHS):
            raw[yr][m] = {}
            for ai, ap in enumerate(ACCESS_POINTS):
                seed = yr * 1000 + mi * 10 + ai
                f = 1 + (yr - 2022) * 0.08
                raw[yr][m][ap] = {
                    "Pedestrian": _rng(round(90000 * f), 25000, seed + 1),
                    "Car":        _rng(round(40000 * f), 12000, seed + 2),
                    "Taxi":       _rng(round(18000 * f), 8000,  seed + 3),
                }
    return raw

RAW = build_raw()

def get_ap(yr, month, ap, etype):
    aps   = ACCESS_POINTS if ap == "All" else [ap]
    types = ["Pedestrian", "Car", "Taxi"] if etype == "All" else [etype]
    return sum(RAW[yr][month][a][t] for a in aps for t in types)

def get_ytd(yr, upto, etype="All"):
    idx = MONTHS.index(upto)
    return sum(get_ap(yr, m, "All", etype) for m in MONTHS[:idx + 1])

def get_monthly(yr, month, etype="All"):
    return get_ap(yr, month, "All", etype)

def fmt_full(n): return f"{n:,}"
def fmt(n):
    if n >= 1_000_000: return f"{n/1_000_000:.1f}M"
    if n >= 1_000:     return f"{n/1_000:.0f}K"
    return str(n)
def calc_pct(a, b): return round((a - b) / b * 100, 1) if b else 0.0

AP_COLORS = ["#2563EB", "#6366F1", "#F59E0B", "#10B981", "#EF4444"]
CAT_COLORS = {"Pedestrian": "#6366F1", "Car": "#10B981", "Taxi": "#F59E0B"}
CAT_BG     = {"Pedestrian": "#EEF2FF", "Car": "#ECFDF5",  "Taxi": "#FFFBEB"}
CAT_ICONS  = {"Pedestrian": "🚶", "Car": "🚗", "Taxi": "🚕"}


# ── Helpers ───────────────────────────────────────────────────────────────
def delta_pill(val: float) -> str:
    cls = "pill-pos" if val >= 0 else "pill-neg"
    arrow = "▲" if val >= 0 else "▼"
    return f'<span class="{cls}">{arrow} {abs(val)}%</span>'

def section_header(icon: str, label: str):
    st.markdown(f"""
    <div class="section-label">
      <span>{icon}</span><span>{label}</span>
      <div class="section-line"></div>
    </div>""", unsafe_allow_html=True)


# ── TOP BAR + HEADER ──────────────────────────────────────────────────────
st.markdown('<div class="top-bar"></div>', unsafe_allow_html=True)

# Header row with logo + filters
header_l, header_r = st.columns([3, 2])

with header_l:
    st.markdown("""
    <div style="padding: 14px 28px 10px 28px; display:flex; align-items:center; gap:14px;">
      <div style="background:#EFF6FF; border:1px solid #BFDBFE; border-radius:10px;
                  padding:7px 11px; text-align:center; line-height:1.2;">
        <div style="font-size:11px; font-weight:900; color:#2563EB;">JOCKEY</div>
        <div style="font-size:8px; font-weight:700; color:#2563EB; letter-spacing:.05em;">PLAZA</div>
      </div>
      <div>
        <div style="font-size:18px; font-weight:900; color:#111827; letter-spacing:-0.02em; line-height:1;">
          VISITOR ENTRY FLOW
        </div>
        <div style="font-size:11px; color:#6B7280; margin-top:3px; font-weight:500;">
          Year-over-Year Comparison &nbsp;·&nbsp; By Access Point
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with header_r:
    st.markdown('<div style="height:10px;"></div>', unsafe_allow_html=True)
    fc1, fc2, fc3 = st.columns(3)
    with fc1:
        year1 = st.selectbox("Year 1", [y for y in YEARS], index=YEARS.index(2026), key="year1")
    with fc2:
        yr2_opts = [y for y in YEARS if y != year1]
        year2 = st.selectbox("Year 2", yr2_opts, index=yr2_opts.index(2024) if 2024 in yr2_opts else 0, key="year2")
    with fc3:
        month = st.selectbox("Month", MONTHS, index=0, key="month")

st.markdown('<div style="height:2px; background:#E8EAF0; margin: 0 0 20px 0;"></div>', unsafe_allow_html=True)

# ── Pre-compute values ────────────────────────────────────────────────────
ytd1 = get_ytd(year1, month)
ytd2 = get_ytd(year2, month)
mo1  = get_monthly(year1, month)
mo2  = get_monthly(year2, month)

ped1 = get_ytd(year1, month, "Pedestrian")
ped2 = get_ytd(year2, month, "Pedestrian")
car1 = get_ytd(year1, month, "Car")
car2 = get_ytd(year2, month, "Car")
tax1 = get_ytd(year1, month, "Taxi")
tax2 = get_ytd(year2, month, "Taxi")
tot1 = ped1 + car1 + tax1 or 1

# ── SECTION 1 — YTD + Monthly ─────────────────────────────────────────────
with st.container():
    st.markdown('<div style="padding: 0 28px;">', unsafe_allow_html=True)
    section_header("◈", f"Year-to-Date Entries — Jan through {month}")

    col1, col2 = st.columns(2, gap="medium")

    for col, label, v1, v2, accent in [
        (col1, f"YTD Entries · Jan – {month}",     ytd1, ytd2, True),
        (col2, f"Monthly Entries · {month} only",  mo1,  mo2,  False),
    ]:
        diff = v1 - v2
        d    = calc_pct(v1, v2)
        border_left = "border-left: 4px solid #2563EB;" if accent else ""
        with col:
            st.markdown(f"""
            <div class="metric-card" style="{border_left}">
              <div class="label-sm">{label}</div>
              <div style="display:flex; gap:24px; align-items:flex-end; flex-wrap:wrap;">
                <div>
                  <div class="yr1-tag" style="margin-bottom:8px;">
                    <div style="width:6px;height:6px;border-radius:50%;background:#2563EB;"></div>
                    {year1}
                  </div>
                  <div class="big-num" style="color:#111827;">{fmt_full(v1)}</div>
                </div>
                <div>
                  <div class="yr2-tag" style="margin-bottom:8px;">
                    <div style="width:6px;height:6px;border-radius:50%;background:#F59E0B;"></div>
                    {year2}
                  </div>
                  <div class="big-num-muted">{fmt_full(v2)}</div>
                </div>
                <div style="margin-left:auto; text-align:right;">
                  <div style="font-size:10px;font-weight:600;color:#9CA3AF;text-transform:uppercase;letter-spacing:.07em;margin-bottom:4px;">Difference</div>
                  <div style="font-size:15px;font-weight:700;color:{'#059669' if diff>=0 else '#DC2626'};margin-bottom:6px;">
                    {'+'if diff>=0 else ''}{fmt_full(diff)}
                  </div>
                  {delta_pill(d)}
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

# ── SECTION 2 — Category Breakdown ────────────────────────────────────────
with st.container():
    st.markdown('<div style="padding: 0 28px;">', unsafe_allow_html=True)
    section_header("◉", "YTD Breakdown by Entry Type")

    cc1, cc2, cc3 = st.columns(3, gap="medium")

    for col, cat, v1, v2 in [
        (cc1, "Pedestrian", ped1, ped2),
        (cc2, "Car",        car1, car2),
        (cc3, "Taxi",       tax1, tax2),
    ]:
        d      = calc_pct(v1, v2)
        clr    = CAT_COLORS[cat]
        bgclr  = CAT_BG[cat]
        icon   = CAT_ICONS[cat]
        pct_of = round(v1 / tot1 * 100, 1)

        with col:
            st.markdown(f"""
            <div class="cat-card">
              <div style="height:4px; background:{clr};"></div>
              <div style="padding:16px 20px;">
                <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:14px;">
                  <div style="display:flex; align-items:center; gap:8px;">
                    <span style="font-size:22px;">{icon}</span>
                    <div>
                      <div style="font-size:11px;font-weight:700;color:#111827;text-transform:uppercase;letter-spacing:.07em;">{cat}</div>
                      <div style="font-size:10px;color:#9CA3AF;margin-top:1px;">{pct_of}% of total YTD</div>
                    </div>
                  </div>
                  {delta_pill(d)}
                </div>
                <div style="display:flex; gap:8px;">
                  <div style="flex:1; background:{bgclr}; border:1px solid #E8EAF0; border-radius:10px; padding:10px 12px;">
                    <div style="font-size:9px;font-weight:700;color:{clr};text-transform:uppercase;margin-bottom:4px;">{year1}</div>
                    <div style="font-size:18px;font-weight:800;color:#111827;letter-spacing:-0.02em;">{fmt_full(v1)}</div>
                  </div>
                  <div style="flex:1; background:#F9FAFB; border:1px solid #E8EAF0; border-radius:10px; padding:10px 12px;">
                    <div style="font-size:9px;font-weight:700;color:#9CA3AF;text-transform:uppercase;margin-bottom:4px;">{year2}</div>
                    <div style="font-size:18px;font-weight:800;color:#9CA3AF;letter-spacing:-0.02em;">{fmt_full(v2)}</div>
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

# ── SECTION 3 — Bar Chart by Access Point ────────────────────────────────
with st.container():
    st.markdown('<div style="padding: 0 28px;">', unsafe_allow_html=True)
    section_header("◐", "Entries by Access Point")

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    fh1, fh2, fh3 = st.columns([3, 1, 1])
    with fh1:
        st.markdown(f"""
        <div>
          <div style="font-size:14px;font-weight:700;color:#111827;">Monthly Comparison by Gate</div>
          <div style="font-size:10px;color:#6B7280;margin-top:3px;">{month} · Selected filters apply</div>
        </div>
        """, unsafe_allow_html=True)
    with fh2:
        chart_ap = st.selectbox("Access Point", ["All"] + ACCESS_POINTS, key="chart_ap")
    with fh3:
        chart_type = st.selectbox("Entry Type", ["All", "Pedestrian", "Car", "Taxi"], key="chart_type")

    aps_to_show = ACCESS_POINTS if chart_ap == "All" else [chart_ap]
    bar_data = []
    for i, ap in enumerate(aps_to_show):
        bar_data.append({
            "gate": ap.replace("Gate ", "G"),
            "full_name": ap,
            str(year1): get_ap(year1, month, ap, chart_type),
            str(year2): get_ap(year2, month, ap, chart_type),
            "color_idx": ACCESS_POINTS.index(ap),
        })
    bar_df = pd.DataFrame(bar_data)

    fig_bar = go.Figure()
    for _, row in bar_df.iterrows():
        clr = AP_COLORS[int(row["color_idx"]) % len(AP_COLORS)]
        fig_bar.add_trace(go.Bar(
            name=str(year1), x=[row["gate"]], y=[row[str(year1)]],
            marker_color=clr, marker_line_width=0,
            showlegend=(_ == bar_df.index[0]),
            legendgroup="yr1",
        ))
        fig_bar.add_trace(go.Bar(
            name=str(year2), x=[row["gate"]], y=[row[str(year2)]],
            marker_color=clr, marker_opacity=0.3, marker_line_width=0,
            showlegend=(_ == bar_df.index[0]),
            legendgroup="yr2",
        ))

    # Rebuild with proper legends
    fig_bar = go.Figure()
    for i, row in bar_df.iterrows():
        clr = AP_COLORS[int(row["color_idx"]) % len(AP_COLORS)]
        fig_bar.add_trace(go.Bar(
            name=f"{row['full_name']} {year1}",
            x=[row["gate"]], y=[row[str(year1)]],
            marker_color=clr, marker_line_width=0,
            legendgroup=row["gate"],
            showlegend=(i == bar_df.index[0]),
            text=[fmt(row[str(year1)])], textposition="outside",
            textfont=dict(size=10, color=clr, family="Inter"),
        ))
        fig_bar.add_trace(go.Bar(
            name=f"{row['full_name']} {year2}",
            x=[row["gate"]], y=[row[str(year2)]],
            marker_color=clr, marker_opacity=0.32, marker_line_width=0,
            legendgroup=row["gate"],
            showlegend=False,
            text=[fmt(row[str(year2)])], textposition="outside",
            textfont=dict(size=10, color="#9CA3AF", family="Inter"),
        ))

    fig_bar.update_layout(
        barmode="group", bargap=0.30, bargroupgap=0.06,
        plot_bgcolor="white", paper_bgcolor="white",
        height=260, margin=dict(l=0, r=0, t=10, b=10),
        font=dict(family="Inter", size=11, color="#6B7280"),
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(size=11, color="#6B7280")),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", zeroline=False,
                   showline=False, tickfont=dict(size=10, color="#9CA3AF"),
                   tickformat=",.0f"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0,
            font=dict(size=11, color="#6B7280"),
        ),
        showlegend=False,
    )

    # Custom legend via annotation
    for i, ap in enumerate(aps_to_show):
        clr = AP_COLORS[ACCESS_POINTS.index(ap) % len(AP_COLORS)]
        fig_bar.add_annotation(
            x=0.0 + i * 0.14, y=1.08, xref="paper", yref="paper",
            text=f"<b>■</b> {ap.replace('Gate ','G')}",
            font=dict(size=10, color=clr, family="Inter"),
            showarrow=False, align="left",
        )

    st.plotly_chart(fig_bar, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown('<div style="height:20px;"></div>', unsafe_allow_html=True)

# ── SECTION 4 — Trend Line Chart ──────────────────────────────────────────
with st.container():
    st.markdown('<div style="padding: 0 28px;">', unsafe_allow_html=True)
    section_header("◷", "Monthly Trend Analysis — Full Year")

    st.markdown('<div class="chart-card">', unsafe_allow_html=True)

    st.markdown(f"""
    <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:16px;">
      <div>
        <div style="font-size:14px;font-weight:700;color:#111827;">Total Entries per Month</div>
        <div style="font-size:10px;color:#6B7280;margin-top:3px;">
          Selected month highlighted &nbsp;·&nbsp; Click on the delta row below to change month
        </div>
      </div>
      <div style="display:flex; gap:20px; align-items:center;">
        <div style="display:flex;align-items:center;gap:6px;">
          <svg width="32" height="12">
            <line x1="0" y1="6" x2="32" y2="6" stroke="#2563EB" stroke-width="2.5" stroke-linecap="round"/>
            <circle cx="16" cy="6" r="4" fill="#2563EB"/>
          </svg>
          <span style="font-size:12px;font-weight:700;color:#2563EB;">{year1}</span>
        </div>
        <div style="display:flex;align-items:center;gap:6px;">
          <svg width="32" height="12">
            <line x1="0" y1="6" x2="32" y2="6" stroke="#F59E0B" stroke-width="2.5"
              stroke-dasharray="6,3" stroke-linecap="round"/>
            <circle cx="16" cy="6" r="4" fill="#F59E0B"/>
          </svg>
          <span style="font-size:12px;font-weight:700;color:#F59E0B;">{year2}</span>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    trend_data = {
        "month": MONTHS,
        str(year1): [get_monthly(year1, m) for m in MONTHS],
        str(year2): [get_monthly(year2, m) for m in MONTHS],
    }
    trend_df = pd.DataFrame(trend_data)
    sel_idx  = MONTHS.index(month)

    fig_line = go.Figure()

    # Area fill under Y1
    fig_line.add_trace(go.Scatter(
        x=MONTHS, y=trend_df[str(year1)],
        mode="none", fill="tozeroy",
        fillcolor="rgba(37,99,235,0.07)",
        showlegend=False, hoverinfo="skip",
    ))

    # Y1 line
    fig_line.add_trace(go.Scatter(
        x=MONTHS, y=trend_df[str(year1)],
        mode="lines+markers",
        name=str(year1),
        line=dict(color="#2563EB", width=2.5),
        marker=dict(
            size=[10 if i == sel_idx else 5 for i in range(12)],
            color=["#2563EB" if i == sel_idx else "white" for i in range(12)],
            line=dict(color="#2563EB", width=2),
        ),
        hovertemplate=f"<b>{year1}</b> %{{x}}: %{{y:,.0f}}<extra></extra>",
    ))

    # Y2 line
    fig_line.add_trace(go.Scatter(
        x=MONTHS, y=trend_df[str(year2)],
        mode="lines+markers",
        name=str(year2),
        line=dict(color="#F59E0B", width=2.5, dash="dot"),
        marker=dict(
            size=[10 if i == sel_idx else 5 for i in range(12)],
            color=["#F59E0B" if i == sel_idx else "white" for i in range(12)],
            line=dict(color="#F59E0B", width=2),
        ),
        hovertemplate=f"<b>{year2}</b> %{{x}}: %{{y:,.0f}}<extra></extra>",
    ))

    # Vertical reference line for selected month
    fig_line.add_shape(
        type="line", x0=month, x1=month,
        y0=0, y1=1, yref="paper",
        line=dict(color="#2563EB", width=1.5, dash="dot"),
    )

    # Data labels for selected month
    y1_sel = trend_df[str(year1)][sel_idx]
    y2_sel = trend_df[str(year2)][sel_idx]
    fig_line.add_annotation(
        x=month, y=y1_sel, text=f"<b>{fmt(y1_sel)}</b>",
        font=dict(size=10, color="#2563EB", family="Inter"),
        showarrow=True, arrowhead=0, ay=-22, ax=0,
        bgcolor="white", bordercolor="#BFDBFE", borderwidth=1, borderpad=4,
    )
    fig_line.add_annotation(
        x=month, y=y2_sel, text=f"<b>{fmt(y2_sel)}</b>",
        font=dict(size=10, color="#B45309", family="Inter"),
        showarrow=True, arrowhead=0, ay=22, ax=0,
        bgcolor="white", bordercolor="#FDE68A", borderwidth=1, borderpad=4,
    )

    fig_line.update_layout(
        plot_bgcolor="white", paper_bgcolor="white",
        height=240, margin=dict(l=0, r=0, t=20, b=10),
        font=dict(family="Inter", size=11, color="#6B7280"),
        xaxis=dict(showgrid=False, zeroline=False, showline=False,
                   tickfont=dict(size=11, color="#6B7280")),
        yaxis=dict(showgrid=True, gridcolor="#F3F4F6", zeroline=False,
                   showline=False, tickfont=dict(size=10, color="#9CA3AF"),
                   tickformat=",.0f"),
        legend=dict(
            orientation="h", yanchor="bottom", y=1.04, xanchor="right", x=1,
            font=dict(size=11, color="#6B7280"),
        ),
        hovermode="x unified",
    )

    st.plotly_chart(fig_line, use_container_width=True, config={"displayModeBar": False})

    # ── Delta month row ───────────────────────────────────────────────────
    st.markdown('<div style="border-top:1px solid #E8EAF0; padding-top:12px; margin-top:4px;">', unsafe_allow_html=True)
    delta_cols = st.columns(12)
    for i, (col, m) in enumerate(zip(delta_cols, MONTHS)):
        v1_m = get_monthly(year1, m)
        v2_m = get_monthly(year2, m)
        d    = calc_pct(v1_m, v2_m)
        pos  = d >= 0
        sel  = m == month
        with col:
            bg      = "#EFF6FF" if sel else "transparent"
            border  = "1px solid #BFDBFE" if sel else "1px solid transparent"
            m_color = "#2563EB" if sel else "#6B7280"
            m_fw    = "700" if sel else "500"
            d_color = "#059669" if pos else "#DC2626"
            arr     = "▲" if pos else "▼"
            st.markdown(f"""
            <div style="text-align:center; border-radius:8px; padding:6px 2px;
                        background:{bg}; border:{border}; cursor:pointer;">
              <div style="font-size:9px; font-weight:{m_fw}; color:{m_color};">{m}</div>
              <div style="font-size:9px; font-weight:700; color:{d_color}; margin-top:2px;">
                {arr}{abs(d)}%
              </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)  # chart-card
    st.markdown("</div>", unsafe_allow_html=True)  # padding container

# Bottom spacer
st.markdown('<div style="height:32px;"></div>', unsafe_allow_html=True)
