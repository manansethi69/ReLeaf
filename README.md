# ReLeaf — Post-Wildfire Ecosystem Recovery Dashboard

> Built for **Hack the Elements** · ShiftKey Labs · May 2026 · Theme: Fire

A dashboard that shows what happens **after** a wildfire goes out — tracking how vegetation, air quality, and soil recover over months and years.

When a wildfire is burning, we see it on the news every day. The day after it stops, the cameras leave. ReLeaf fills the gap: a calm, readable view of the slow recovery that follows.

---

## What it does

For five real wildfire events from the last six years, ReLeaf visualises:

- **NDVI (Vegetation Index)** — satellite-style measure of how green the land is, 0 to 1, over 24 months
- **AQI / PM2.5 (Air Quality)** — smoke particle concentration over 12 months, colour-coded by EPA breakpoints
- **Soil Health Index** — composite of soil structure, organic matter, and microbial return over 24 months
- **Burn scar map** — interactive Folium map of the approximate fire location
- **Cross-fire comparison** — side-by-side comparison of all five events
- **Eco Score** — a single composite number blending all three systems

The five fires included:

- Camp Fire (California, 2018)
- Lytton Fire (British Columbia, 2021)
- Black Summer (Australia, 2019–2020)
- Okanagan Complex (British Columbia, 2023)
- Eaton Fire (California, 2025)

---

## How to run it

You need Python 3.11 or newer.

```bash
pip install -r requirements.txt
streamlit run app.py
```

The dashboard opens at `http://localhost:8501` by default.

---

## How it works

- **Frontend:** Streamlit + custom CSS for the dark editorial look
- **Charts:** Plotly (interactive vegetation, air, and soil charts)
- **Map:** Folium + Leaflet (CartoDB dark tiles)
- **Data model:** Logistic S-curve recovery functions, calibrated to ranges from published post-fire ecology research, seeded per fire so results are reproducible
- **Every dataset can be exported as CSV** from the dashboard

The recovery curves are not real-time satellite data — they are research-calibrated simulations. The next step is plugging in NASA MODIS for live NDVI and the EPA AirNow API for real historical air quality.

---

## Tech stack

- Python 3.11
- Streamlit 1.45
- Plotly
- Folium + streamlit-folium
- Pandas + NumPy

---

## Project files

```
app.py                  Main Streamlit application (all dashboard logic)
requirements.txt        Python dependencies
.streamlit/config.toml  Streamlit server config
PITCH_SCRIPT.md         4-minute pitch script used at the hackathon
```

---

## Who it is for

Teachers, journalists, NGOs, and local governments — anyone who needs to explain or understand long-term wildfire recovery to a non-technical audience.

---

## License

MIT
