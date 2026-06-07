"""price_audit.py — audit EDSL model pricing against the canonical price list.

For every working model, run the smallest possible question once (all models are
batched into a SINGLE remote job, so this is fast and cheap), then compare three
price sources per model and report any disagreement:

  canonical : Coop.fetch_working_models()  usd_per_1M_*        (source of truth)
  local     : PriceManager.get_price()      local price table  (used by estimates)
  applied   : the price the server actually billed for this run (raw_model_response)

The "deepseek price bug" was a disagreement between these sources, so this is the
exact check to confirm it's fixed across the board.

It also reads the credit balance before/after the run and verifies that the
credits actually deducted on the panel match the sum of the per-model costs EDSL
reports (cost_usd * 10000 = minicredits, since 1 credit = $0.01 = 100 minicredits).

Usage:
    .venv/bin/python experiments/price_audit.py                 # all working models
    .venv/bin/python experiments/price_audit.py --limit 10      # first N (smoke test)
    .venv/bin/python experiments/price_audit.py --service deepseek
"""

import argparse
import csv
import math
import os

from edsl import QuestionFreeText, Model, ModelList, Coop
from edsl.language_models.price_manager import PriceManager

QUESTION = "What is the capital of Turkey? Answer in one word."
TOL_REL = 1e-4          # relative tolerance for price comparison
OUT_CSV = os.path.join(os.path.dirname(__file__), "price_audit_results.csv")


def close(a, b):
    """True if two prices agree (within tolerance). None on either side -> not comparable."""
    if a is None or b is None:
        return None
    return math.isclose(a, b, rel_tol=TOL_REL, abs_tol=1e-9)


