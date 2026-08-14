"""Input pedigree: where a number came from, and when that disqualifies it.

Exact arithmetic over an invented quantity launders a guess into a result. The
gate **refuses rather than labels**: a disclaimer beside a number is read as care
rather than as a warning, so it does not stop a motivated caller, while a refusal
names what is missing and stops the pipeline until it arrives.

  given     handed to the caller — a spec, a requirement, a measured input
  sourced   from a named external source
  elicited  from a fresh subagent that never saw the lean
  invented  nobody sourced it; the model made it up

`elicited` computes and is stamped: elicited-from-a-fresh-mind is a real
improvement over self-assigned, and is not the same as sourced. `invented`
computes only where it cannot reach the headline — each aggregator states the
*mechanical* rule by which it decides that, because a load-bearing test left to
judgment is a label again.

Duplicated by hand in the bundled skill scripts, which are stdlib-only and cannot
import this. Parity is pinned by tests/test_parity.py — change both or neither.
"""

PEDIGREES = ("given", "sourced", "elicited", "invented")


def check(value: object, where: str) -> str:
    """Validate one pedigree tag, naming where a missing or unknown one sat."""
    tag = "" if value is None else str(value).strip()
    if not tag:
        raise ValueError(
            f"{where}: pedigree is required — one of {', '.join(PEDIGREES)}. "
            "Say where the number came from; 'invented' is an honest answer."
        )
    if tag not in PEDIGREES:
        raise ValueError(f"{where}: pedigree must be one of {', '.join(PEDIGREES)}, got {tag!r}")
    return tag


def refuse(what: str, why: str) -> ValueError:
    """The refusal, worded so the caller knows what would unblock it."""
    return ValueError(
        f"{what} is invented and {why} — refusing to compute. Supply it elicited "
        "(a fresh subagent that never saw your lean), sourced (a named external "
        "source), or given (handed to you) — or drop the estimate and report which "
        "quantity is missing. Computing it and disclaiming it is the failure mode "
        "this gate exists to stop."
    )


def tally(tags: list[str]) -> dict[str, int]:
    """Counts per pedigree in canonical order, omitting absent ones."""
    return {p: tags.count(p) for p in PEDIGREES if p in tags}


def phrase(tags: list[str]) -> str:
    """'3 sourced, 1 elicited' — the inputs half of an aggregator's stamp."""
    return ", ".join(f"{count} {tag}" for tag, count in tally(tags).items())
