# Thinking Tools for Language Models

**A critical-thinking skill set, and the line where skills end and machinery begins**

*White paper v1.3 · critical-thinking-mcp project · August 2026*

---

## Abstract

Chain-of-thought prompting improved language-model reasoning by borrowing one practice
from human thinking: writing intermediate steps down. This paper argues that
chain-of-thought was the first item taken from a much longer, better-tested library —
the critical-thinking practices that human sciences have validated over seventy years —
and that the rest of the library can now be systematically translated for LLM agents.
We catalog nineteen critical-thinking *acts*, derive each from established findings in
cognitive science, and translate them into agent capabilities. The central design
question is the delivery vehicle. We show that the acts split cleanly along one line —
**does the act still work when the model is being a lawyer?** Acts that survive
motivated reasoning ship as *skills* (procedures, templates, and small deterministic
scripts loaded into context). Acts whose value depends on a *guarantee* — validated
structure, judgment sourcing from uncontaminated contexts, tamper-evident records,
enforced gates — need *machinery*: code that runs outside the model's control. We ship
the skill tier as nineteen working skills accompanying this paper, classify every act
across three tiers (skill / harness / service), and present the argLLM server — an
implementation of Argumentative LLMs (Freedman et al. 2024) — as the worked example of
the machinery tier. Transparency is a by-product of this architecture rather than an
added feature — every act leaves an artifact, and the artifacts are the audit trail —
but only up to a limit we now state plainly: **an artifact can be produced without its
process, so a receipt is evidence that a receipt was written, not that the procedure
ran.** Observability is necessary and not sufficient, which is why this revision adds a
fourth guarantee, a measurement designed to quantify the gap, and a preference for checks
that *refuse* over checks that *label*.

---

## 1. From chain-of-thought to thinking environments

The path between a question and an answer is rarely a single hop. Chain-of-thought
(Wei et al. 2022) worked by making the intermediate steps explicit — mistakes got a
place to be visible, and later steps could build on earlier ones held in context rather
than in superposition. It was a *thinking tool*: not more capability, but a better
environment for the capability that existed.

But chain-of-thought implements only one move — externalization — and implements it
weakly: free-text steps, written by the same mind that will judge them, checked by
nobody. Human critical-thinking research suggests two further moves, and a stronger
form of the first:

1. **Externalize** — thinking goes into a *structure* (a tree, a table, a ledger), not
   into prose. Structure is checkable; prose is only readable.
2. **Mechanize** — the mechanical parts (counting, arithmetic, aggregation) are done by
   deterministic rules, not by judgment. Same input, same output.
3. **Contest** — an opponent is built into the process, and every product remains open
   to attack. Disagreement is the error-correction mechanism.

The claim of this paper: each established finding about human thinking translates into
a concrete agent capability built from these three moves — and the translation forces a
design decision (skill or machinery?) that current agent practice mostly gets wrong by
defaulting everything to prompts.

## 2. What we know about thinking

### 2.1 Eight findings from the human sciences

**F1 — Fast thinking dominates; slow checking is lazy and often post-hoc.** Deliberate
checking is expensive and rarely engaged, and when engaged it frequently rationalizes
the fast answer rather than testing it (Kahneman 2011). *Implication: never ask a mind
to check itself in the same breath; separate the steps and let something else decide
when checking runs.*

**F2 — Errors are systematic, and representation changes ability.** Biases push in
predictable directions (Tversky & Kahneman 1974), but the same statistical problem
posed in natural frequencies instead of percentages roughly triples correct Bayesian
answers, including among physicians (Gigerenzer & Hoffrage 1995). *Implication: half of
"can't reason about X" is "X is badly formatted"; translate first.*

**F3 — Working memory holds about four chunks; serious thinking is external.**
(Cowan 2001; Miller 1956.) Notation, diagrams, and writing are not records of thought
but components of it (Clark & Chalmers 1998; Hutchins 1995). *Implication: the tool
holds the structure; the mind contributes one judgment at a time.*

**F4 — Reasoning evolved for argument, and disagreement corrects.** Humans are biased
*producers* of arguments (myside bias) but competent *evaluators* of others' arguments
(Mercier & Sperber 2011, 2017). On a classic logic task, roughly one in ten individuals
succeeds, while small disagreeing groups succeed around eight in ten (Moshman & Geil
1998). *Implication: split production from evaluation; give the strong faculty the
final word.*

**F5 — Intelligence and rationality dissociate, and skill amplifies lawyering.**
Cognitive ability correlates weakly with resistance to most biases (Stanovich 2009).
On politically charged questions, *more* numerate subjects polarize *more* — skill is
recruited by the side, not by the truth (Kahan et al. 2017). *Implication: capability
without stance control yields better rationalizations, a warning with obvious force for
increasingly capable models.*

**F6 — Confidence tracks accuracy only where score is kept.** Long-range expert
political forecasts barely beat chance (Tetlock 2005); weather forecasters are nearly
perfectly calibrated because feedback is fast and unambiguous. Granular probabilities,
small updates, and score-keeping produce superforecasters (Tetlock & Gardner 2015);
intuition is trustworthy only in "kind" environments with valid cues and quick feedback
(Kahneman & Klein 2009). *Implication: build the feedback loop; where reality is slow,
measure consistency instead.*

**F7 — Simple mechanical rules beat holistic expert judgment surprisingly often, and
judgment is noisy.** Meehl's clinical-vs-statistical result has held for seventy years:
in a meta-analysis of 136 comparisons, mechanical combination matched or beat clinical
judgment in the large majority (Meehl 1954; Grove et al. 2000). Beyond bias, judgment
wobbles across occasions — noise (Kahneman, Sibony & Sunstein 2021). *Implication: the
mind rates the pieces; arithmetic delivers the verdict.*

**F8 — Procedures work; awareness does not.** Telling people about biases barely
helps. What replicates: consider-the-opposite (Lord, Lepper & Preston 1984), premortems
(Klein 2007), checklists (Gawande 2009), structured analytic techniques (Heuer 1999),
independent-then-aggregate group methods, and argument-mapping practice, which yields
critical-thinking gains around 0.7–0.8 standard deviations per semester (van Gelder
2005; Twardy 2004). Meanwhile "teach critical thinking as a general skill" transfers
poorly (Willingham 2007), and several pop-psychology favorites (ego depletion, most
social priming, power posing) failed replication while the boring procedural results
survived. *Implication: encode practices as required stages with artifacts, not as
advice.*

### 2.2 The same effects in silicon

The translation is not an analogy. LLMs learned to reason from human text and exhibit
strikingly parallel failure modes, and the parallel interventions already have
independent LLM-side evidence:

