from pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
from config.settings import settings

pc = Pinecone(api_key=settings.PINECONE_API_KEY)
index = pc.Index(settings.PINECONE_INDEX_NAME)
embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

def get_vendor_rag_context(vendor_id):
    # Retrieve the "Dynamic Governance Logic" and "SLA Metrics"
    query = "SLA benchmarks, milestone dates, and vendor responsibilities"
    xq = embeddings.embed_query(query)
    
    res = index.query(
        vector=xq,
        top_k=5,
        include_metadata=True,
        filter={"vendorId": {"$eq": vendor_id}}
    )
    return "\n".join([m['metadata']['text'] for m in res['matches']])