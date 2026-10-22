# Tacna Solar & Climate Explorer

A small, serverless Bokeh dashboard for comparing daily NASA POWER solar radiation and near-surface temperature in Tacna, Peru (2015–2024). All data is embedded in a standalone HTML page; selectors and charts work in the browser without Python, a server, or a runtime data API.

## Build locally

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
python build_dashboard.py
python -m http.server 8000
```

Open http://localhost:8000. The deterministic CSV snapshot is tracked in `data/`; regenerate it from NASA POWER only when intentionally refreshing the dataset.

## Data and limitations

NASA POWER daily point data, coordinates 18.0066° S, 70.2463° W, parameters `ALLSKY_SFC_SW_DWN` (kWh/m²/day) and `T2M` (°C), 2015-01-01 through 2024-12-31, community `RE`, metric units. POWER provides gridded/reanalysis-derived estimates, not measurements from a Tacna ground station. This is exploratory context, not a bankable PV-yield estimate.

- API: https://power.larc.nasa.gov/api/temporal/daily/point
- NASA POWER: https://power.larc.nasa.gov/
- Data snapshot metadata: `data/metadata.json`

## Deploy

Push to `main`; GitHub Actions tests and builds the page on pull requests, then publishes to GitHub Pages on main. In repository Settings → Pages, select **GitHub Actions** as the build and deployment source.

## License

Application code: MIT. NASA data is attributed to NASA POWER; review NASA POWER data-use guidance before redistribution for other purposes.
