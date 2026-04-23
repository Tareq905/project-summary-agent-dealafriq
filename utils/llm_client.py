from openai import OpenAI
from config.settings import settings
import json

client = OpenAI(api_key=settings.OPENAI_API_KEY)

def llm_summary(prompt: str):
    """
    Standardized LLM Client for all Agents.
    Forces JSON output and strictly enforces type schema for Health and RAIDD flags.
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
            # Ensures the model output is always a parsable JSON dictionary
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user", "content": prompt}
            ]
        )
        
        # Parse the JSON string into a Python Dictionary
        result = json.loads(res.choices[0].message.content)
        
        # Post-processing fix: Ensure health_label didn't accidentally come back as a list
        if "health_label" in result and isinstance(result["health_label"], list):
            result["health_label"] = result["health_label"][0] if len(result["health_label"]) > 0 else "Bad"
            
        return result

    except Exception as e:
        print(f"LLM Critical Error: {e}")
        # Standardized fallback to prevent Orchestrator crashes
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