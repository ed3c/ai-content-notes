# Domain Context Supply Plane｜Zero-Context Architecture Contract

This document is the canonical architecture decision for turning frontier content, conversation context, repeated failures, and review knowledge into reusable domain context **without building a new framework for every source**.

## One-sentence objective

Make the next Agent need fewer decisions, not more concepts.

`ai-content-notes` is a knowledge compiler and supply plane. It discovers reusable concepts and candidate invariants, preserves provenance, and routes only the material subset that needs architectural or behavioral action.

It is not a runtime verifier, FeatureMap authority, Spatial Loop authority, or substitute for repository shape, compiler rules, tests, or production evidence.

## The shortest canonical path

```text
External source / conversation / repeated failure / PR comment
  -> source-constrained cards
  -> candidate invariant or reusable domain concept
  -> Existing-System Check
       already encoded? -> map to authority; stop
       missing?         -> Promotion Gate
  -> lowest deterministic owner
       Shape | Guard | Guide
  -> only if actor-visible behavior or proof obligations materially change
       FeatureMap
  -> only if material requirements/edges remain unresolved
       Spatial Loop
  -> executable/runtime proof
```

A downstream Agent must not invoke the heavier stages merely because the artifacts exist.

## Enforcement hierarchy: Shape -> Guard -> Guide

### Shape

Prefer repository and API structure that makes the locally obvious change globally correct.

Examples:
- feature-owned folders;
- one obvious writer for durable state;
- typed public contracts;
- allowed import direction;
- auto-discovery instead of shared central registries;
- isolated extension files instead of branches in shared roots;
- narrow explicit exception paths.

Question: **Can the invalid state be made difficult or impossible to express?**

If yes, stop here. Do not compensate with more prose.

### Guard

When Shape cannot remove the invalid state, reject it mechanically.

Examples:
- compiler/type restriction;
- static analysis;
- lint;
- dependency rules;
- CI assertions;
- deterministic integration/runtime checks.

Question: **Can a deterministic predicate reject this violation?**

If yes, encode the guard instead of relying on Agent memory or review comments.

### Guide

Use probabilistic guidance only when contextual judgment is genuinely required.

Examples:
- AGENTS.md;
- Skills;
- BugBot guidance;
- style guidance;
- exploration procedure;
- domain reasoning that cannot yet be reduced to a deterministic predicate.

A repeatedly violated mechanically expressible invariant must migrate downward from Guide to Guard or Shape.

## Promotion Gate

Every source/card insight goes through the same decision sequence:

```text
1. Is this only useful knowledge?
   YES -> preserve it in the knowledge plane; stop.

2. Does it expose a recurring failure, missing invariant, or reusable domain contract?
   NO -> stop.

3. Is the target repository already encoding it?
   YES -> record the mapping to the existing authority; do not create a parallel mechanism.

4. What is the lowest deterministic layer that can own it?
   Shape -> Guard -> Guide.

5. Does it materially alter actor-visible behavior, reachable states, outcomes,
   persistence, external boundaries, or proof obligations?
   NO -> do not invoke FeatureMap/Spatial Loop.
   YES -> FeatureMap.

6. Does FeatureMap comparison expose a material BROWNFIELD/GREENFIELD/CONFLICTED
   requirement whose closure is not decidable from current deterministic authority?
   NO -> stop.
   YES -> Spatial Loop + executable proof question.
```

This is the anti-overengineering invariant.

## Domain Context Pack

The minimum pack is intentionally small:

```text
domain identity/version
source + conversation provenance
stable card IDs
vocabulary/aliases
candidate invariants/domain contracts
existing-system mappings
promotion decisions + rationale
evidence ceiling
downstream extraction queries
```

The following are **optional derived projections**, never independent sources of truth:

- Code Graph projection — when dependency/ownership/API structure is material;
- Product Graph projection — when actor-visible behavior is material;
- Verification Graph projection — when proof/evidence obligations are material.

Authority remains with bound source evidence and the target repository's actual shape, types, tests, runtime receipts, and maintained behavioral contracts.

## Multi-pass knowledge convergence