- Externalizing steps helps (chain-of-thought: Wei et al. 2022) — F3.
- Sampling several attempts and aggregating mechanically helps (self-consistency:
  Wang et al. 2023) — F7's noise reduction.
- Multi-agent debate improves factuality and reasoning (Du et al. 2023; the safety
  literature proposed debate as an alignment mechanism earlier: Irving et al. 2018) —
  F4.
- Models largely cannot self-correct reasoning without external information (Huang et
  al. 2024) — F1's post-hoc checking.
- LLM evaluators recognize and favor their own generations (Panickssery et al. 2024) —
  F4's ownership problem, verbatim.
- Long-context attention is effectively shallow ("lost in the middle": Liu et al.
  2024) — F3's small working memory, re-created at a larger scale.
- Performance swings widely with prompt format changes that carry no information
  (Sclar et al. 2024) — F2's format sensitivity.

The human library is therefore not inspiration but a tested starting catalog: the
failure modes carried over, so the fixes are worth porting — with their evidence.

## 3. The catalog of critical-thinking acts

Each act below follows the same scheme as the chain-of-thought origin story: *what is
usually true about thinking; what externalizing/mechanizing/contesting it buys.*

1. **Question tree.** A big question is several small ones wearing a coat; answered in
   one jump, some get skipped invisibly. Split, answer leaves independently, synthesize
   only from children. (Numeric variant: Fermi decomposition with interval arithmetic.)
2. **Definition pin.** Many disputes are two meanings of one word. Pin operational
   definitions before arguing; keep them fixed; name equivocation when it appears.
3. **Reformat.** The difficulty is often in the wording. Translate to the tractable
   representation (frequencies, tables, affirmatives, concrete cases) before thinking.
4. **Assumption audit.** Claims stand on unstated premises, and break there. List what
   must be true, rate load-bearing × confidence, attack the weakest load-bearing one.
5. **Steelman.** Producers are lawyers; the other side's case gets decoration. Have a
   fresh mind with no ownership build the opposing case at full strength; judge blind.
6. **Competing hypotheses (ACH).** We test one story instead of racing several. Matrix
   of hypotheses × evidence, cells rated independently; the survivor is the story with
   the *least evidence against it* (Heuer 1999).
7. **Evidence ledger.** Confident sentences outlive their sources. Tie every factual
   claim to a source with a quality grade; make naked claims visible.
8. **Consistency log.** Long work contradicts itself quietly. Log commitments at
   decision time; sweep pairs mechanically; have a fresh mind judge contradictions.
9. **Judgment panel.** Same mind, different day, different answer — noise. Several
   independent draws, mechanical aggregation, disagreement surfaced rather than
   averaged away.
10. **Calibration scorecard.** Confidence grows without accuracy unless score is kept.
    Log probabilities with deadlines; resolve on observation; read the bins.
11. **Premortem.** "Any risks?" produces polite nothing. Declare the failure already
    happened; explain it; convert causes into plan changes and observable tripwires.
12. **Sensitivity probe.** You rarely know which piece carries the conclusion. Flip
    inputs one at a time; recompute; the flip set is what deserves scrutiny. (In this
    release, folded into the ACH script's flip report and the argument-map probe loop
    rather than shipped standalone.)
13. **Verdict gate.** Checks get skipped exactly when confident and hurried. A
    checklist that must produce written output before the conclusion ships.
14. **Argument map.** Answers rest on reasons pulling both ways, with reasons about
    those reasons. A tree of pro/con arguments with elicited base scores; the verdict
    computed from the structure by gradual semantics; every part editable, with
    automatic re-evaluation (Freedman et al. 2024).
15. **Entailment check.** A source can be genuinely relevant to a claim it does not
    support, and repetition reads as corroboration. Ask a fresh context the narrow
    question — does this text *entail* this claim, *contradict* it, or is it
    *insufficient*? — record the supporting span, and collapse sources by origin before
    counting, so syndication and quoting chains stop inflating the count. Report distinct
    origins, never document counts.

16. **Ensemble of perspectives.** One pass sees everything and commits once; splitting
    the evidence down to one item per mind buys independence by destroying competence,
    and independent nonsense does not average into sense. Bag it instead, as a random
    forest does: each fresh mind gets the whole question and a random *subset* of the
    evidence, votes aggregate mechanically, and permutation importance over the subsets
    reports which evidence the verdict actually rests on.

17. **Reframe and anomaly hunt.** A question silently fixes the target, boundary, unit,
    timeframe, and success criterion before reasoning begins. Separate observations from
    that frame, start from the anomaly it explains worst, generate materially different
    boundaries, and record what would make each frame wrong. This is problem finding,
    not another solution pass.
18. **Counterexample search.** Universal claims are asymmetric: one admissible witness
    kills them, while friendly examples do not prove them. Freeze the domain and
    premises, search with execution, enumeration, tests, retrieval, or a solver before
    model judgment, shrink any witness, and distinguish proof from bounded search that
    merely found none.
19. **Formalize and compute.** Many questions are ordinary formal objects in domain
    clothes: an allocation, a graph, a schedule, a threshold, a queue, a feedback loop, a
    filter over noisy readings. Name the object, encode it in a file, let a solver,
    enumeration or simulation answer it, then attack the encoding with a known case, units,
    a degenerate case and a sensitivity sweep. Where the shape has no name, describe the
    behavior and borrow the field that studies it, treating the borrowed frame as a
    hypothesis that must predict something checkable. The leverage is independent
    computation: no new evidence about the world, but fallible in-head work replaced on the
    property actually checked — and the solver certifies the encoding, never the modelling.

## 4. Two delivery vehicles — and a test for choosing

### 4.1 Skills

A *skill* is procedure knowledge loaded into the model's context on demand:
instructions, prompt templates, artifact conventions, and (in modern agent harnesses)
bundled deterministic scripts the agent runs. Modern agentic loops quietly supply the
primitives the acts need: the file system is the external memory (F3), subagents are
fresh minds (F1, F4), bundled scripts are the arithmetic (F7), web/search tools feed
evidence (F6). A skill orchestrates these primitives into a named practice.

Skills are the right vehicle for *method knowledge*: when to decompose, how to phrase
an advocate's brief, what a tripwire is. They are cheap, portable, composable with the
agent's whole toolbox, and adjustable by reading a markdown file.

### 4.2 What skills cannot give

Three structural gaps, each an LLM re-instantiation of F8's "awareness doesn't work":

1. **Skills are read, not run.** Compliance is probabilistic and decays with context
   distance and confidence — the conditions under which checks matter most are the
   conditions under which they are skipped. A tool schema re-asserts its structure at
   every call; an instruction loaded 40k tokens ago has faded.
