def apply_nsl_logic(project):

    logical_facts = []

    tasks = project.get("tasks", [])
    milestones = project.get("milestones", [])
    health = project.get("health", [])

    # -----------------------------
    # Task Delay Risk
    # -----------------------------
    for task in tasks:
        if task.get("status") == "PENDING":
            logical_facts.append("Pending task may delay delivery.")

    # -----------------------------
    # Milestone Risk
    # -----------------------------
    for milestone in milestones:
        if milestone.get("status") == "UPCOMING":
            logical_facts.append("Upcoming milestone requires readiness.")

    # -----------------------------
    # Health Risk
    # -----------------------------
    for h in health:
        if h.get("status") == "Healthy":
            logical_facts.append("Project currently healthy.")

        if h.get("healthStatus") == "ON_TRACK":
            logical_facts.append("Execution currently on track.")

    return logical_facts


# -----------------------------
# DOCUMENT NSL
# -----------------------------
def apply_document_logic(document):

    doc_facts = []

    title = document.get("title", "")
    key_points = document.get("keyPoints", [])
    action_points = document.get("actionPoints", [])

    if title and "agreement" in title.lower():
        doc_facts.append("Execution requires signed agreement.")

    for ap in action_points:
        if ap.get("status") == "PENDING":
            doc_facts.append("Pending approval blocks execution.")

    for kp in key_points:
        if kp.get("status") == "TO_BE_VALIDATED":
            doc_facts.append("Validation pending for execution artifact.")

    return doc_facts