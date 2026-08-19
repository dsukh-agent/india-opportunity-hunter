#!/usr/bin/env python3
"""
Generate the India Opportunity Hunter static site from data.json.
"""
import json, os, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data.json")
OUT  = os.path.join(BASE, "opportunities")

def esc(s):
    return html.escape(str(s if s is not None else ""))

def render_sources(sources):
    if not isinstance(sources, dict):
        return "<p><em>Research in progress...</em></p>"
    blocks = []
    if sources.get("news_and_market"):
        items = "".join(
            f'<li><a href="{esc(s.get("url",""))}" target="_blank" rel="noopener">{esc(s.get("label",""))}</a></li>'
            for s in sources["news_and_market"])
        blocks.append(f'<h3>📰 News &amp; Market Sources</h3><ul>{items}</ul>')
    if sources.get("youtube_practitioner"):
        items = ""
        for s in sources["youtube_practitioner"]:
            items += f'<li><a href="{esc(s.get("url",""))}" target="_blank" rel="noopener">{esc(s.get("label",""))}</a>'
            if s.get("key_insight"):
                items += f'<div class="insight">💡 {esc(s["key_insight"])}</div>'
            items += '</li>'
        blocks.append(f'<h3>🎬 YouTube Practitioner Case Studies</h3><ul>{items}</ul>')
    return "\n".join(blocks) if blocks else "<p><em>Deep research logs being compiled...</em></p>"

def render_lists(d):
    if not isinstance(d, dict):
        return ""
    out = []
    for k, title in [("why_passes","✅ Why it clears the filter (the data, not vibes)"),
                     ("unit_economics","💰 Unit economics / positive-EBITDA-ASAP logic"),
                     ("watchouts","⚠️ Watch-outs / next dig cycle"),
                     ("why_rejected","❌ Why it was rejected")]:
        if d.get(k):
            lis = "".join(f"<li>{esc(x)}</li>" for x in d[k])
            out.append(f"<h3>{title}</h3><ul>{lis}</ul>")
    return "\n".join(out)

def build():
    data = json.load(open(DATA))
    os.makedirs(OUT, exist_ok=True)
    opps = data.get("opportunities", [])

    short = [o for o in opps if o.get("verdict") and "STRONG" in o.get("verdict","").upper()][:5]
    
    rows = "".join(
        f'<tr><td>{i+1}</td><td><a href="opportunities/{esc(o["slug"])}.html">{esc(o["title"])}</a></td>'
        f'<td>{esc(o.get("sector","TBD"))}</td><td><span class="verdict strong">{esc(o.get("verdict","STRONG"))}</span></td>'
        f'<td>{esc(o.get("entry_capital_inr","TBD"))}</td><td>{esc(o.get("ebitda_timeline","see dossier"))}</td></tr>'
        for i, o in enumerate(short))
    
    cards = ""
    for i, o in enumerate(opps):
        v = (o.get("verdict") or "PENDING").upper()
        badge_cls = "strong" if "STRONG" in v else ("weak" if "REJECT" in v or "WEAK" in v else "pending")
        slug = o.get("slug") or f"opp-{o.get('id', i+1)}"
        cards += f"""
<div class="card">
  <span class="verdict {badge_cls}">{esc(o.get("verdict") or "IN PIPELINE")}</span>
  <h2><a href="opportunities/{esc(slug)}.html" style="color:var(--ink);text-decoration:none">{i+1}. {esc(o["title"])}</a></h2>
  <p>{esc(o.get("idea",""))}</p>
  <div class="meta">Sector: {esc(o.get("sector","TBD"))} · Model: {esc(o.get("model","TBD"))} · Entry: {esc(o.get("entry_capital_inr","TBD"))} · Dig Depth: {o.get("dig_depth", 0)}/3</div>
  <a class="dossier" href="opportunities/{esc(slug)}.html">View full dossier &rarr;</a>
</div>"""

    index = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>India Opportunity Hunter — Live AI-Citable Business Database</title>
