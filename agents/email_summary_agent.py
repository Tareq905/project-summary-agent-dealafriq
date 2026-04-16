# agents/email_summary_agent.py
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
    
    TASK 1: CLASSIFICATION (ARRAY)
    Identify ALL applicable categories that describe the email content and return them in the 'category' array:
    - 'Issue': Current problems, errors, or blockers happening NOW.
    - 'Risk': Potential future problems or uncertainties.
    - 'Dependency': Waiting for external input, approvals, or prerequisites.
    - 'Decision': Confirmed choices, approvals, or directions.
    - 'Assumption': Unvalidated expectations.
    - 'Informational': General updates with no specific RAIDD elements.

    TASK 2: EXTRACTION LOGIC
    - flag: "Red" if 'Issue' is in the category array. "Amber" if 'Risk' or 'Dependency' is present (and no Issues). "Green" otherwise.
    - summary: A brief summary of the email.
    - raiddAnalysis: Descriptive paragraphs for each RAIDD type.
    - sentiment: "positive", "negative", or "neutral".
    
    STRICT RULE: Every RAIDD entry MUST be a short paragraph explaining the 'WHY' and the 'IMPACT'.
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
        "category": ["string"],
        "flag": "Red | Amber | Green",
        "raiddAnalysis": {{
            "risks": ["paragraph"] or null,
            "assumptions": ["paragraph"] or null,
            "issues": ["paragraph"] or null,
            "dependencies": ["paragraph"] or null,
            "decisions": ["paragraph"] or null
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