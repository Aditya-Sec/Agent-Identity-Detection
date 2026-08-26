# Agent vs. Human: Can Your SOC Tell a Compromised AI Agent From a Compromised Human?

**Status:** Week 1 — simulator + baseline built, real dataset validation next.

## Research question

When an AI agent's credentials are compromised, does it produce a behaviorally
distinguishable signature from a compromised human account — and can a
lightweight classifier detect it faster than identity-agnostic SIEM rules do?

## Why this matters

Most SIEM/IAM alerting was tuned on human behavioral baselines (login times,
geolocation, click cadence). AI agents are increasingly given real credentials
and tool access, but are commonly treated as generic service accounts with no
dedicated identity or behavioral model. Nobody has published a clean
before/after comparison of detection performance across the two identity
types.

## Hypothesis

Agent identities produce structurally different telemetry than human
identities, even under compromise: tighter timing regularity, higher
action-call density, near-zero idle time, and batch-style tool invocation.
A detector trained on these features should out-perform generic,
identity-agnostic anomaly rules at flagging agent-specific compromise.

## Method

1. **Simulate** four session types: human-normal, human-compromised,
   agent-normal, agent-compromised (`src/simulator.py`).
2. **Baseline**: run simple identity-agnostic SIEM-style threshold rules
   against all sessions (`src/baseline_rules.py`) — this represents "what
   current workflows already catch."
3. **Classifier**: train a lightweight logistic regression on 6 behavioral
   features (`src/classifier.py`).
4. **Evaluate** both approaches, broken out separately by identity type
   (`src/evaluate.py`) — the interesting result is the *gap* between human
   and agent detection rates, not the absolute numbers.

## Features used

| Feature | Description |
|---|---|
| `session_duration` | Total session length (seconds) |
| `inter_action_variance` | Variance in time between consecutive actions |
| `actions_per_session` | Count of discrete actions/tool calls |
| `batch_size_mean` | Average number of actions fired within a 2s window |
| `idle_ratio` | Fraction of session with no activity |
| `tool_diversity` | Number of distinct tools/APIs called |

## Quickstart

```bash
pip install -r requirements.txt
python src/simulator.py          # generates data/sessions.csv
python src/evaluate.py           # trains classifier, compares vs baseline,
                                  # writes results/metrics.json + confusion matrices
```

## Known limitation (read before citing results)

The current dataset is **synthetic** — agent-compromise sessions are generated
from a behavioral model, not from a real prompt-injection attack against a
live tool-calling agent. Treat early results as a proof-of-concept for the
method, not a final finding. Next step: replace the synthetic
agent-compromised generator with logs from an actual injected LangChain/MCP
agent (see `src/simulator.py::TODO`).

## Roadmap

- [x] Synthetic session simulator
- [x] Baseline rule-based detector
- [x] Lightweight classifier + evaluation
- [ ] Replace synthetic agent-compromise data with real injected-agent logs
- [ ] Add multilingual/multimodal session variants
- [ ] Write up findings as an article + local meetup talk

## License

MIT
