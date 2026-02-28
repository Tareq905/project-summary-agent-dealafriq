from utils.llm_client import llm_summary

def run_weekly_summary(project, logs):
    # Use the 'transcripts' field from your API response
    transcripts = project.get("transcripts", [])
    transcript_text = ""
    if transcripts:
        # Get the speeches from the latest transcript
        speeches = transcripts[0].get("parsedData", {}).get("speeches", [])
        transcript_text = " ".join([s.get("message") for s in speeches if s.get("message")])

    prompt = f"""
    Project: {project.get('name')}
    Recent Transcript Data: {transcript_text[:2000]} # Limit to save tokens
    Activity Logs: {logs}
    
    Task: Identify the most recent meeting discussed.
    Provide a weekly summary based ONLY on the provided data.
    """
    return llm_summary(prompt)