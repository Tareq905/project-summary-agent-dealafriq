from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary(prompt: str):
    system_instruction = """
    You are an AI Project Intelligence Agent. You must return a valid JSON object with these EXACT keys:
    - summary (string)
    - action_points (list of strings)
    - discussion_points (list of strings)
    - notes (string)
    - flag (string: "Red", "Amber", or "Green")
    - raidd_flags (object: lists for risks, assumptions, issues, dependencies, decisions)
    """

    res = client.chat.completions.create(
        model="gpt-4o-mini",
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return json.loads(res.choices[0].message.content)