# Data pipeline

## Discovery
Candidate companies can originate from official sites, industry associations, exhibition lists, public filings, directories and supplier submissions.

## Extraction
Automated extraction may suggest:
- legal/display name;
- addresses and regions;
- machine categories;
- capabilities;
- applications;
- certifications;
- public contact channels;
- source URLs.

Automated extraction never directly publishes a claim.

## Normalization
Normalize names into stable IDs and shared taxonomies. Resolve aliases and duplicate legal entities before publication.

## Evidence review
Each publishable claim should eventually map to one or more evidence records with source, source type, checked date and confidence.

## Publication
Only approved records enter the public snapshot. GitHub Pages is generated from that approved snapshot.

## Re-check
Sources age. Records should move to a stale-review queue based on evidence type and age instead of remaining permanently “verified.”
