from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary(prompt: str):
    system_instruction = """
    You are an AI Project Intelligence Agent. You must return a valid JSON object.
    
    STRICT MODULAR RAIDD REQUIREMENT:
    Inside the 'raiddFlags' or 'raiddAnalysis' object, you must NOT return simple strings. 
    Every entry in those lists must be a structured object:
    {
      "category": "String",
      "status": "High | Medium | Low",
      "ai_summary": "A descriptive paragraph",
      "details": ["Specific evidence bullet 1", "Specific evidence bullet 2"]
    }
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
        return {"summary": "Error", "flag": "Unknown", "raiddFlags": {"risks":[], "issues":[], "dependencies":[], "decisions":[]}}