# noodles Agent-Friendly Architecture — evidence-bound extraction fixture

Status: **knowledge extraction fixture / not runtime verification**

Target repository: `ed3c/noodles` (`main`)
Reference contract: Lauren Tan / Dune Agent-Friendly Architecture text supplied in conversation.

This fixture exists to test whether `ai-content-notes` can supply reusable architecture context without over-design, semantic drift, hallucination, guarantee laundering, or loss of low-level invariants that would cause a downstream Agent to infer the wrong Best Path.

## 1. Extraction rule

Preserve this distinction for every statement:

- **SOURCE INVARIANT** — meaning carried by the supplied Dune text;
- **NOODLES EVIDENCE** — directly readable repository artifact or executable gate;
- **ADAPTATION** — noodles-specific implementation of the same underlying design pressure;
- **DIVERGENCE** — noodles intentionally solves a different domain problem;
- **GAP / UNKNOWN** — no sufficient mechanical evidence was found; do not fill from analogy.

No similarity score, prose repetition, test name, or model interpretation upgrades a GAP into an enforced invariant.

## 2. Semantic kernel that must not be compressed away

The Dune reference has one design objective and five coupled rules.

**Design objective:** contributors/Agents arrive with narrow context, so repository design must make the locally obvious change the globally correct change. Unsafe shortcuts should fail with diagnostics naming the supported path.

**Behavioral assumptions:** an Agent tends to copy the nearest working pattern, edit the currently open file, choose the shortest compiling path, preserve code whose callers are invisible, and follow requested implementation even when it conflicts with a wider invariant.

**Five rules:**

1. conventional path requires fewer decisions than a shortcut;
2. forbidden dependencies fail mechanically;
3. every durable value has one obvious writer;
4. new product work adds isolated files rather than branches in shared roots;
5. exceptions are narrow, explicit, and reviewed as architecture changes.

The Dune-specific nouns (`Feature`, `Entrypoints`, `Transcript`, `Client`, `Host`, `sand/dune`, `sand/src`) are examples that carry these rules, not the universal architecture itself. A valid domain adaptation may use different nouns only if it preserves the underlying invariants.

## 3. noodles extraction

### 3.1 Contributor context model

`noodles` explicitly assumes narrow-context Agent execution. Its repository route is bounded to at most three nodes:

```text
AGENTS.md
  -> contracts/system-v1.md when needed
  -> issue-named executable contract/test
  -> stop
```

The route is mechanically checked, including a planted fourth-hop negative control. This is a noodles-specific Shape/Guard adaptation of Dune's narrow-context premise: reduce document traversal and route the Agent toward the nearest executable authority instead of requiring a global mental model.

Classification: **ADAPTATION, mechanically supported for route shape; Agent comprehension remains probabilistic.**

### 3.2 Best Path / conventional path

The noodles Golden Path is:

```text
exact GitHub Issue
  -> deterministic admission
  -> Noodle-owned isolated worktree
  -> pinned engineering route
  -> smallest independently useful atom
  -> nearest executable contract/test/oracle
  -> exact-head local evidence
  -> trusted GitHub verification
  -> exact-head provider landing + closure readback
  -> reconciliation
```

This is the closest noodles analogue to Dune rule 1. It deliberately makes the supported path explicit and tries to reduce alternative decision surfaces.

Important evidence ceiling: the route selection itself is P-class; only named local gates and provider readback have L/R authority. Therefore do **not** summarize this as “the Golden Path is mechanically guaranteed end-to-end.”

Classification: **ADAPTATION with mixed P/L/R authority.**

### 3.3 Forbidden states fail mechanically

Observed mechanical controls include:

- forbidden runtime dependency manifests are rejected by repository verification;
- forbidden tracked residue/provider/runtime paths are rejected;
- scheduler/task skill contracts and required paths are checked;
- exact Issue marker shape is parsed fail-closed;
- PR auto-close keywords are forbidden and exact `Refs owner/repo#N` shape is required;
- trusted candidate/provider boundaries reject wrong subject/head/tree or unsupported transitions;
- document route >3 nodes is rejected;
- component-surface verification is designed to reject changed paths outside a declared component using trusted default-branch policy.

This strongly corresponds to Dune rule 2, but the domain is delivery/evidence authority rather than package-import direction.

Classification: **STRONG ADAPTATION.**

Do not infer that every architectural prohibition in noodles is mechanically enforced. `contracts/system-v1.md` explicitly admits that repository-wide semantic duplicate-owner detection is not yet mechanically proven.

### 3.4 Durable values have obvious owners/writers

`contracts/system-v1.md` contains an explicit durable owner/writer map separating:

