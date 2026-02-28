from utils.llm_client import llm_summary

def run_meeting_summary(mtg):
    # Extract data from the arrays in your JSON
    kps = [kp.get("content") for kp in mtg.get("keyPoints", [])]
    aps = [ap.get("content") for ap in mtg.get("actionPoints", [])]
    
    prompt = f"""
    Meeting Title: {mtg.get('title')}
    Manual Summary: {mtg.get('projectSummary')}
    Key Points: {kps}
    Action Points: {aps}
    
    Task: Provide a technical AI summary of this meeting. 
    Focus on progress and blockers.
    """
    return llm_summary(prompt)