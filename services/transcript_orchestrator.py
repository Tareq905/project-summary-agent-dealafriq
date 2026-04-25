from fetchers.transcript_fetcher import fetch_meeting_transcripts
from agents.transcript_deep_analysis_agent import run_transcript_deep_analysis

def analyze_all_meeting_transcripts():
    # Call the normalized fetcher
    raw_meetings = fetch_meeting_transcripts()
    
    if not raw_meetings:
        return []

    output = []
    for meeting in raw_meetings:
        # Run AI analysis
        analysis = run_transcript_deep_analysis(meeting)
        
        if analysis:
            # Consistent RAIDD structure with meetingId
            report = {
                "flag": analysis.get("flag", "Green"),
                "meetingId": str(meeting.get("id")),
                "summary": analysis.get("summary"),
                "category": analysis.get("category", ["Informational"]),
                "sentiment": analysis.get("sentiment", "neutral"),
                "raiddAnalysis": analysis.get("raiddAnalysis"),
                "additional_info": {
                    "meetingTitle": meeting.get("title"),
                    "meetingDate": meeting.get("meetingDate"),
                    "projectId": meeting.get("projectId")
                },
                "generatedReply": None,
                "vendor": None,
                "type": "meeting_transcript"
            }
            output.append(report)

    return output