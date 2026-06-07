# Models for experiments

Curated shortlist of models runnable via EDSL → Expected Parrot remote inference.
Prices are **USD per 1,000,000 tokens** (input / output). Source:
`Coop.fetch_working_models()`, fetched 2026-05-29. (233 models exist total; this
is the useful subset.)

Usage in EDSL:

```python
from edsl import Model
m = Model("gpt-4o-mini")          # service auto-resolved
m = Model("claude-haiku-4-5-20251001", service_name="anthropic")  # if ambiguous
```

Cost intuition: EP credits are **$0.01 each** (you have ~2500 ≈ $25). A small
survey (a handful of questions × a few agents) on a cheap model costs well under
a cent.

---

## Tier 1 — Ultra-cheap (large fan-outs, many agents, smoke tests)

| Model | Service | In $/1M | Out $/1M | img |
|-------|---------|--------:|---------:|:---:|
| `meta-llama/Meta-Llama-3.1-8B-Instruct-Turbo` | deep_infra | $0.02 | $0.03 | |
| `llama-3.1-8b-instant` | groq | $0.05 | $0.08 | |
| `gpt-5-nano` | openai | $0.05 | $0.40 | ✓ |
| `gemini-2.0-flash-lite` | google | $0.08 | $0.30 | ✓ |

## Tier 2 — Cheap workhorses (sensible default for most experiments)

| Model | Service | In $/1M | Out $/1M | img |
|-------|---------|--------:|---------:|:---:|
| `gemini-2.0-flash` | google | $0.10 | $0.40 | ✓ |
| `deepseek-v4-flash` | deepseek | $0.14 | $0.28 | |
| `gpt-4o-mini` | openai | $0.15 | $0.60 | ✓ |
| `gpt-5-mini` | openai | $0.25 | $2.00 | ✓ |
| `gemini-2.5-flash` | google | $0.30 | $2.50 | ✓ |
| `gpt-4.1-mini` | openai | $0.40 | $1.60 | ✓ |

## Tier 3 — Strong mid-tier (better reasoning, still affordable)

| Model | Service | In $/1M | Out $/1M | img |
|-------|---------|--------:|---------:|:---:|
| `llama-3.3-70b-versatile` | groq | $0.59 | $0.79 | |
| `claude-haiku-4-5-20251001` | anthropic | $1.00 | $5.00 | ✓ |
| `o4-mini` | openai | $1.10 | $4.40 | ✓ |
| `gemini-2.5-pro` | google | $1.25 | $10.00 | ✓ |
| `deepseek-v4-pro` | deepseek | $1.74 | $3.48 | |

## Tier 4 — Frontier (final runs, hardest reasoning, quality benchmarks)

| Model | Service | In $/1M | Out $/1M | img |
|-------|---------|--------:|---------:|:---:|
| `gpt-5` | openai | $1.25 | $10.00 | ✓ |
| `gpt-5.2` | openai | $1.25 | $10.00 | ✓ |
| `gpt-4o` | openai | $2.50 | $10.00 | ✓ |
| `claude-sonnet-4-6` | anthropic | $3.00 | $15.00 | ✓ |
| `grok-4.3` | xai | $5.00 | $25.00 | ✓ |
| `gpt-5.5` | openai | $5.00 | $30.00 | ✓ |
| `claude-opus-4-8` | anthropic | $15.00 | $75.00 | ✓ |

---

**Notes**

- `img ✓` = accepts image input (multimodal). Blank = text-only.
- `openai` also exists as a parallel `openai_v2` service with the same IDs/prices — use plain `openai` unless you have a reason not to.
- Perplexity `sonar*` models ($1–$3 in) are search-grounded — useful only if you want live web context in answers.
- To refresh prices later: `from edsl import Coop; Coop().fetch_working_models()`.
