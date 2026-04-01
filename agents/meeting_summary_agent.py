from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_meeting_summary(mtg, transcript_list):
    """
    Extracts structured intelligence, including Agenda, from meeting data and transcripts.
    """
    # Retrieve RAIDD and Agenda extraction patterns from RAG
    context = retrieve_context("meeting patterns RAIDD extraction action points agenda topics")
    
    # Compile all speeches from the project transcripts into one block
    transcript_text = ""
    if transcript_list:
        for t in transcript_list:
            speeches = t.get("parsedData", {}).get("speeches", [])
            transcript_text += " ".join([f"{s.get('speaker')}: {s.get('message')}" for s in speeches if s.get("message")])

    prompt = f"""
    Rules & Patterns: {context}
    
    MEETING DATA:
    Title: {mtg.get('title')}
    Manual Summary: {mtg.get('projectSummary')}
    
    TRANSCRIPT (Conversation):
    {transcript_text[:7000]} 

    TASK:
    Analyze the meeting and return a JSON object with these EXACT keys:
    - flag: (Red/Yellow/Green)
    - summary: (A paragraph summarizing the meeting)
    - agenda: {{ "meetingTopics": ["pointwise list"], "coreDiscussionPoints": ["pointwise list"] }}
    - action_points: [List of strings]
    - discussion_points: [List of strings]
    - notes: (Short metadata or observations)
    - raidd_flags: {{ "risks": [], "assumptions": [], "issues": [], "dependencies": [], "decisions": [] }}

    Note: RAIDD items MUST be descriptive paragraphs.
    """
    
    return llm_summary(prompt)