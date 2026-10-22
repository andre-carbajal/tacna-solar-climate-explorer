from pathlib import Path
import csv
from datetime import date
from bokeh.layouts import column, row
from bokeh.models import ColumnDataSource, CustomJS, Div, Select
from bokeh.plotting import figure, save
from bokeh.resources import CDN

ROOT = Path(__file__).parent
with (ROOT / "data/tacna_daily.csv").open() as f:
    rows = list(csv.DictReader(f))
all_data = {"date": [r["date"] for r in rows], "year": [int(r["date"][:4]) for r in rows],
            "month": [int(r["date"][5:7]) for r in rows],
            "solar": [float(r["solar_kwh_m2_day"]) for r in rows],
            "temperature": [float(r["temperature_c"]) for r in rows]}
YEARS = sorted(set(all_data["year"]))

# The committed NASA snapshot keeps the public page reproducible and independent of a runtime API.
def for_year(key, selected):
    return [(date.fromisoformat(d), vals) for d, y, vals in zip(all_data["date"], all_data["year"], all_data[key]) if y == selected]
initial = for_year("solar", YEARS[-1])
source = ColumnDataSource(data={"date": [r[0] for r in initial], "value": [r[1] for r in initial]})
sums = [0.0] * 12; counts = [0] * 12
for m, y, v in zip(all_data["month"], all_data["year"], all_data["solar"]):
    if y == YEARS[-1]: sums[m-1] += v; counts[m-1] += 1
month_source = ColumnDataSource(data={"month": [str(i) for i in range(1, 13)], "value": [sums[i]/counts[i] if counts[i] else 0 for i in range(12)]})

metric = Select(title="Measure", value="solar", options=[("solar", "Solar radiation"), ("temperature", "Air temperature")], width=240)
year = Select(title="Year", value=str(YEARS[-1]), options=[str(y) for y in YEARS], width=140)
line = figure(height=330, sizing_mode="stretch_width", x_axis_type="datetime", tools="pan,wheel_zoom,box_zoom,reset,save", toolbar_location="above")
line.line("date", "value", source=source, line_width=3, color="#e87935")
line.scatter("date", "value", source=source, size=3, alpha=.45, color="#e87935")
line.xaxis.axis_label = "Date"
line.yaxis.axis_label = "Daily solar radiation (kWh/m²/day)"
line.title.text = "Daily signal"
bar = figure(height=280, sizing_mode="stretch_width", x_range=[str(i) for i in range(1, 13)], tools="", toolbar_location=None)
bar.vbar(x="month", top="value", source=month_source, width=.72, color="#1e8a83")
bar.xaxis.axis_label = "Month"
bar.yaxis.axis_label = "Monthly mean · kWh/m²/day"
bar.title.text = "Seasonality · monthly mean"

callback = CustomJS(args=dict(source=source, month_source=month_source, metric=metric, year=year,
                              dates=all_data["date"], years=all_data["year"], months=all_data["month"],
                              solar=all_data["solar"], temperature=all_data["temperature"], line=line, bar=bar), code="""
const key = metric.value, selected = Number(year.value), vals = key === 'solar' ? solar : temperature;
const xs = [], ys = [], sums = Array(12).fill(0), counts = Array(12).fill(0);
years.forEach((value, i) => {
  if (value !== selected) return;
  xs.push(new Date(dates[i] + 'T00:00:00Z')); ys.push(vals[i]);
  sums[months[i]-1] += vals[i]; counts[months[i]-1]++;
});
source.data = {date: xs, value: ys}; source.change.emit();
month_source.data = {month: Array.from({length:12}, (_,i)=>String(i+1)), value:sums.map((v,i)=>counts[i] ? v/counts[i] : 0)}; month_source.change.emit();
const solarMode = key === 'solar';
line.yaxis.axis_label = solarMode ? 'Daily solar radiation (kWh/m²/day)' : 'Daily air temperature (°C)';
line.title.text = `${solarMode ? 'Solar radiation' : 'Air temperature'} · ${selected}`;
bar.yaxis.axis_label = solarMode ? 'Monthly mean · kWh/m²/day' : 'Monthly mean · °C';
bar.title.text = `Seasonality · monthly mean · ${selected}`;
""")
metric.js_on_change("value", callback); year.js_on_change("value", callback)
header = Div(text="""
<div class='hero'><div class='eyebrow'>FIELD NOTES / TACNA, PERU</div><h1>Sunlight, seasons &amp; the desert coast</h1>
<p>Explore a decade of NASA POWER daily solar radiation and near-surface temperature at one point in southern Peru. Switch the signal or year; the charts update in your browser.</p>
<div class='meta'>18.0066° S · 70.2463° W <span>•</span> 2015–2024 <span>•</span> NASA POWER / MERRA-2</div></div>
""")
footer = Div(text="<small>Daily point estimates, not ground-station measurements. NASA POWER solar variable: ALLSKY_SFC_SW_DWN (kWh/m²/day); temperature: T2M (°C). Values and provenance are in the repository. Not an engineering-grade PV-yield forecast.</small>")
layout = column(header, row(metric, year), line, bar, footer, sizing_mode="stretch_width", width=1050)
layout.tags = ["Tacna solar climate explorer"]
layout.css_classes = ["dashboard"]
save(layout, filename=str(ROOT / "index.html"), title="Tacna Solar & Climate Explorer", resources=CDN)
html = (ROOT / "index.html").read_text()
html = html.replace("</head>", """<meta name='viewport' content='width=device-width, initial-scale=1'><style>
body{margin:0;background:#f4f3ee;color:#172b2a;font-family:Inter,ui-sans-serif,system-ui,sans-serif}.bk-root{max-width:1120px;margin:0 auto;padding:28px 22px}.hero{padding:28px 34px 24px;background:#123d3a;color:#fff;border-radius:16px;margin-bottom:18px}.eyebrow{font-size:11px;letter-spacing:.18em;color:#f3b37a;font-weight:700}.hero h1{font-size:clamp(28px,5vw,48px);line-height:1.05;max-width:700px;margin:14px 0}.hero p{max-width:700px;color:#d7e7e3;font-size:16px;line-height:1.6}.meta{font-size:12px;color:#f3c18d}.meta span{padding:0 8px}.bk-Column{gap:14px!important}small{display:block;color:#63706e;line-height:1.6;padding:4px 2px 20px}@media(max-width:600px){.bk-root{padding:12px}.hero{padding:22px}}
</style></head>""")
(ROOT / "index.html").write_text(html)
