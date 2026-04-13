import json
from utils.llm_client import llm_summary
from rag.pinecone_retriever import get_vendor_rag_context

def run_vendor_analysis(vendor, pm_list):
    v_id = vendor.get("id")
    v_name = vendor.get("name")
    
    # 1. Pull Rules from Pinecone
    rag_context = get_vendor_rag_context(v_id)

    # 2. Prepare dynamic prompt
    prompt = f"""
    GOVERNANCE RULES (Pinecone):
    {rag_context}

    EVIDENCE DATA:
    Vendor: {v_name}
    Projects: {json.dumps(vendor.get('projects', []))}
    Emails: {json.dumps(vendor.get('emails', []))}
    PM Context: {json.dumps(pm_list)}

    TASK:
    Analyze the vendor performance.
    
    CRITICAL AUDIT:
    - Cross-reference the email body content with the 'projects' milestone status.
    - If the vendor claims progress in emails that is NOT reflected in the project data, flag this as an 'Issue'.

    RETURN ARCHITECTURE:
    Return a JSON object matching the requested structure:
    {{
        "projectId": "string",
        "session": "string",
        "vendors": [
            {{
                "vendorId": "{v_id}",
                "vendorName": "{v_name}",
                "summary": "Date: April 13, 2026\\n\\n🔹 Performance Overview\\n...\\n🔹 SLA Compliance\\n...\\n🔹 Final Insight",
                "performanceScore": 0.0,
                "flag": "Red/Amber/Green",
                "actionPoints": [],
                "discussionPoints": [],
                "lessonsLearned": ["Detailed paragraph suggesting improvements"],
                "notes": "string",
                "raiddFlags": {{ "risks": [], "assumptions": [], "issues": [], "dependencies": [], "decisions": [] }}
            }}
        ]
    }}
    """
    return llm_summary(prompt)