# agents/email_summary_agent.py
import json
from openai import OpenAI
from config.settings import settings
from rag.retriever import retrieve_context

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def run_email_analysis(email_data, projects_context):
    rules_context = retrieve_context("EMAIL_RAIDD_DEFINITIONS EMAIL_FALSE_POSITIVES EMAIL_IMPLICIT_LANGUAGE")

    available_projects =[
        {"id": p.get("id"), "name": p.get("name"), "description": p.get("description")} 
        for p in projects_context
    ]

    # --- UPDATED PROMPT ---
    system_instruction = """
    You are an AI Email Analyzer for a Project Management Office.
    You must output a strictly valid JSON object.
    
    TASK 1: PROJECT MAPPING
    Attempt to match the email to a project in the 'Available Projects' list. 
    - If you find a match, output the project UUID.
    - If it discusses a project but you cannot find an exact match in the list, set 'projectId' to null.
    
    TASK 2: EXTRACTION LOGIC
    - If the email is a completely automated system notification (e.g., "Welcome to Outlook", "Security Alert", "Verify your email"), set 'summary' and all RAIDD fields to null.
    - If the email is a human business/work communication (even if you couldn't match the projectId), YOU MUST EXTRACT THE FOLLOWING:
        - summary: A brief summary of the email.
        - actionPoints: List of tasks, actions, or reviews requested.
        - decisionPoints: List of decisions made or proposed.
        - notes: Any general observations.
        - tasks: Any formal project tasks mentioned (e.g., "review the circumstances").
        - sentiment: "positive", "negative", or "neutral".
        - raiddAnalysis: Object containing descriptive paragraphs for risks, assumptions, issues, dependencies, and decisions based on the RAG rules. If a specific RAIDD field is not present, set that specific field to null.
    """

    user_prompt = f"""
    RAG RULES:
    {rules_context}

    AVAILABLE PROJECTS:
    {json.dumps(available_projects)}

    EMAIL TO ANALYZE:
    Subject: {email_data.get('subject')}
    Sender: {email_data.get('senderEmail')}
    Body: {email_data.get('body')}

    RETURN EXPECTED JSON FORMAT:
    {{
        "emailId": "{email_data.get('id')}",
        "projectId": "uuid or null",
        "summary": "string or null",
        "actionPoints": ["string"] or null,
        "decisionPoints": ["string"] or null,
        "notes": "string or null",
        "tasks":["string"] or null,
        "sentiment": "string or null",
        "raiddAnalysis": {{
            "risks": ["paragraph"] or null,
            "assumptions": ["paragraph"] or null,
            "issues": ["paragraph"] or null,
            "dependencies": ["paragraph"] or null,
            "decisions": ["paragraph"] or null
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