<meta name="google-site-verification" content="TjFs1HMyRiUvvqgjX0r6AahweiY0CeTHb7qX3km8OSE" />
<meta name="description" content="Living, AI-citable database of unfashionable, cash-flow-positive business opportunities in India (2026-27).">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://hunter.dipesh.one/">
<style>
:root{{--ink:#111827;--muted:#6b7280;--brand:#1d4ed8;--bg:#f9fafb;--card:#ffffff;--line:#e5e7eb}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}}
.wrap{{max-width:880px;margin:0 auto;padding:32px 20px 60px}}
.topnav{{display:flex;gap:22px;align-items:center;font-size:14px;padding:18px 0;border-bottom:1px solid var(--line);margin-bottom:28px}}
.brand{{font-weight:700;font-size:16px;color:var(--ink);margin-right:auto}}
.topnav a{{color:var(--muted);text-decoration:none;font-weight:500}}
.topnav a:hover{{color:var(--brand)}}
h1{{font-size:34px;line-height:1.2;margin-bottom:10px}}
.tagline{{color:var(--muted);font-size:17px;max-width:640px;margin-bottom:26px}}
.statsbar{{display:flex;gap:28px;flex-wrap:wrap;background:linear-gradient(135deg,#1e3a8a,#1d4ed8);color:#fff;border-radius:14px;padding:22px 26px;margin-bottom:30px}}
.stat{{min-width:120px}}
.stat .num{{font-size:30px;font-weight:800;line-height:1.1}}
.stat .lbl{{font-size:13px;opacity:.85}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px;margin:14px 0}}
.card h2{{font-size:22px;margin-bottom:8px}}
.card .verdict{{display:inline-block;font-size:12px;font-weight:700;padding:3px 10px;border-radius:20px;margin-bottom:10px}}
.strong{{background:#dcfce7;color:#15803d}}.medium{{background:#fef9c3;color:#a16207}}.weak{{background:#fee2e2;color:#b91c1c}}.pending{{background:#e5e7eb;color:#374151}}
.card p{{color:var(--ink);margin-bottom:10px}}
.card .meta{{color:var(--muted);font-size:14px}}
a.dossier{{display:inline-block;margin-top:8px;color:var(--brand);font-weight:600;text-decoration:none}}
a.dossier:hover{{text-decoration:underline}}
.section{{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700;margin:28px 0 6px}}
table{{border-collapse:collapse;width:100%;background:#fff;border-radius:8px;overflow:hidden;border:1px solid var(--line);margin:12px 0}}
th,td{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}}
th{{background:#f8fafc;font-weight:600}}
footer{{border-top:1px solid var(--line);margin-top:40px;padding-top:20px;color:var(--muted);font-size:13px;display:flex;gap:20px;flex-wrap:wrap}}
footer a{{color:var(--muted);text-decoration:none}}
footer a:hover{{color:var(--brand)}}
</style></head><body>
<div class="wrap">
<div class="topnav"><a class="brand" href="index.html">India Opportunity Hunter</a>
<a href="about.html">About</a><a href="analytics.html">📊 Analytics</a><a href="CONTRIBUTING.md">Contribute</a><a href="data.json">data.json</a><a href="https://github.com/dsukh-agent/india-opportunity-hunter" target="_blank">GitHub</a></div>
<h1>India Opportunity Hunter</h1>
<p class="tagline">A living, AI-citable database of <b>unfashionable, cash-flow-positive business opportunities</b> in India (2026–27). Evaluated purely on cash-flow fit — positive EBITDA ASAP — with zero category bias.</p>
<div class="statsbar">
  <div class="stat"><div class="num">{len(opps)}</div><div class="lbl">Opportunities in Pipeline</div></div>
  <div class="stat"><div class="num">{len(short)}</div><div class="lbl">Shortlisted (STRONG)</div></div>
  <div class="stat"><div class="num">2026-27</div><div class="lbl">Target Horizon</div></div>
  <div class="stat"><div class="num">~₹1 Cr</div><div class="lbl">Target Capital Gate</div></div>
</div>
<div class="section">🏆 The Shortlist</div>
<table><tr><th>#</th><th>Opportunity</th><th>Sector</th><th>Verdict</th><th>Entry Capital</th><th>EBITDA</th></tr>{rows}</table>
<div class="section">📋 Full Opportunity Pipeline ({len(opps)} Verticals)</div>
{cards}
<footer><span>Est. Aug 2026 · Dipesh Sukhani + DBot</span>
<a href="about.html">About</a><a href="terms.html">Terms &amp; Disclaimer</a><a href="privacy.html">Privacy</a><a href="data.json">data.json</a><a href="sitemap.xml">Sitemap</a></footer>
</div></body></html>"""
    open(os.path.join(BASE, "index.html"), "w").write(index)

    # --- Subpages ---
    for i, o in enumerate(opps):
        slug = o.get("slug") or f"opp-{o.get('id', i+1)}"
        page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(o["title"])} — India Opportunity Hunter</title>
<meta name="description" content="{esc(o.get("idea","")[:150])}">
<link rel="canonical" href="https://hunter.dipesh.one/opportunities/{esc(slug)}.html">
<style>body{{font-family:system-ui,-apple-system,sans-serif;max-width:820px;margin:40px auto;padding:0 20px;line-height:1.65;color:#111827}}h1,h2,h3{{line-height:1.25}}hr{{border:none;border-top:1px solid #e5e7eb;margin:24px 0}}a{{color:#1d4ed8;text-decoration:none}}a:hover{{text-decoration:underline}}.meta{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:14px 18px;font-size:14px;margin:16px 0}}li{{margin:8px 0}}.insight{{color:#4b5563;font-size:14px;margin-top:4px;background:#f3f4f6;padding:6px 10px;border-radius:6px}}</style></head>
<body><p><a href="../index.html">&larr; Back to all opportunities</a></p>
<h1 style="margin-top:14px">{i+1}. {esc(o["title"])}</h1>
<div class="meta"><b>Verdict:</b> {esc(o.get("verdict") or "IN PIPELINE (Dig Depth: " + str(o.get("dig_depth",0)) + "/3)")} · <b>Sector:</b> {esc(o.get("sector","TBD"))} · <b>Model:</b> {esc(o.get("model","TBD"))} · <b>Geography:</b> {esc(o.get("city_focus","Mumbai/Bangalore"))}<br>
<b>Entry capital:</b> {esc(o.get("entry_capital_inr","TBD"))} · <b>EBITDA timeline:</b> {esc(o.get("ebitda_timeline","see dossier"))} · <b>Margins:</b> {esc(o.get("margins","TBD"))}</div>
<p><b>The Core Thesis:</b> {esc(o.get("idea",""))}</p>
{render_lists(o.get("breakdown", {}))}
<hr>
{render_sources(o.get("sources", {}))}
<hr><p><small>Updated {esc(o.get("updated_at","2026-08-18"))} · <a href="../data.json">data.json</a></small></p>
</body></html>"""
        open(os.path.join(OUT, f"{slug}.html"), "w").write(page)

    print(f"Generated index.html + {len(opps)} subpages -> {OUT}")

if __name__ == "__main__":
    build()
