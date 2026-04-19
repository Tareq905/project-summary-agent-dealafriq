import json
from openai import OpenAI
from config.settings import settings
from rag.retriever import retrieve_context

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def run_email_analysis(email_data, projects_context):
    rules_context = retrieve_context("EMAIL_RAIDD_DEFINITIONS EMAIL_FALSE_POSITIVES EMAIL_IMPLICIT_LANGUAGE")

    system_instruction = """
    You are an AI Email Analyzer for a Project Management Office.
    You must output a strictly valid JSON object.
    
    TASK: Extract RAIDD items. If the email contains a Risk, Issue, Dependency, Decision, or Assumption, you MUST use the following modular structure:
    {
      "category": "String",
      "status": "High | Medium | Low",
      "ai_summary": "One paragraph explaining the impact",
      "details": ["Bullet point 1", "Bullet point 2"]
    }

    RULE: If a category (e.g., risks) has no items, return null. Do not return [].
    """

    user_prompt = f"""
    RAG RULES: {rules_context}

    EMAIL TO ANALYZE:
    Subject: {email_data.get('subject')}
    Body: {email_data.get('body')}

    RETURN EXPECTED JSON FORMAT:
    {{
        "emailId": "{email_data.get('id')}",
        "summary": "string",
        "category": ["Issue", "Risk", "..."],
        "flag": "Red | Amber | Green",
        "raiddAnalysis": {{
            "risks": [object] or null,
            "assumptions": [object] or null,
            "issues": [object] or null,
            "dependencies": [object] or null,
            "decisions": [object] or null
        }},
        "sentiment": "string"
    }}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": user_prompt}
            ]
        )
        return json.loads(res.choices[0].message.content)
    except Exception as e:
        print(f"LLM Error on email {email_data.get('id')}: {e}")
        return None