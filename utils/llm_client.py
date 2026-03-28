from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary(prompt: str):
    """
    Standardizes intelligence into a structured JSON object.
    The AI Agent defines the keys based on the specific analysis type.
    """
    system_instruction = """
    You are an AI Project Intelligence Agent. You must return a valid JSON object.
    
    STRICT RULES:
    1. For 'raidd_flags', each category must be a LIST OF STRINGS.
    2. Each string in those lists must be a short paragraph explaining 'WHY' and 'IMPACT'.
    3. NEVER return objects/dictionaries inside RAIDD lists.
    4. You must decide the 'flag' as "Red", "Amber", or "Green" based on the data.
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            # Forces the model to output a valid JSON object
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
            "summary": "Error analyzing data.",
            "flag": "Unknown",
            "notes": str(e)
        }