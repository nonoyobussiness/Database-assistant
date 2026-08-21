'''import chromadb
from config import CHROMA_PATH, CHROMA_COLLECTION
from rag.embeddings import OllamaEmbeddingFunction

def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        CHROMA_COLLECTION,
        embedding_function=OllamaEmbeddingFunction()
    )

_collection = _get_collection()


def retrieve_context(question, n_results=3):
    results = _collection.query(
        query_texts=[question],
        n_results=n_results
    )
    return "\n".join(results["documents"][0])


def table_exists(table_name):
    try:
        data = _collection.get(ids=[table_name.lower()])
        return len(data["ids"]) > 0
    except:
        return False


def get_all_tables():
    try:
        return _collection.get()["ids"]
    except:
        return []
'''

import chromadb
from config import CHROMA_PATH, CHROMA_COLLECTION
from rag.embeddings import OllamaEmbeddingFunction

def _get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        CHROMA_COLLECTION,
        embedding_function=OllamaEmbeddingFunction()
    )

_collection = _get_collection()


def wants_all_tables(question):
    """
    Detects whether the question is asking about the *whole* database
    (all tables) rather than something targeted at specific tables.
    Used to decide whether to widen RAG retrieval beyond the usual top-k.
    """
    keywords = [
        "all table", "every table", "all data",
        "entire database", "whole database", "each table",
    ]
    q = question.lower()
    return any(k in q for k in keywords)


def retrieve_context(question, n_results=3):
    results = _collection.query(
        query_texts=[question],
        n_results=n_results
    )
    return "\n".join(results["documents"][0])


def table_exists(table_name):
    try:
        data = _collection.get(ids=[table_name.lower()])
        return len(data["ids"]) > 0
    except:
        return False


def get_all_tables():
    try:
        return _collection.get()["ids"]
    except:
        return []