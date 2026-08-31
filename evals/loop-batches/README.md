# LOOP batches｜經 harness 編譯到完成契約的卡片批次

A batch here was compiled by `tools/run_loop_harness.py` driving `RUN_MODE:
LOOP` to the section 9 completion contract. The harness owns the run directory,
so `cards/`, `card-registry.json`, `rounds/` and `run-receipt.json` are its
output rather than files anyone edited afterwards.

```text
<content-id>/
  cards/                  the product: ten payload-first v7.1 cards
  card-registry.json      produced by tools/reconcile_card_registry.py
  card-manifest.json      batch identity, authority and card order
  evidence-manifest.json  URL, fetched-content digest, retrieval date, anchors
  high-signal.json        the coverage controls DONE required cards to anchor
  rounds/                 every request the harness sent and response it got
  run-receipt.json        rounds, digests, and how the run stopped
```

## sqlite-testing

One real, public, substantive article: [How SQLite Is
Tested](https://www.sqlite.org/testing.html), retrieved 2026-08-31, retained
under `sources/sqlite-testing/`. The rights basis is `public-domain` —
sqlite.org states that all SQLite code and documentation is dedicated to the
public domain, and that statement was read back from
[copyright.html](https://www.sqlite.org/copyright.html) on the retrieval date.
It is one of the five bases `governance/LICENSE_POLICY.md` admits for
`authorization_status: verified`, unlike the evaluation-only YouTube record.

Ten cards, one per series across N/C/D/T/X/S/P/E/V/K, reached DONE in three
rounds. The run is replayable from its own `rounds/` directory:

```sh
python3 tools/run_loop_harness.py \
  --run-dir "$(mktemp -d)" \
  --source sources/sqlite-testing/article.txt \
  --source-id article:sqlite.org-testing --content-id sqlite-testing \
  --updated-at 2026-08-31T17:29:21Z \
  --high-signal evals/loop-batches/sqlite-testing/high-signal.json \
  --replay evals/loop-batches/sqlite-testing/rounds
```

## Why the anchors are character offsets into a second retained file

The evidence manifest pins each quote to `char_start..char_end` in
`sources/sqlite-testing/article.txt`, not in the fetched HTML. An offset into
markup would move the moment anyone stripped a tag differently, so the text
plane is retained as an artifact in its own right and produced by exactly one
function, `tools/html_article_adapter.py`. That makes the whole chain
checkable rather than merely recorded:

```sh
python3 tools/html_article_adapter.py \
  --html sources/sqlite-testing/article.raw.html \
  --check sources/sqlite-testing/article.txt
```

The protocol's own locator ladder (section 3) has no character-offset rung, so
the cards do not invent one: each card anchors with `TEXT_MATCH::<quote>`, and
the manifest is the index that makes those quotes mechanically resolvable.
`tests/test_sqlite_testing_batch.py` holds every anchor to its offsets, every
card claim to an anchor, and the batch to a byte-identical replay.

## What DONE means here, and what it does not

`run-receipt.json` records `gate_authority: "none"` and `digest_authority:
"runner"`. QG-01..QG-24 labels inside the round responses are model claims;
the external gate is `tools/publication_guard.py`, which enforces the
mechanically checkable subset (QG-03, 07, 08, 10, 16, 24, I-06) and lists the
rest as prompt-enforced. The eight controls in `high-signal.json` are the part
of `high_signal_unmapped = 0` that can be refuted: DONE was unreachable until
a card anchored each of them. `run-receipt.json`'s `high_signal_digest` binds
the receipt to the exact controls file checked, not just a count.

For this specific batch, `high-signal.json` and the cards were both authored
in the same offline pass by the same hand (the authoring scaffold that
produced this batch, not a repository component), not pre-registered before
compilation and blind to the cards that would follow -- six of the eight
control keys name the same topic as the card that anchors them. That the
harness's unmapped-control check is a real refusal rather than a rubber stamp
is proven at the code level, on a synthetic plant a card genuinely does not
see: `tests/test_planted_signal_falsifier.py`. This batch exercises that
mechanism; it does not re-derive independence from it.
