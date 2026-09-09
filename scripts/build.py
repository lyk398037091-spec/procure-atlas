#!/usr/bin/env python3
import json, os, html, shutil
from pathlib import Path
from urllib.parse import urljoin

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data'; SITE=ROOT/'site'
SITE_URL=os.environ.get('SITE_URL','https://example.github.io/procure-atlas').rstrip('/')+'/'

def load(name): return json.loads((DATA/name).read_text(encoding='utf-8'))
M=load('manufacturers.json'); P=load('products.json'); C=load('capabilities.json'); A=load('applications.json'); MARKET=json.loads((DATA/'market.json').read_text())
PB={x['slug']:x for x in P}; CB={x['slug']:x for x in C}; AB={x['slug']:x for x in A}

def esc(s): return html.escape(str(s or ''), quote=True)
def eurl(s): return esc(s)

def rel(depth, path=''):
    return ('../'*depth)+path

def page_shell(title, description, body, depth=0, canonical='', structured=None):
    prefix='../'*depth
    canon=urljoin(SITE_URL, canonical.lstrip('/')) if canonical else SITE_URL
    jsonld=''
    if structured:
        jsonld=f'<script type="application/ld+json">{json.dumps(structured,ensure_ascii=False)}</script>'
    return f'''<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}">
<link rel="canonical" href="{esc(canon)}"><meta name="robots" content="index,follow">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website">
<link rel="stylesheet" href="{prefix}assets/styles.css">{jsonld}
</head><body>
<div class="announcement">Independent sourcing database · <strong>public-source evidence, not paid rankings</strong></div>
<nav class="nav"><div class="container nav-inner">
<a class="brand" href="{prefix}index.html"><span class="brand-mark">P</span>ProcureAtlas</a>
<div class="nav-links"><a href="{prefix}manufacturers/index.html">Manufacturers</a><a href="{prefix}products/index.html">Machines</a><a href="{prefix}compare/index.html">Compare</a><a href="{prefix}methodology/index.html">Methodology</a></div>
<div class="nav-cta"><a class="btn btn-sm" href="{prefix}methodology/index.html">How evidence works</a><a class="btn btn-primary btn-sm" href="{prefix}rfq/index.html">Create RFQ</a></div>
</div></nav>
{body}
<footer class="footer"><div class="container"><div class="footer-grid">
<div><a class="brand" href="{prefix}index.html"><span class="brand-mark">P</span>ProcureAtlas</a><p class="meta">A neutral manufacturer-discovery and procurement-decision layer. Initial vertical: packaging machinery in China.</p></div>
<div><h4>Explore</h4><a href="{prefix}manufacturers/index.html">Manufacturers</a><a href="{prefix}products/index.html">Machines</a><a href="{prefix}compare/index.html">Compare</a></div>
<div><h4>Trust</h4><a href="{prefix}methodology/index.html">Methodology</a><a href="{prefix}llms.txt">llms.txt</a><a href="{prefix}data/manufacturers.json">Public data snapshot</a></div>
<div><h4>Procurement</h4><a href="{prefix}rfq/index.html">Create RFQ</a><a href="{prefix}manufacturers/index.html">Find suppliers</a></div>
</div><div class="footer-note">MVP v0.1 · Manufacturer profiles are built from cited public sources. ProcureAtlas has not conducted on-site factory audits of the listed companies.</div></div></footer>
<div class="compare-box" data-compare-box data-base="{prefix}"><div class="compare-items" data-compare-items></div><div class="compare-actions"><button class="btn btn-sm btn-ghost" data-compare-clear>Clear</button><a class="btn btn-lime btn-sm" data-compare-go href="{prefix}compare/index.html">Compare now</a></div></div>
<script src="{prefix}assets/data.js"></script><script src="{prefix}assets/app.js"></script></body></html>'''

def write(path, content):
    p=SITE/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(content,encoding='utf-8')

def pills(items, lookup, maxn=5):
    return ''.join(f'<span class="pill">{esc(lookup[x]["name"])}</span>' for x in items[:maxn] if x in lookup)

