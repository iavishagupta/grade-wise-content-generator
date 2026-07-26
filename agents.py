from openai import OpenAI
import os, json

from dotenv import load_dotenv
load_dotenv()

llm = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

def _invoke(system: str, user: str):
    response = llm.responses.create(
        model=os.getenv("OPENAI_MODEL_NAME"),
        instructions=system,
        input=[{"role": "user", "content": user},]
    )

    text = response.output[0].content[0].text
    if text.startswith('`'):
        text = text.strip('`')
        # text = text.removeprefix('json')
        text = text.split("json", 1)[-1] if text.startswith("json") else text

    return json.loads(text)

class GeneratorAgent:

    system = (
        "You are an educational content generator. Given a grade and topic, "
        "produce an explanation and 3 multiple-choice questions. "
        "Language complexity MUST match the grade level. "
        "Respond ONLY with valid JSON, no preamble, no markdown fences, "
        "in exactly this shape:\n"
        '{"explanation": "...", "mcqs": [{"question": "...", '
        '"options": ["A","B","C","D"], "answer": "B"}]}'
    )

    def invoke(self, grade: int, topic: str, feedback: list[str] | None = None) -> dict:
        user = f"Grade: {grade}\nTopic:{topic}"

        if feedback:
            user += (
                "\n\nThe previous draft was reviewed and marked FAIL. "
                "Address this feedback in the new draft:\n- "
                + "\n- ".join(feedback)
            )

        return _invoke(system=self.system, user=user)

class ReviewerAgent :
    system = (
        "You are a strict educational content reviewer. Evaluate the given "
        "content JSON for: age appropriateness, conceptual correctness, and "
        "clarity. Respond ONLY with valid JSON, no preamble, no markdown "
        "fences, in exactly this shape:\n"
        '{"status": "pass" | "fail", "feedback": ["...", "..."]}\n'
        "If everything is acceptable, status is 'pass' and feedback can be "
        "an empty list or minor notes."
    )

    def invoke(self, grade: int, topic: str, content: dict) -> dict:
        user = (
            f"Grade: {grade}\nTopic: {topic}\n\n"
            f"Content to review:\n{json.dumps(content, indent=2)}"
        )
        return _invoke(system=self.system, user=user)

def pipeline(grade: int, topic: str) -> dict:
    agent_generator = GeneratorAgent()
    agent_reviewer = ReviewerAgent()

    draft = agent_generator.invoke(grade=grade, topic=topic)
    review = agent_reviewer.invoke(grade=grade, topic=topic, content=draft)

    refined = None
    refined_review = None

    if review.get("status") == "fail":
        refined = agent_generator.invoke(grade=grade, topic=topic, feedback=review)
        refined_review = agent_reviewer.invoke(grade=grade, topic=topic, content=refined)

    return {
        "draft":draft,
        "review":review,
        "refined_draft":refined,
        "refined_draft_review":refined_review,
    }
