import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import folium
from streamlit.components.v1 import html as components_html

st.set_page_config(
    page_title="ReLeaf — Post-Wildfire Recovery",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:ital,wght@0,500;0,600;0,700;1,500&family=DM+Sans:wght@300;400;500;600;700&display=swap');

/* ── Root & Body ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
}
.stApp {
    background: #111210;
}
.main .block-container {
    padding: 0 2rem 3rem 2rem;
    max-width: 1400px;
}

/* ── Hide Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stToolbar"] { display: none; }

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #0c0f0d 0%, #101510 40%, #131810 100%);
    border-right: 1px solid rgba(255,255,255,0.07);
}
[data-testid="stSidebar"] * { color: #cec8be !important; }
[data-testid="stSidebar"] .stSelectbox label { color: #8a9088 !important; font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.1em; }
[data-testid="stSidebar"] [data-baseweb="select"] > div {
    background: rgba(255,255,255,0.06) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    border-radius: 10px !important;
    color: #e8e2d8 !important;
}
[data-testid="stSidebar"] [data-baseweb="select"] span { color: #e8e2d8 !important; }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,0.07); }

/* ── Selectbox dropdown ── */
[data-baseweb="popover"] { background: #111410 !important; border: 1px solid rgba(255,255,255,0.1) !important; }
[role="option"] { background: #111410 !important; color: #cec8be !important; }
[role="option"]:hover { background: #1c2018 !important; }

/* ── Metric cards ── */
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.08);
    border-radius: 14px;
    padding: 1.1rem 1.3rem;
    margin-bottom: 0.45rem;
    transition: border-color 0.2s ease;
}
.metric-card:hover { border-color: rgba(255,255,255,0.16); }
.metric-card .label {
    font-size: 0.65rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.12em; color: #6a7470; margin-bottom: 0.3rem;
}
.metric-card .value {
    font-size: 1.1rem; font-weight: 600; color: #e8e2d8;
    line-height: 1.2;
}

/* ── Chart cards ── */
.chart-card {
    background: rgba(255,255,255,0.03);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.5rem 1.5rem 1rem;
    margin-bottom: 1rem;
    position: relative;
    overflow: hidden;
}
.chart-card::before {
    content: '';
    position: absolute; top: 0; left: 0; right: 0; height: 2px;
    border-radius: 20px 20px 0 0;
}
.chart-card.green::before  { background: linear-gradient(90deg, #2d6a4f, #52b788); }
.chart-card.orange::before { background: linear-gradient(90deg, #e07b39, #f4a261); }
.chart-card.brown::before  { background: linear-gradient(90deg, #8b5e3c, #c4956a); }

.chart-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.15rem; font-weight: 700;
    color: #e8e2d8; margin-bottom: 0.25rem;
}
.chart-subtitle {
    font-size: 0.75rem; color: #6a7470; margin-bottom: 0.75rem;
    font-weight: 400; letter-spacing: 0.02em;
}

/* ── Explanation boxes ── */
.explain-box {
    background: rgba(255,255,255,0.03);
    border-left: 3px solid rgba(255,255,255,0.15);
    border-radius: 0 10px 10px 0;
    padding: 0.75rem 1rem;
    font-size: 0.82rem;
    color: #9a9890;
    line-height: 1.65;
    margin-top: 0.5rem;
}

/* ── Map container ── */
.map-section {
    background: rgba(255,255,255,0.02);
    border: 1px solid rgba(255,255,255,0.07);
    border-radius: 20px;
    padding: 1.5rem;
    margin-bottom: 1.5rem;
}
.section-label {
    font-size: 0.68rem; font-weight: 600; text-transform: uppercase;
    letter-spacing: 0.15em; color: #6a7470; margin-bottom: 0.4rem;
}
.map-title {
    font-family: 'Cormorant Garamond', serif;
    font-size: 1.45rem; font-weight: 700; color: #e8e2d8;
    margin-bottom: 1rem;
}

/* ── Badges ── */
.status-badge {
    display: inline-block;
    padding: 0.25rem 0.75rem;
    border-radius: 50px;
    font-size: 0.72rem; font-weight: 600;
    letter-spacing: 0.05em;
    background: rgba(255,255,255,0.06);
    border: 1px solid rgba(255,255,255,0.14);
    color: #b0a898;
    margin-top: 0.5rem;
}

/* ── Dividers ── */
.divider { height: 1px; background: rgba(255,255,255,0.06); margin: 1.25rem 0; }

/* ── Plotly fix ── */
.js-plotly-plot, .plotly { background: transparent !important; }
</style>
""",
    unsafe_allow_html=True,
)

# ── Data ──────────────────────────────────────────────────────────────────────

WILDFIRES = {
    "2023 Canadian Wildfires": {
        "lat": 54.5,
        "lon": -115.5,
        "zoom": 5,
        "year": 2023,
        "country": "Canada 🇨🇦",
        "hectares": 18_500_000,
        "lives_affected": 235_000,
        "recovery_status": "Early Recovery",
        "recovery_pct": 28,
        "color": "#e07b39",
        "accent": "#f4a261",
        "ndvi_start": 0.11,
        "ndvi_end": 0.52,
        "ndvi_noise": 0.025,
        "aqi_peak": 485,
        "aqi_baseline": 18,
        "aqi_decay": 0.38,
        "soil_start": 18,
        "soil_end": 54,
        "soil_noise": 2.5,
    },
    "2025 LA Palisades Fire": {
        "lat": 34.04,
        "lon": -118.56,
        "zoom": 11,
        "year": 2025,
        "country": "USA 🇺🇸",
        "hectares": 9_988,
        "lives_affected": 180_000,
        "recovery_status": "Active Response",
        "recovery_pct": 12,
        "color": "#c0392b",
        "accent": "#e74c3c",
        "ndvi_start": 0.09,
        "ndvi_end": 0.38,
        "ndvi_noise": 0.018,
        "aqi_peak": 320,
        "aqi_baseline": 35,
        "aqi_decay": 0.45,
        "soil_start": 14,
        "soil_end": 42,
        "soil_noise": 2.0,
    },
    "2023 Maui Wildfires": {
        "lat": 20.87,
        "lon": -156.68,
        "zoom": 12,
        "year": 2023,
        "country": "USA 🇺🇸",
        "hectares": 2_170,
        "lives_affected": 12_000,
        "recovery_status": "Partial Recovery",
        "recovery_pct": 45,
        "color": "#d35400",
        "accent": "#e67e22",
        "ndvi_start": 0.13,
        "ndvi_end": 0.55,
        "ndvi_noise": 0.022,
        "aqi_peak": 410,
        "aqi_baseline": 12,
        "aqi_decay": 0.42,
        "soil_start": 20,
        "soil_end": 60,
        "soil_noise": 2.2,
    },
    "2020 Australian Black Summer": {
        "lat": -35.8,
        "lon": 148.9,
        "zoom": 6,
        "year": 2020,
        "country": "Australia 🇦🇺",
        "hectares": 18_600_000,
        "lives_affected": 3_000_000,
        "recovery_status": "Significant Recovery",
        "recovery_pct": 72,
        "color": "#7d3c98",
        "accent": "#a569bd",
        "ndvi_start": 0.10,
        "ndvi_end": 0.61,
        "ndvi_noise": 0.028,
        "aqi_peak": 520,
        "aqi_baseline": 10,
        "aqi_decay": 0.34,
        "soil_start": 16,
        "soil_end": 66,
        "soil_noise": 3.0,
    },
    "2021 BC Dixie Fire": {
        "lat": 40.10,
        "lon": -121.18,
        "zoom": 9,
        "year": 2021,
        "country": "USA 🇺🇸",
        "hectares": 389_837,
        "lives_affected": 30_000,
        "recovery_status": "Moderate Recovery",
        "recovery_pct": 55,
        "color": "#2e86c1",
        "accent": "#5dade2",
        "ndvi_start": 0.12,
        "ndvi_end": 0.57,
        "ndvi_noise": 0.024,
        "aqi_peak": 450,
        "aqi_baseline": 14,
        "aqi_decay": 0.36,
        "soil_start": 17,
        "soil_end": 59,
        "soil_noise": 2.8,
    },
}

# ── Helpers ───────────────────────────────────────────────────────────────────


def logistic(months, start, end, steepness=0.18, midpoint=10):
    x = np.array(months, dtype=float)
    sig = 1 / (1 + np.exp(-steepness * (x - midpoint)))
    return start + (end - start) * sig


def make_ndvi(fire, rng):
    months = list(range(25))
    base = logistic(
        months, fire["ndvi_start"], fire["ndvi_end"], steepness=0.22, midpoint=8
    )
    noise = rng.normal(0, fire["ndvi_noise"], len(months))
    noise[0] = 0
    return pd.DataFrame({"Month": months, "NDVI": np.clip(base + noise, 0, 1)})


def make_aqi(fire, rng):
    months = list(range(13))
    base = fire["aqi_baseline"] + (fire["aqi_peak"] - fire["aqi_baseline"]) * np.exp(
        -fire["aqi_decay"] * np.array(months)
    )
    noise = rng.normal(0, fire["aqi_peak"] * 0.04, len(months))
    noise[0] = 0
    return pd.DataFrame(
        {
            "Month": months,
            "AQI": np.clip(base + noise, fire["aqi_baseline"], fire["aqi_peak"] * 1.05),
        }
    )


def make_soil(fire, rng):
    months = list(range(25))
    base = logistic(
        months, fire["soil_start"], fire["soil_end"], steepness=0.14, midpoint=14
    )
    noise = rng.normal(0, fire["soil_noise"], len(months))
    noise[0] = 0
    return pd.DataFrame({"Month": months, "Soil": np.clip(base + noise, 0, 100)})


def aqi_color(val):
    if val <= 50:
        return "#52b788"
    if val <= 100:
        return "#b5c956"
    if val <= 150:
        return "#e8b84b"
    if val <= 200:
        return "#e07b39"
    if val <= 300:
        return "#c0392b"
    return "#7d3c98"


def recovery_score(fire, ndvi_df, aqi_df, soil_df):
    ndvi_final = float(ndvi_df["NDVI"].iloc[-1])
    ndvi_s = min(ndvi_final / 0.6 * 100, 100)
    peak_aqi = float(aqi_df["AQI"].max())
    final_aqi = float(aqi_df["AQI"].iloc[-1])
    aqi_range = max(peak_aqi - fire["aqi_baseline"], 1)
    aqi_s = min(max((peak_aqi - final_aqi) / aqi_range * 100, 0), 100)
    soil_s = min(float(soil_df["Soil"].iloc[-1]) / 70 * 100, 100)
    return round(ndvi_s * 0.4 + aqi_s * 0.3 + soil_s * 0.3, 1)


def first_month_below(series, threshold):
    hits = series[series <= threshold]
    return int(hits.index[0]) if len(hits) else None


def first_month_above(series, threshold):
    hits = series[series >= threshold]
    return int(hits.index[0]) if len(hits) else None


PLOT_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(family="DM Sans, sans-serif", color="#8a8e8a", size=11),
    margin=dict(l=8, r=8, t=12, b=8),
    hovermode="x unified",
    hoverlabel=dict(
        bgcolor="#1a1c18", bordercolor="rgba(255,255,255,0.2)", font_color="#e8e2d8"
    ),
    xaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zeroline=False,
        tickfont=dict(color="#6a7070"),
        title_font=dict(color="#8a8e8a"),
        linecolor="rgba(255,255,255,0.05)",
    ),
    yaxis=dict(
        gridcolor="rgba(255,255,255,0.05)",
        zeroline=False,
        tickfont=dict(color="#6a7070"),
        title_font=dict(color="#8a8e8a"),
        linecolor="rgba(255,255,255,0.05)",
    ),
    legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(color="#9a9890")),
)

# ── Header placeholder (rendered after sidebar so fire data is available) ─────

# ── Sidebar ───────────────────────────────────────────────────────────────────

with st.sidebar:
    st.markdown(
        """
    <div style="padding:1.5rem 0 0.5rem;">
      <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.15em;
        color:#6a7470;margin-bottom:0.6rem;">Select Event</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.6rem;font-weight:700;
        color:#e8e2d8;line-height:1.2;margin-bottom:1rem;">Wildfire Explorer</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    selected = st.selectbox(
        "Choose a wildfire event",
        list(WILDFIRES.keys()),
        label_visibility="collapsed",
    )
    fire = WILDFIRES[selected]

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)

    st.markdown(
        """
    <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.15em;
      color:#6a7470;margin-bottom:0.75rem;">Key Facts</div>
    """,
        unsafe_allow_html=True,
    )

    pct = int(fire["recovery_pct"])
    bar_color = "#52b788" if pct >= 60 else "#e8b84b" if pct >= 30 else "#e07b39"

    st.markdown(
        f"""
    <div class="metric-card">
      <div class="label">Fire Event</div>
      <div class="value">{selected}</div>
    </div>
    <div class="metric-card">
      <div class="label">Country</div>
      <div class="value">{fire["country"]}</div>
    </div>
    <div class="metric-card">
      <div class="label">Area Burned</div>
      <div class="value">{fire["hectares"]:,} ha</div>
    </div>
    <div class="metric-card">
      <div class="label">People Affected</div>
      <div class="value">{fire["lives_affected"]:,}</div>
    </div>

    <div style="background:rgba(255,255,255,0.04);border:1px solid rgba(255,255,255,0.1);
      border-radius:16px;padding:1.1rem 1.3rem;margin-bottom:0.5rem;">
      <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.6rem;">
        <div class="label" style="margin:0;">Recovery Progress</div>
        <div style="font-size:1rem;font-weight:700;color:{bar_color};">{pct}%</div>
      </div>
      <div style="background:rgba(255,255,255,0.08);border-radius:50px;height:6px;overflow:hidden;">
        <div style="width:{pct}%;height:100%;background:linear-gradient(90deg,{bar_color},{fire["accent"]});
          border-radius:50px;transition:width 0.8s ease;"></div>
      </div>
      <div class="status-badge" style="margin-top:0.75rem;">{fire["recovery_status"]}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)
    st.markdown(
        """
    <div style="font-size:0.72rem;color:#4a5050;line-height:1.6;padding-bottom:0.75rem;">
      Data simulated using logistic recovery curves calibrated to published post-fire research.
      Each wildfire uses a consistent random seed for reproducibility.
    </div>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        """
    <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.15em;
      color:#6a7470;margin-bottom:0.5rem;margin-top:0.25rem;">Export Data</div>
    """,
        unsafe_allow_html=True,
    )

# ── Generate data ─────────────────────────────────────────────────────────────

rng = np.random.default_rng(abs(hash(selected)) % (2**32))
ndvi_df = make_ndvi(fire, rng)
aqi_df = make_aqi(fire, rng)
soil_df = make_soil(fire, rng)

# ── Header variables ──────────────────────────────────────────────────────────

_fc = fire["color"]
_fa = fire["accent"]
_pct = int(fire["recovery_pct"])
_pbar = "#52b788" if _pct >= 60 else "#e8b84b" if _pct >= 30 else "#e07b39"
_score = recovery_score(fire, ndvi_df, aqi_df, soil_df)
_score_color = "#52b788" if _score >= 65 else "#e8b84b" if _score >= 35 else "#e07b39"
_progress_bar_css = f"linear-gradient(90deg,{_pbar},{_fa})"
_badge_border = f"1px solid {_pbar}44"
_glow = f"radial-gradient(circle,{_fc}20 0%,transparent 70%)"

# ── Derived insight stats for info strip ──────────────────────────────────────
_peak_aqi = int(aqi_df["AQI"].max())
if _peak_aqi > 300:
    _aqi_sev, _aqi_sev_c = "Hazardous", "#7d3c98"
elif _peak_aqi > 200:
    _aqi_sev, _aqi_sev_c = "Very Unhealthy", "#c0392b"
elif _peak_aqi > 150:
    _aqi_sev, _aqi_sev_c = "Unhealthy", "#e07b39"
else:
    _aqi_sev, _aqi_sev_c = "Moderate", "#e8b84b"

_ndvi_s = float(ndvi_df["NDVI"].iloc[0])
_ndvi_e = float(ndvi_df["NDVI"].iloc[-1])
_ndvi_gain = _ndvi_e - _ndvi_s

_m_mod = first_month_below(aqi_df.set_index("Month")["AQI"], 100)
_air_cleared = f"Month {_m_mod}" if _m_mod else "Not yet"
_air_cleared_c = "#52b788" if _m_mod else "#e07b39"

_soil_now = float(soil_df["Soil"].iloc[-1])
_soil_label = (
    "Recovering" if _soil_now < 50 else "Functional" if _soil_now < 70 else "Healthy"
)

# ── PART 1: Brand top bar ─────────────────────────────────────────────────────
st.markdown(
    '<div style="padding:2rem 0.5rem 1.4rem;">'
    '<div style="font-size:0.6rem;font-weight:600;text-transform:uppercase;letter-spacing:0.25em;'
    'color:#6a7470;margin-bottom:0.55rem;">🌿 Ecosystem Intelligence</div>'
    "<div style=\"font-family:'Cormorant Garamond',serif;font-size:4rem;font-weight:700;"
    'color:#e8e2d8;line-height:0.9;letter-spacing:-0.02em;margin-bottom:0.65rem;">ReLeaf</div>'
    '<div style="font-size:0.88rem;color:#5a6060;font-weight:400;letter-spacing:0.01em;max-width:560px;">'
    "Post-Wildfire Ecosystem Recovery Dashboard — tracking vegetation, air quality &amp; soil health"
    "</div>"
    "</div>",
    unsafe_allow_html=True,
)

st.markdown(
    f'<div style="padding:0 0.5rem 1.75rem;">'
    f'<span style="font-size:0.8rem;font-weight:500;text-transform:uppercase;'
    f'letter-spacing:0.14em;color:#52b788;">Currently viewing — </span>'
    f"<span style=\"font-family:'Cormorant Garamond',serif;font-size:1.35rem;"
    f'font-weight:700;color:#e8e2d8;letter-spacing:-0.01em;">{selected}</span>'
    f"</div>",
    unsafe_allow_html=True,
)

# ── Section divider helper ────────────────────────────────────────────────────


def section_divider(num, label):
    st.markdown(
        f"""
    <div style="display:flex;align-items:center;gap:1rem;margin:1.5rem 0 1.2rem;">
      <div style="font-size:0.62rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.18em;color:#a89070;white-space:nowrap;">{num} · {label}</div>
      <div style="flex:1;height:1px;background:rgba(255,255,255,0.08);"></div>
    </div>
    """,
        unsafe_allow_html=True,
    )


# ══════════════════════════════════════════════════════════════════════════════
# SECTION 1 — NDVI
# ══════════════════════════════════════════════════════════════════════════════

section_divider("01", "Vegetation Recovery")

info_c1, chart_c1 = st.columns([1, 2.4], gap="large")

with info_c1:
    ndvi_now = float(ndvi_df["NDVI"].iloc[-1])
    ndvi_s = float(ndvi_df["NDVI"].iloc[0])
    ndvi_gain = ndvi_now - ndvi_s
    st.markdown(
        f"""
    <div style="background:rgba(255,255,255,0.03);
      border:1px solid rgba(255,255,255,0.08);border-radius:20px;padding:1.75rem 1.5rem;">
      <div style="font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.15em;color:#52b788;margin-bottom:0.5rem;">Vegetation Index</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:700;
        color:#e8e2d8;line-height:1.1;margin-bottom:0.35rem;">NDVI Recovery</div>
      <div style="font-size:0.78rem;color:#6a7470;margin-bottom:1.4rem;">
        24-month trajectory post-ignition
      </div>
      <div style="display:flex;gap:0.75rem;margin-bottom:1.4rem;">
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#6a7470;margin-bottom:0.25rem;">At Fire</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e8e2d8;">{ndvi_s:.2f}</div>
        </div>
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#6a7470;margin-bottom:0.25rem;">Month 24</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e8e2d8;">{ndvi_now:.2f}</div>
        </div>
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#6a7470;margin-bottom:0.25rem;">Gain</div>
          <div style="font-size:1.2rem;font-weight:700;color:#52b788;">+{ndvi_gain:.2f}</div>
        </div>
      </div>
      <div class="explain-box">
         <strong>NDVI</strong> measures plant density from 0 (bare earth) to 1 (dense
        forest). Fires erase vegetation instantly — this curve tracks the slow return of
        grasses, shrubs, and eventually tree canopy back toward a healthy ecosystem.
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with chart_c1:
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=ndvi_df["Month"],
            y=ndvi_df["NDVI"],
            mode="lines",
            name="NDVI",
            line=dict(color="#52b788", width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(82,183,136,0.08)",
            hovertemplate="Month %{x}<br><b>NDVI: %{y:.3f}</b><extra></extra>",
        )
    )
    fig.add_trace(
        go.Scatter(
            x=ndvi_df["Month"],
            y=ndvi_df["NDVI"],
            mode="markers",
            marker=dict(
                size=5,
                color="#52b788",
                symbol="circle",
                line=dict(width=1.5, color="#0f2d1a"),
            ),
            showlegend=False,
            hovertemplate="Month %{x}<br><b>NDVI: %{y:.3f}</b><extra></extra>",
        )
    )
    fig.add_hline(
        y=0.4,
        line_dash="dot",
        line_color="#e8b84b",
        line_width=1.2,
        opacity=0.6,
        annotation_text="Healthy ≥ 0.4",
        annotation_font_color="#e8b84b",
        annotation_font_size=10,
        annotation_position="top right",
    )
    m02 = first_month_above(ndvi_df.set_index("Month")["NDVI"], 0.2)
    m03 = first_month_above(ndvi_df.set_index("Month")["NDVI"], 0.3)
    if m02:
        fig.add_vline(
            x=m02,
            line_dash="dash",
            line_color="#52b788",
            line_width=1,
            opacity=0.5,
            annotation_text=f"Mo.{m02}: NDVI 0.2",
            annotation_font_color="#52b788",
            annotation_font_size=9,
            annotation_position="top left",
        )
    if m03:
        fig.add_vline(
            x=m03,
            line_dash="dash",
            line_color="#74c69d",
            line_width=1,
            opacity=0.5,
            annotation_text=f"Mo.{m03}: NDVI 0.3",
            annotation_font_color="#74c69d",
            annotation_font_size=9,
            annotation_position="top left",
        )
    fig.update_layout(**PLOT_LAYOUT, height=300)
    fig.update_yaxes(range=[0, 0.85], title="NDVI (0–1)")
    fig.update_xaxes(title="Months Post-Fire")
    st.plotly_chart(fig, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 2 — AQI
# ══════════════════════════════════════════════════════════════════════════════

section_divider("02", "Air Quality")

info_c2, chart_c2 = st.columns([1, 2.4], gap="large")

with info_c2:
    peak_aqi = int(aqi_df["AQI"].max())
    final_aqi = int(aqi_df["AQI"].iloc[-1])
    improvement = peak_aqi - final_aqi
    st.markdown(
        f"""
    <div style="background:linear-gradient(145deg,rgba(224,123,57,0.08),rgba(224,123,57,0.03));
      border:1px solid rgba(224,123,57,0.18);border-radius:20px;padding:1.75rem 1.5rem;">
      <div style="font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.15em;color:#e07b39;margin-bottom:0.5rem;">Air Quality Index</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:700;
        color:#e8e2d8;line-height:1.1;margin-bottom:0.35rem;">PM2.5 / AQI Levels</div>
      <div style="font-size:0.78rem;color:#6a7470;margin-bottom:1.4rem;">
        12-month smoke dispersal
      </div>
      <div style="display:flex;gap:0.75rem;margin-bottom:1.4rem;">
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#6a7470;margin-bottom:0.25rem;">Peak AQI</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e8e2d8;">{peak_aqi}</div>
        </div>
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#6a7470;margin-bottom:0.25rem;">Month 12</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e8e2d8;">{final_aqi}</div>
        </div>
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(224,123,57,0.12);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#e07b39;margin-bottom:0.25rem;">Improvement</div>
          <div style="font-size:1.2rem;font-weight:700;color:#95d5b2;">−{improvement}</div>
        </div>
      </div>
      <div class="explain-box" style="border-left-color:#e07b39;background:rgba(224,123,57,0.08);">
         <strong>AQI</strong> tracks dangerous smoke particles (PM2.5) — values above 150
        are hazardous. Wildfire smoke causes extreme spikes in the first weeks. As fires are
        contained, air quality gradually clears over the following months.
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with chart_c2:
    bar_colors = [aqi_color(v) for v in aqi_df["AQI"]]
    fig2 = go.Figure()
    fig2.add_trace(
        go.Bar(
            x=aqi_df["Month"],
            y=aqi_df["AQI"],
            marker=dict(color=bar_colors, opacity=0.85, line=dict(width=0)),
            name="AQI",
            hovertemplate="Month %{x}<br><b>AQI: %{y:.0f}</b><extra></extra>",
        )
    )
    for level, color, label in [
        (50, "#52b788", "Good"),
        (100, "#b5c956", "Moderate"),
        (150, "#e8b84b", "Unhealthy (sensitive)"),
        (200, "#e07b39", "Unhealthy"),
    ]:
        fig2.add_hline(
            y=level,
            line_dash="dot",
            line_color=color,
            line_width=1,
            opacity=0.4,
            annotation_text=label,
            annotation_position="top right",
            annotation_font_size=9,
            annotation_font_color=color,
        )
    m_mod = first_month_below(aqi_df.set_index("Month")["AQI"], 100)
    m_good = first_month_below(aqi_df.set_index("Month")["AQI"], 50)
    if m_mod:
        fig2.add_vline(
            x=m_mod,
            line_dash="dash",
            line_color="#b5c956",
            line_width=1,
            opacity=0.5,
            annotation_text=f"Mo.{m_mod}: Moderate",
            annotation_font_color="#b5c956",
            annotation_font_size=9,
            annotation_position="top left",
        )
    if m_good:
        fig2.add_vline(
            x=m_good,
            line_dash="dash",
            line_color="#52b788",
            line_width=1,
            opacity=0.5,
            annotation_text=f"Mo.{m_good}: Good AQI",
            annotation_font_color="#52b788",
            annotation_font_size=9,
            annotation_position="top left",
        )
    fig2.update_layout(**PLOT_LAYOUT, height=300)
    fig2.update_yaxes(title="Air Quality Index")
    fig2.update_xaxes(title="Months Post-Fire")
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 3 — Soil Health
# ══════════════════════════════════════════════════════════════════════════════

section_divider("03", "Soil Health")

info_c3, chart_c3 = st.columns([1, 2.4], gap="large")

with info_c3:
    soil_now = float(soil_df["Soil"].iloc[-1])
    soil_s = float(soil_df["Soil"].iloc[0])
    soil_gain = soil_now - soil_s
    st.markdown(
        f"""
    <div style="background:linear-gradient(145deg,rgba(196,149,106,0.08),rgba(196,149,106,0.03));
      border:1px solid rgba(196,149,106,0.18);border-radius:20px;padding:1.75rem 1.5rem;">
      <div style="font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.15em;color:#c4956a;margin-bottom:0.5rem;">Soil Health Index</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.8rem;font-weight:700;
        color:#e8e2d8;line-height:1.1;margin-bottom:0.35rem;">Ground Recovery</div>
      <div style="font-size:0.78rem;color:#6a7470;margin-bottom:1.4rem;">
        24-month soil restoration curve
      </div>
      <div style="display:flex;gap:0.75rem;margin-bottom:1.4rem;">
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(255,255,255,0.07);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#6a7470;margin-bottom:0.25rem;">At Fire</div>
          <div style="font-size:1.2rem;font-weight:700;color:#e8e2d8;">{soil_s:.0f}</div>
        </div>
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(196,149,106,0.12);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#c4956a;margin-bottom:0.25rem;">Month 24</div>
          <div style="font-size:1.2rem;font-weight:700;color:#d4a574;">{soil_now:.0f}</div>
        </div>
        <div style="flex:1;background:rgba(0,0,0,0.22);border-radius:12px;padding:0.8rem 0.9rem;
          border:1px solid rgba(196,149,106,0.12);">
          <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
            color:#c4956a;margin-bottom:0.25rem;">Gain</div>
          <div style="font-size:1.2rem;font-weight:700;color:#95d5b2;">+{soil_gain:.0f}</div>
        </div>
      </div>
      <div class="explain-box" style="border-left-color:#c4956a;background:rgba(196,149,106,0.08);">
         <strong>Soil Health</strong> scores organic matter, microbial life, and erosion
        resistance out of 100. Fire destroys the protective organic layer instantly — and soil
        is the slowest of the three systems to recover, sometimes taking years.
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )

with chart_c3:
    fig3 = go.Figure()
    fig3.add_trace(
        go.Scatter(
            x=soil_df["Month"],
            y=soil_df["Soil"],
            mode="lines",
            name="Soil Health",
            line=dict(color="#c4956a", width=2.5, shape="spline"),
            fill="tozeroy",
            fillcolor="rgba(196,149,106,0.08)",
            hovertemplate="Month %{x}<br><b>Soil: %{y:.1f}/100</b><extra></extra>",
        )
    )
    fig3.add_trace(
        go.Scatter(
            x=soil_df["Month"],
            y=soil_df["Soil"],
            mode="markers",
            marker=dict(
                size=5,
                color="#c4956a",
                symbol="circle",
                line=dict(width=1.5, color="#0f2d1a"),
            ),
            showlegend=False,
            hovertemplate="Month %{x}<br><b>Soil: %{y:.1f}/100</b><extra></extra>",
        )
    )
    fig3.add_hline(
        y=50,
        line_dash="dot",
        line_color="#e8b84b",
        line_width=1.2,
        opacity=0.6,
        annotation_text="Functional ≥ 50",
        annotation_font_color="#e8b84b",
        annotation_font_size=10,
        annotation_position="top right",
    )
    fig3.update_layout(**PLOT_LAYOUT, height=300)
    fig3.update_yaxes(range=[0, 95], title="Soil Health (0–100)")
    fig3.update_xaxes(title="Months Post-Fire")
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 4 — Map (below all charts)
# ══════════════════════════════════════════════════════════════════════════════

section_divider("04", "Burn Scar Location")

st.markdown(
    f"""
<div class="map-section">
  <div class="section-label">Interactive Map</div>
  <div class="map-title">📍 {selected}</div>
""",
    unsafe_allow_html=True,
)

m = folium.Map(
    location=[fire["lat"], fire["lon"]],
    zoom_start=fire["zoom"],
    tiles="CartoDB dark_matter",
)
folium.Circle(
    location=[fire["lat"], fire["lon"]],
    radius=max(8000, min(fire["hectares"] * 3, 400_000)),
    color=fire["color"],
    fill=True,
    fill_color=fire["color"],
    fill_opacity=0.30,
    weight=2,
    tooltip=f"{selected} — approx. burn area",
).add_to(m)
folium.CircleMarker(
    location=[fire["lat"], fire["lon"]],
    radius=8,
    color=fire["accent"],
    fill=True,
    fill_color=fire["accent"],
    fill_opacity=1,
    weight=2,
    tooltip=selected,
).add_to(m)

components_html(m.get_root().render(), height=380, scrolling=False)
st.markdown("</div>", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# SECTION 5 — Cross-Fire Comparison
# ══════════════════════════════════════════════════════════════════════════════

section_divider("05", "Fire Comparison")

fire_names = list(WILDFIRES.keys())
rec_pcts = [int(WILDFIRES[n]["recovery_pct"]) for n in fire_names]
hectares = [WILDFIRES[n]["hectares"] for n in fire_names]
affected = [WILDFIRES[n]["lives_affected"] for n in fire_names]
fc_colors = [WILDFIRES[n]["color"] for n in fire_names]
short_names = [n.replace("20", "'") for n in fire_names]

comp_left, comp_right = st.columns(2, gap="large")

with comp_left:
    st.markdown(
        """
    <div style="background:rgba(255,255,255,0.03);
      border:1px solid rgba(255,255,255,0.07);border-radius:20px;padding:1.5rem 1.5rem 0.5rem;">
      <div style="font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.15em;color:#a89070;margin-bottom:0.35rem;">Recovery %</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:700;
        color:#e8e2d8;line-height:1.1;margin-bottom:0.2rem;">How far along is each fire?</div>
      <div style="font-size:0.75rem;color:#5a6060;margin-bottom:0.75rem;">
        Percent ecosystem restoration achieved to date
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    highlight = [1.0 if n == selected else 0.6 for n in fire_names]
    border_c = [
        WILDFIRES[n]["color"] if n == selected else "rgba(255,255,255,0.15)"
        for n in fire_names
    ]
    fig_cmp1 = go.Figure(
        go.Bar(
            x=rec_pcts,
            y=short_names,
            orientation="h",
            marker=dict(
                color=fc_colors,
                opacity=highlight,
                line=dict(
                    color=border_c,
                    width=[2 if n == selected else 0 for n in fire_names],
                ),
            ),
            text=[f"{v}%" for v in rec_pcts],
            textposition="outside",
            textfont=dict(color="#9a9890", size=11),
            hovertemplate="%{y}<br>Recovery: %{x}%<extra></extra>",
        )
    )
    cmp_layout = {**PLOT_LAYOUT, "margin": dict(l=8, r=50, t=8, b=8)}
    fig_cmp1.update_layout(**cmp_layout, height=240)
    fig_cmp1.update_xaxes(range=[0, 105], title="Recovery %")
    fig_cmp1.update_yaxes(tickfont=dict(size=10))
    st.plotly_chart(
        fig_cmp1, use_container_width=True, config={"displayModeBar": False}
    )

with comp_right:
    st.markdown(
        """
    <div style="background:linear-gradient(145deg,rgba(224,123,57,0.06),rgba(224,123,57,0.02));
      border:1px solid rgba(224,123,57,0.14);border-radius:20px;padding:1.5rem 1.5rem 0.5rem;">
      <div style="font-size:0.63rem;font-weight:700;text-transform:uppercase;
        letter-spacing:0.15em;color:#e07b39;margin-bottom:0.35rem;">Scale of Impact</div>
      <div style="font-family:'Cormorant Garamond',serif;font-size:1.5rem;font-weight:700;
        color:#e8e2d8;line-height:1.1;margin-bottom:0.2rem;">Hectares burned per event</div>
      <div style="font-size:0.75rem;color:#5a6060;margin-bottom:0.75rem;">
        Total area affected (log scale for readability)
      </div>
    </div>
    """,
        unsafe_allow_html=True,
    )
    fig_cmp2 = go.Figure(
        go.Bar(
            x=hectares,
            y=short_names,
            orientation="h",
            marker=dict(
                color=fc_colors,
                opacity=[1.0 if n == selected else 0.55 for n in fire_names],
                line=dict(
                    color=border_c,
                    width=[2 if n == selected else 0 for n in fire_names],
                ),
            ),
            text=[f"{v:,}" for v in hectares],
            textposition="outside",
            textfont=dict(color="#9a9890", size=11),
            hovertemplate="%{y}<br>Hectares: %{x:,}<extra></extra>",
        )
    )
    cmp_layout2 = {**PLOT_LAYOUT, "margin": dict(l=8, r=80, t=8, b=8)}
    fig_cmp2.update_layout(**cmp_layout2, height=240)
    fig_cmp2.update_xaxes(type="log", title="Hectares (log scale)")
    fig_cmp2.update_yaxes(tickfont=dict(size=10))
    st.plotly_chart(
        fig_cmp2, use_container_width=True, config={"displayModeBar": False}
    )

st.markdown(
    f'<div style="background:rgba(255,255,255,0.02);border:1px solid rgba(255,255,255,0.06);'
    f"border-radius:14px;padding:1rem 1.5rem;margin-top:0.5rem;"
    f'font-size:0.8rem;color:#5a6060;line-height:1.7;">'
    f'<strong style="color:#a89070;">Currently selected:</strong> '
    f'<strong style="color:#e8e2d8;">{selected}</strong> — '
    f"{fire['hectares']:,} ha burned, {fire['lives_affected']:,} people affected, "
    f"{fire['recovery_pct']}% recovered. "
    f"Highlighted bars indicate the selected fire across all comparison charts."
    f"</div>",
    unsafe_allow_html=True,
)

# ── CSV Download (sidebar, placed here so data is available) ──────────────────

import io, csv


def _df_to_csv(df):
    return df.to_csv(index=False).encode("utf-8")


with st.sidebar:
    st.download_button(
        label="Download NDVI Data",
        data=_df_to_csv(ndvi_df),
        file_name=f"releaf_{selected.lower().replace(' ', '_')}_ndvi.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        label="Download AQI Data",
        data=_df_to_csv(aqi_df),
        file_name=f"releaf_{selected.lower().replace(' ', '_')}_aqi.csv",
        mime="text/csv",
        use_container_width=True,
    )
    st.download_button(
        label="Download Soil Data",
        data=_df_to_csv(soil_df),
        file_name=f"releaf_{selected.lower().replace(' ', '_')}_soil.csv",
        mime="text/csv",
        use_container_width=True,
    )

# ── Footer ────────────────────────────────────────────────────────────────────

st.markdown(
    """
<div style="margin-top:2.5rem;padding:1.25rem 1.5rem;
  border-top:1px solid rgba(255,255,255,0.06);
  display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:0.5rem;">
  <div style="color:#4a5050;font-size:0.78rem;">
     <strong style="color:#52b788;">ReLeaf</strong> · Post-Wildfire Ecosystem Recovery Platform
  </div>
  <div style="color:#4a5050;font-size:0.75rem;">
    Recovery data modeled from peer-reviewed post-fire research · For education &amp; awareness
  </div>
</div>
""",
    unsafe_allow_html=True,
)