def manufacturer_card(m, depth=0):
    search=' '.join([m['name'],m['shortName'],m['city'],m['province'],m['summary']]+[PB[x]['name'] for x in m['products'] if x in PB]+[CB[x]['name'] for x in m['capabilities'] if x in CB])
    href=('../'*depth)+f'manufacturers/{m["slug"]}/index.html' if depth==0 else ('../'*depth)+f'manufacturers/{m["slug"]}/index.html'
    return f'''<article class="card" data-manufacturer-card data-products="{','.join(m['products'])}" data-region="{esc(m['province'])}" data-search="{esc(search)}">
<div class="card-top"><div><div class="meta">{esc(m['province'])} · {esc(m['city'])}</div><h3>{esc(m['shortName'])}</h3></div><span class="badge badge-green">Evidence linked</span></div>
<p class="meta">{esc(m['summary'])}</p><div class="pill-row">{pills(m['products'],PB,4)}</div>
<div class="card-footer"><a class="link-arrow" href="{href}">View evidence profile →</a><button class="btn btn-sm" data-compare-toggle="{esc(m['slug'])}">Compare</button></div></article>'''

# data assets
(SITE/'assets').mkdir(parents=True,exist_ok=True)
write(Path('assets/data.js'),'window.PROCURE_ATLAS_DATA='+json.dumps({'manufacturers':M,'products':P,'capabilities':C,'applications':A},ensure_ascii=False,separators=(',',':'))+';')
public_data=SITE/'data'; public_data.mkdir(exist_ok=True)
for fname in ['manufacturers.json','products.json','capabilities.json','applications.json','market.json']:
    shutil.copy2(DATA/fname,public_data/fname)

# home
featured=''.join(manufacturer_card(m,0) for m in M[:6])
product_cards=''.join(f'''<a class="card product-card" href="products/{p['slug']}/index.html"><div class="meta">{esc(p['category'])}</div><h3>{esc(p['name'])}</h3><p class="meta">{esc(p['description'])}</p><div class="card-footer"><span class="link-arrow">Explore matching manufacturers →</span></div></a>''' for p in P[:6])
home=f'''<main>
<section class="hero"><div class="container hero-grid"><div><span class="eyebrow"><span class="eyebrow-dot"></span>Evidence-first manufacturer discovery</span><h1>Find the right packaging machinery manufacturer. Faster.</h1><p class="hero-copy">Search machine types, capabilities and applications across independent manufacturer profiles. Every important claim is designed to trace back to a source.</p>
<form class="search-shell"><input data-sourcing-input aria-label="Sourcing requirement" placeholder="e.g. premade pouch line with end-of-line palletizing"><button class="btn btn-primary">Find matches</button></form><div class="search-results" data-sourcing-results></div><div class="search-hint">MVP search is deterministic keyword matching — it does not invent supplier capabilities.</div></div>
<div class="hero-panel"><div class="panel-kicker">What the platform should answer</div><div class="match-card"><div class="match-title">“Who can fit this packaging project — and what is the evidence?”</div><div class="match-list"><div class="match-row"><span>Machine fit</span><span class="score">Structured</span></div><div class="match-row"><span>Capability fit</span><span class="score">Comparable</span></div><div class="match-row"><span>Source evidence</span><span class="score">Traceable</span></div><div class="match-row"><span>Paid ranking influence</span><span class="score">0%</span></div></div></div><div class="hero-metric"><span class="metric-chip">{len(M)} seed manufacturers</span><span class="metric-chip">{len(P)} machine types</span><span class="metric-chip">{sum(len(x['evidence']) for x in M)} evidence records</span></div></div></div></section>
<section class="stats"><div class="container stat-grid"><div class="stat"><div class="stat-value">US$1.873B</div><div class="stat-label">China packaging machinery exports, Jan–Apr 2026*</div></div><div class="stat"><div class="stat-value">+11.3%</div><div class="stat-label">YoY export value growth in that period*</div></div><div class="stat"><div class="stat-value">Claim-level</div><div class="stat-label">Evidence model, not one vague company score</div></div><div class="stat"><div class="stat-value">Neutral</div><div class="stat-label">Organic matching separated from sponsorship</div></div></div><div class="container"><p class="search-hint">* Market context source is recorded in the public market data snapshot.</p></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">Manufacturer database</span><h2>Start with evidence, not “top 10” lists.</h2><p>Seed profiles are deliberately conservative. A public-source profile is not presented as an on-site factory audit.</p></div><a class="btn" href="manufacturers/index.html">Browse all manufacturers</a></div><div class="grid-3">{featured}</div></div></section>
<section class="section"><div class="container"><div class="section-head"><div><span class="eyebrow">Machine taxonomy</span><h2>Procurement starts from the machine, process and application.</h2></div><a class="btn" href="products/index.html">View machine directory</a></div><div class="product-grid">{product_cards}</div></div></section>
<section class="section dark-section"><div class="container"><div class="section-head"><div><span class="eyebrow">Trust architecture</span><h2>How a supplier claim becomes publishable.</h2><p>No AI-generated capability goes live merely because it sounds plausible.</p></div></div><div class="process-grid"><div class="process"><div class="process-num">01 / DISCOVER</div><h3>Find the official source</h3><p>Manufacturer website, association directory, filings or other public evidence.</p></div><div class="process"><div class="process-num">02 / EXTRACT</div><h3>Structure the claim</h3><p>Turn free text into products, capabilities, applications and company facts.</p></div><div class="process"><div class="process-num">03 / REVIEW</div><h3>Keep source + date</h3><p>Every evidence record carries source type, checked date and confidence.</p></div><div class="process"><div class="process-num">04 / MATCH</div><h3>Rank by procurement fit</h3><p>Matching is intended to use requirement fit and evidence, never hidden payment.</p></div></div></div></section>
</main>'''
write(Path('index.html'),page_shell('ProcureAtlas — Evidence-first packaging machinery sourcing','Find and compare Chinese packaging machinery manufacturers using structured machine, capability and source evidence.',home,0,'',{'@context':'https://schema.org','@type':'WebSite','name':'ProcureAtlas','url':SITE_URL}))

