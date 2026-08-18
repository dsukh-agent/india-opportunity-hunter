#!/usr/bin/env python3
"""
Generate the India Opportunity Hunter static site from data.json.
- index.html: numbered shortlist + all opportunities with link to each subpage
- opportunities/<slug>.html: full dossier per opportunity (Perplexity-style), numbered,
  with clickable news + YouTube sources and transcript-derived key insights.
Run: python3 generate_site.py
"""
import json, os, html

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data.json")
OUT  = os.path.join(BASE, "opportunities")

def esc(s):
    return html.escape(str(s))

def render_sources(sources):
    blocks = []
    if sources.get("news_and_market"):
        items = "".join(
            f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a></li>'
            for s in sources["news_and_market"])
        blocks.append(f'<h3>📰 News &amp; Market Sources</h3><ul>{items}</ul>')
    if sources.get("youtube_practitioner"):
        items = ""
        for s in sources["youtube_practitioner"]:
            items += f'<li><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["label"])}</a>'
            if s.get("key_insight"):
                items += f'<div class="insight">💡 {esc(s["key_insight"])}</div>'
            items += '</li>'
        blocks.append(f'<h3>🎬 YouTube Practitioner Goldmine</h3><ul>{items}</ul>')
    return "\n".join(blocks)

def render_lists(d):
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
    opps = data["opportunities"]

    # --- index ---
    short = [o for o in opps if o.get("verdict") and "STRONG" in o["verdict"].upper()][:5]
    rows = "".join(
        f'<tr><td>{i+1}</td><td><a href="opportunities/{esc(o["slug"])}.html">{esc(o["title"])}</a></td>'
        f'<td>{esc(o["sector"])}</td><td><b>{esc(o["verdict"])}</b></td>'
        f'<td>{esc(o["entry_capital_inr"])}</td><td>{esc(o["ebitda_timeline"])}</td></tr>'
        for i, o in enumerate(short))
    all_opps = "".join(
        f'<hr><h2>{i+1}. <a href="opportunities/{esc(o["slug"])}.html">{esc(o["title"])}</a></h2>'
        f'<p><b>Verdict:</b> {esc(o["verdict"])} · <b>Entry:</b> {esc(o["entry_capital_inr"])} · '
        f'<b>EBITDA:</b> {esc(o["ebitda_timeline"])}</p>'
        f'<p>{esc(o["idea"])}</p><p><a href="opportunities/{esc(o["slug"])}.html">View full dossier &rarr;</a></p>'
        for i, o in enumerate(opps))
    index = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>India Opportunity Hunter — Live AI-Citable Business Database</title>
<meta name="description" content="Living, AI-citable database of unfashionable cash-flow business opportunities in India (2026-27). Each opportunity has its own full source dossier.">
<link rel="canonical" href="https://dsukh-agent.github.io/india-opportunity-hunter/">
<style>body{{font-family:system-ui,sans-serif;max-width:820px;margin:40px auto;padding:0 20px;line-height:1.6;color:#222}}h1,h2,h3{{line-height:1.25}}hr{{border:none;border-top:2px solid #e5e5e5;margin:28px 0}}a{{color:#0969da}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ddd;padding:8px;text-align:left;font-size:14px}}</style></head>
<body><p><a href="about.html">About</a> · <a href="analytics.html">📊 Live Analytics</a> · <a href="CONTRIBUTING.md">Contribute</a> · <a href="data.json">data.json</a> · <a href="https://github.com/dsukh-agent/india-opportunity-hunter" target="_blank">GitHub</a></p>
<h1>India Opportunity Hunter</h1>
<p>A living, AI-citable database of <b>unfashionable, cash-flow-positive business opportunities in India (2026–27)</b>.</p>
<p>Continuously updated by an automated research hunter (Perplexity + YouTube practitioner content + market research). Every entry is vetted for: any sector/model, <b>positive EBITDA ASAP</b>, NRI-return founder fit (Mumbai/Bangalore), ~₹1 Cr entry. Deliberately <b>un-biased</b> toward tech/web3/startup ideas.</p>
<ul><li><b>Machine-readable:</b> <a href="data.json">data.json</a></li><li><b>Contribute:</b> <a href="CONTRIBUTING.md">CONTRIBUTING.md</a></li></ul>
<h2>🏆 The Shortlist (ranked by cash-flow fit)</h2>
<table><tr><th>#</th><th>Opportunity</th><th>Sector</th><th>Verdict</th><th>Entry</th><th>EBITDA</th></tr>{rows}</table>
<h2>📋 All Vetted Opportunities (click for full source dossier)</h2>
{all_opps}
<hr><p><small>Last updated {esc(data["last_updated"])} · Schema v{esc(data["schema_version"])} · Scope: India (global-ready)</small></p>
<script>fetch("https://hunter-analytics.dipeshsukhani.dev/hit").catch(()=>{});</script>
</body></html>"""
    open(os.path.join(BASE, "index.html"), "w").write(index)

    # --- subpages ---
    for i, o in enumerate(opps):
        slug = o["slug"]
        page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(o["title"])} — India Opportunity Hunter</title>
<meta name="description" content="{esc(o["idea"][:150])}">
<link rel="canonical" href="https://dsukh-agent.github.io/india-opportunity-hunter/opportunities/{esc(slug)}.html">
<style>body{{font-family:system-ui,sans-serif;max-width:820px;margin:40px auto;padding:0 20px;line-height:1.6;color:#222}}h1,h2,h3{{line-height:1.25}}hr{{border:none;border-top:2px solid #e5e5e5;margin:24px 0}}a{{color:#0969da}}.meta{{background:#f6f8fa;border-radius:8px;padding:12px 16px;font-size:14px}}li{{margin:8px 0}}.insight{{color:#57606a;font-size:14px;margin-top:4px}}</style></head>
<body><p><a href="../index.html">&larr; Back to all opportunities</a></p>
<h1>{i+1}. {esc(o["title"])}</h1>
<div class="meta"><b>Verdict:</b> {esc(o["verdict"])} · <b>Sector:</b> {esc(o["sector"])} · <b>Model:</b> {esc(o["model"])} · <b>Country:</b> {esc(o["country"])} ({esc(o["city_focus"])})<br>
<b>Entry capital:</b> {esc(o["entry_capital_inr"])} · <b>EBITDA timeline:</b> {esc(o["ebitda_timeline"])} · <b>Margins:</b> {esc(o["margins"])}</div>
<p><b>The idea:</b> {esc(o["idea"])}</p>
{render_lists(o.get("breakdown", {}))}
<hr>
{render_sources(o.get("sources", {}))}
<hr><p><small>Updated {esc(o["updated_at"])} · <a href="../data.json">data.json</a></small></p>
</body></html>"""
        open(os.path.join(OUT, f"{slug}.html"), "w").write(page)

    print(f"Generated index.html + {len(opps)} subpages -> {OUT}")

if __name__ == "__main__":
    build()
