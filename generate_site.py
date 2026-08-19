#!/usr/bin/env python3
"""
Generate the India Opportunity Hunter static site from data.json.
"""
import json, os, html, urllib.parse

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data.json")
OUT  = os.path.join(BASE, "opportunities")

def esc(s):
    return html.escape(str(s if s is not None else ""))

def render_sources(sources):
    if not isinstance(sources, dict) or not sources:
        return "<p><em>⏳ Field research and practitioner interviews currently in progress...</em></p>"
    blocks = []
    if sources.get("news_and_market"):
        items = "".join(
            f'<li style="margin:8px 0"><a href="{esc(s.get("url",""))}" target="_blank" rel="noopener" style="color:#1d4ed8;font-weight:500">{esc(s.get("label",""))}</a></li>'
            for s in sources["news_and_market"])
        blocks.append(f'<h3 style="margin-top:20px;font-size:16px">📰 News, Market Data &amp; Industry Reports</h3><ul style="padding-left:20px">{items}</ul>')
    if sources.get("youtube_practitioner"):
        items = ""
        for s in sources["youtube_practitioner"]:
            insight = f'<div style="color:#4b5563;font-size:13px;margin-top:4px;background:#f3f4f6;padding:8px 12px;border-radius:6px;border-left:3px solid #1d4ed8">💡 <b>On-Ground Teardown Summary:</b> {esc(s["key_insight"])}</div>' if s.get("key_insight") else ""
            items += f'<li style="margin:14px 0"><a href="{esc(s.get("url",""))}" target="_blank" rel="noopener" style="color:#1d4ed8;font-weight:600;font-size:15px">▶️ {esc(s.get("label",""))}</a>{insight}</li>'
        blocks.append(f'<h3 style="margin-top:24px;font-size:16px">🎬 YouTube Practitioner Case Studies &amp; Teardowns</h3><ul style="padding-left:20px;list-style:none">{items}</ul>')
    return "\n".join(blocks) if blocks else "<p><em>⏳ Field research logs being compiled...</em></p>"

def render_scorecard(sc):
    if not isinstance(sc, dict) or not sc:
        return ""
    labels = [
        ("working_capital", "1. Working Capital & Bad Debt (30%)"),
        ("vendor_lockin", "2. Vendor / OEM Lock-in (20%)"),
        ("labor_friction", "3. Labor & Route Friction (20%)"),
        ("regulatory_moat", "4. Regulatory Moat (15%)"),
        ("capital_velocity", "5. Capital & EBITDA Velocity (15%)")
    ]
    lis = "".join(f'<li style="margin:8px 0"><b>{label}:</b> {esc(sc.get(key, "⏳ Under Audit"))}</li>' for key, label in labels if key in sc)
    return f'<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px;padding:16px;margin:16px 0"><h3 style="margin-top:0;font-size:16px">🎯 5-Pillar Ground-Reality Scorecard</h3><ul style="padding-left:20px">{lis}</ul></div>'

def render_lists(d):
    if not isinstance(d, dict) or not d:
        return ""
    out = []
    if "scorecard" in d:
        out.append(render_scorecard(d["scorecard"]))
    for k, title in [("why_passes","✅ Why it clears the filter (the on-ground data)"),
                     ("unit_economics","💰 Unit Economics & P&L Breakdown"),
                     ("watchouts","⚠️ On-Ground Watch-Outs & Failure Modes"),
                     ("why_rejected","❌ Fatal Flaws & Rejection Reasons")]:
        if d.get(k):
            lis = "".join(f'<li style="margin:8px 0">{esc(x)}</li>' for x in d[k])
            out.append(f'<h3 style="margin-top:24px;font-size:16px">{title}</h3><ul style="padding-left:20px">{lis}</ul>')
    return "\n".join(out)

