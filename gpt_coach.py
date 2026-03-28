import json
import os

from config import OPENAI_MODEL


class GPTCoach:
    def __init__(self):
        self.model = os.getenv("OPENAI_MODEL", OPENAI_MODEL)
        self.client = None

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return

        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=api_key)
        except Exception:
            self.client = None

    def enabled(self):
        return self.client is not None

    def generate_report(self, analysis):
        if not self.enabled():
            return None

        compact_data = {
            "score": analysis.get("score"),
            "rating_text": analysis.get("rating_text"),
            "batsman_hand": analysis.get("batsman_hand"),
            "stance_style": analysis.get("stance_style"),
            "corrections": analysis.get("corrections"),
            "metrics": analysis.get("metrics"),
        }

        prompt = f"""
You are a cricket batting stance coach.

Using the JSON below, write:
1. A short overall assessment
2. The top 3 corrections in priority order
3. One practical drill the player can do
4. Keep the tone simple and encouraging
5. Max 180 words

JSON:
{json.dumps(compact_data, indent=2)}
"""

        try:
            response = self.client.responses.create(
                model=self.model,
                input=prompt,
                max_output_tokens=300
            )

            text = getattr(response, "output_text", None)
            if text:
                return text.strip()

            return "AI report generated, but no output text was returned."
        except Exception as e:
            return f"AI report unavailable: {e}"
