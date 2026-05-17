from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def llm_summary(prompt: str):
    """
    Standardized LLM Client for Project / Document / Weekly agents.
    Forces JSON output and strictly enforces type schema for Health and RAIDD flags.
    Used by: project_summary_agent, document_summary_agent, weekly_summary_agent
    """
    system_instruction = """
    You are an expert AI Project Management Intelligence Agent. 
    Your task is to analyze raw data and return a strictly valid JSON object.
    
    STRICT TYPE RULES:
    1. REQUIRED KEYS: "summary", "weekly_summary", "flag", "health_label", "action_points", "discussion_points", "notes", "raidd_flags".
    2. "health_label": This MUST be a single STRING (e.g., "Excellent", "Good", or "Bad"). Do NOT return a list or array.
    3. "raidd_flags": Every category (risks, issues, etc.) MUST be a LIST OF STRINGS. Each string must be a descriptive paragraph.
    4. "summary": MUST include 🔹 icons and use professional executive language.

    LOGIC HIERARCHY:
    - Project health must be analyzed based on Tasks (Dates and Completion). 
    - If no tasks exist, analyze based on Milestones.
    - If neither exists, analyze based on Timeline progress.

    DATA INTEGRITY:
    - Do not hallucinate. 
    - If a required list field has no data, return an empty list [].
    - Ensure all JSON keys are lowercase and match the requested schema exactly.
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

        result = json.loads(res.choices[0].message.content)

        # Post-processing fix: Ensure health_label didn't accidentally come back as a list
        if "health_label" in result and isinstance(result["health_label"], list):
            result["health_label"] = result["health_label"][0] if result["health_label"] else "Bad"

        return result

    except Exception as e:
        print(f"LLM Critical Error: {e}")
        return {
            "summary": "Technical error: AI analysis currently unavailable.",
            "weekly_summary": "Status unavailable due to a technical error.",
            "flag": "Unknown",
            "health_label": "Bad",
            "action_points": [],
            "discussion_points": [],
            "notes": "Error during LLM processing.",
            "raidd_flags": {
                "risks": [],
                "issues": [],
                "dependencies": [],
                "decisions": [],
                "assumptions": []
            }
        }


def llm_meeting_summary(prompt: str):
    """
    Dedicated LLM Client for Meeting Summary Agent ONLY.
    Does NOT force RAIDD population or health_label.
    Only extracts what is genuinely present in the meeting data.
    Used by: meeting_summary_agent
    """
    system_instruction = """
    You are an expert AI Meeting Intelligence Agent.
    Your task is to analyze meeting data and return a strictly valid JSON object.

    STRICT TYPE RULES:
    1. "aiMeetingSummary": Always a string. Write from available data only.
    2. "agenda": String or null. Only populate if agenda content exists in the data.
    3. "notes": String or null. Only populate if real notes exist in the data.
    4. "keyPoints": List of strings. Only extract from real data. Return [] if nothing available.
    5. "actionPoints": List of strings. Only extract from real data. Return [] if nothing available.
    6. "raidd_flags": Each category MUST be a list of strings.
       Only populate if real evidence exists in the meeting data.
       Return empty lists [] if no genuine RAIDD items are found.

    DATA INTEGRITY:
    - Do NOT hallucinate, infer, or invent content that is not present in the input.
    - Do NOT treat the absence of data as a RAIDD flag.
    - Do NOT fabricate discussion points, action items, or risks.
    - If a field has no real data, return null (for strings) or [] (for lists).
    - Ensure all JSON keys match the requested schema exactly.
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

        result = json.loads(res.choices[0].message.content)
        return result

    except Exception as e:
        print(f"LLM Meeting Summary Error: {e}")
        return {
            "aiMeetingSummary": "Technical error: Meeting analysis currently unavailable.",
            "agenda": None,
            "notes": None,
            "keyPoints": [],
            "actionPoints": [],
            "raidd_flags": {
                "risks": [],
                "issues": [],
                "dependencies": [],
                "decisions": [],
                "assumptions": []
            }
        }