def build():
    data = json.load(open(DATA))
    os.makedirs(OUT, exist_ok=True)
    opps = data.get("opportunities", [])

    short = [o for o in opps if o.get("verdict") == "STRONG"]
    rejected = [o for o in opps if o.get("verdict") in ["REJECTED", "WEAK"]]
    queue = [o for o in opps if o.get("verdict") == "IN QUEUE"]
    
    rows = "".join(
        f'<tr><td>{i+1}</td><td><a href="opportunities/{esc(o["slug"])}.html" style="color:#1d4ed8;font-weight:600">{esc(o["title"])}</a></td>'
        f'<td>{esc(o.get("sector","⏳ Under Research"))}</td><td><span class="verdict strong">STRONG</span></td>'
        f'<td>{esc(o.get("entry_capital_inr","⏳ Under Research"))}</td><td>{esc(o.get("ebitda_timeline","⏳ Under Research"))}</td></tr>'
        for i, o in enumerate(short))
    
    cards = ""
    for i, o in enumerate(opps):
        v = (o.get("verdict") or "IN QUEUE").upper()
        if "STRONG" in v:
            badge = '<span class="verdict strong">STRONG (PASSED)</span>'
        elif "REJECT" in v or "WEAK" in v:
            badge = '<span class="verdict weak">REJECTED</span>'
        else:
            badge = '<span class="verdict pending">⏳ IN QUEUE</span>'
            
        slug = o.get("slug") or f"opp-{o.get('id', i+1)}"
        rej_box = f'<div class="rej-box"><b>❌ Fatal Flaw:</b> {esc(o["rejection_reason"])}</div>' if o.get("rejection_reason") else ""
        
        cards += f"""
<div class="card">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px">
    <h2><a href="opportunities/{esc(slug)}.html" style="color:var(--ink);text-decoration:none">{i+1}. {esc(o["title"])}</a></h2>
    {badge}
  </div>
  <p>{esc(o.get("idea",""))}</p>
  {rej_box}
  <div class="meta" style="margin-top:10px">
    <b>Sector:</b> {esc(o.get("sector","⏳ Under Research"))} · <b>Model:</b> {esc(o.get("model","⏳ Under Research"))} · <b>Capital:</b> {esc(o.get("entry_capital_inr","⏳ Under Research"))} · <b>EBITDA Margin:</b> {esc(o.get("ebitda_margin","⏳ Under Research"))} · <b>Timeline:</b> {esc(o.get("ebitda_timeline","⏳ Under Research"))}
  </div>
  <a class="dossier" href="opportunities/{esc(slug)}.html">View full research dossier &rarr;</a>
</div>"""

    index = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>India Opportunity Hunter — Live AI-Citable Business Database</title>
