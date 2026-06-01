import os
from pinecone import Pinecone
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config.settings import settings

# --- INITIALIZATION ---

# 1. OpenAI embeddings — used for FAISS (global) and vendor index
#    MUST match model used in ingest.py (text-embedding-3-small → 1536 dims)
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. Initialize Pinecone
pc = Pinecone(api_key=settings.PINECONE_API_KEY)

vendor_index   = pc.Index(settings.PINECONE_INDEX_NAME)       # Vendor intelligence (OpenAI embeddings)
email_index_v2 = pc.Index(settings.PINECONE_EMAIL_INDEX_NAME) # email-agent-v2 (multilingual-e5-large, 1024 dims)

# NOTE: email-agent (legacy) is no longer used. Client requirement is email-agent-v2 only.

# 3. Load Local FAISS (For Global Governance Rules)
local_db_path = "rag/vector_store"
db = None

if os.path.exists(local_db_path):
    try:
        db = FAISS.load_local(
            local_db_path,
            embeddings,
            allow_dangerous_deserialization=True
        )
        print("✅ Local FAISS (Governance Rules) loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading local FAISS: {e}")
else:
    print("⚠️ Local FAISS index not found. Global rules will be unavailable.")


# --- CORE RETRIEVAL LOGIC ---

def retrieve_context(query, vendor_id=None, mode="global"):
    """
    A Hybrid Retriever that switches between intelligence layers.

    :param query: The search string.
    :param vendor_id: Required if mode is 'vendor'.
    :param mode:
        'global' -> Searches Local FAISS (Governance Rules) — OpenAI embeddings (1536 dims).
        'vendor' -> Searches Pinecone vendor index — OpenAI embeddings (1536 dims).
        'email'  -> Searches Pinecone email-agent-v2 — Pinecone native inference
                    using multilingual-e5-large (1024 dims) to match ingestion model.
    """

    # --- MODE A: VENDOR INTELLIGENCE (Pinecone + OpenAI embeddings) ---
    if mode == "vendor":
        if not vendor_id:
            print("❌ Error: vendor_id is required for 'vendor' mode.")
            return ""

        print(f"🔍 [MODE: VENDOR] Searching Pinecone for vendor: {vendor_id}")
        try:
            xq = embeddings.embed_query(query)
            res = vendor_index.query(
                vector=xq,
                top_k=5,
                include_metadata=True,
                filter={"vendorId": {"$eq": vendor_id}}
            )
            if not res['matches']:
                return ""
            return "\n".join([m['metadata']['text'] for m in res['matches']])
        except Exception as e:
            print(f"❌ Pinecone Vendor Error: {e}")
            return ""

    # --- MODE B: EMAIL INTELLIGENCE (email-agent-v2 via Pinecone native inference) ---
    elif mode == "email":
        print(f"🔍 [MODE: EMAIL] Querying email-agent-v2 (multilingual-e5-large)...")
        try:
            # Use Pinecone's native inference API — MUST match ingestion model
            # Ingestion used: multilingual-e5-large (1024 dims)
            embedding_response = pc.inference.embed(
                model="multilingual-e5-large",
                inputs=[query],
                parameters={"input_type": "query", "truncate": "END"}
            )
            query_vector = embedding_response[0]["values"]

            res = email_index_v2.query(
                vector=query_vector,
                top_k=7,
                include_metadata=True
            )

            if not res['matches']:
                print("⚠️ [EMAIL] No results from email-agent-v2.")
                return ""

            texts = [m['metadata']['text'] for m in res['matches']]
            print(f"✅ [EMAIL] Retrieved {len(texts)} chunks from email-agent-v2.")
            return "\n".join(texts)

        except Exception as e:
            print(f"❌ Pinecone email-agent-v2 Error: {e}")
            return ""

    # --- MODE C: GLOBAL GOVERNANCE (FAISS + OpenAI embeddings) ---
    else:
        print(f"🔍 [MODE: GLOBAL] Searching Local FAISS...")
        if db:
            try:
                docs = db.similarity_search(query, k=3)
                return " ".join([d.page_content for d in docs])
            except Exception as e:
                print(f"❌ FAISS Error: {e}")
                return ""
        else:
            print("❌ Error: Local FAISS not available.")
            return ""