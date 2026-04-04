# type: ignore
"""
Builds and persists a LangChain Qdrant vector store over the Arize documentation.
"""

from dotenv import load_dotenv

load_dotenv()

from langchain_community.document_loaders import SitemapLoader
from langchain_community.vectorstores import Qdrant
from langchain_openai import OpenAIEmbeddings

loader = SitemapLoader(
    "https://arize.com/docs/sitemap.xml",
)
documents = loader.load()
embeddings = OpenAIEmbeddings(
    model="text-embedding-3-large",
)
Qdrant.from_documents(
    documents,
    embeddings,
    path="./vector-store",
    collection_name="arize-documentation",
)
