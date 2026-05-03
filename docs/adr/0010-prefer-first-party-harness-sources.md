# Prefer First-Party Harness Sources

The canonical Harness Capability Catalog will prefer first-party evidence: official documentation, official changelogs, official release pages, and first-party source repositories. Third-party metadata may be used only when first-party version evidence is unavailable or inconsistent, and local CLI observations are recorded separately from web evidence.

## Considered Options

- Prefer first-party harness sources and label all fallbacks.
- Treat all accessible web sources equally.
- Use only local CLI versions and avoid web refresh.

## Consequences

- Every non-obvious harness claim needs an evidence category, source URL, checked-at date, checked version or version basis, and uncertainty note when the evidence is incomplete or inconsistent.
- Third-party metadata must be explicitly labeled as fallback evidence.
- Local installed-tool observations can supplement the catalog but do not replace source-backed harness facts.