# manufacturers list
regions=sorted({m['province'] for m in M})
options_p=''.join(f'<option value="{p["slug"]}">{esc(p["name"])}</option>' for p in P)
options_r=''.join(f'<option value="{esc(r)}">{esc(r)}</option>' for r in regions)
cards=''.join(manufacturer_card(m,1) for m in M)
body=f'''<main data-manufacturer-finder><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> / Manufacturers</div><h1>Packaging machinery manufacturers</h1><p>Search by machine, capability, company or region. Profiles remain public-source records until a stronger verification layer is completed.</p></div></section><section class="section-tight"><div class="container"><div class="toolbar"><input class="input" data-filter-q placeholder="Search manufacturer or capability"><select class="select" data-filter-product><option value="">All machine types</option>{options_p}</select><select class="select" data-filter-region><option value="">All regions</option>{options_r}</select></div><div class="result-summary"><span data-result-count></span><a href="../methodology/index.html">Read verification methodology →</a></div><div class="manufacturer-grid">{cards}</div></div></section></main>'''
write(Path('manufacturers/index.html'),page_shell('Packaging machinery manufacturers — ProcureAtlas','Browse independent public-source profiles of Chinese packaging machinery manufacturers.',body,1,'manufacturers/'))

# individual manufacturer pages
for m in M:
    product_links=''.join(f'<a class="pill pill-strong" href="../../products/{s}/index.html">{esc(PB[s]["name"])}</a>' for s in m['products'] if s in PB)
    cap_pills=''.join(f'<span class="pill">{esc(CB[s]["name"])}</span>' for s in m['capabilities'] if s in CB)
    app_pills=''.join(f'<span class="pill">{esc(AB[s]["name"])}</span>' for s in m['applications'] if s in AB)
    ev=''.join(f'''<div class="evidence"><div class="evidence-claim">{esc(x['claim'])}</div><div class="evidence-source"><span class="badge badge-green">{esc(x['confidence'])} confidence</span><span>{esc(x['sourceType'])}</span><span>Checked {esc(x['checked'])}</span><a rel="nofollow noopener" target="_blank" href="{eurl(x['source'])}">Open source ↗</a></div></div>''' for x in m['evidence'])
    founded=m['founded'] if m['founded'] else 'Not yet verified'
    b=f'''<main><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../../index.html">Home</a> / <a href="../index.html">Manufacturers</a> / {esc(m['shortName'])}</div><div class="profile-hero"><div class="profile-main"><span class="badge badge-green">{esc(m['status'])}</span><h1>{esc(m['shortName'])}</h1><p class="hero-copy">{esc(m['summary'])}</p><div class="pill-row">{product_links}</div></div><aside class="profile-side"><div class="panel-kicker">Profile status</div><h3>{esc(m['auditStatus'])}</h3><p class="meta">This page distinguishes public-source evidence from an on-site or document-level factory audit.</p><a class="btn btn-lime" href="{eurl(m['website'])}" target="_blank" rel="nofollow noopener">Visit official website ↗</a><button class="btn" data-compare-toggle="{esc(m['slug'])}">Compare manufacturer</button></aside></div></div></section>
<section class="section-tight"><div class="container detail-grid"><div><section class="info-section"><h2>Publicly evidenced products</h2><div class="pill-row">{product_links}</div></section><section class="info-section"><h2>Capabilities in current data snapshot</h2><div class="pill-row">{cap_pills}</div><p class="search-hint">A capability shown here should be supported by one or more public evidence records; the MVP still requires claim-level mapping to be completed for every individual capability.</p></section><section class="info-section"><h2>Evidence records</h2>{ev}</section></div><div><section class="info-section"><h2>Company facts</h2><dl class="kv"><dt>Legal/display name</dt><dd>{esc(m['name'])}</dd><dt>Location</dt><dd>{esc(m['city'])}, {esc(m['province'])}</dd><dt>Founded</dt><dd>{esc(founded)}</dd><dt>Evidence status</dt><dd>{esc(m['status'])}</dd><dt>Audit status</dt><dd>{esc(m['auditStatus'])}</dd></dl></section><section class="info-section"><h2>Applications</h2><div class="pill-row">{app_pills}</div></section></div></div></section></main>'''
    structured={'@context':'https://schema.org','@type':'Organization','name':m['name'],'url':m['website'],'address':{'@type':'PostalAddress','addressLocality':m['city'],'addressRegion':m['province'],'addressCountry':'CN'}}
    write(Path(f'manufacturers/{m["slug"]}/index.html'),page_shell(f'{m["shortName"]} — packaging machinery manufacturer profile | ProcureAtlas',m['summary'],b,2,f'manufacturers/{m["slug"]}/',structured))

