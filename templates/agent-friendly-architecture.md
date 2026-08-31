# Agent-Friendly Architecture Contract

## Context Model

Assume a coding Agent usually works with incomplete context.

It may see only the current task, a few nearby files, the nearest working implementation, part of the dependency graph, and only some callers of the code it is changing.

Under these conditions, an Agent will often copy the nearest working pattern, edit the file already in context, choose the implementation with the fewest immediate decisions, preserve code whose unseen callers are uncertain, and follow the requested implementation even when a wider system invariant is not visible.

Treat these behaviors as predictable architectural inputs rather than problems that prompting alone should solve.

> **The repository should make the locally obvious change the globally correct change.**

Unsafe shortcuts should either be difficult to express or fail mechanically with a diagnostic that points to the supported path.

## Core Architecture Rules

### 1. Make the conventional path the easiest path

A correct implementation should require fewer decisions than a shortcut. Prefer repository structures where following nearby correct examples naturally preserves architecture. If the supported path repeatedly requires substantially more knowledge, files, registration, or coordination than an unsafe shortcut, treat that as an architecture defect.

### 2. Make forbidden states fail mechanically

Do not rely on instructions when a rule can be enforced by the system. Prefer, in order: architecture that prevents the invalid state; type or package boundaries; static analysis or lint; CI or executable tests; Agent instructions only when deterministic enforcement is impractical.

A forbidden dependency, invalid transition, unsupported configuration, or unsafe shortcut should fail with a diagnostic that names the supported path.

### 3. Give every durable value one obvious writer

Every persistent value should have one canonical owner, one obvious mutation or transition surface, and read-only projections elsewhere. If an Agent must choose among several competing files, services, registries, commands, or workflows to change the same durable truth, the ownership model is ambiguous.

### 4. Prefer isolated extension surfaces

New work should usually add or extend an isolated unit instead of adding another conditional branch to a shared root. Prefer feature-owned modules, isolated handlers, reserved extension points, auto-discovered files, typed interfaces, and narrowly owned configuration. Avoid central registries, giant switches, shared root configuration, global mutable inventories, and common files that every feature must edit.

### 5. Keep exceptions narrow and explicit

Every exception should state why the normal path cannot be used, the exact boundary being bypassed, the smallest permitted scope, the condition under which the exception ends, and the verification required before acceptance. Repeated exceptions indicate that the architecture or supported path should change.

## Enforcement Hierarchy

Use the strongest practical enforcement layer:

1. **Architecture / repository shape** — make the preferred solution naturally easier and invalid structures difficult or impossible.
2. **Type system / package boundaries** — prevent invalid relationships from being represented.
3. **Static analysis / lint** — reject known invalid patterns mechanically.
4. **CI / executable verification** — reject behavioral or structural violations.
5. **Rules / Skills / Agent instructions** — guide decisions that still require contextual reasoning.
6. **Style guides / review comments** — communicate preferences not yet mechanized.

If the same review comment appears repeatedly, ask whether it should become an architectural constraint, type restriction, dependency rule, lint rule, CI failure, or executable test. Repeated human correction is evidence of a missing system constraint.

## Shortest Path Should Be the Best Path

Agents strongly exploit local precedent. Repository design should combine local imitation and small edit distance with architecture-preserving defaults and hard executable constraints:

```text
nearest working pattern
+ smallest edit distance
+ architecture-preserving defaults
+ hard executable constraints
= high-probability correct implementation path
```

Do not fight local imitation only with more prompting. Make the pattern most likely to be copied the pattern you want repeated.

## Greenfield Systems

Greenfield repositories are dangerous because the first implementations become precedent for later Agents. Establish a small Golden Path before scaling implementation. A representative first feature should demonstrate an owned module, typed public contract, single state writer, supported dependency direction, canonical test, observable verification path, and mechanical negative controls.

Prefer one executable reference implementation over a large architecture document containing rules that have never been exercised.

## Human Slop and Agent Slop

Bad code is not unique to AI. The structural problem is allowing repeated mistakes and unverifiable decisions to accumulate without converting what was learned into system constraints.

Use this loop:

```text
failure
-> diagnose
-> identify violated invariant
-> reproduce
-> determine whether it recurs
-> move the lesson to the strongest practical enforcement layer
```

For repeated failures, mechanically expressible lessons belong in architecture, types, lint, CI, or tests. Only genuinely contextual lessons should remain Rules, Skills, or Agent guidance. Do not create a global rule from a single anecdote, and do not leave a repeatedly violated deterministic invariant only in prose.

## Rewrite Safety

Before replacing an existing subsystem, extract the contract that must survive: observable behavior, state transitions, ownership, dependency boundaries, persistence semantics, failure/recovery behavior, and external compatibility.

```text
existing behavior + invariants
-> executable migration contract
-> new implementation
-> prove contract preservation
```

A rewrite is complete when required behavior and invariants survive, not when the new code merely compiles or looks cleaner.

## Adding New Architecture

Before adding a registry, abstraction layer, router, manager, framework, policy system, or extra architecture document, ask:

1. What concrete failure does it prevent?
2. Can the nearest existing boundary prevent that failure instead?
3. Does the new layer reduce decisions on the normal path?
4. Does it introduce another source of truth?
5. Will future Agents need to understand it before making ordinary changes?
6. Can the same result be achieved by deleting or simplifying something?

A new layer that makes every future Agent understand more concepts before a normal change is presumptively suspect. Prefer strengthening an existing boundary over creating another coordination layer.

## Implementation Procedure

When modifying a repository:

1. Identify the required actor-visible or system-level outcome.
2. Find the nearest existing correct implementation pattern.
3. Identify the owner of every durable value being changed.
4. Identify supported dependency and extension boundaries.
5. Check whether the requested implementation conflicts with an invariant.
6. Prefer an isolated extension over another branch in a shared root.
7. Use the smallest change that follows the supported architecture.
8. Run the strongest available executable verification.
9. Exercise relevant negative or failure paths.
10. Remove obsolete local code when its callers and replacement boundary are known.
11. Do not introduce an exception silently.
12. If the same failure has appeared repeatedly, move the invariant toward stronger mechanical enforcement.

## Best Path Decision Rule

When several implementations are possible, prefer the one that maximizes:

```text
local obviousness
+ existing architectural precedent
+ isolation
+ single ownership
+ mechanical enforcement
+ verifiability
```

and minimizes:

```text
new concepts
+ shared-root edits
+ manual registration
+ duplicate state
+ implicit exceptions
+ prose-only invariants
+ human-only verification
```

Do not choose the shortest path merely because it compiles. Choose the shortest path that preserves system invariants and can be verified through the strongest available boundary.

If that path is consistently harder than an unsafe shortcut, treat the repository architecture—not the Agent—as the thing that needs improvement.
