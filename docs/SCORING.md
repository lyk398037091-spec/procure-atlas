# Matching and ranking principles

ProcureAtlas should separate **eligibility**, **match score**, **evidence confidence**, and **commercial sponsorship**.

## 1. Eligibility
A manufacturer is eligible for a requirement only when the relevant machine category is recorded and published. Missing data is not converted into a positive capability.

## 2. Match score (planned Gate 4)
Suggested 100-point procurement-fit score:

- 35 points — required machine/process fit
- 30 points — required capability coverage
- 10 points — application/industry fit
- 10 points — evidence quality and claim coverage
- 10 points — data freshness
- 5 points — public profile completeness

Hard requirements can be configured as filters rather than weighted preferences.

## 3. Evidence score
Evidence is not a single magical “verified factory” badge. Each claim can carry:

- source type;
- checked date;
- confidence A/B/C/U;
- review state;
- later: exact source excerpt/hash and reviewer ID.

## 4. Sponsorship
Sponsorship contributes **0 points** to organic match score. Sponsored inventory must be visibly marked and rendered separately.

## 5. Missing data
`not recorded` is not equivalent to `does not support`. Comparison UIs must preserve this distinction.
