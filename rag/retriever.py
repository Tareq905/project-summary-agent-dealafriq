import os
from pinecone import Pinecone
from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config.settings import settings 

# --- INITIALIZATION ---

# 1. IMPORTANT: The model MUST match the one used in ingest.py (text-embedding-3-small)
# If they don't match, the math will be wrong and you will get no results.
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")

# 2. Initialize Pinecone (For Vendor and Email Intelligence)
pc = Pinecone(api_key=settings.PINECONE_API_KEY)
vendor_index = pc.Index(settings.PINECONE_INDEX_NAME)      # The standard vendor index
email_index = pc.Index(settings.PINECONE_EMAIL_INDEX_NAME)

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
    A Hybrid Retriever that switches between three intelligence layers.
    
    :param query: The search string.
    :param vendor_id: Required if mode is 'vendor'.
    :param mode: 
        'global' -> Searches Local FAISS (Governance Rules).
        'vendor' -> Searches Pinecone (Vendor Documents) filtered by vendor_id.
        'email'  -> Searches Pinecone (Advanced Email Intelligence).
    """
    
    # --- MODE A: VENDOR INTELLIGENCE (Pinecone) ---
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
                filter={"vendorId": {"$eq": vendor_id}} # Strict isolation
            )
            if not res['matches']:
                return ""
            return "\n".join([m['metadata']['text'] for m in res['matches']])
        except Exception as e:
            print(f"❌ Pinecone Vendor Error: {e}")
            return ""

    # --- MODE B: EMAIL INTELLIGENCE (Pinecone) ---
    elif mode == "email":
        print(f"🔍 [MODE: EMAIL] Searching Pinecone Email-Agent Index...")
        try:
            xq = embeddings.embed_query(query)
            res = email_index.query(
                vector=xq,
                top_k=5,
                include_metadata=True
            )
            if not res['matches']:
                return ""
            return "\n".join([m['metadata']['text'] for m in res['matches']])
        except Exception as e:
            print(f"❌ Pinecone Email Error: {e}")
            return ""

    # --- MODE C: GLOBAL GOVERNANCE (FAISS) ---
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