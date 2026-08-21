# nldb — Natural Language Database Assistant

Talk to your PostgreSQL database in plain English. `nldb` converts natural-language
requests into SQL using a local LLM, grounds its answers in your *actual* schema via
retrieval-augmented generation (RAG), and adds a safety layer that previews and
confirms any destructive or structural change before it touches your database.

Everything runs locally — no external API calls. SQL generation and embeddings are
served by [Ollama](https://ollama.com/), and schema context is stored in a local
[ChromaDB](https://www.trychroma.com/) vector store.

```
You: create a table for students with name, email, and department id

Generating SQL...

CREATE TABLE students (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    department_id INTEGER REFERENCES departments(id)
);

This will CREATE a new table 'students' with columns:
  - id (Primary Key)
  - name (required, NOT NULL)
  - email (required, NOT NULL)
  - department_id (Foreign Key -> departments.id)

Type YES to apply this change: YES

Query Executed Successfully

Updating RAG...
RAG Updated
```

---

## How it works

```
Question
   │
   ▼
RAG retrieval (ChromaDB) ──► pulls relevant table schemas from your live DB
   │
   ▼
Prompt builder ──► injects schema context + rules into a structured prompt
   │
   ▼
LLM (Ollama) ──► streams back a SQL statement
   │
   ▼
Validator ──► blocks dangerous commands (DROP DATABASE, TRUNCATE, unscoped DELETE)
   │
   ▼
DDL preview + confirmation ──► human-readable summary for CREATE / ALTER / DROP
   │
   ▼
Executor ──► runs the statement(s) against PostgreSQL, formats results
   │
   ▼
RAG re-index ──► schema changes automatically refresh the vector store
```

| Layer | File(s) | Responsibility |
|---|---|---|
| Entry point | `main.py` | REPL loop tying every layer together |
| LLM | `agent/llm.py` | Streams SQL generation from Ollama |
| Prompting | `agent/prompt.py` | Builds the schema-grounded prompt + generation rules |
| Validation | `agent/validator.py` | Blocklist checks, statement-type detection |
| DDL preview | `agent/ddl_preview.py` | Parses CREATE/ALTER SQL into a human-readable summary |
| Execution | `agent/executor.py` | Runs SQL, splits multi-statement responses, formats SELECT results |
| Retrieval | `rag/retriever.py` | Semantic search over table schemas, "all tables" detection |
| Indexing | `rag/builder.py` | Reads Postgres `information_schema` and upserts into ChromaDB |
| Embeddings | `rag/embeddings.py` | Ollama-backed embedding function for ChromaDB |
| DB connection | `db/connection.py` | psycopg2 connection using `config.py` |

---

## Prerequisites

- **Python 3.10+**
- **PostgreSQL**, running locally with a database already created
- **[Ollama](https://ollama.com/)**, running locally, with these models pulled:
  ```bash
  ollama pull llama3
  ollama pull hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest
  ```

## Setup

1. **Clone the repo**
   ```bash
   git clone https://github.com/eldho-1/nldb.git
   cd nldb
   ```

2. **Create a virtual environment and install dependencies**
   ```bash
   python -m venv .venv
   source .venv/bin/activate   # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

3. **Configure your database connection**

   Edit `config.py` (or, preferably, set environment variables — see
   [Security notes](#security-notes) below):
   ```python
   DB_HOST = "localhost"
   DB_NAME = "your_database"
   DB_USER = "your_user"
   DB_PASSWORD = "your_password"
   ```

4. **Run it**
   ```bash
   python main.py
   ```

   On first run, `nldb` scans your database's schema and builds the RAG index
   automatically (stored locally under `./rag_db`).

## Usage

Type questions in plain English at the `You:` prompt. Type `exit` to quit.

**Examples:**
```
You: show me all teachers
You: create a table called departments with a name column
You: add a column called gpa of type numeric to students
You: rename column dept_id to department_id in students
You: delete the row from students where id = 5
You: exit
```

**Safety behavior:**
- `CREATE TABLE` / `ALTER TABLE` → shows a plain-English preview and asks for `YES` before applying.
- `DROP TABLE` → separate warning, requires explicit `YES`.
- `DROP DATABASE`, `TRUNCATE` → always blocked.
- `DELETE` without a `WHERE` clause → always blocked.
- Schema changes automatically trigger a RAG re-index so future questions stay grounded in the current schema.

---

## Project structure

```
nldb/
├── main.py                 # REPL entry point
├── config.py                # DB / model / ChromaDB configuration
├── requirements.txt
├── agent/
│   ├── llm.py                # Ollama chat streaming
│   ├── prompt.py              # Prompt template + generation rules
│   ├── validator.py           # Blocklist + statement-type helpers
│   ├── ddl_preview.py          # Human-readable CREATE/ALTER previews
│   └── executor.py             # Statement execution + result formatting
├── rag/
│   ├── builder.py              # Builds/refreshes schema index from Postgres
│   ├── retriever.py             # Semantic retrieval over schema index
│   └── embeddings.py            # Ollama embedding function for ChromaDB
└── db/
    └── connection.py            # psycopg2 connection factory
```

---

## Configuration reference (`config.py`)

| Variable | Description | Default |
|---|---|---|
| `DB_HOST` | PostgreSQL host | `localhost` |
| `DB_NAME` | Database name | `university_db` |
| `DB_USER` | Database user | `postgres` |
| `DB_PASSWORD` | Database password | — |
| `EMBEDDING_MODEL` | Ollama embedding model | `hf.co/CompendiumLabs/bge-base-en-v1.5-gguf:latest` |
| `LLM_MODEL` | Ollama chat model used for SQL generation | `llama3:latest` |
| `CHROMA_PATH` | Local path for the ChromaDB vector store | `./rag_db` |
| `CHROMA_COLLECTION` | ChromaDB collection name | `schema` |

---

## Security notes

- **Don't commit real credentials.** `config.py` currently holds a plaintext
  password. Prefer loading these from environment variables (e.g. via
  `python-dotenv`) and keep an untracked `.env` locally.
- **Use a restricted database role.** Avoid connecting as `postgres`
  (superuser). Create a dedicated role scoped to only the schema/permissions
  `nldb` needs.
- **Validation is a blocklist, not a sandbox.** `agent/validator.py` blocks
  a specific set of dangerous commands but does not parse or fully sanitize
  arbitrary LLM output. Review generated SQL for anything running against
  production data.

---

## Known limitations

- Each question is handled independently — there's no multi-turn memory
  (e.g. "now add a column to that table" won't know which table "that" refers to).
- `extract_table_name` uses simple keyword matching and may misparse
  unusual phrasing.
- Requires Ollama and PostgreSQL to be running locally; there's currently no
  graceful error handling if either is unavailable.


