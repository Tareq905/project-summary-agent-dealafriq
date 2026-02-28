def map_project_for_ai(project):

    health_score = None
    health = project.get("health")

    if isinstance(health, list) and len(health) > 0:
        health_score = health[0].get("score")

    return {
        "project_id": project.get("id"),
        "status": project.get("status"),

        "tasks": [
            {
                "title": t.get("title"),
                "status": t.get("status")
            }
            for t in project.get("tasks", [])
        ],

        "milestones": [
            {
                "title": m.get("title"),
                "status": m.get("status")
            }
            for m in project.get("milestones", [])
        ],

        "health_score": health_score,

        "meeting_key_points": [
            kp.get("content")
            for meeting in project.get("meetings", [])
            for kp in meeting.get("keyPoints", [])
        ],

        "meeting_action_points": [
            ap.get("content")
            for meeting in project.get("meetings", [])
            for ap in meeting.get("actionPoints", [])
        ]
    }