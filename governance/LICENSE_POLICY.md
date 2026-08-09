# License Policy｜授權 Gate

## Core rule｜核心規則

Code, model weights, data, and trajectories are separate artifacts with separate licenses and provenance. A permissive code license does not authorize model weights, training data, outputs, or captured trajectories.

程式碼、模型權重、資料與 trajectory 是四種不同資產。Code 採 permissive license，不代表模型、資料、輸出或軌跡可自由使用。

## Artifact planes｜資產平面

| Plane | Examples | Required checks |
|---|---|---|
| `code` | repository, SDK, server, adapter | exact version, LICENSE file, NOTICE, dependency obligations, patent clauses |
| `model` | weights, tokenizer, config, adapter | model license, use restrictions, distribution, derivatives, provider terms |
| `data` | dataset, transcript, benchmark, labels | collection consent, redistribution, PII, commercial use, attribution |
| `trajectory` | prompts, tool calls, session traces, eval traces | user consent, secrets, private code, retention, derivative training rights |

## Status values｜狀態

```text
pass             exact-version evidence supports the declared use
fail             an explicit restriction blocks the declared use
unknown          evidence is missing or ambiguous
not-applicable   the claim does not introduce or recommend this artifact plane
```

`unknown` is fail-closed for ranking, packaging, training, redistribution, and production adoption.

## Evidence contract｜證據契約

A license decision must record:

```text
artifact identity and exact version or digest
plane
license identifier or source URL
retrieval date
commercial-use status
distribution and derivative obligations
attribution/NOTICE requirements
model/data/trajectory restrictions
reviewer and decision date
```

## Ranking gate｜排名 Gate

A library, model, dataset, or trajectory asset cannot receive a Production recommendation until every applicable plane is `pass`.

```text
commercial score available only when applicable planes pass
production score available only when applicable planes pass
unknown plane -> candidate remains discovery-only
license change -> invalidate ranking and queue review
```

## Note and claim boundary｜筆記與 Claim 邊界

A note may discuss a tool or model before its license is known. The corresponding claim map must mark the applicable plane `unknown`; it must not convert discovery into approval.

## Prohibited shortcuts｜禁止捷徑

- Do not infer license from repository visibility or popularity.
- Do not treat “open weights” as equivalent to open source.
- Do not copy a source article or transcript into a public Skill artifact.
- Do not use private session trajectories for training without explicit authority.
- Do not collapse code/model/data/trajectory into one `license` string.
