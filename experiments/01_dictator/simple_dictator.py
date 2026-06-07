"""Simplest possible dictator game: one agent decides how much of $100 to give."""

from edsl import QuestionNumerical, Agent, Model

model = Model("openai/gpt-oss-120b", service_name="deep_infra", temperature=1)

q = QuestionNumerical(
    question_name="give",
    question_text=(
        "You have $100. You can give any amount to an anonymous other person who "
        "must accept whatever you give (they have no say). How much do you give?"
    ),
)

results = q.by(Agent(name="dictator")).by(model).run()
results.select("give").print()
