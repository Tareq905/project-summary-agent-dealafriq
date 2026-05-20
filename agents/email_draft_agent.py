import json
from openai import OpenAI
from config.settings import settings

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def run_email_draft(email_data: dict) -> dict | None:
    """
    Email Draft Agent.
    Generates a professional email draft with only 3 fields:
    subject, greeting, and body.
    """

    subject      = email_data.get("subject", "")
    body         = email_data.get("body", "")
    sender       = email_data.get("from_name") or email_data.get("fromName") or ""
    sender_email = email_data.get("from") or email_data.get("fromEmail") or ""
    received_at  = email_data.get("receivedAt") or email_data.get("createdAt") or ""

    system_instruction = """
    You are a Senior Professional Email Drafting Agent embedded in a Project Management Intelligence System.
    Your task is to generate a complete, well-structured, professional email draft as a reply
    to the provided email.

    STRICT OUTPUT RULES:
    - Return a strictly valid JSON object with EXACTLY 3 keys: "subject", "greeting", "body".
    - No other keys. No markdown. No code fences. No extra text.
    - The draft must be ready to send — professional, clear, and appropriately detailed.
    - Do NOT be generic. Reference the actual subject, concerns, and context from the email.
    - The tone must be professional but warm. Not robotic. Not overly formal.
    """

    user_prompt = f"""
    ORIGINAL EMAIL:
    Subject: {subject}
    Sender Name: {sender}
    Sender Email: {sender_email}
    Received At: {received_at}
    Body:
    {body}

    ═══════════════════════════════════════════════
    TASK: Generate a complete professional email draft as a reply to the above email.
    ═══════════════════════════════════════════════

    FIELD RULES:

    "subject":
    - A clear, professional reply subject line.
    - Use "Re: [original subject]" format unless a more specific subject is warranted.

    "greeting":
    - Address the sender by first name if identifiable from sender name.
    - Use "Dear [Name]," format.
    - If name is unknown, use "Dear Sir/Madam," or "Hello Team,".

    "body":
    - The full email body as a single string. Include ALL content here.
    - Start directly with the opening line — no greeting repeated here.
    - Structure: 
        • Opening (1-2 sentences): Acknowledge the email's key concern specifically.
          Do NOT use "I hope this email finds you well" or "Thank you for your email."
        • Main paragraphs (3-5): Address each concern raised in the original email.
          Paragraph 1 — Validate and acknowledge the key concern(s).
          Paragraph 2 — Provide context, current status, or relevant information.
          Paragraph 3 — Outline next steps or actions being taken.
          Paragraph 4 (if needed) — Address additional points or questions.
          Paragraph 5 (if needed) — Timeline, commitment, or escalation path.
        • Closing (1-2 sentences): Invite further questions, confirm availability.
        • Sign-off: End with "Best regards," followed by a blank line and "[Your Name]\\n[Your Title]\\n[Your Company]"
    - Each paragraph separated by \\n\\n.
    - Dense with relevance. Zero filler.

    RETURN THIS EXACT JSON STRUCTURE — NO OTHER KEYS:
    {{
        "subject": "string",
        "greeting": "string",
        "body": "string"
    }}
    """

    try:
        res = client.chat.completions.create(
            model="gpt-4o-mini",
            response_format={"type": "json_object"},
            messages=[
                {"role": "system", "content": system_instruction},
                {"role": "user",   "content": user_prompt}
            ]
        )
        result = json.loads(res.choices[0].message.content)

        # Enforce only the 3 allowed keys — strip anything else the LLM may have added
        clean = {
            "subject":  result.get("subject", ""),
            "greeting": result.get("greeting", ""),
            "body":     result.get("body", "")
        }

        print(f"✅ [EMAIL_DRAFT_AGENT] Draft generated for subject: '{subject[:60]}'")
        return clean

    except Exception as e:
        print(f"❌ [EMAIL_DRAFT_AGENT] LLM Error for email [{email_data.get('id')}]: {e}")
        return None