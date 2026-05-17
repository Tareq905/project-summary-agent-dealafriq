import logging
from fetchers.project_fetcher import fetch_all_projects
from fetchers.meeting_fetcher import fetch_all_meetings
from fetchers.document_fetcher import fetch_all_documents

logger = logging.getLogger(__name__)


def build_session_data():

    projects  = fetch_all_projects()
    meetings  = fetch_all_meetings()
    documents = fetch_all_documents()

    logger.info(f"📦 Fetched → Projects: {len(projects)} | Meetings: {len(meetings)} | Documents: {len(documents)}")

    meetings_by_project = {}
    for mtg in meetings:
        pid = mtg.get("projectId")
        if pid:
            meetings_by_project.setdefault(pid, []).append(mtg)

    documents_by_project = {}
    for doc in documents:
        pid = doc.get("projectId")
        if pid:
            documents_by_project.setdefault(pid, []).append(doc)

    enriched_projects = []
    for project in projects:
        pid = project.get("id")
        enriched = {
            **project,
            "meetings":  meetings_by_project.get(pid, []),
            "documents": documents_by_project.get(pid, [])
        }
        enriched_projects.append(enriched)
        logger.info(
            f"  ✔ Project '{project.get('name')}' → "
            f"{len(enriched['meetings'])} meetings, "
            f"{len(enriched['documents'])} documents"
        )

    return {"projects": enriched_projects}