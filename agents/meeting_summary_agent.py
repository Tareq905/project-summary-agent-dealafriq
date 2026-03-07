from utils.llm_client import llm_summary
from rag.retriever import retrieve_context

def run_meeting_summary(mtg):
    # 1. Get meeting patterns and RAIDD indicators from RAG
    context = retrieve_context("meeting patterns RAIDD extraction indicators action points")
    
    prompt = f"""
    Rules: {context}
    
    Raw Meeting Data:
    Title: {mtg.get('title')}
    Project Summary (Manual): {mtg.get('projectSummary')}
    Key Points: {mtg.get('keyPoints')}
    Action Points: {mtg.get('actionPoints')}

    Task: Analyze this specific meeting and return a JSON object.
    - 'summary': Concise recap of the meeting purpose and outcome.
    - 'action_points': List tasks assigned during this meeting.
    - 'discussion_points': List topics debated or reviewed.
    - 'notes': Observations on meeting engagement or blockers mentioned.
    - 'raidd_flags': Identify Risks, Assumptions, Issues, Dependencies, Decisions specifically mentioned in this sync.
    """
    
    return llm_summary(prompt)