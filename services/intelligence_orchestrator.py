from agents.project_summary_agent import run_project_summary
from agents.meeting_summary_agent import run_meeting_summary
from agents.document_summary_agent import run_document_summary
from agents.health_score_agent import run_health_score
from services.nsl_reasoner import apply_nsl_logic

def analyze_all_projects(all_sessions_data):
    """Generates a flat list of project intelligence with timeline math and flags."""
    output = []
    
    # Debug info to trace why Postman is getting an empty list
    print(f"DEBUG: Sessions found in builder: {list(all_sessions_data.keys())}")

    for session_name, data in all_sessions_data.items():
        # Ensure we look for the key "projects" as defined in session_data_builder.py
        projects = data.get("projects", [])
        print(f"DEBUG: Found {len(projects)} projects for session: {session_name}")

        for project in projects:
            try:
                # 1. Run Mathematical NSL to get timeline facts
                nsl_res = apply_nsl_logic(project)
                
                # 2. Run AI Agent with facts to get descriptive paragraphs
                intel = run_project_summary(project, nsl_res["facts"])
                
                # 3. Format Milestones with the "project progress" field
                milestones_output = []
                for m in project.get("milestones", []):
                    milestones_output.append({
                        "id": m.get("id"),
                        "projectId": project.get("id"),
                        "title": m.get("title"),
                        "description": m.get("description"),
                        "project progress": nsl_res["progress_str"],
                        "milestoneDate": m.get("milestoneDate"),
                        "status": m.get("status"),
                        "createdAt": m.get("createdAt")
                    })

                # 4. Construct the flat project object
                output.append({
                    "projectId": project.get("id"),
                    "projectName": project.get("name"),
                    "session": session_name,
                    "flag": intel.get("flag", "Unknown"), # Updated to use Agent's decided flag
                    "projectScore": float(run_health_score(project)),
                    "summary": intel.get("summary"),
                    "actionPoints": intel.get("action_points", []),
                    "discussionPoints": intel.get("discussion_points", []),
                    "notes": intel.get("notes", ""),
                    "raiddFlags": intel.get("raidd_flags", {}),
                    "milestones": milestones_output
                })
            except Exception as e:
                print(f"ERROR analyzing project {project.get('id', 'Unknown')}: {e}")
                continue # Skip this project if it fails and move to the next
                
    return output

def analyze_all_meetings(all_sessions_data):
    """Generates granular intelligence for every meeting transcript, flattened by project."""
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        for project in projects:
            try:
                mtgs_list = []
                # Collect transcripts at the project level to pass to the agent
                project_transcripts = project.get("transcripts", [])
                for mtg in project.get("meetings", []):
                    # Updated: Passing project_transcripts so the agent can find the discussion
                    intel = run_meeting_summary(mtg, project_transcripts)
                    mtgs_list.append({
                        "meetingId": mtg.get("id"),
                        "meetingTitle": mtg.get("title"),
                        "summary": intel.get("summary"),
                        "actionPoints": intel.get("action_points", []),
                        "discussionPoints": intel.get("discussion_points", []),
                        "notes": intel.get("notes", ""),
                        "raiddFlags": intel.get("raidd_flags", {})
                    })
                
                # Only add to output if project actually has meetings
                if mtgs_list:
                    output.append({
                        "projectId": project.get("id"),
                        "session": session_name,
                        "meetings": mtgs_list
                    })
            except Exception as e:
                print(f"ERROR analyzing meetings for {project.get('id')}: {e}")
                continue
    return output

def analyze_all_documents(all_sessions_data):
    """Generates detailed analysis for every uploaded project document, flattened."""
    output = []
    for session_name, data in all_sessions_data.items():
        projects = data.get("projects", [])
        for project in projects:
            try:
                docs_list = []
                for doc in project.get("documents", []):
                    intel = run_document_summary(doc)
                    docs_list.append({
                        "documentId": doc.get("id"),
                        "documentName": doc.get("fileName"),
                        "summary": intel.get("summary"),
                        "actionPoints": intel.get("action_points", []),
                        "discussionPoints": intel.get("discussion_points", []),
                        "notes": intel.get("notes", ""),
                        "raiddFlags": intel.get("raidd_flags", {})
                    })
                
                # Only add to output if project actually has documents
                if docs_list:
                    output.append({
                        "projectId": project.get("id"),
                        "session": session_name,
                        "documents": docs_list
                    })
            except Exception as e:
                print(f"ERROR analyzing documents for {project.get('id')}: {e}")
                continue
    return output