- stable intent -> system contract;
- Issue lifecycle -> GitHub Issue/provider transition surfaces;
- scheduling/worktrees -> Noodle;
- engineering playbook selection -> pstack;
- acceptance/oracles -> nearest executable verification boundary;
- candidate source -> Git in isolated worktree;
- merge/default branch/closure -> GitHub;
- reconciliation -> noodles + Noodle.

This is a direct adaptation of Dune rule 3, with an important refinement: noodles defines “one writer” as one admitted transition surface, not one process owning all authority.

Mechanical support is partial. Some single-source rules are strongly enforced (for example task profile literals are checked against one policy source); system-wide semantic duplicate writer/owner detection is explicitly incomplete.

Classification: **ADAPTATION, PARTIALLY MECHANIZED.**

### 3.5 Isolation instead of shared-root branching

The nearest noodles invariant is not Dune's feature-owned file auto-discovery. It is mutation containment:

- repository-mutating work occurs only in a Noodle-owned isolated worktree;
- the shared control checkout is read/reconcile only;
- one Issue is one repository-mutating atom;
- target changes are bounded by a declared component surface;
- the system tells implementers to choose the smallest independently useful atom.

This preserves the deeper pressure behind Dune rule 4 — local changes should be isolated rather than accumulating branches in a shared mutation surface — but it is **not semantically identical** to Dune's “new product work adds isolated files rather than branches in shared roots.”

The distinction matters: Dune shapes source-code extension topology; noodles primarily shapes execution/mutation topology.

Classification: **DOMAIN DIVERGENCE WITH SHARED INVARIANT PRESSURE.**

Do not rewrite this as “noodles implements Dune owned feature folders/auto-discovery.” Evidence for that stronger claim was not found.

### 3.6 Narrow explicit exceptions

`noodles` says bootstrap/recovery exceptions must be exact, narrow, bounded atoms with receipts and cannot become a second normal path by precedent. The system contract also requires proof before adding a registry/router/framework/manager/document layer and treats trusted-transition changes as staged transitions rather than bypasses.

This closely preserves Dune rule 5.

Potential weakness: `policy/components.json` has a `contract` component whose admitted path glob is `*`, specifically for legitimate cross-component atoms. This is an explicit escape surface. Its safety depends on surrounding Issue/component admission and trusted verification rather than the glob itself being narrow. Downstream consumers must preserve this caveat.

Classification: **ADAPTATION with an explicit broad escape surface that requires external narrowing.**

## 4. Enforcement hierarchy comparison

| Dune semantic layer | noodles equivalent | Evidence class | Difference that must survive extraction |
|---|---|---|---|
| Repository/architecture shape | isolated Noodle worktree, one-Issue atom, bounded document route, owner/writer separation, component surfaces | mixed N/L/R | noodles shapes delivery/evidence topology more than product module topology |
| Static analysis / CI | repository verifier, trusted verify workflow, provider protection/readback | L/R where executed | closest strong equivalence |
| Lint/compiler diagnostics | Python/shell syntax, deterministic structural/parser/contract checks, dependency-manifest rejection | L when executed | Python project has less type/compiler-bound architecture than Dune example |
| Rules/Skills/style guidance | AGENTS, pstack route, Skills, comments | P/N | noodles explicitly prohibits authority laundering from P/N to L/R |

A critical anti-drift rule follows: **do not translate every noodles policy into “architecture enforcement.”** Some metrics/fitness surfaces are report-only N-class warnings. For example tracked-file count, root-surface count, Markdown share, line entropy, file size, and test/code ratio are reported as architecture warnings rather than admission failures. Only enabled-provider count is currently a failing fitness limit in that mechanism.

## 5. Where noodles is stronger than the supplied Dune excerpt

These are domain extensions, not claims that Dune lacks them globally:

1. **Authority classes (`P/L/R/N`).** noodles explicitly prevents prose, model consensus, or repeated review from laundering into deterministic/provider authority.
2. **Exact-subject evidence binding.** Issue, repo, head/tree, oracle and provider receipt must refer to the same candidate.
3. **No self-authorization.** candidate-modified bytes cannot be the sole authority that admits the same candidate.
4. **Provider landing as part of completion.** local correctness and repository/provider reality are separate states.
5. **Learning migration.** repeated failures should become executable tests/lint/contracts/oracles, not more global prose.
6. **Subtraction gate.** adding a layer requires a physical failure the nearest existing seam cannot close.

These are compatible with the Dune semantic kernel because they push recurring judgment toward Shape/Guard rather than adding Guide-only complexity.

## 6. Where noodles is weaker, different, or currently incomplete

### A. Product extension topology is not equivalent

Dune gives concrete source-shape primitives: Feature-owned folder, reserved-file auto-discovery, Client single writer, typed Host contract, one-way package boundary. noodles' strongest source-shape evidence is different: isolated mutation worktrees, component path bounds, nearest executable contracts and provider authority.

