from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from config.settings import settings 

embeddings = OpenAIEmbeddings(openai_api_key=settings.OPENAI_API_KEY)

db = FAISS.load_local(
    "rag/vector_store",
    embeddings,
    allow_dangerous_deserialization=True
)

def retrieve_context(query):
    docs = db.similarity_search(query, k=3)
    return " ".join([d.page_content for d in docs])