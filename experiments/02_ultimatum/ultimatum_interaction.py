"""Ultimatum game #2 — INTERACTION method.

Two agents, two stages: the proposer picks a real offer, then that exact offer is
fed to the responder. EDSL runs questions independently, so we wire stage 1's
output into stage 2 ourselves.
"""

from edsl import QuestionNumerical, QuestionYesNo, Agent, Model, Scenario

POT = 100
model = Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)

proposer = Agent(name="proposer")
responder = Agent(name="responder")

q_offer = QuestionNumerical(
    question_name="offer",
    question_text=(
        "You are splitting $100 with another person. You offer them some amount and "
        "keep the rest. If they REJECT, you both get $0. How much do you offer?"
    ),
)
q_accept = QuestionYesNo(
    question_name="accept",
    question_text=(
        "Someone splitting $100 offers you ${{ scenario.offer }}. "
        "If you accept, you keep it. If you reject, you BOTH get $0. Do you accept?"
    ),
)

# Stage 1: proposer picks the offer
offer = q_offer.by(proposer).by(model).run().select("offer").to_list()[0]
print(f"Proposer offered: ${offer}")

# Stage 2: feed the REAL offer to the responder
accepted = (
    q_accept.by(Scenario({"offer": offer})).by(responder).by(model)
    .run().select("accept").to_list()[0]
)
print(f"Responder: {accepted}")

if accepted == "Yes":
    print(f"Deal: proposer keeps ${POT - offer}, responder gets ${offer}")
else:
    print("Rejected: both get $0")