<meta name="google-site-verification" content="TjFs1HMyRiUvvqgjX0r6AahweiY0CeTHb7qX3km8OSE" />
<meta name="description" content="Living, AI-citable database of unfashionable, cash-flow-positive business opportunities in India (2026-27).">
<meta name="robots" content="index,follow">
<link rel="canonical" href="https://hunter.dipesh.one/">
<style>
:root{{--ink:#111827;--muted:#6b7280;--brand:#1d4ed8;--bg:#f9fafb;--card:#ffffff;--line:#e5e7eb;--danger:#dc2626;--success:#16a34a}}
*{{box-sizing:border-box;margin:0;padding:0}}
body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;background:var(--bg);color:var(--ink);line-height:1.65}}
.wrap{{max-width:880px;margin:0 auto;padding:32px 20px 60px}}
.topnav{{display:flex;gap:22px;align-items:center;font-size:14px;padding:18px 0;border-bottom:1px solid var(--line);margin-bottom:28px}}
.brand{{font-weight:700;font-size:16px;color:var(--ink);margin-right:auto}}
.topnav a{{color:var(--muted);text-decoration:none;font-weight:500}}
.topnav a:hover{{color:var(--brand)}}
h1{{font-size:32px;line-height:1.2;margin-bottom:10px}}
.tagline{{color:var(--muted);font-size:16px;max-width:680px;margin-bottom:26px}}
.statsbar{{display:grid;grid-template-columns:repeat(auto-fit,minmax(130px,1fr));gap:16px;background:linear-gradient(135deg,#1e3a8a,#1d4ed8);color:#fff;border-radius:14px;padding:20px 24px;margin-bottom:30px}}
.stat .num{{font-size:28px;font-weight:800;line-height:1.1}}
.stat .lbl{{font-size:12px;opacity:.9;margin-top:4px}}
.card{{background:var(--card);border:1px solid var(--line);border-radius:12px;padding:22px;margin:16px 0;box-shadow:0 1px 3px rgba(0,0,0,0.02)}}
.card h2{{font-size:20px}}
.verdict{{display:inline-block;font-size:12px;font-weight:700;padding:4px 10px;border-radius:20px}}
.strong{{background:#dcfce7;color:#15803d}}.weak{{background:#fee2e2;color:#b91c1c}}.pending{{background:#f3f4f6;color:#4b5563}}
.card p{{color:var(--ink);margin:8px 0}}
.card .meta{{color:var(--muted);font-size:13px;border-top:1px solid var(--line);padding-top:10px}}
.rej-box{{background:#fef2f2;border-left:3px solid var(--danger);padding:10px 14px;border-radius:4px;font-size:13px;color:#991b1b;margin:10px 0}}
.crowd-banner{{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:10px;padding:16px 20px;margin:24px 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.crowd-banner p{{margin:0;font-size:14px;color:#166534}}
.btn-feedback{{background:#16a34a;color:#fff;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;text-decoration:none;display:inline-block}}
.btn-feedback:hover{{background:#15803d}}
a.dossier{{display:inline-block;margin-top:10px;color:var(--brand);font-weight:600;font-size:14px;text-decoration:none}}
a.dossier:hover{{text-decoration:underline}}
.section{{font-size:14px;text-transform:uppercase;letter-spacing:.06em;color:var(--muted);font-weight:700;margin:32px 0 10px}}
table{{border-collapse:collapse;width:100%;background:#fff;border-radius:8px;overflow:hidden;border:1px solid var(--line);margin:12px 0}}
th,td{{padding:12px 14px;border-bottom:1px solid var(--line);text-align:left;font-size:14px}}
th{{background:#f8fafc;font-weight:600}}
footer{{border-top:1px solid var(--line);margin-top:40px;padding-top:20px;color:var(--muted);font-size:13px;display:flex;gap:20px;flex-wrap:wrap}}
footer a{{color:var(--muted);text-decoration:none}}
footer a:hover{{color:var(--brand)}}
</style></head><body>
<div class="wrap">
<div class="topnav"><a class="brand" href="index.html">India Opportunity Hunter</a>
<a href="about.html">About &amp; Scorecard</a><a href="analytics.html">📊 Analytics</a><a href="CONTRIBUTING.md">Contribute</a><a href="data.json">data.json</a><a href="https://github.com/dsukh-agent/india-opportunity-hunter" target="_blank">GitHub</a></div>
<h1>India Opportunity Hunter</h1>
<p class="tagline">A living, AI-citable database of <b>unfashionable, cash-flow-positive business opportunities</b> in India (2026–27). Evaluated purely on cash-flow fit — positive EBITDA ASAP — with zero category bias.</p>

<div class="crowd-banner">
  <p><b>💬 Crowdsourced Intelligence:</b> Have on-ground data, supplier pricing, or want to challenge our numbers? Submit your field intel to help sharpen the database.</p>
  <a href="https://github.com/dsukh-agent/india-opportunity-hunter/issues/new?title=%5BField+Intel%5D+General+Feedback&labels=field-intel&body=Describe+the+on-ground+numbers%2C+pricing%2C+or+new+opportunity+proposal+here:" target="_blank" class="btn-feedback">Submit Field Intel &rarr;</a>
</div>

<div class="statsbar">
  <div class="stat"><div class="num">{len(opps)}</div><div class="lbl">Total Evaluated</div></div>
  <div class="stat"><div class="num" style="color:#86efac">{len(short)}</div><div class="lbl">Shortlisted (STRONG)</div></div>
  <div class="stat"><div class="num" style="color:#fca5a5">{len(rejected)}</div><div class="lbl">Rejected / Unviable</div></div>
  <div class="stat"><div class="num">{len(queue)}</div><div class="lbl">In Queue</div></div>
</div>
<div class="section">🏆 Qualified Shortlist ({len(short)} Passed All Gates)</div>
<table><tr><th>#</th><th>Opportunity</th><th>Sector</th><th>Verdict</th><th>Capital Required</th><th>EBITDA Timeline</th></tr>{rows}</table>
<div class="section">📋 Full Pipeline Analysis ({len(opps)} Verticals)</div>
{cards}
<footer><span>Est. Aug 2026 · Dipesh Sukhani + DBot</span>
<a href="about.html">About &amp; Scorecard</a><a href="terms.html">Terms &amp; Disclaimer</a><a href="privacy.html">Privacy</a><a href="data.json">data.json</a><a href="sitemap.xml">Sitemap</a></footer>
</div></body></html>"""
    open(os.path.join(BASE, "index.html"), "w").write(index)

    # --- Generate Dense Dossier Subpages ---
    for i, o in enumerate(opps):
        slug = o.get("slug") or f"opp-{o.get('id', i+1)}"
        v = o.get("verdict", "IN QUEUE")
        badge_style = "color:#15803d;background:#dcfce7;" if v == "STRONG" else ("color:#b91c1c;background:#fee2e2;" if v in ["REJECTED","WEAK"] else "color:#374151;background:#f3f4f6;")
        
        rej_section = f'<div style="background:#fef2f2;border-left:4px solid #dc2626;padding:14px 18px;border-radius:6px;margin:18px 0;color:#991b1b"><h3 style="margin-top:0;font-size:16px">❌ Fatal Flaw &amp; Rejection Reason</h3><p style="margin:6px 0">{esc(o.get("rejection_reason",""))}</p></div>' if o.get("rejection_reason") else ""
        
        issue_title = urllib.parse.quote(f"[Field Intel] Challenge/Feedback on #{i+1} {o['title']}")
        issue_body = urllib.parse.quote(f"### Feedback on {o['title']}\n\n**1. What did we get wrong?** (e.g. capital range, EBITDA timeline, operational flaw, bad source link):\n\n**2. Real-world / On-ground Evidence:** (Provide YouTube teardowns, supplier quotes, invoice data, or municipal facts):\n\n**3. Proposed Scorecard Correction:** (Working Capital, OEM Lockin, etc.):\n")
        issue_url = f"https://github.com/dsukh-agent/india-opportunity-hunter/issues/new?title={issue_title}&labels=field-intel,dossier-review&body={issue_body}"
        
        page = f"""<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(o["title"])} — Research Dossier | India Opportunity Hunter</title>
<meta name="description" content="{esc(o.get("idea","")[:150])}">
<link rel="canonical" href="https://hunter.dipesh.one/opportunities/{esc(slug)}.html">
<style>
body{{font-family:system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;max-width:840px;margin:40px auto;padding:0 24px;line-height:1.7;color:#111827;background:#fff}}
h1{{font-size:28px;line-height:1.2;margin-top:16px;margin-bottom:12px}}
h2{{font-size:20px;margin-top:32px;margin-bottom:12px;border-bottom:1px solid #e5e7eb;padding-bottom:6px}}
h3{{font-size:16px;margin-top:20px;margin-bottom:6px}}
hr{{border:none;border-top:1px solid #e5e7eb;margin:28px 0}}
a{{color:#1d4ed8;text-decoration:none}}
a:hover{{text-decoration:underline}}
.meta-box{{background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:18px 22px;font-size:14px;margin:20px 0}}
.badge{{padding:4px 12px;border-radius:20px;font-weight:700;font-size:13px;display:inline-block}}
.feedback-box{{background:#f0fdf4;border:1px solid #bbf7d0;border-radius:8px;padding:16px 20px;margin:28px 0;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:12px}}
.feedback-box p{{margin:0;font-size:14px;color:#166534}}
.btn-feedback{{background:#16a34a;color:#fff;padding:8px 16px;border-radius:6px;font-size:13px;font-weight:600;text-decoration:none;display:inline-block}}
.btn-feedback:hover{{background:#15803d}}
li{{margin:8px 0}}
footer{{color:#6b7280;font-size:13px;margin-top:40px;border-top:1px solid #e5e7eb;padding-top:16px;display:flex;gap:18px;flex-wrap:wrap}}
</style></head>
<body>
<p><a href="../index.html">&larr; Back to all opportunities</a></p>
<h1>{i+1}. {esc(o["title"])}</h1>
<div class="meta-box">
  <span class="badge" style="{badge_style}">{esc(v)}</span><br><br>
  <b>Sector:</b> {esc(o.get("sector","⏳ Under Research"))} · <b>Business Model:</b> {esc(o.get("model","⏳ Under Research"))} · <b>Target Geography:</b> {esc(o.get("city_focus","Mumbai / Bangalore"))}<br>
  <b>Capital Required:</b> {esc(o.get("entry_capital_inr","⏳ Under Research"))} · <b>EBITDA Margin:</b> {esc(o.get("ebitda_margin","⏳ Under Research"))} · <b>EBITDA Timeline:</b> {esc(o.get("ebitda_timeline","⏳ Under Research"))}
</div>

<h2>Business Concept &amp; Strategy</h2>
<p>{esc(o.get("idea",""))}</p>

{rej_section}
{render_lists(o.get("breakdown", {}))}

<hr>
<h2>📚 Research Dossier &amp; Primary Sources</h2>
{render_sources(o.get("sources", {}))}

<div class="feedback-box">
  <p><b>💬 Challenge this Dossier:</b> Have on-ground data, supplier quotes, or think our numbers/links are wrong?</p>
  <a href="{issue_url}" target="_blank" class="btn-feedback">Submit Correction / Intel &rarr;</a>
</div>

<footer>
  <a href="../index.html">All Opportunities</a>
  <a href="../about.html">About &amp; Scorecard</a>
  <a href="../data.json">data.json</a>
  <span style="margin-left:auto">Last updated {esc(o.get("updated_at","2026-08-19"))}</span>
</footer>
</body></html>"""
        open(os.path.join(OUT, f"{slug}.html"), "w").write(page)

    print(f"Generated clean index.html + {len(opps)} dense subpage dossiers with Crowdsource Intel buttons.")

if __name__ == "__main__":
    build()
