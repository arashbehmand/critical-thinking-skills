# Shared conventions for the critical-thinking skill set

Every `ct-*` skill assumes these rules. They exist because each one closes a documented
failure mode of unaided reasoning — the failure mode is named next to each rule.

## 1. Workspace and receipts

- All artifacts live in `.ct/` at the project root. Create it on first use
  (`mkdir -p .ct`). It is gitignored by default; force-add a receipt deliberately when it
  should be kept.
- File naming: `.ct/<act>--<topic-slug>.<ext>` — e.g. `.ct/steelman--rust-rewrite.md`,
  `.ct/ach--latency-spike/matrix.json`. Slugs: lowercase, hyphens, ≤5 words.
- Every act ends with the artifact path cited in the delivered answer. An act that left
  no receipt did not happen.
- *Failure mode closed:* conclusions whose reasoning cannot be inspected or re-run.

## 2. The fresh-mind rule (who supplies the judgments)

When a skill calls for an independent judgment — an advocate, a rater, a panelist — spawn
a subagent (Agent tool, `general-purpose`) whose prompt contains **only**:

- the question or item, verbatim;
- the raw materials needed to answer (documents, evidence text);
- the required output format.

**Forbidden in a fresh-mind prompt:** your draft answer; your lean; scores you already
assigned; the phrase "confirm that"; any hint of which side is "ours"; other panelists'
answers. The test: *if the subagent could infer your preferred answer from the prompt, it
is not a fresh mind.* Templates with the exact wording: `subagent-templates.md`.

- *Failure mode closed:* the lawyer problem — a mind that has committed to an answer
  produces evidence for it, not about it.

**Same-weights caveat (state it when reporting):** subagents share this model's weights.
Fresh contexts remove contamination and self-ownership and cancel noise; they do **not**
cancel blind spots the model class shares. For high stakes, source one judgment from a
different model family or a human.

## 3. Script arithmetic

Combining numbers — scores, counts, ranges, probabilities — is done by the bundled
scripts (`fermi.py`, `ach_score.py`, `aggregate.py`, `brier.py`, `origins.py`, `bag.py`), never in
prose. Each script prints the rule it applied so a reader can check it by hand. Counting
sources is arithmetic too: `origins.py` reports **distinct origins**, and a citation count
that never drops below the document count means the collapse never ran.

- *Failure mode closed:* holistic in-head aggregation, which is where noise and
  motivated rounding live.

Script paths in the recipes are repo-relative (`skills/<skill>/scripts/…`). When a
skill is installed into another project, its scripts travel with the skill directory —
adjust the base path to wherever the skill landed (e.g.
`.claude/skills/<skill>/scripts/…`). Where the critical-thinking-mcp math server is
registered, the same rules are also available as pure MCP tools (`evaluate_qbaf`,
`score_ach`, `aggregate_numeric`, `aggregate_vote`, `score_calibration`,
`combine_fermi`) — script and server compute identical results by pinned parity tests.

## 4. Append-only ledgers

Ledger files (`evidence--*.jsonl`, `commitments--*.jsonl`, `entailment--*.jsonl`,
`predictions.jsonl`) are append-only. A correction is a new entry with `supersedes: <id>`
— the superseded line stays. Editing history destroys the record's meaning.

Retraction is not deletion. In `commitments--*.jsonl`, superseding an entry marks every
entry that *depends on* it `OUT`, transitively: a conclusion resting on a withdrawn
premise looks identical to a correct one, which is why the walk is mechanical and
deliberately over-marks when edges are missing.

- *Failure mode closed:* quiet retroactive harmonizing — the record always agreeing with
  the present.

## 5. Enforcement honesty

These conventions are discipline, not guarantees: nothing here *prevents* a skipped
sweep, a contaminated prompt, or an edited ledger line. When an act's value depends on a
guarantee, the skill's "Limits" section names the machinery that would provide it
(validated structure, server-side elicitation, immutable stores, harness hooks). Do not
present a skill-kept record with the authority of a machine-kept one; label which it is.

**A receipt is evidence that a receipt was written, not that the procedure ran.** An
artifact can be produced without its process, and producing it is cheaper than running
the procedure that should have produced it — a matrix can be filled in one lawyerly
breath. Observability is necessary and not sufficient, so "the act left an artifact" is
where the audit starts, not where it ends.

**Gate over label.** Where a check is self-administered — which is most of them — prefer
the form that *refuses* over the form that *labels*. `NO_REFERENCE_CLASS` stops the
pipeline and names what is missing; "grade D — unsourced" lets the value flow onward
wearing a disclaimer. Labels are useful and they do not stop a motivated actor, because
structure persuades independently of correctness and a disclaimer beside a number is read
as care rather than as a warning. Where a script refuses, the fix is to go get the
quantity — never to relabel the input to get past the gate.
