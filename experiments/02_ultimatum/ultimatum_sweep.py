"""Ultimatum game #1 — SWEEP method.

The responder answers many hypothetical offers ($0, $5, ... $50) via a ScenarioList.
This recovers the acceptance curve: at what offer does the agent start rejecting?
No real proposer here — offers are a fixed grid.
"""

from edsl import QuestionYesNo, Agent, Model, Scenario, ScenarioList

model = Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)

q_accept = QuestionYesNo(
    question_name="accept",
    question_text=(
        "Someone splitting $100 offers you ${{ scenario.offer }}. "
        "If you accept, you keep it. If you reject, you BOTH get $0. "
        "Do you accept?"
    ),
)

# one Scenario per offer amount -> same question asked once per offer
offers = ScenarioList([Scenario({"offer": x}) for x in range(0, 55, 5)])

results = q_accept.by(offers).by(Agent(name="responder")).by(model).run()
results.select("offer", "accept").print()
