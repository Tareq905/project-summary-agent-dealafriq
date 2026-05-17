def map_project_to_backend(ai_data, project_id):
    return {
        "id": project_id,
        "projectAiSummary": [ai_data.get("summary", "")],  # string → array তে wrap
        "projectProgress": ai_data.get("progress_str", "0.0%"),
        "projectHealth": ai_data.get("health_label", "Bad").lower(),
        "notes": ai_data.get("notes", ""),
        "discussionPoints": ai_data.get("discussion_points", []),
        "actionPoints": ai_data.get("action_points", []),
        "raiddData": {
            "risks":        ai_data.get("raidd_flags", {}).get("risks", []),
            "issues":       ai_data.get("raidd_flags", {}).get("issues", []),
            "assumptions":  ai_data.get("raidd_flags", {}).get("assumptions", []),
            "dependencies": ai_data.get("raidd_flags", {}).get("dependencies", []),
            "decisions":    ai_data.get("raidd_flags", {}).get("decisions", [])
        }
    }


def map_meeting_to_backend(ai_data, meeting_id):
    raw_key_points    = ai_data.get("discussion_points") or []
    raw_action_points = ai_data.get("action_points") or []
    raidd_flags       = ai_data.get("raidd_flags", {})
    summary           = ai_data.get("summary") or None

    return {
        "id": meeting_id,
        "notes":            ai_data.get("notes") or None,
        "aiMeetingSummary": summary,
        "agenda":           ai_data.get("agenda") or None,
        # Prisma nested create format
        "keyPoints": {
            "create": [{"content": str(k)} for k in raw_key_points if k]
        } if raw_key_points else None,

        "actionPoints": {
            "create": [{"content": str(a)} for a in raw_action_points if a]
        } if raw_action_points else None,

        # RAIDD data
        "raiddData": {
            "risks":        [{"data": d} for d in raidd_flags.get("risks", [])        if d],
            "issues":       [{"data": d} for d in raidd_flags.get("issues", [])       if d],
            "assumptions":  [{"data": d} for d in raidd_flags.get("assumptions", [])  if d],
            "dependencies": [{"data": d} for d in raidd_flags.get("dependencies", []) if d],
            "decisions":    [{"data": d} for d in raidd_flags.get("decisions", [])    if d],
        }
    }


def map_document_to_backend(ai_data, doc_id):
    raw_key_points    = ai_data.get("action_points") or []
    raw_action_points = ai_data.get("discussion_points") or []

    return {
        "id": doc_id,
        "aiDocumentSummary": ai_data.get("summary"),

        # Prisma nested create format
        "keyPoints": {
            "deleteMany": {},
            "create": [{"content": str(k)} for k in raw_key_points if k]
        } if raw_key_points else None,

        "actionPoints": {
            "deleteMany": {},
            "create": [{"content": str(a)} for a in raw_action_points if a]
        } if raw_action_points else None,
    }


def map_email_to_backend(ai_data, email_id):
    raidd = ai_data.get("raiddAnalysis", {})
    return {
        "id": email_id,
        "tasks": [],
        "raiddCategory": ai_data.get("category", []),
        "raiddData": {
            "risks":        [{"data": d} for d in raidd.get("risks", [])],
            "issues":       [{"data": d} for d in raidd.get("issues", [])],
            "assumptions":  [{"data": d} for d in raidd.get("assumptions", [])],
            "decisions":    [{"data": d} for d in raidd.get("decisions", [])],
            "dependencies": [{"data": d} for d in raidd.get("dependencies", [])]
        }
    }