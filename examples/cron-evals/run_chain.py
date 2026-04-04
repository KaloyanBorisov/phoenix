# type: ignore
"""
Loads a pre-built Qdrant vector store and defines a simple `RetrievalQA` chain.
Downloads a set of queries and invokes the chain on loop to simulate a
production environment with continuously incoming traces and spans.

Note: You must first build the Qdrant vector store using the
`build_vector_store.py` script before running this script.
"""

import os
from itertools import cycle

import pandas as pd
from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnablePassthrough
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_qdrant import QdrantVectorStore
from phoenix.otel import register
from qdrant_client import QdrantClient

_SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

load_dotenv(os.path.join(_SCRIPT_DIR, ".env"))


def get_chain():
    """
    Loads a pre-built Qdrant vector store and defines a simple `RetrievalQA` chain.
    """
    qdrant_client = QdrantClient(path=os.path.join(_SCRIPT_DIR, "vector-store"))
    embeddings = OpenAIEmbeddings(
        model="text-embedding-3-large",
    )
    vector_store = QdrantVectorStore(
        client=qdrant_client,
        collection_name="arize-documentation",
        embedding=embeddings,
    )
    retriever = vector_store.as_retriever(
        search_type="mmr", search_kwargs={"k": 2}, enable_limit=True
    )
    llm = ChatOpenAI(model="gpt-4o", temperature=0.0)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", "Answer the question using only the following context:\n\n{context}"),
            ("human", "{question}"),
        ]
    )
    return (
        {"context": retriever, "question": RunnablePassthrough()} | prompt | llm | StrOutputParser()
    )


def instrument_langchain():
    """
    Instruments LangChain with OpenInference, exporting traces to Phoenix Cloud.
    """
    endpoint = os.environ["PHOENIX_COLLECTOR_ENDPOINT"].rstrip("/") + "/v1/traces"
    register(
        project_name="cron-evals",
        endpoint=endpoint,
        batch=True,
        auto_instrument=True,
    )


def load_queries():
    """
    Loads a set of queries from a parquet file.
    """
    return pd.read_parquet(
        os.path.join(
            _SCRIPT_DIR,
            "queries",
            "langchain_pinecone_query_dataframe_with_user_feedbackv2.parquet",
        )
    ).text.to_list()


if __name__ == "__main__":
    queries = load_queries()
    chain = get_chain()
    instrument_langchain()
    for query in cycle(queries):
        response = chain.invoke(query)
        print("Query")
        print("=====")
        print(query)
        print()
        print("Response")
        print("========")
        print(response)
        print()
