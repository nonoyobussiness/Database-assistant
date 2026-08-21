import chromadb
from config import CHROMA_PATH, CHROMA_COLLECTION
from db import get_connection
from rag.embeddings import OllamaEmbeddingFunction


def get_collection():
    client = chromadb.PersistentClient(path=CHROMA_PATH)
    return client.get_or_create_collection(
        CHROMA_COLLECTION,
        embedding_function=OllamaEmbeddingFunction()
    )


def build_rag():
    collection = get_collection()
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema='public'
    """)
    tables = cursor.fetchall()

    existing_ids = set(collection.get()["ids"])
    current_ids = set()

    for (table_name,) in tables:
        current_ids.add(table_name)

        cursor.execute("""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_name=%s
            ORDER BY ordinal_position
        """, (table_name,))
        columns = cursor.fetchall()

        doc = f"Table: {table_name}\n\nColumns:\n"
        for col_name, col_type in columns:
            doc += f"{col_name} ({col_type})\n"

        collection.upsert(ids=[table_name], documents=[doc])

    # Remove deleted tables from RAG
    removed = existing_ids - current_ids
    if removed:
        collection.delete(ids=list(removed))

    cursor.close()
    conn.close()


if __name__ == "__main__":
    build_rag()
    print("RAG Built")
