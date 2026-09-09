# ProcureAtlas execution roadmap

## Gate 0 — Product boundary ✅
- Independent product; no sponsor-company promotion or seed data.
- Initial vertical: China packaging machinery for global B2B buyers.
- Organic matching separated from sponsorship.
- Public-source profile explicitly separated from factory audit.

## Gate 1 — Static evidence MVP ✅ v0.1
Acceptance criteria:
- structured manufacturer/product/capability/application data;
- source-linked evidence with checked date;
- machine directory and manufacturer profiles;
- manufacturer finder and browser-side compare;
- RFQ workflow preview;
- sitemap, robots, JSON-LD, llms.txt;
- GitHub Pages CI/CD;
- no production secrets in client code.

## Gate 2 — Evidence productionization
Target before broad public scaling:
- 60+ manufacturers;
- 30+ machine/product categories;
- 100+ standardized capabilities;
- 300+ claim-level evidence records;
- every manufacturer-product/capability relation mapped to evidence IDs;
- stale-source detection and re-check queue;
- duplicate-company/entity resolution;
- evidence reviewer audit log.

## Gate 3 — Operational backend
- Supabase/Postgres becomes system of record.
- Internal admin review console.
- role model: researcher, reviewer, admin;
- import queue for website extraction;
- approved snapshot exporter regenerates the static GitHub Pages catalogue;
- object storage for PDFs, catalogues and certificates where permitted.

## Gate 4 — RFQ and matching
- protected RFQ Edge Function;
- Cloudflare Turnstile or equivalent bot protection;
- rate limiting and abuse controls;
- structured requirements: machine, package, throughput, product material, automation, target market, quantity, certifications;
- deterministic matching score with visible explanation;
- buyer can compare and shortlist suppliers;
- no supplier receives buyer contact without explicit buyer action.

## Gate 5 — AI sourcing assistant
AI comes **after** deterministic data and evidence:
- server-side requirement parser;
- retrieval only from approved catalogue/evidence records;
- citations in every recommendation;
- explicit “not verified” for missing facts;
- model cannot create certifications, machine capabilities or factory facts;
- provider adapter so model vendor is replaceable.

## Gate 6 — Supplier workspace
- claim-company workflow;
- supplier-submitted updates enter review queue, not live database;
- analytics: profile views, RFQ fit, missing evidence, buyer countries;
- premium profile completeness may be sold, but not organic rank.

## Gate 7 — Commercialization
Priority:
1. qualified RFQ/lead subscription;
2. supplier workspace subscription;
3. verified-document / video / on-site audit services;
4. paid research reports;
5. data/API access;
6. clearly labelled sponsorship.

## Gate 8 — Expand verticals
Only after packaging machinery has repeatable data acquisition and paid demand. Expansion candidates are scored independently; familiarity with any sponsor business is not a selection factor.