# products list
pcards=''.join(f'''<a class="card product-card" href="{p['slug']}/index.html"><div class="meta">{esc(p['category'])}</div><h3>{esc(p['name'])}</h3><p class="meta">{esc(p['description'])}</p><div class="card-footer"><span class="link-arrow">View manufacturers →</span><span class="badge badge-gray">{sum(p['slug'] in m['products'] for m in M)} matches</span></div></a>''' for p in P)
body=f'''<main><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> / Machines</div><h1>Packaging machine directory</h1><p>Machine pages act as structured procurement entry points, linking requirements to manufacturer evidence instead of publishing generic SEO listicles.</p></div></section><section class="section-tight"><div class="container product-grid">{pcards}</div></section></main>'''
write(Path('products/index.html'),page_shell('Packaging machine directory — ProcureAtlas','Explore packaging machine categories and manufacturers with public-source evidence.',body,1,'products/'))

# product detail
for p in P:
    matches=[m for m in M if p['slug'] in m['products']]
    mcards=''.join(manufacturer_card(m,2) for m in matches) or '<div class="empty">No manufacturer profile is linked to this machine type yet.</div>'
    b=f'''<main><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../../index.html">Home</a> / <a href="../index.html">Machines</a> / {esc(p['name'])}</div><span class="eyebrow">{esc(p['category'])}</span><h1>{esc(p['name'])}</h1><p>{esc(p['description'])}</p></div></section><section class="section-tight"><div class="container"><div class="section-head"><div><h2>{len(matches)} manufacturers in current evidence snapshot</h2><p>Inclusion means the product category is publicly evidenced in the current dataset; it is not a quality ranking or procurement endorsement.</p></div><a class="btn btn-primary" href="../../rfq/index.html">Create an RFQ</a></div><div class="manufacturer-grid">{mcards}</div></div></section></main>'''
    structured={'@context':'https://schema.org','@type':'CollectionPage','name':p['name'],'description':p['description'],'mainEntity':{'@type':'ItemList','itemListElement':[{'@type':'ListItem','position':i+1,'name':m['name'],'url':urljoin(SITE_URL,f'manufacturers/{m["slug"]}/')} for i,m in enumerate(matches)]}}
    write(Path(f'products/{p["slug"]}/index.html'),page_shell(f'{p["name"]} manufacturers — ProcureAtlas',f'Find manufacturers associated with {p["name"]} and review source evidence.',b,2,f'products/{p["slug"]}/',structured))