2. **Artifacts can be produced without their process.** A model can fill an ACH matrix
   in one lawyerly breath: the table exists; the independent rating never happened.
   Artifact and process have come apart — the checklist has been pencil-whipped.
   Machinery binds them: in argLLM there is no way to get a base score into the tree
   except through an actual fresh-context elicitation. This one generalises past the
   skill tier and is stated as a guarantee in §5: **producing the artifact is cheaper
   than running the procedure that should have produced it**, so the presence of a
   receipt is evidence that a receipt was written. Since "every act leaves an artifact"
   is otherwise the whole argument for the skill tier, this is the load-bearing caveat on
   it, and §8 names the measurement that would size it.
3. **The committed mind supplies the numbers.** In a skill-only argument map, the mind
   that holds the lean writes every score into the file — a lawyer with a spreadsheet.
   In the machinery version the server elicits each judgment through a controlled
   channel from a context that has never seen the lean. *Who supplies the judgments* is
   the deepest difference between the tiers.

Additionally, skill-kept state is mutable (a ledger the model can rewrite is a diary,
not a record), and skill-kept randomness is reportable selectively (a panel whose
"weird" draws can be silently dropped is not a panel).

### 4.3 The lawyer test and the three tiers

**Does the act still work when the model is being a lawyer?** If yes — the act's value
survives motivated reasoning because its failure is visible in the artifact — it is a
skill. If the act only works because something outside the model refuses to let the
lawyering through, it needs machinery.

There is a reason the line falls there, but the information-theoretic claim needs a
precise scope. For any chain *truth → one model output → post-processing*, where the
post-processing is a function of that output alone, the data-processing inequality gives
I(truth; processed) ≤ I(truth; output). A second call that sees the original problem is
not literally a function of the first sample: additional draws can expose usable
information the first draw did not and can reduce noise. They still introduce no
**external evidence** about the world, and their errors remain correlated. The usable-
information literature likewise shows that structure can improve what a computationally
bounded decoder extracts. The operational rule is therefore **model-only structure and
resampling can improve extraction and computation; they cannot improve evidence**.
Sources, executed results, observations, and independently constrained computation break
that limitation in different ways, which is why the recipes must say which one they add.

Machinery comes in two grades, giving three tiers overall:

- **Tier 1 — Skill.** Procedure in context: instructions, templates, scripts,
  conventions. Provides *method*. (Education, in the human analogy.)
- **Tier 2 — Harness.** Enforcement without domain logic: hooks and gates in the agent
  runtime that block transitions until artifacts exist (e.g. a Stop-hook refusing to
  end a turn that ships a verdict without a gate file). Provides *locks*.
- **Tier 3 — Service.** Domain machinery behind a boundary (an MCP server): schema
  validation, server-side elicitation, recomputation, append-only state, typed audit
  trails. Provides *guarantees*.

The human-science precedent for the tier distinction is exact: the replication crisis
was not fixed by teaching scientists more statistics (Tier 1); it was fixed by
preregistration and registered reports (Tiers 2–3) — gates you pass *before* knowing
the answer, kept by someone other than the author.

## 5. Classification: every act, its tier, and what the upgrade buys

The skill tier of every act ships with this paper (Appendix A). The table classifies
coverage honestly: *Full* means the skill delivers the act's value under the lawyer
test; *Strong* means discipline-dependent but with failures visible in artifacts;
*Partial/Weak* means a determined lawyer defeats it silently — the skill ships anyway
because the weak form still pays, and it says so on the label.

One rule now qualifies that last clause. Where a check must be self-administered — which
is most of them — **prefer the form that refuses over the form that labels.**
`NO_REFERENCE_CLASS` is a gate: the pipeline stops and names what is missing. "Grade D —
unsourced" is a label: the value flows onward wearing a disclaimer. Labels are useful and
they do not stop a motivated actor, because structure persuades independently of
correctness and a disclaimer beside a number is read as care rather than as a warning.
The worked example is this release's pedigree gate: `aggregate_numeric` and
`combine_fermi` require a provenance tag per input and *refuse* when an `invented` one is
load-bearing, rather than computing and disclaiming. Two details matter. First, each tool
states the **mechanical** rule by which it decided "load-bearing" — the draw at the median
position; the factor at or above the average share of total `log10(high/low)`, or stated
as a point — because a load-bearing test left to judgment is a label again. Second, the
gate is deliberately *not* applied to `score_ach`: ordinal C/I/N cells over 1–3
credibility already sit near the honest resolution limit of the underlying judgment, and
the output is a ranking plus flip cells rather than a decimal. The gate belongs where
exact arithmetic meets continuous invented inputs, not everywhere a judgment enters.

| # | Act | Skill (shipped) | Coverage as skill | What only machinery guarantees | Machinery shape | Machinery status |
|---|-----|-----------------|-------------------|-------------------------------|-----------------|------------------|
| 3 | Reformat | `ct-reformat` | **Full** | — | — | not needed |
| 2 | Definition pin | `ct-definition-pin` | **Full** | — | — | not needed |
| 17 | Reframe / anomaly hunt | `ct-reframe` | **Strong** | alternative generated before commitment; frames outside the model's distribution | pre-registration boundary + affected-human review | optional for high stakes |
| 1 | Question tree / Fermi | `ct-question-tree` + `fermi.py` | **Full** | synthesis-citation binding | workflow engine | not worth it |
| 4 | Assumption audit | `ct-assumption-audit` | **Full** | — | — | not needed |
| 18 | Counterexample search | `ct-counterexample` | **Strong**; **Formal** when a complete oracle covers the frozen domain | that the search ran; encoding faithful; certificate valid | execution/solver boundary | use existing host tools; no general solver here |
| 19 | Formalize and compute | `ct-formalize` | **Strong** for the computation; **None** for the modelling choice | that the encoding matches the situation; that inputs are not invented | execution/solver boundary | host tooling; no solver ships here |
| 11 | Premortem | `ct-premortem` | **Full** | tripwire follow-through | scheduler/hook watching signals | Tier 2, optional |
| 5 | Steelman | `ct-steelman` | **Strong** | advocate blindness; symmetric effort; timestamped pre-registration | debate service, hidden channels, effort accounting | worth building |
| 9 | Judgment panel | `ct-panel` + `aggregate.py` | **Strong** | every draw reported; that a `source` tag is true | sampling service with server-side draw log | argLLM's sampling adapter is this shape |
| 6 | ACH | `ct-ach` + `ach_score.py` | **Strong** | per-cell fresh elicitation | ACH server — the natural sibling of argLLM | **best next server** |
| 7 | Evidence ledger | `ct-evidence-ledger` + `ledger.py` | **Partial** | honest grading; immutability | citation-checker + append-only store | worth building |
| 8 | Consistency log | `ct-consistency-log` + `commitlog.py` + `analyze_dependencies` | **Partial** | complete capture (logging is voluntary); that recorded edges match real dependence; immutability | boundary auto-logger of stated positions | withdrawal impact exists; capture remains voluntary |
| 10 | Calibration | `ct-calibration` + `brier.py` | **Weak** (self-graded, now *measurably* so via `resolved_by`) | untamperable history; outcomes fed by non-predictor (CI, tracker, human) | prediction-ledger service | **second-best next server** |
| 13 | Verdict gate | `ct-verdict-gate` + `hooks/verdict_gate_stop.py` | **Strong** (locked; the hook fails open) | that the gate was *filled*, not merely written | harness Stop hook + process audit | **exists** (`hooks/`) |
| 15 | Entailment check | `ct-entailment` + `origins.py` | **Strong** | that retrieval happened and spans are real; fetched-source verification | citation-checker fetching each source | worth building |
| 16 | Ensemble of perspectives | `ct-ensemble` + `bag.py` | **Strong** | that each perspective saw only its slice; that draws were not re-rolled | sampling service with a server-side draw log | shares argLLM's sampling shape |
| 12 | Sensitivity probe | inside `ct-ach` / `ct-argument-map` | **Strong** (it is arithmetic) | computed over guaranteed structure | comes free with ACH/argLLM servers | partially exists |
| 14 | Argument map | `ct-argument-map` (driver only) | **orchestration only** | validated tree; fresh-context τ; recomputed-never-stored σ; copy-on-write revisions | **argLLM server** | **exists** |
| — | Fresh-mind sourcing (cross-cutting) | conventions §2 + templates | discipline | a channel the orchestrator cannot contaminate | MCP sampling at the server boundary | exists in argLLM |

