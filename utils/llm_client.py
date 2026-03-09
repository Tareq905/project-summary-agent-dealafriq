from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary(prompt: str):
    system_instruction = """
    You are an AI Project Intelligence Agent. You must return a valid JSON object.
    
    IMPORTANT RULE FOR RAIDD FLAGS:
    Do not provide short, single-line items. For every Risk, Assumption, Issue, Dependency, or Decision, provide a short paragraph explaining the 'WHY' and the potential impact on the project timeline or health.
    
    EXACT KEYS REQUIRED:
    - summary (string)
    - action_points (list of strings)
    - discussion_points (list of strings)
    - notes (string)
    - flag (string: "Red", "Amber", or "Green")
    - raidd_flags (object: lists of descriptive paragraphs)
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