**Do not infer Dune-style feature-owned source topology from noodles.**

### B. Some architecture budgets are advisory

`policy/fitness.json` declares tracked-file/root-surface/Markdown-share/entropy/test-ratio thresholds, but their implementation classifies them as report-only N warnings. They help detect entropy; they do not mechanically prevent it.

**Do not summarize them as hard architecture limits.**

### C. One-writer enforcement is not universal

The system contract explicitly states that repository-wide semantic duplicate-owner detection is not mechanically proven.

**Do not convert the owner/writer table into a claim of complete enforcement.**

### D. Broad cross-component escape exists

The `contract` component maps to `*`. This is intentional for cross-component atoms but is broader than the normal component surfaces.

**Do not call component isolation absolute.** The exception must remain explicit and be evaluated through the surrounding admission/proof path.

### E. Documentation tests can become brittle if mistaken for semantic proof

`tests/test_agent_friendly_architecture.py` asserts required phrases and unique requirement IDs. This is useful anti-drift protection for the contract surface, but phrase presence proves documentation shape, not the truth of each invariant.

**Do not promote text-presence tests into architecture correctness.**

## 7. Original Dune rules vs noodles — compact matrix

| Dune rule | noodles status | Exact interpretation |
|---|---|---|
| conventional path requires fewer decisions | **Strong adaptation** | exact Issue -> isolated worktree -> nearest executable boundary -> exact-head provider path; routing remains P-class |
| forbidden dependencies fail mechanically | **Strong adaptation, domain-shifted** | many invalid repository/delivery/provider states fail mechanically; not every conceptual invariant is covered |
| every durable value has one obvious writer | **Partial adaptation** | explicit owner/transition map plus some single-source gates; universal semantic duplicate-writer proof is absent |
| new work adds isolated files rather than shared-root branches | **Different implementation pressure** | noodles isolates mutation/worktree/component atoms; no evidence for Dune-style feature-owned-file/auto-discovery topology |
| exceptions narrow, explicit, reviewed | **Strong adaptation with caveat** | bounded exception atoms and staged transitions; `contract:*` is a deliberately broad component escape that relies on surrounding gates |

## 8. Best Path inference for a zero-context Agent

A downstream Agent consuming this fixture MUST infer only this Best Path:

```text
1. Start from the exact Issue and its declared component/feature markers.
2. Use Noodle's isolated worktree; never mutate the shared control checkout.
3. Read AGENTS -> system contract only if required -> nearest executable contract/test; stop traversal.
4. Implement the smallest independently useful atom.
5. Run baseline acceptance plus any applicable specialized physical oracle.
6. Bind evidence to the exact candidate head/tree.
7. Use trusted GitHub verification/provider landing/readback for repository completion.
8. Reconcile after provider reality is read back.
```

It MUST NOT infer any of these unsupported shortcuts:

- “AGENTS.md says it, therefore it is enforced.”
- “A passing phrase-presence test proves the architecture invariant.”
- “All fitness thresholds are hard gates.”
- “`contract` component means unrestricted cross-repo mutation is normal.”
- “noodles has Dune-style Feature-owned folders and auto-discovery.”
- “local tests alone authorize merge/completion.”
- “one-writer is fully mechanically proven across arbitrary repository prose.”

## 9. Context-supply anti-degradation contract

When this fixture is converted into cards or a downstream Context Pack, preserve these fields per material concept:

```text
semantic_kernel          # invariant before domain-specific nouns
domain_realization       # exact noodles mechanism
mechanical_evidence      # exact file/test/gate or UNKNOWN
authority_ceiling        # P | L | R | N | mixed
divergence               # how noodles differs from Dune
negative_claims          # tempting but unsupported stronger interpretations
best_path_consequence    # what the next Agent should actually do
```

Compression is invalid if it removes any `negative_claims`, `authority_ceiling`, or material `divergence` field and thereby makes a stronger Best Path inference possible than the evidence permits.

## 10. Promotion decision

This fixture is useful knowledge and a regression oracle for the Domain Context Supply Plane. It does **not** justify creating another architecture framework inside noodles.

Promotion decisions:

- preserve the extracted kernel and difference matrix as knowledge context;
- use existing noodles Shape/Guard authorities where they already encode the invariant;
- treat product-topology gaps as `UNKNOWN/DIFFERENT`, not a request to copy Dune nouns;
- only create a new noodles guard if a reproducible failure demonstrates that an existing seam cannot prevent a wrong Best Path;
- FeatureMap/Spatial Loop escalation is unnecessary for this comparison unless a concrete actor-visible noodles capability or unresolved verification edge is later identified.

This is the intended anti-overengineering outcome.