Four observations on the table.

**The split is not simple-vs-complex.** Reformatting and definition-pinning are
cognitively deep and fully skill-coverable, because their failures are visible: an
unfaithful restatement or a self-serving definition sits in the artifact where the next
reader (or the steelman advocate) can attack it. Calibration is mechanically trivial —
a file and a mean of squared errors — and is the *worst*-covered act in the set,
because its entire value is a history the predictor must not control.

**The machinery column is mostly about four guarantees.** Across rows, what upgrades
buy reduces to: (a) *judgment sourcing* — elicitation from contexts the orchestrator
cannot contaminate; (b) *process-bound artifacts* — records that could only exist if
the procedure ran; (c) *protected state* — append-only, non-repudiable history; and
(d) *artifact–process binding*, which the earlier revisions folded into (b) and which
deserves to stand alone because it is the caveat on the skill tier's whole case:
**an artifact can be produced without its process, and producing it is cheaper than
running the procedure that should have produced it.** The presence of a receipt is
therefore evidence that a receipt was written, not that the procedure ran. A model can
fill a hypothesis matrix in one lawyerly breath — the table exists; the independent
rating never happened. Observability is necessary and not sufficient. These are all
boundary properties: no amount of in-context instruction provides a boundary, and the
verdict-gate hook shipped in this release makes the point sharply — it can check that a
gate file *exists*, never that its seven items were honestly answered. How much this
bites in practice is an empirical question nobody has measured, which is why §8's
process-vs-artifact audit is the first thing built and the thing that decides how much of
the rest is worth building.

**Two acts are named as next servers.** ACH is argLLM's natural sibling: same
architecture (structure validated at the boundary, judgments elicited per-cell from
fresh contexts, verdict recomputed from structure), different formalism (matrix +
inconsistency counting instead of QBAF + gradual semantics). The calibration ledger is
the other: small, high-leverage, and impossible to do honestly as a skill. **The audit
picks between them, and may say neither.** If artifact-without-process proves rare, the
elicitation server is not worth building and the prediction ledger becomes the obvious
first machinery — its value is a history the predictor must not control, which is a
different problem from compliance and is unaffected by the audit's result. If
artifact-without-process proves common, the order reverses.

### 5.1 The evidence behind each act

The founding claim is that these are ports of tested human findings, not prompt folklore.
That claim is only auditable if each act names the finding it implements and, where one
exists, the LLM-side replication of the same failure. **An act with an empty cell here is
a candidate for the next cut, not a candidate for defence.**

