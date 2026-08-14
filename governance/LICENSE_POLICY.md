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

## Acquisition rights bases｜取材權利依據

Five bases can carry `authorization_status: verified`. Until now the pipeline enforced the
strings and nowhere stated the conditions, so the gate was five words and a free-text
reference. The canonical set lives in `tools/rights_vocabulary.py`;
`tests/test_rights_vocabulary.py` binds every adapter, schema and gate to it.

| Basis | Condition | Reference that must read back |
|---|---|---|
| `owned` | the repository owner holds the copyright in the material | the record establishing ownership |
| `licensed` | a licence covering **this use** exists | the licence identifier and where it is published |
| `creator-permission` | the rights holder gave permission for this use | granting party, date, and a non-secret record or ticket |
| `public-domain` | out of copyright, or dedicated to the public domain | the basis for that status |
| `user-provided-media` | the operator supplies the media through a channel they are authorized to use | how the media was obtained |

`user-directed-evaluation` is **not** one of them. It records that the owner pointed at
material they do not own. The schemas pin it to `evaluation-only` and
`rights_vocabulary.may_acquire_media()` refuses it for every status.

### Two licence traps, verified against primary sources

**A Creative Commons licence on a platform video does not authorize retrieving it.**
CC BY 4.0 §2(a)(1) grants rights *the Licensor* holds in the *Licensed Material* — it is a
copyright licence from the creator. The platform's access terms are separate and are not
waived by it. The [YouTube Terms of Service](https://www.youtube.com/t/terms) state:

> You are not allowed to: access, reproduce, download, distribute, transmit, broadcast,
> display, sell, license, alter, modify or otherwise use any part of the Service or any
> Content except: (a) as expressly authorized by the Service; or (b) with prior written
> permission from YouTube and, if applicable, the respective rights holders

Route (b) requires YouTube **and** the rights holder. A CC licence supplies only the second.
Creative Commons is not listed as an exception in that section. So `licensed` is not
satisfied by a CC marker on a third-party platform video; it would need a licence covering
retrieval from that platform.

**A paid viewing subscription is not a rights basis.** YouTube Premium offline downloads are
"stored encrypted on the device and can only be watched in the YouTube app", expire after
29 days, and require being signed in. They do not yield a media file, and extracting one
would engage the separate ToS prohibition on circumventing features that "prevent or
restrict the copying or other use of Content". Premium changes what you may *watch*, not
what you may *acquire*.

### Why the pipeline uses unofficial transports

The authorized programmatic route does not exist for third-party videos.
[`captions.download`](https://developers.google.com/youtube/v3/docs/captions/download)
"requires the user to have permission to edit the video" — owner only. That is why every
adapter in `tools/` reaches a caption track by an unofficial path, and why an
`evaluation-only` record is the honest label for such an acquisition rather than a
formality.

Sources: [License types on YouTube](https://support.google.com/youtube/answer/2797468),
[YouTube ToS](https://www.youtube.com/t/terms),
[videos resource `status.license`](https://developers.google.com/youtube/v3/docs/videos),
[captions.download](https://developers.google.com/youtube/v3/docs/captions/download),
[CC BY 4.0 legal code](https://creativecommons.org/licenses/by/4.0/legalcode.en),
[YouTube offline FAQs](https://support.google.com/youtube/answer/7381437).

## Prohibited shortcuts｜禁止捷徑

- Do not infer license from repository visibility or popularity.
- Do not treat a Creative Commons marker on a platform video as authorization to retrieve it.
- Do not treat a paid viewing subscription as a rights basis.
- Do not treat “open weights” as equivalent to open source.
- Do not copy a source article or transcript into a public Skill artifact.
- Do not use private session trajectories for training without explicit authority.
- Do not collapse code/model/data/trajectory into one `license` string.
