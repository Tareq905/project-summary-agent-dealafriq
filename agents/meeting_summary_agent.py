from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_meeting_summary(mtg, transcript_list):
    """
    Generates intelligence matching the original architecture 
    but with the new visual formatting inside the summary field.
    """
    context = retrieve_context("CLIENT_SUMMARY_STYLE meeting patterns RAIDD extraction")
    
    transcript_text = ""
    if transcript_list:
        for t in transcript_list:
            speeches = t.get("parsedData", {}).get("speeches", [])
            transcript_text += " ".join([f"{s.get('speaker')}: {s.get('message')}" for s in speeches if s.get("message")])

    mtg_date = mtg.get('meetingDate') or mtg.get('createdAt') or "Unknown Date"

    prompt = f"""
    Rules & Style Guidelines:
    {context}
    
    MEETING DATA:
    Title: {mtg.get('title')}
    Date: {mtg_date}
    
    TRANSCRIPT:
    {transcript_text[:7000]} 

    TASK:
    Analyze the meeting and return a JSON object.
    
    CRITICAL INSTRUCTION FOR 'summary' FIELD:
    The 'summary' value must be a string formatted exactly as follows:
    Date: [Meeting Date]
    
    🔹 Overview
    [Summary text]
    
    🔹 Key Features (if applicable)
    [Bullet points]
    
    🔹 Key Discussions
    [Bullet points]
    
    🔹 Final Insight
    [One sentence]

    REQUIRED JSON ARCHITECTURE:
    {{
      "summary": "Formatted string with 🔹 icons",
      "agenda": {{
          "meetingTopics": ["string"],
          "coreDiscussionPoints": ["string"]
      }},
      "action_points": ["string"],
      "discussion_points": ["string"],
      "notes": "string",
      "raidd_flags": {{
          "risks": ["paragraph"],
          "assumptions": ["paragraph"],
          "issues": ["paragraph"],
          "dependencies": ["paragraph"],
          "decisions": ["paragraph"]
      }}
    }}
    """
    
    return llm_summary(prompt)