| # | Act | Human finding | LLM-side replication of the failure |
|---|-----|---------------|-------------------------------------|
| 3 | Reformat | F2 — frequency formats roughly triple correct Bayesian answers, physicians included (Gigerenzer & Hoffrage 1995) | performance swings widely on prompt-format changes carrying no information (Sclar et al. 2024) |
| 2 | Definition pin | F8 — structured analytic techniques; equivocation control (Heuer 1999) | — *(no direct LLM study; flagged, not defended)* |
| 1 | Question tree / Fermi | F3 — working memory ≈ 4 chunks; cognition is externalized (Cowan 2001; Clark & Chalmers 1998) | chain-of-thought's gains are exactly externalized intermediate steps (Wei et al. 2022) |
| 4 | Assumption audit | F8 — consider-the-opposite replicates (Lord, Lepper & Preston 1984) | — *(inherits F4's evidence indirectly)* |
| 11 | Premortem | F8 — prospective hindsight raises cause identification (Klein 2007) | — *(no direct LLM study)* |
| 5 | Steelman | F4 — biased producers, competent evaluators; groups 8-in-10 vs individuals 1-in-10 (Mercier & Sperber 2011; Moshman & Geil 1998) | evaluators recognize and favor their own generations (Panickssery et al. 2024); debate improves factuality (Du et al. 2023) |
| 9 | Judgment panel | F7 — judgment is noisy across occasions (Kahneman, Sibony & Sunstein 2021); mechanical combination wins (Meehl 1954; Grove et al. 2000) | self-consistency: sample several, aggregate mechanically (Wang et al. 2023) |
| 6 | ACH | F8 + F1 — least-inconsistency beats most-support; testing one story is the default failure (Heuer 1999) | models largely cannot self-correct reasoning without external information (Huang et al. 2024) |
| 7 | Evidence ledger | F6 — score-keeping is what couples confidence to accuracy (Tetlock 2005) | — *(hallucinated-citation literature is adjacent, not a replication)* |
| 15 | Entailment check | F2/F8 — relevance is not entailment; independence of sources is the classic corroboration error | retrieval-augmented models cite sources that do not support the claim; repetition inflates apparent support |
| 16 | Ensemble of perspectives | F7 — mechanical combination beats holistic judgment, and judgment is noisy (Meehl 1954; Kahneman, Sibony & Sunstein 2021); bagging is the statistical form (Breiman 1996, 2001) | self-consistency samples and aggregates mechanically (Wang et al. 2023); debate across independent contexts improves factuality (Du et al. 2023) |
| 17 | Reframe / anomaly hunt | F2 — representation changes reasoning ability; F8 — structured methods beat awareness alone | prompt-format changes swing performance without changing information (Sclar et al. 2024) |
| 18 | Counterexample search | F8 — consider-the-opposite works when made procedural; a valid witness mechanically defeats a universal | intrinsic self-correction degrades without external feedback (Huang et al. 2024); the specific generate–execute–shrink recipe is unmeasured here |
| 8 | Consistency log | F3 — small working memory; drift over long horizons | "lost in the middle": long-context attention is effectively shallow (Liu et al. 2024) |
| 10 | Calibration | F6 — weather forecasters are calibrated because feedback is fast; superforecasters keep score (Tetlock & Gardner 2015) | — *(LLM calibration is well studied; the *ledger* intervention is not)* |
| 13 | Verdict gate | F8 — checklists work; awareness does not (Gawande 2009) | F1's post-hoc checking: self-critique without external information does not correct (Huang et al. 2024) |
| 12 | Sensitivity probe | F7 — it is arithmetic, not judgment | — *(mechanical; no replication needed)* |
| 14 | Argument map | F8 — argument mapping yields ~0.7–0.8 SD gains per semester (van Gelder 2005; Twardy 2004) | QBAF-structured verification improves contestable claim checking (Freedman et al. 2024) |

Read the empty and qualified cells honestly. Several acts rest on human evidence with no
LLM-side replication of the specific intervention. They ship because the human evidence
is strong and the cost is low — but they are the first candidates for removal if
measurement does not support them, and saying so here is the point of the column.

## 6. Case study: argLLM as the machinery tier

The argLLM server (companion repository) implements Argumentative LLMs (Freedman et al.
2024; demoed as ArgLLM-App, arXiv 2602.24172): claim verification by constructing a
Quantitative Bipolar Argumentation Framework (QBAF) with LLM-elicited arguments and
base scores, evaluated by gradual semantics, exposed for contestation over MCP. Its
design decisions read as a checklist of exactly the guarantees §4.2 says skills lack:

- **Who supplies the judgments.** Base scores (τ) are elicited server-side via MCP
  sampling, one fresh context per elicitation. The orchestrating model that wants a
  verdict never writes a τ. (Guarantee (a).)
- **Validated structure.** Pydantic validators enforce tree shape, no cycles, root
  rules, id discipline at every tool boundary. A malformed argument framework cannot
  exist, rather than being advised against. (Guarantee (b).)
- **The verdict is arithmetic.** Strength σ is a pure function of (structure,
  semantics), recomputed per response and never stored — there is no way for a stale or
  hand-edited strength to survive. DF-QuAD and the other semantics are the Meehl move
  (F7): local judgments in, mechanical combination out.
- **Contestation is first-class and non-repudiable.** Edits are copy-on-write
  revisions; every mutating call reports old vs new strength and verdict. Setting an
  inconvenient counter-argument's score to zero is *permitted* — and permanently
  visible. (Guarantee (c).)
- **Receipts.** Every response carries the rendered tree; OpenTelemetry traces mirror
  tool → Γ/ℰ/Σ → per-elicitation spans. The audit trail is machine-generated, not
  self-reported.

The accompanying `ct-argument-map` skill is deliberately thin — a driver's manual. The
division of labor is the paper's thesis in miniature: the skill knows *when and how* to
use the map; the server guarantees *that what the map shows actually happened*.

## 7. Architecture: skills orchestrating machinery

The stable composition is not skills *or* machinery but skills *driving* machinery:

```
  user intent
      │
  Tier 1  controller: silently choose the minimum useful act — or NO_SCAFFOLD
      │
  Tier 1  skill (method): phrase prompts, invoke tools, route artifacts
      │
  Tier 2  harness (locks): gates that block transitions until artifacts exist
      │
  Tier 3  service (guarantees): validated structure, clean elicitation,
          arithmetic verdicts, append-only history        ←── the receipts live here
```

The controller is part of this package, not a second system. The user states the problem,
not the technique. `critical-thinking` triages from visible failure signals, starts with
one act, and escalates only when that act exposes a split, unsupported load-bearing claim,
fragile input, missing observable, or failed check. It asks the user only for a value
judgment, a meaning whose ambiguity changes the answer, evidence only they can supply, or
authority for an irreversible action. `NO_SCAFFOLD` is a successful route: most ordinary
queries should pay no critical-thinking ceremony at all.

The controller also applies an epistemic-leverage stamp. A stage may add external
evidence, independently constrained computation, or model-only structure. These are
reported separately. A fresh same-model perspective is useful contestation and not a new
source; a solver certifies the encoded statement and not its faithfulness; dependency
impact is exact about recorded edges and not about edges the author failed to record.

Rationality, on the ecological view (Gigerenzer), is a fit between a mind and its
environment; you improve reasoning by designing the environment, not by exhorting the
thinker. A skill set is a library of environment designs; the machinery tier is the
part of the environment the thinker cannot redecorate. Transparency falls out rather
than being added: every act ends in an artifact (a tree, a matrix, a ledger, a gate
file), the artifacts compose into an audit trail, and at the machinery tier the trail
is process-bound — it could not exist unless the procedure ran.

Two honest caveats about the skill tier's own foundations:

- **Same-weights correlation.** Fresh subagents remove context contamination and
  self-ownership and cancel noise; they do not cancel blind spots shared by the model
  class (Panickssery et al. 2024 shows even self-*recognition* biases evaluation).
  Cross-model or human panelists are the mitigation where stakes warrant.
- **Ritual risk.** Checklists decay into ritual when their outputs are never audited
  (aviation and medicine both relearned this). The verdict gate's SKIPPED-with-reason
  convention is designed to keep skipping *expensive in candor* rather than forbidden —
  forbidding produces pencil-whipping, candor produces signal.
- **Routing risk.** Autonomy removes user micromanagement by moving method selection into
  the model. A confident misroute can now be invisible. Progressive escalation,
  `NO_SCAFFOLD`, and receipts for acts that actually ran limit the cost; only matched
  evaluation can show whether the controller selects well.

## 8. Evaluation plan

The set makes falsifiable claims; here is how we would test them (not yet run):

- **Accuracy.** Contested-claim verification (the datasets used in the argLLM paper's
  experiments) under four arms: bare model / chain-of-thought / skill tier / skill +
  machinery. Claim: monotone improvement, largest step at the machinery arm for
  contested claims specifically.
- **Calibration.** Forecast-style questions with known resolutions; Brier score with
  and without `ct-calibration` + panel; claim: variance shrinks (panels), calibration
  bins flatten toward the diagonal (score-keeping).
- **Belief revision.** Seeded wrong-lean tasks: does `ct-steelman` move the answer when
  the opposing case is objectively stronger, at a higher rate than "consider both
  sides" prompting? (This is the LLM version of Lord–Lepper–Preston.)
- **Drift.** Long agent tasks with planted contradictions; catch rate with and without
  `ct-consistency-log` sweeps.
- **Cost.** Tokens and wall-clock per act, because the honest comparison is
  quality-per-dollar, and because some acts (reformat, definition pin) should pay for
  themselves while others (full ACH) are reserved for stakes.
- **Autonomous routing.** Compare user-selected acts, the autonomous controller, and
  `NO_SCAFFOLD` at matched compute. Report both directions of harm: cases the controller
  fixes and cases direct work got right but the selected scaffold breaks. A router that
  never chooses no scaffold has failed before its downstream scores are read.
- **Problem finding and falsification.** Seed tasks whose asked question targets the
  wrong boundary and universal claims with small executable counterexamples. Measure
  useful frame changes, invalid frame changes, witness validity, shrink quality, and the
  rate at which bounded search is falsely reported as proof.
- **Process-vs-artifact audit.** The measurement for guarantee (d), and the one built
  first because its result decides what else is worth building. `bench/process_audit/`
  holds the protocol. Take N tasks suited to hypothesis-matrix analysis and produce two
  matrices each. **Arm A** runs the prescribed procedure: one fresh cell-rater per
  evidence item, each seeing the hypothesis list and that one item only, no lean.
  **Arm B** produces the same matrix in a single pass by a model that has been shown a
  lean. Compare cell-by-cell agreement between arms, and both against ground truth where
  the instance is synthetic. Instrument compliance at the same time: whether the
  subagents were actually spawned in normal operation, and how that varies with context
  length and task confidence. The readings are unambiguous — *Arm B ≈ Arm A, both
  accurate*: the fresh-mind discipline is not doing work, skills suffice. *Arm B ≈ Arm A,
  both lean-shifted*: the procedure is not being run, machinery is required. *Arm B
  shifted, Arm A not*: the discipline works when followed, so harness hooks become the
  priority. This lives in `bench/` rather than `tests/` on purpose: tests pin behaviour
  deterministically, and this measures a live model and will be noisy.
- **Instances with planted traps.** `bench/generate_instance.py` procedurally generates a
  diagnosis-and-intervention packet with an authoritative synthetic prediction model. A
  reference solver must reconstruct every keyed field from only the agent-visible packet
  and the separately queryable registry; the generator refuses a draw that it cannot.
  Each trap maps to one act and each wrong discipline produces a *different* wrong answer,
  so a failure is attributable rather than merely wrong:
  counting restatements of one origin as four observations lands on one hypothesis;
  missing a mid-episode retraction lands on another; ignoring the base rates that exist
  only in a queryable registry lands on a third. A shared-budget probe plan must contain
  an affordable discriminator for the matrix-tied pair, and a response schedule is
  infeasible in a stated fraction of instances (the scorer accepts any inclusion-minimal
  conflict, not one generator-chosen witness). The honest limit: handing over predictions
  and constraints already formalised means the instrument tests **procedural discipline
  only**. Whether a model can produce a faithful formalisation in the first place is the
  harder question, and this does not reach it. Solver packets omit `truth.json`; judge
  bundles are generated separately after the answer commits.

## 9. Limitations and open questions

**No experiment has been run.** Everything above rests on human-sciences evidence,
LLM-side parallels established for the *failure modes* rather than for these specific
interventions, and design argument. That is a reasonable basis for building and a poor
basis for confidence, and the §5.1 table exists so the thinness is visible per act rather
than averaged away.

One adversarial trial of this general approach — one instance, two agents, one following a
structured procedure and one unaided — tied on nine of thirteen sub-questions. The
structured arm won decisively on exactly two: a machine-checked minimal unsatisfiable
core, where prose reasoning produced a plausible but non-minimal answer; and detecting
that the instance's evidence was internally inconsistent, which the unaided arm never
encountered because it only bought probes confirming its leading hypothesis. Notably,
origin clustering and retraction handling — two things this revision invests in — were
handled correctly by **both** arms within a single short context.

Read that carefully. It supports the thesis where computation replaces judgment and where
a gate resists a motivated actor. It does **not** support the claim that these disciplines
help within a short, well-structured context. The real bet is that they help **across long
horizons, under load, when the correction was twenty steps ago and the context has moved
on** — and that has not been tested.

- **Structure has overhead.** Decomposition and matrices cost tokens and can hurt on
  tasks where the model's holistic judgment is already good — the LLM evidence on
  chain-of-thought's uneven benefits (helping mainly symbolic/mathematical tasks;
  Sprague et al. 2024) likely has analogs here. Routing (`critical-thinking`'s table)
  is itself a judgment call and can misfire in both directions.
- **The skill tier is only as honest as its artifacts are audited.** Without occasional
  process audits (§8), Strong-coverage acts degrade toward Weak in practice.
- **Same-weights panels bound the contest move.** How much of F4's group benefit
  survives when all "group members" share weights is an open empirical question; the
  debate literature (Du et al. 2023) is encouraging but not decisive.
- **Enforcement can relocate lawyering rather than remove it.** With argLLM, the
  orchestrator still chooses *which* edits to make; the guarantee is visibility, not
  virtue. We consider visible lawyering a success condition — it is what contestability
  means — but users should not mistake a receipt for a proof of good faith.
- **Subagents do not remove blind spots.** Fresh contexts remove contamination,
  self-ownership, and noise; they do not remove failure modes shared by the model class,
  and a panel of five wrong in the same direction is still wrong. The `source` tag added
  in this revision moves that caveat from prose into the output — which is the part a
  skill can do — but it does not make the tags true.
- **Transfer — the deepest open question.** Human critical-thinking training transfers
  poorly across domains (Willingham 2007). Whether a model that *practices* these acts
  (or is fine-tuned on their receipts) improves its unaided reasoning, **or merely
  produces better receipts** — the van Gelder question, ported — is unanswered, testable,
  and decides how much any of this is worth. Everything above is worth exactly as much as
  the measurements that follow it.

## 10. Conclusion

Chain-of-thought was not a trick; it was the first borrowed practice from a long,
well-tested human library. The rest of the library ports the same way, provided each
practice is delivered at the right tier. Method knowledge — when to decompose, how to
steelman, what a premortem asks — belongs in skills, and this paper ships that tier
whole. Guarantees — who supplied the judgments, whether the procedure actually ran,
whether the history survived intact — cannot be prompted into existence at any level of
model capability, because they are properties of the environment, not of the thinker.
The line between the tiers is drawn by one question: *does it still work when the model
is being a lawyer?* Everything on the wrong side of that line is an engineering
roadmap, and its first two entries — an ACH server and a calibration ledger — are
already visible from here.

## Addendum (v1.1) — the project split and the middle rung

The skill tier first shipped inside the argLLM repository; it now lives here, in
**critical-thinking-mcp**, together with a second deliverable the classification table
called for: a lean MCP server of purely mathematical aggregators (`src/ctmcp/`) — QBAF
evaluation under DF-QuAD, ACH inconsistency scoring with flip-cell sensitivity, panel
statistics, Brier calibration bins, Fermi interval arithmetic, and truth-maintenance
withdrawal impact over recorded dependency graphs.

This server is a deliberately *partial* Tier 3. Of §5's four machinery guarantees it
provides only the arithmetic half of (b) — verdicts computed by rule, with the rule
echoed alongside every result. It provides **no** judgment-sourcing guarantee (a) and
**no** protected state (c); it will faithfully aggregate a lawyer's spreadsheet if fed
one. That is by design: it creates a usable **middle rung** between "skill only" and
"full argLLM" — *recipes elicit judgments through fresh subagents (Tier-1 discipline),
and the server aggregates them mechanically (Tier-3 arithmetic).* The `ct-argument-map`
degraded mode now names this rung explicitly, and the honesty rule extends to it: every
reported number is labeled with the rung that produced it (self-assigned /
subagent-elicited / server-enforced). Full machinery for argument mapping remains
argLLM, the companion repository.

## Addendum (v1.2) — refusal, retraction, origins, and the measurement

Four capability changes and four doctrine changes, all additive.

The doctrine changes are stated where they belong rather than here: guarantee (d),
artifact–process binding (§5); the data-processing bound that explains where the lawyer
test draws its line (§4.3); gate-over-label (§5); and the per-act evidence table (§5.1),
whose empty cells are the point.

The capability changes each close a failure the set previously permitted:

- **Origins.** `score_ach` counts evidence credibility **once per origin cluster**. Four
  restatements of one shift-log entry are one observation, and counting four independent
  weights from them could manufacture a confident wrong survivor from a single source.
  Absent the field, every item is its own origin and matrices score exactly as before.
- **Retraction propagates.** The commitment log records `depends_on` at write time, and
  superseding an entry marks its transitive dependents `OUT`. The pair-sweep catches *"I
  said A at step 3 and not-A at step 40"*; it cannot catch *"I withdrew A at step 4 and
  step 19 still rests on it"* — a failure invisible in the output by construction, since a
  conclusion resting on a retracted premise looks identical to a correct one. The walk
  claims no structural certificate: the record is model-authored, dependencies it did not
  notice are absent, and it deliberately over-marks so that silence is the safe failure.
- **Entailment.** Act 15 asks a fresh context whether a source *entails* a claim, and
  collapses sources by origin before counting. Relevance is the failure mode; entailment
  is the check.
- **Refusal and provenance.** The pedigree gate on the two continuous aggregators; a
  `source` per panel draw so composition stops being invisible; `resolved_by` per
  calibration resolution so a self-graded ledger says so on its own face. None of these
  is a guarantee — you can write `ci` on a self-resolution, or `sonnet` on five more draws
  from the same model. What they do is make the gap **measurable rather than merely
  disclosed**, which is the most a Tier-1 record can honestly claim.

And the lock the set had been describing for two revisions now exists: `hooks/`
(Appendix B). It checks that a gate file exists, not that its items were honestly
answered — which is guarantee (d) restated, and exactly what `bench/process_audit/` is
built to measure.

## Addendum (v1.3) — autonomous selection, problem finding, and recorded impact

The toolbox now selects itself. The `critical-thinking` skill is an autonomous outer
controller: it routes by failure signal, begins with the minimum useful act, treats
`NO_SCAFFOLD` as success, and escalates only on a concrete finding. The user supplies the
problem and retains authority over values and irreversible action; they no longer have to
know that ACH, entailment checking, or a premortem exists. This removes micromanagement,
not the lawyer problem — routing remains a model judgment and is now an explicit
evaluation target.

Two acts widen the set from error checking toward problem finding and independently
constrained falsification. `ct-reframe` separates observations from the question's hidden
target and boundary, starts from the anomaly the original frame explains worst, and
records what would falsify each alternative frame. `ct-counterexample` freezes a
universal claim's domain and premises, prefers enumeration, execution, tests, retrieval,
or a solver to model critique, shrinks any witness, and makes
`SURVIVED_BOUNDED_SEARCH` different from proof in the artifact itself.

The commitment graph gained a narrow endogenous computation without claiming the free
soundness such computations are often given. `commitlog.py impact` and the pure
`analyze_dependencies` MCP tool withdraw each ACTIVE entry in simulation and count which
recorded live claims become `OUT`; targets name which recorded premises carry a final
conclusion. Script and core parity tests pin the result. The rank is exact about the
append-only record and is a verification-budget heuristic only: the model still authored
the edges, so a missing dependency remains invisible.

Finally, the shared convention now distinguishes **external evidence**, **independently
constrained computation**, and **model-only structure**. Additional model calls can
improve extraction and reduce noise; they do not become external evidence by being
numerous or well formatted. Every consequential result says which kind of leverage it
actually received.

---

## References

*Human sciences*

- Clark, A. & Chalmers, D. (1998). The extended mind. *Analysis*.
- Cowan, N. (2001). The magical number 4 in short-term memory. *Behavioral and Brain
  Sciences*.
- Doyle, J. (1979). A truth maintenance system. *Artificial Intelligence*.
- Gawande, A. (2009). *The Checklist Manifesto*.
- Gigerenzer, G. & Hoffrage, U. (1995). How to improve Bayesian reasoning without
  instruction: frequency formats. *Psychological Review*.
- Grove, W. et al. (2000). Clinical versus mechanical prediction: a meta-analysis.
  *Psychological Assessment*.
- Heuer, R. (1999). *Psychology of Intelligence Analysis*. CIA Center for the Study of
  Intelligence. (Ch. 8: Analysis of Competing Hypotheses.)
- Hutchins, E. (1995). *Cognition in the Wild*.
- Kahan, D. et al. (2017). Motivated numeracy and enlightened self-government.
  *Behavioural Public Policy*.
- Kahneman, D. (2011). *Thinking, Fast and Slow*.
- Kahneman, D. & Klein, G. (2009). Conditions for intuitive expertise: a failure to
  disagree. *American Psychologist*.
- Kahneman, D., Sibony, O. & Sunstein, C. (2021). *Noise: A Flaw in Human Judgment*.
- Klein, G. (2007). Performing a project premortem. *Harvard Business Review*.
- Lord, C., Lepper, M. & Preston, E. (1984). Considering the opposite: a corrective
  strategy for social judgment. *JPSP*.
- Meehl, P. (1954). *Clinical versus Statistical Prediction*.
- Mercier, H. & Sperber, D. (2011). Why do humans reason? *Behavioral and Brain
  Sciences*; (2017). *The Enigma of Reason*.
- Miller, G. (1956). The magical number seven, plus or minus two. *Psychological
  Review*.
- Moshman, D. & Geil, M. (1998). Collaborative reasoning: evidence for collective
  rationality. *Thinking & Reasoning*.
- Stanovich, K. (2009). *What Intelligence Tests Miss: The Psychology of Rational
  Thought*.
- Tetlock, P. (2005). *Expert Political Judgment*; Tetlock, P. & Gardner, D. (2015).
  *Superforecasting*.
- Tversky, A. & Kahneman, D. (1974). Judgment under uncertainty: heuristics and biases.
  *Science*.
- van Gelder, T. (2005). Teaching critical thinking: some lessons from cognitive
  science. *College Teaching*; Twardy, C. (2004). Argument maps improve critical
  thinking. *Teaching Philosophy*.
- Willingham, D. (2007). Critical thinking: why is it so hard to teach? *American
  Educator*.

*Language models*

- Du, Y. et al. (2023). Improving factuality and reasoning in language models through
  multiagent debate. arXiv:2305.14325.
- Freedman, G., Dejl, A., Gorur, D., Yin, X., Rago, A. & Toni, F. (2024).
  Argumentative large language models for explainable and contestable claim
  verification. arXiv:2405.02079. (ArgLLM-App demo: arXiv:2602.24172.)
- Huang, J. et al. (2024). Large language models cannot self-correct reasoning yet.
  *ICLR*.
- Irving, G., Christiano, P. & Amodei, D. (2018). AI safety via debate.
  arXiv:1805.00899.
- Liu, N. et al. (2024). Lost in the middle: how language models use long contexts.
  *TACL*.
- Panickssery, A., Bowman, S. & Feng, S. (2024). LLM evaluators recognize and favor
  their own generations. *NeurIPS*.
- Sclar, M. et al. (2024). Quantifying language models' sensitivity to spurious
  features in prompt design. *ICLR*.
- Sprague, Z. et al. (2024). To CoT or not to CoT? Chain-of-thought helps mainly on
  math and symbolic reasoning. arXiv:2409.12183.
- Wang, X. et al. (2023). Self-consistency improves chain of thought reasoning in
  language models. *ICLR*.
- Wei, J. et al. (2022). Chain-of-thought prompting elicits reasoning in large
  language models. *NeurIPS*.

*Statistics*

- Breiman, L. (1996). Bagging predictors. *Machine Learning*; (2001). Random forests.
  *Machine Learning*. (Resample-and-aggregate, and permutation importance.)

---

## Appendix A — the shipped skill set

Nineteen skills under `skills/` (symlinked as `.claude/skills` in this repository, so
they are live here; copy skill directories into another project's `.claude/skills/` or
into `~/.claude/skills/` for global use). Scripts are Python-stdlib-only.

| Skill | Files | Role |
|---|---|---|
| `critical-thinking` | SKILL.md, references/conventions.md, references/subagent-templates.md | autonomous controller, NO_SCAFFOLD, progressive escalation, shared rules, templates T1–T12 |
| `ct-reframe` | SKILL.md | alternative frames, anomaly-first problem finding, wrong-frame tests |
| `ct-counterexample` | SKILL.md | oracle-first witness search, shrinking, proof-vs-bounded-search distinction |
| `ct-question-tree` | SKILL.md, scripts/fermi.py | decomposition + Fermi interval arithmetic |
| `ct-definition-pin` | SKILL.md | operational definitions, equivocation naming |
| `ct-reformat` | SKILL.md | representation translation catalog |
| `ct-formalize` | SKILL.md | shape catalog, model-in-a-file, solver/enumeration/simulation, encoding attacks, discipline borrowing |
| `ct-assumption-audit` | SKILL.md | premise surfacing, kill-zone triage |
| `ct-steelman` | SKILL.md | blind symmetric advocacy + blind judging |
| `ct-premortem` | SKILL.md | declarative-failure analysis, tripwires |
| `ct-ach` | SKILL.md, scripts/ach_score.py, references/method.md | hypothesis racing, inconsistency scoring, flip-cell sensitivity |
| `ct-evidence-ledger` | SKILL.md, scripts/ledger.py | claim–source coupling, naked-claim report |
| `ct-ensemble` | SKILL.md, scripts/bag.py, references/example.md | bagged perspectives, mechanical vote, permutation importance |
| `ct-entailment` | SKILL.md, scripts/origins.py | per-claim entailment verdicts, origin clustering, distinct-origin counts |
| `ct-consistency-log` | SKILL.md, scripts/commitlog.py | commitment capture, contradiction sweep, retraction and withdrawal-impact bookkeeping |
| `ct-panel` | SKILL.md, scripts/aggregate.py | independent draws, mechanical aggregation |
| `ct-calibration` | SKILL.md, scripts/brier.py | prediction ledger, Brier bins (self-graded, labeled) |
| `ct-verdict-gate` | SKILL.md | pre-verdict checklist with written skips |
| `ct-argument-map` | SKILL.md | driver for the argLLM MCP server (Tier 3) |

Workspace convention: artifacts under `.ct/` (gitignored; force-add receipts worth
keeping). Every skill ends its act by citing its artifact path — the receipts are the
transparency, subject to guarantee (d): they show a receipt was written.

## Appendix B — the other two rungs in this repository

| Directory | Tier | Contents |
|---|---|---|
| `hooks/` | 2 — locks | `verdict_gate_stop.py`, a Claude Code `Stop` hook refusing to end a turn that ships a verdict marker with no `.ct/gate--*.md` written that session, plus install notes. Blocks at most once per turn and fails open — a lock on the careless path, not on a determined one. |
| `bench/` | — measurement | `generate_instance.py` (seeded adversarial instances generated from hidden ground truth), `score_instance.py` (exact scoring with per-trap attribution), `process_audit/` (the Arm A / Arm B protocol and `compare_arms.py`). Calls no model. **Not in the repository at time of writing** — held back while the instrument is still being corrected, so the citations to it below record findings rather than point at files. |

Neither is imported by `src/ctmcp`. The hook is executed by the agent runtime; the bench
is run by hand. Both are stdlib-only, and both are linted, typechecked, and — for their
deterministic parts — pinned by tests, because a harness that is itself unreliable
measures nothing.
