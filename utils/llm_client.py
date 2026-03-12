from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary(prompt: str):
    """
    Standardizes intelligence into a structured JSON object.
    """
    system_instruction = """
    You are an AI Project Intelligence Agent. You must return a valid JSON object.
    
    REQUIRED JSON KEYS (Strictly follow this naming):
    - summary: A descriptive string (paragraph).
    - action_points: A LIST of strings.
    - discussion_points: A LIST of strings.
    - notes: A string.
    - flag: "Red", "Amber", or "Green".
    - raidd_flags: An object containing lists: { "risks": [], "assumptions": [], "issues": [], "dependencies": [], "decisions": [] }
    
    For RAIDD items, write short paragraphs explaining the "WHY".
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"LLM Error: {e}")
        return {
            "summary": "Error generating analysis",
            "action_points": [],
            "discussion_points": [],
            "notes": str(e),
            "flag": "Amber",
            "raidd_flags": {}
        }