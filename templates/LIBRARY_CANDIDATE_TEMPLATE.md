# Library / Model / Data / Trajectory Candidate

## Identity｜身份

```yaml
id: asset:<stable-id>
name: <artifact name>
artifact_type: code|model|data|trajectory|multi-plane
canonical_url: <URL>
version: <tag/commit/model revision/dataset version>
digest: sha256:<64-hex>|git-commit:<40-hex>
discovered_from_note: <note id/path>
```

## Intended use｜使用目的

```yaml
views:
  hackathon_mvp: true|false
  commercial: true|false
  research: true|false
  production: true|false
implementation_context: <target stack and problem>
```

## Artifact-plane licenses｜四平面授權

| Plane | Status | Identifier/source | Obligations or Bug |
|---|---|---|---|
| Code | pass/fail/unknown/not-applicable | ... | ... |
| Model | pass/fail/unknown/not-applicable | ... | ... |
| Data | pass/fail/unknown/not-applicable | ... | ... |
| Trajectory | pass/fail/unknown/not-applicable | ... | ... |

`unknown` blocks Commercial and Production recommendation.

## Hard gates｜硬 Gate

| Gate | Status | Evidence |
|---|---|---|
| Exact identity/version | pass/fail/unknown | ... |
| License | pass/fail/unknown | ... |
| Security | pass/fail/unknown | ... |
| Maintenance | pass/fail/unknown | ... |
| Compatibility | pass/fail/unknown | ... |
| Evidence reproducibility | pass/fail/unknown | ... |

## Scores｜分數

All scores are 0–100 and require evidence.

```yaml
mvp_speed: 0
commercial_fit: 0
research_value: 0
production_readiness: 0
compatibility: 0
evidence: 0
```

## Compatibility｜相容性

```yaml
languages: []
runtimes: []
frameworks: []
hosts: []
deployment_targets: []
hardware: []
model_formats: []
data_formats: []
network_policy: <none/conditional/required>
secret_policy: <none/conditional/required>
```

## Evidence｜證據

```yaml
grade: E0
sources:
  - kind: official-docs|official-source|release|license|security-advisory|benchmark|sandbox-receipt|production-observation
    url: <URL>
    digest: <optional>
last_verified_at: <ISO-8601>
stale_after: <ISO-8601>
```

## Outcome and recommendation｜結果

```yaml
status: discovery|candidate|recommended-mvp|recommended-commercial|recommended-research|recommended-production|blocked|deprecated|invalidated
recommended_for: []
not_recommended_for: []
required_patches: []
requalification_triggers: []
```

Machine-readable entries must validate against `schemas/rank-entry.schema.json`.
