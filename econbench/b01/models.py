"""Model lineup for b1.

deepseek-v4-flash is EXCLUDED: Expected Parrot billed it at ~1000x the listed
price (real charge, confirmed on the credits panel — see memory/cost-control).
Re-add only after experiments/price_audit.py shows all three price sources
agree for it. gpt-oss-120b on deep_infra is the audited-safe workhorse.
"""

from edsl import Model

# rough measured cost per interview for gating estimates (USD, generous)
EST_COST_PER_CALL = {"openai/gpt-oss-120b": 0.0008}

MODELS = {
    "gpt-oss-120b": lambda: Model("openai/gpt-oss-120b", service_name="deep_infra",
                                  temperature=1, max_tokens=8192),
}