# compare
headers='''<div class="empty" data-compare-empty>Select 2–4 manufacturers from the manufacturer directory, then return here.</div><div data-compare-render></div>'''
body=f'''<main><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> / Compare</div><h1>Compare manufacturers by evidence.</h1><p>Comparison shows product and capability coverage recorded in the current public-source snapshot. It deliberately does not invent missing data.</p></div></section><section class="section-tight"><div class="container">{headers}</div></section></main>'''
write(Path('compare/index.html'),page_shell('Compare packaging machinery manufacturers — ProcureAtlas','Compare machine and capability evidence across selected packaging machinery manufacturers.',body,1,'compare/'))

# methodology
body='''<main><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> / Methodology</div><h1>Evidence before recommendation.</h1><p>ProcureAtlas separates a public claim, source evidence and factory audit status so buyers can see what is known and what is still unverified.</p></div></section><section class="section-tight"><div class="container method-grid"><div class="info-section"><h2>Evidence confidence</h2><div class="grade"><div class="grade-letter">A</div><div><h3>Multiple strong sources</h3><p>Official and independent sources materially agree on the claim.</p></div></div><div class="grade"><div class="grade-letter">B</div><div><h3>Strong official source</h3><p>The manufacturer’s official material supports the claim, but independent corroboration is limited.</p></div></div><div class="grade"><div class="grade-letter">C</div><div><h3>Supplier-submitted / limited</h3><p>Useful lead information that still requires stronger verification.</p></div></div><div class="grade"><div class="grade-letter">U</div><div><h3>Unverified</h3><p>Not enough evidence to publish as a confirmed capability.</p></div></div></div><div class="info-section"><h2>Factory-audit status is separate</h2><div class="callout"><strong>Public-source profile ≠ verified factory audit</strong><p>The MVP does not claim that ProcureAtlas has visited or document-audited the seed manufacturers.</p></div><div class="pill-row"><span class="pill">Not audited</span><span class="pill">Document checked</span><span class="pill">Video checked</span><span class="pill">On-site checked</span></div><h2 style="margin-top:24px">Ranking rule</h2><p class="meta">The intended organic matching model uses technical fit, evidence quality, project fit and data freshness. Payment must not silently increase an organic match score. Future sponsored placements must be visibly labelled.</p></div></div><div class="container" style="margin-top:18px"><div class="info-section"><h2>Current MVP limitation</h2><p class="meta">Evidence is attached at manufacturer level in v0.1. The production model already anticipates claim-level evidence mapping, where each product/capability assertion points to one or more exact source records. That mapping is a Gate 2 requirement before scaling the database aggressively.</p></div></div></section></main>'''
write(Path('methodology/index.html'),page_shell('Verification methodology — ProcureAtlas','How ProcureAtlas separates public-source evidence, confidence and factory-audit status.',body,1,'methodology/'))