One card pass may be insufficient. Continue card compilation while there are material unmodeled assertions, unresolved concept boundaries, material K cards, contradictions, typed-link targets that expose a new decision-relevant concept, or source novelty not represented in the registry.

But:

```text
CONVERGED knowledge != promoted architecture
CONVERGED knowledge != FeatureMap coverage
CONVERGED knowledge != runtime VERIFIED
```

Knowledge convergence only states that the bound source/config/registry has no material unresolved knowledge frontier according to its external convergence receipt.

## Semantic-space exploration

Semantic/vector search is proposal machinery, not authority.

Preferred matching order:

1. stable IDs / canonical keys;
2. typed-link neighborhoods;
3. domain vocabulary and aliases;
4. embeddings/vector neighbors as proposal-only;
5. evidence-bound adjudication.

Never create a new architecture task because a vector neighborhood merely looks novel.

## FeatureMap escalation

Invoke `skill-concerns/feature-map-engineering` only if the promoted concept is about actor-visible behavior or its proof contract, including:

- actor or intent;
- entry point;
- externally meaningful state;
- transition;
- variant/gate;
- terminal outcome;
- persistence/recovery;
- external boundary;
- observable contract.

The Context Pack is domain-adapter input. It never replaces the FeatureMap and never authorizes `VERIFIED`.

When invoked, semantic gap labels may be:

```text
COVERED
BROWNFIELD
GREENFIELD
UNKNOWN
CONFLICTED
```

These labels describe comparison state, not runtime correctness.

## Spatial Loop escalation

Invoke `skills-shared/spatial-loop-systems-engineering` only for material unresolved behavioral/architectural requirements after existing authorities and FeatureMap comparison have been checked.

An escalated item must carry:

```text
implicit requirement
actor/use case when applicable
affected edge/boundary
expected invariant
failure mode
required observable
executable proof question
source/card provenance
evidence ceiling
```

Spatial Loop is therefore a closure tool, not the default reading path for every article.

## Greenfield risk

The first paved road matters more than a long architecture document.

A golden feature should make the desired architecture locally copyable:

```text
golden feature
├── owned folder
├── typed public contract
├── one writer
├── canonical test
├── production-equivalent verification path
├── allowed dependency shape
└── mechanical negative controls
```

Then the Agent tendency to copy the nearest working pattern becomes beneficial.

## Human Slop and Agent Slop

Repeated identical review comments are system-design evidence.

```text
first occurrence -> diagnose/review
repeated failure taxonomy -> mechanization candidate
mechanizable -> Shape / Guard
contextual only -> Guide
```

Review knowledge should monotonically migrate into the system when it can be encoded without losing necessary context.

## Rewrite risk

Do not begin a rewrite with only a clean target architecture. First extract observable behavior and invariants into executable contracts.

```text
old behavior + invariants
  -> executable migration contract
  -> new implementation
  -> prove contract preservation
```

FeatureMap and Verification projections are useful migration oracles for rewrites, but they are not mandatory ceremony for implementation-only refactors that preserve behavior.

## Lauren Tan / Agent-Friendly Architecture reference fixture

This corpus is the first reference fixture because it demonstrates the architecture principle directly:

- Agents optimize for context-local patterns;
- locally obvious should equal globally correct;
- conventional paths should require fewer decisions than shortcuts;
- forbidden dependencies should fail mechanically;
- every durable value should have one obvious writer;
- new product work should prefer isolated owned files/folders;
- package boundaries should be typed and one-directional;
- exceptions should be narrow, explicit, and reviewed;
- runtime Verification is stronger than source-only plausibility;
- Skills guide probabilistic behavior but should not carry invariants that can be physically enforced;
- repeated failures can become Skills/Evals, but recurring mechanical failures should be pushed lower into Shape/Guard;
- higher autonomy requires stronger executable evidence gates.

## Zero-context reading contract

For any task involving domain context supply or architectural promotion, read:

1. `AGENTS.md`;
2. `INTEGRATION_REQUIREMENTS.md`;
3. this file;
4. GitHub Issue #75 for implementation status/acceptance;
5. the exact source/card artifacts involved;
6. downstream FeatureMap/Spatial Loop contracts only if the Promotion Gate requires escalation.

Do not read every downstream framework by default. The architecture is successful only if the common path stays short.