def local_prices(pm, service, model):
    """(input, output) price per 1M from EDSL's local PriceManager table, or (None, None)."""
    try:
        p = pm.get_price(service, model)
        if not p:
            return None, None
        return (
            p.get("input", {}).get("service_stated_token_price"),
            p.get("output", {}).get("service_stated_token_price"),
        )
    except Exception:
        return None, None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=None, help="only the first N models")
    ap.add_argument("--service", default=None, help="only models from this service")
    args = ap.parse_args()

    coop = Coop()
    pm = PriceManager()

    # --- canonical reference list -------------------------------------------------
    canonical = coop.fetch_working_models()
    canonical = [m for m in canonical if m.get("works_with_text")]
    if args.service:
        canonical = [m for m in canonical if m["service"] == args.service]
    if args.limit:
        canonical = canonical[: args.limit]

    ref = {
        (m["service"], m["model"]): (
            m.get("usd_per_1M_input_tokens"),
            m.get("usd_per_1M_output_tokens"),
        )
        for m in canonical
    }
    print(f"Auditing {len(canonical)} models with: {QUESTION!r}\n")

    # --- balance before -----------------------------------------------------------
    bal_before = coop.get_balance()
    mini_before = bal_before["minicredits"]
    print(f"Balance before: {bal_before['balance']} credits ({mini_before} minicredits)\n")

    # --- build models, skipping any whose provider SDK is not installed -----------
    buildable, skipped_sdk = [], set()
    for m in canonical:
        try:
            buildable.append(Model(m["model"], service_name=m["service"]))
        except Exception as e:
            skipped_sdk.add((m["service"], m["model"]))
            print(f"  skip (no SDK): {m['service']}/{m['model']} [{type(e).__name__}]")
    if skipped_sdk:
        print(f"\n{len(skipped_sdk)} model(s) skipped (provider SDK not installed); "
              f"they still get the offline canonical-vs-local check.\n")

    # --- one batched job over every buildable model -------------------------------
    q = QuestionFreeText(question_name="cap", question_text=QUESTION)
    results = q.by(ModelList(buildable)).run(disable_remote_inference=False)

    rows = results.select(
        "model.model",
        "model.inference_service",
        "raw_model_response.cap_cost",
        "raw_model_response.cap_input_tokens",
        "raw_model_response.cap_output_tokens",
        "raw_model_response.cap_thinking_tokens",
        "raw_model_response.cap_input_price_per_million_tokens",
        "raw_model_response.cap_output_price_per_million_tokens",
    ).to_dicts()

    got = {(r["inference_service"], r["model"]): r for r in rows}

    # --- balance after + authoritative EP job cost --------------------------------
    bal_after = coop.get_balance()
    mini_after = bal_after["minicredits"]
    try:
        job = coop.remote_inference_get(results.job_uuid)
        ep = job["latest_job_run_details"]
        ep_credits = ep.get("cost_credits")  # what EP actually billed for this job
        ep_usd = ep.get("cost_usd")
    except Exception as e:
        ep_credits = ep_usd = None
        print(f"(could not fetch authoritative job cost: {e})")

    # --- compare ------------------------------------------------------------------
    records = []
    mismatches = []
    errored = []
    total_cost_usd = 0.0

    for (service, model), (can_in, can_out) in ref.items():
        r = got.get((service, model))
        loc_in, loc_out = local_prices(pm, service, model)

        if r is None:
            no_sdk = (service, model) in skipped_sdk
            errored.append((service, model))
            # offline table check still applies even without an empirical run
            tbl_flags = []
            if close(loc_in, can_in) is False:
                tbl_flags.append(f"local_in {loc_in}!=canon {can_in}")
            if close(loc_out, can_out) is False:
                tbl_flags.append(f"local_out {loc_out}!=canon {can_out}")
            rec = {
                "service": service, "model": model,
                "status": "NO_SDK" if no_sdk else "NO_RESULT",
                "cost_usd": None, "in_tok": None, "out_tok": None,
                "applied_in": None, "applied_out": None,
                "canon_in": can_in, "canon_out": can_out,
                "local_in": loc_in, "local_out": loc_out,
                "flags": ("no SDK; " if no_sdk else "errored; ") + "; ".join(tbl_flags),
            }
            records.append(rec)
            if tbl_flags:
                mismatches.append(rec)
            continue

        app_in = r["cap_input_price_per_million_tokens"]
        app_out = r["cap_output_price_per_million_tokens"]
        cost = r["cap_cost"]
        in_tok = r["cap_input_tokens"] or 0
        out_tok = r["cap_output_tokens"] or 0
        think_tok = r["cap_thinking_tokens"] or 0
        if cost is not None:
            total_cost_usd += cost

        flags = []
        # 1) applied (server billing) vs canonical reference
        if close(app_in, can_in) is False:
            flags.append(f"applied_in {app_in}!=canon {can_in}")
        if close(app_out, can_out) is False:
            flags.append(f"applied_out {app_out}!=canon {can_out}")
        # 2) local estimate table vs canonical reference
        if close(loc_in, can_in) is False:
            flags.append(f"local_in {loc_in}!=canon {can_in}")
        if close(loc_out, can_out) is False:
            flags.append(f"local_out {loc_out}!=canon {can_out}")
        # 3) cost self-consistency: cost == (in*app_in + (out+think)*app_out)/1M
        #    thinking tokens are billed at the output rate, so they must be included
        if cost is not None and app_in is not None and app_out is not None:
            recomputed = (in_tok * app_in + (out_tok + think_tok) * app_out) / 1_000_000
            if not math.isclose(cost, recomputed, rel_tol=1e-3, abs_tol=1e-12):
                flags.append(f"cost {cost:.3e}!=recomputed {recomputed:.3e} "
                             f"(in={in_tok},out={out_tok},think={think_tok})")

        rec = {
            "service": service, "model": model,
            "status": "OK" if not flags else "MISMATCH",
            "cost_usd": cost, "in_tok": in_tok, "out_tok": out_tok,
            "applied_in": app_in, "applied_out": app_out,
            "canon_in": can_in, "canon_out": can_out,
            "local_in": loc_in, "local_out": loc_out,
            "flags": "; ".join(flags),
        }
        records.append(rec)
        if flags:
            mismatches.append(rec)

    # --- write full detail to CSV -------------------------------------------------
    with open(OUT_CSV, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(records[0].keys()))
        w.writeheader()
        w.writerows(records)

    # --- report -------------------------------------------------------------------
    ok = sum(1 for r in records if r["status"] == "OK")
    print(f"\n{'='*70}\nRESULTS")
    print(f"{'='*70}")
    print(f"models checked   : {len(records)}")
    print(f"  OK             : {ok}")
    print(f"  MISMATCH       : {len(mismatches)}")
    print(f"  errored/skipped: {len(errored)}")
    print(f"full detail CSV  : {OUT_CSV}")

    # credit reconciliation: authoritative EP job charge vs sum of per-result cap_cost
    edsl_credits = total_cost_usd * 100  # 1 credit = $0.01
    print(f"\n--- credit reconciliation (authoritative EP job cost vs EDSL results) ---")
    print(f"EDSL sum of cap_cost : {edsl_credits:8.2f} credits (${total_cost_usd:.5f})")
    if ep_credits is not None:
        print(f"EP actually charged  : {ep_credits:8.2f} credits (${ep_usd:.5f})   [job {results.job_uuid[:8]}]")
        if edsl_credits > 0:
            ratio = ep_credits / edsl_credits
            flag = "  <-- EP >> EDSL: investigate!" if ratio > 1.1 else "  (consistent)"
            print(f"ratio EP / EDSL      : {ratio:8.2f}x{flag}")
    # secondary: raw balance delta (coarse: integer-minicredit resolution, rounds tiny jobs to 0)
    print(f"balance delta (coarse): {mini_before - mini_after} minicredits "
          f"({bal_before['balance']} -> {bal_after['balance']} credits)")

    if mismatches:
        print(f"\n{'='*70}\nPRICE MISMATCHES ({len(mismatches)})\n{'='*70}")
        for r in mismatches:
            print(f"\n  {r['service']}/{r['model']}")
            print(f"    applied in/out : {r['applied_in']} / {r['applied_out']}")
            print(f"    canonical      : {r['canon_in']} / {r['canon_out']}")
            print(f"    local table    : {r['local_in']} / {r['local_out']}")
            print(f"    -> {r['flags']}")
    else:
        print("\n✅ No price mismatches: applied == canonical == local for every model.")

    if errored:
        print(f"\nErrored/skipped ({len(errored)}): "
              + ", ".join(f"{s}/{m}" for s, m in errored))


if __name__ == "__main__":
    main()
