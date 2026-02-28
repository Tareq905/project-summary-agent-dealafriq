from dotenv import load_dotenv
import os

load_dotenv()

from langchain_community.vectorstores import FAISS
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
import os

documents = []

path = "documents"

for file in os.listdir(path):

    with open(f"{path}/{file}", "r", encoding="utf-8") as f:
        text = f.read()
        documents.append(Document(page_content=text))

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

docs = splitter.split_documents(documents)

embeddings = OpenAIEmbeddings()

db = FAISS.from_documents(docs, embeddings)

db.save_local("rag/vector_store")