# RFQ
product_opts=''.join(f'<option>{esc(p["name"])}</option>' for p in P)
body=f'''<main><section class="page-head"><div class="container"><div class="breadcrumb"><a href="../index.html">Home</a> / RFQ</div><h1>Describe the procurement project.</h1><p>The production system will convert this into structured requirements and match evidence-backed suppliers. The GitHub Pages MVP stores submissions locally only.</p></div></section><section class="section-tight"><div class="container rfq-layout"><form class="form-card" data-rfq-form><div class="form-grid"><div class="field"><label>Machine type</label><select class="select" name="machine" required><option value="">Choose a machine</option>{product_opts}</select></div><div class="field"><label>Quantity / line count</label><input class="input" name="quantity" placeholder="e.g. 2 lines"></div><div class="field"><label>Target country</label><input class="input" name="country" placeholder="e.g. Germany"></div><div class="field"><label>Industry/application</label><input class="input" name="application" placeholder="e.g. snack food"></div><div class="field full"><label>Technical requirements</label><textarea class="textarea" name="requirements" required placeholder="Throughput, package format, materials, automation, integrations, certifications, factory acceptance test requirements..."></textarea><div class="help">Specific requirements improve matching and reduce irrelevant supplier responses.</div></div><div class="field"><label>Business email</label><input class="input" type="email" name="email" required placeholder="name@company.com"></div><div class="field"><label>Company</label><input class="input" name="company" required placeholder="Company name"></div><div class="field full"><button class="btn btn-primary" type="submit">Save RFQ preview</button><div class="form-status" data-form-status></div></div></div></form><aside><div class="info-section"><h2>Production flow</h2><div class="grade"><div class="grade-letter">1</div><div><h3>Parse requirements</h3><p>Machine, process, throughput, package type, target market.</p></div></div><div class="grade"><div class="grade-letter">2</div><div><h3>Filter manufacturers</h3><p>Only fields supported by the evidence database participate.</p></div></div><div class="grade"><div class="grade-letter">3</div><div><h3>Explain matches</h3><p>Every recommendation should show why it matched and what remains unverified.</p></div></div></div></aside></div></section></main>'''
write(Path('rfq/index.html'),page_shell('Create packaging machinery RFQ — ProcureAtlas','Create a structured packaging machinery sourcing request for evidence-based supplier matching.',body,1,'rfq/'))

# machine-readable files
llms=f'''# ProcureAtlas\n\n> Evidence-first manufacturer discovery and procurement decision layer. Initial vertical: packaging machinery in China.\n\n## Core principles\n- Manufacturer pages distinguish public-source evidence from factory-audit status.\n- Missing capability data must not be inferred as true.\n- Organic matching is intended to remain independent from paid placement.\n\n## Data\n- {urljoin(SITE_URL,'data/manufacturers.json')}\n- {urljoin(SITE_URL,'data/products.json')}\n- {urljoin(SITE_URL,'data/capabilities.json')}\n- {urljoin(SITE_URL,'data/applications.json')}\n- {urljoin(SITE_URL,'data/market.json')}\n\n## Important pages\n- {urljoin(SITE_URL,'manufacturers/')}\n- {urljoin(SITE_URL,'products/')}\n- {urljoin(SITE_URL,'methodology/')}\n- {urljoin(SITE_URL,'compare/')}\n'''
write(Path('llms.txt'),llms)
write(Path('robots.txt'),f'User-agent: *\nAllow: /\nSitemap: {urljoin(SITE_URL,"sitemap.xml")}\n')
urls=['']+['manufacturers/','products/','compare/','methodology/','rfq/']+[f'manufacturers/{m["slug"]}/' for m in M]+[f'products/{p["slug"]}/' for p in P]
sitemap='<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+''.join(f'<url><loc>{esc(urljoin(SITE_URL,u))}</loc></url>\n' for u in urls)+'</urlset>\n'
write(Path('sitemap.xml'),sitemap)
write(Path('.nojekyll'),'')
print(f'Built {len(urls)} indexable pages into {SITE}')
