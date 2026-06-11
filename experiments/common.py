"""Shared helpers for all experiments: model, run folders, saving, reasoning.

Usage in a game script:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from common import make_model, new_run_dir, run_and_save
"""

import os
from datetime import datetime

from edsl import Model


def make_model():
    return Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)


def new_run_dir(results_root, suffix=None):
    """Create and return results/<timestamp>[_suffix]/ for this run."""
    name = datetime.now().strftime("%Y-%m-%d_%H-%M-%S") + (f"_{suffix}" if suffix else "")
    run_dir = os.path.join(results_root, name)
    os.makedirs(run_dir, exist_ok=True)
    return run_dir


def append_reasoning(results, run_dir, tag):
    """Append every result row's answer + reasoning to run-level REASONING.md."""
    cols = results.columns
    qnames = [c.split(".", 1)[1] for c in cols if c.startswith("answer.")]
    scen_fields = [
        c.split(".", 1)[1]
        for c in cols
        if c.startswith("scenario.") and c != "scenario.scenario_index"
    ]
    has_iter = "iteration.iteration" in cols

    sel = ["agent.agent_name"]
    if has_iter:
        sel.append("iteration.iteration")
    for q in qnames:
        sel.append(f"answer.{q}")
        if f"comment.{q}_comment" in cols:
            sel.append(f"comment.{q}_comment")
    sel += [f"scenario.{s}" for s in scen_fields]

    rows = results.select(*sel).to_dicts()
    lines = [f"\n## {tag}\n"]
    for row in rows:
        bits = []
        if has_iter:
            bits.append(f"rep {row.get('iteration')}")
        for s in scen_fields:  # truncate long fields (history, persona) in headers
            val = str(row.get(s)).replace("\n", " ")
            bits.append(f"{s}={val[:80]}{'...' if len(val) > 80 else ''}")
        ctx = ", ".join(bits)
        lines.append(f"### {row.get('agent_name', 'agent')}" + (f"  ({ctx})" if ctx else ""))
        for q in qnames:
            lines.append(f"- **{q} = {row.get(q)}**")
            reason = row.get(f"{q}_comment")
            if reason:
                lines.append(f"  - {reason}")
        lines.append("")

    with open(os.path.join(run_dir, "REASONING.md"), "a") as f:
        f.write("\n".join(lines))


def run_and_save(job, run_dir, tag, n=1, retries=2):
    """Run a job n times, save results 3 ways (.json.gz, .csv, coop link) + reasoning."""
    results = job.run(n=n)
    # A transient API failure leaves answer=None. Re-running is cheap: successful
    # answers come back from cache, only the failed ones are actually retried.
    for _ in range(retries):
        answer_cols = [c for c in results.columns if c.startswith("answer.")]
        if not any(None in results.select(c).to_list() for c in answer_cols):
            break
        print(f"[{tag}] got a None answer, retrying failed interviews...")
        results = job.run(n=n)

    stage_dir = os.path.join(run_dir, tag)
    os.makedirs(stage_dir, exist_ok=True)
    results.save(os.path.join(stage_dir, tag))
    results.to_csv(os.path.join(stage_dir, f"{tag}.csv"))

    try:
        url = results.push(visibility="unlisted")["url"]
    except Exception as e:
        url = f"(push failed: {e})"
    with open(os.path.join(stage_dir, "coop.txt"), "w") as f:
        f.write(f"url: {url}\n")

    append_reasoning(results, run_dir, tag)
    return results
