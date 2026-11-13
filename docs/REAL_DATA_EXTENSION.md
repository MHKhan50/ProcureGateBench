# Real-data extension plan

The v0.1.0 release is synthetic-only. A later real-data extension should be a separately versioned research release.

## Candidate public sources

- UK Find a Tender exposes procurement notices in Open Contracting Data Standard (OCDS) JSON.
- The Open Contracting Partnership Data Registry provides discovery and downloads for OCDS datasets from multiple publishers.
- UK government guidance describes OCDS v1.1 as a common model for publishing planning, tender, award, contract, and implementation data.

## Required safeguards

1. Define a jurisdiction and procurement stage before collecting records.
2. Read each dataset's licence, coverage, and known data-quality limitations.
3. Do not infer misconduct from a red-flag indicator.
4. Remove or protect personal data and commercially sensitive material.
5. Document missingness, publication delays, amendments, and selection effects.
6. Obtain procurement-professional review of labels and contextual explanations.
7. Preserve original records and versioned transformations.
8. Keep real-data labels separate from the synthetic benchmark labels.
9. Do not publish supplier-level allegations or risk rankings without lawful authority and independent review.

## Data endpoints

- UK Find a Tender developer documentation: https://www.find-tender.service.gov.uk/Developer/Documentation
- UK OCDS profile: https://www.gov.uk/government/publications/open-standards-for-government/open-contracting-data-standard-profile
- Open Contracting Partnership Data Registry: https://data.open-contracting.org/en/
