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
    
    1. CATEGORY:
    Analyze the email and select ALL applicable labels from this list ONLY: 
    "Issue", "Risk", "Dependency", "Decision", "Assumption", "Informational".

    2. RAIDD ANALYSIS:
    - Each field (risks, issues, decisions, assumptions, dependencies) must be a LIST OF STRINGS.
    - Each string must be a descriptive paragraph explaining the impact.
    - If a category has no items, return null.
    """

    user_prompt = f"""
    RAG RULES: {rules_context}
    EMAIL: Subject: {email_data.get('subject')} | Body: {email_data.get('body')}

    RETURN THIS EXACT JSON STRUCTURE:
    {{
        "flag": "Red | Amber | Green",
        "emailId": "{email_data.get('id')}",
        "summary": "string",
        "category": ["Issue", "Risk", "Dependency", "Decision", "Assumption"],
        "sentiment": "positive | negative | neutral",
        "raiddAnalysis": {{
            "risks": ["paragraph string"] or null,
            "issues": ["paragraph string"] or null,
            "decisions": ["paragraph string"] or null,
            "assumptions": ["paragraph string"] or null,
            "dependencies": ["paragraph string"] or null
        }}
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