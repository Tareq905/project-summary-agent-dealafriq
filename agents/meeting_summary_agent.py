from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_meeting_summary(mtg, transcript_list):
    """
    Extracts structured intelligence from meeting metadata and transcripts.
    """
    # 1. Retrieve RAIDD patterns and extraction rules from RAG
    context = retrieve_context("meeting patterns RAIDD extraction indicators action points")
    
    # 2. Compile all speeches from the project transcripts
    transcript_text = ""
    if transcript_list:
        for t in transcript_list:
            speeches = t.get("parsedData", {}).get("speeches", [])
            transcript_text += " ".join([s.get("message", "") for s in speeches if s.get("message")])

    # 3. Build the prompt
    prompt = f"""
    Governance Rules: {context}
    
    MEETING CONTEXT:
    Title: {mtg.get('title')}
    Manual Summary: {mtg.get('projectSummary')}
    
    TRANSCRIPT SPEECHES (Actual Conversation):
    {transcript_text[:6000]} 

    TASK:
    - Analyze the actual conversation recorded in the transcript.
    - Extract 'action_points' (Tasks assigned to individuals).
    - Extract 'discussion_points' (Key topics, debates, or reviews).
    - Identify any 'raidd_flags' specifically mentioned in the discussion.
    - You must decide the 'flag' for this meeting based on whether it was productive or revealed blockers.
    """
    
    return llm_summary(prompt)