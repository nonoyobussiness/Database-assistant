'''from db import get_connection
from rag import build_rag, retrieve_context, table_exists, get_all_tables
from agent import stream_sql, build_prompt, validate_sql, extract_table_name, execute_sql
from agent.validator import is_ddl, is_drop, is_select


# -----------------------------
# RAG Initialization
# -----------------------------

import chromadb
from rag import OllamaEmbeddingFunction
from config import CHROMA_PATH, CHROMA_COLLECTION

client = chromadb.PersistentClient(path=CHROMA_PATH)
ef = OllamaEmbeddingFunction()

try:
    collection = client.get_collection(CHROMA_COLLECTION, embedding_function=ef)
    if len(collection.get()["ids"]) == 0:
        print("Building RAG...")
        build_rag()
except:
    print("Creating RAG...")
    build_rag()

    
# -----------------------------
# PostgreSQL
# -----------------------------

conn = get_connection()
cursor = conn.cursor()


# -----------------------------
# Main Loop
# -----------------------------

print("=" * 60)
print("AI DATABASE ASSISTANT")
print("=" * 60)

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    # CREATE TABLE pre-check
    if "create" in question.lower() and "table" in question.lower():
        table_name = extract_table_name(question)
        if table_name and table_exists(table_name):
            print(f"\nTable '{table_name}' already exists.")
            continue

    # RAG retrieval
    context = retrieve_context(question)
    all_tables = get_all_tables()

    # Build prompt and stream SQL
    prompt = build_prompt(question, context, all_tables)
    print("\nGenerating SQL...\n")
    sql = stream_sql(prompt)

    # Validate
    valid, message = validate_sql(sql)
    if not valid:
        print(f"\nBlocked: {message}")
        continue

    # DROP TABLE confirmation
    if is_drop(sql):
        confirm = input("\nWARNING: Table will be deleted.\nType YES to continue: ")
        if confirm.strip().upper() != "YES":
            print("Operation Cancelled")
            continue

    # Execute
    success, result = execute_sql(cursor, conn, sql)

    if not success:
        print(f"\nDatabase Error:\n{result}")
        continue

    if is_select(sql):
        print("\nResults")
        print("-" * 60)
        for row in result:
            print(row)
    else:
        print("\nQuery Executed Successfully")

        # Update RAG on schema changes
        if is_ddl(sql):
            print("\nUpdating RAG...")
            build_rag()
            print("RAG Updated")

cursor.close()
conn.close()
'''

from db import get_connection
from rag import build_rag, retrieve_context, table_exists, get_all_tables, wants_all_tables
from agent import stream_sql, build_prompt, validate_sql, extract_table_name, execute_sql, preview_ddl
from agent.validator import is_ddl, is_drop, is_select, is_create, is_alter


# -----------------------------
# RAG Initialization
# -----------------------------

import chromadb
from rag import OllamaEmbeddingFunction
from config import CHROMA_PATH, CHROMA_COLLECTION

client = chromadb.PersistentClient(path=CHROMA_PATH)
ef = OllamaEmbeddingFunction()

try:
    collection = client.get_collection(CHROMA_COLLECTION, embedding_function=ef)
    if len(collection.get()["ids"]) == 0:
        print("Building RAG...")
        build_rag()
except:
    print("Creating RAG...")
    build_rag()


# -----------------------------
# PostgreSQL
# -----------------------------

conn = get_connection()
cursor = conn.cursor()


# -----------------------------
# Main Loop
# -----------------------------

print("=" * 60)
print("AI DATABASE ASSISTANT")
print("=" * 60)

while True:
    question = input("\nYou: ")

    if question.lower() == "exit":
        break

    # CREATE TABLE pre-check
    if "create" in question.lower() and "table" in question.lower():
        table_name = extract_table_name(question)
        if table_name and table_exists(table_name):
            print(f"\nTable '{table_name}' already exists.")
            continue

    # RAG retrieval
    all_tables = get_all_tables()
    if wants_all_tables(question) and all_tables:
        # Question implies the whole database -> widen retrieval to cover every table
        context = retrieve_context(question, n_results=len(all_tables))
    else:
        # Targeted question -> keep normal top-3 semantic retrieval
        context = retrieve_context(question)

    # Build prompt and stream SQL
    prompt = build_prompt(question, context, all_tables)
    print("\nGenerating SQL...\n")
    sql = stream_sql(prompt)

    # Validate
    valid, message = validate_sql(sql)
    if not valid:
        print(f"\nBlocked: {message}")
        continue

    # CREATE / ALTER preview + confirmation
    if is_create(sql) or is_alter(sql):
        preview = preview_ddl(sql)
        if preview:
            print(f"\n{preview}")
        confirm = input("\nType YES to apply this change: ")
        if confirm.strip().upper() != "YES":
            print("Operation Cancelled")
            continue

    # DROP TABLE confirmation
    if is_drop(sql):
        confirm = input("\nWARNING: Table will be deleted.\nType YES to continue: ")
        if confirm.strip().upper() != "YES":
            print("Operation Cancelled")
            continue

    # Execute
    success, result = execute_sql(cursor, conn, sql)

    if not success:
        print(f"\nDatabase Error:\n{result}")
        continue

    if is_select(sql):
        print("\nResults")
        print("-" * 60)
        for block in result:
            if block["table"]:
                print(f"\n[{block['table']}]")
            print(" | ".join(block["columns"]))
            for row in block["rows"]:
                print(row)
    else:
        print("\nQuery Executed Successfully")

        # Update RAG on schema changes
        if is_ddl(sql):
            print("\nUpdating RAG...")
            build_rag()
            print("RAG Updated")

cursor.close()
conn.close()