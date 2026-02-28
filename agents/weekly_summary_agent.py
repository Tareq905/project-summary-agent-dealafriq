from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_weekly_summary(project, logs):
    # 1. Extract Transcripts (The richest source of data)
    transcripts = project.get("transcripts", [])
    transcript_content = ""
    if transcripts:
        # Get speeches from the most recent transcript
        speeches = transcripts[0].get("parsedData", {}).get("speeches", [])
        transcript_content = " ".join([s.get("message") or "" for s in speeches])

    # 2. Extract Meeting Key/Action Points
    meetings = project.get("meetings", [])
    meeting_details = ""
    for mtg in meetings:
        kps = [kp.get("content") for kp in mtg.get("keyPoints", [])]
        aps = [ap.get("content") for ap in mtg.get("actionPoints", [])]
        meeting_details += f"Meeting: {mtg.get('title')}. Points: {kps}. Actions: {aps}\n"

    # 3. Use Activity Logs as supplementary info
    activity_text = str(logs)

    prompt = f"""
    Project Name: {project.get('name')}
    
    PRIMARY SOURCE (Transcripts): {transcript_content[:4000]} 
    SECONDARY SOURCE (Meeting Points): {meeting_details}
    SUPPLEMENTARY SOURCE (Logs): {activity_text}

    TASK:
    - Identify the LATEST meeting or discussion.
    - Provide a concise Weekly Summary of what was discussed and what the next steps are.
    - If Transcripts are available, use them as the primary source of truth.
    - DO NOT say 'no data available' if there is any text in the sources above.
    """
    
    return llm_summary(prompt)