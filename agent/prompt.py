'''def build_prompt(question, context, tables):
    """
    Build the prompt sent to the LLM.
    To change prompting strategy (few-shot, chain-of-thought etc),
    modify this function.
    """
    tables_text = "\n".join(tables)

    return f"""
Database Context:

{context}

Existing Tables:

{tables_text}

You are a PostgreSQL Expert.

Rules:

1. Generate VALID PostgreSQL SQL.
2. Return ONLY SQL.
3. No markdown.
4. No explanation.
5. Never create existing tables.
6. Every CREATE TABLE must contain:
    id SERIAL PRIMARY KEY
7. Never generate incomplete SQL.
8. Generate executable PostgreSQL.
9. If user creates a table without columns,
    generate reasonable columns.

User Request:

{question}
"""
'''

def build_prompt(question, context, tables):
    """
    Build the prompt sent to the LLM.
    To change prompting strategy (few-shot, chain-of-thought etc),
    modify this function.
    """
    tables_text = "\n".join(tables)

    return f"""
Database Context:

{context}

Existing Tables:

{tables_text}

You are a PostgreSQL Expert.

Rules:

1. Generate VALID PostgreSQL SQL.
2. Return ONLY SQL.
3. No markdown.
4. No explanation.
5. Never create existing tables.
6. Every CREATE TABLE must contain:
   id SERIAL PRIMARY KEY
7. Never generate incomplete SQL.
8. Generate executable PostgreSQL.
9. If user creates a table without columns,
   generate reasonable columns.
10. PostgreSQL does NOT allow RENAME COLUMN to be combined
    with other ALTER TABLE actions in the same statement.
    RENAME COLUMN must always be its own standalone
    ALTER TABLE statement, e.g.:
    ALTER TABLE table_name RENAME COLUMN old_name TO new_name;
11. Do not add clauses the user did not ask for
    (e.g. SET DEFAULT, constraints, extra columns) unless
    they are required to satisfy an explicit request.
12. If a requested column name matches or clearly refers to
    another existing table (e.g. "deptid", "dept_id",
    "department_id" for table "departments"; "teacherid" for
    table "teachers"), make it a foreign key with
    REFERENCES to that table's primary key column, using
    the schema info given in Database Context above.
    Only do this when the referenced table actually exists
    in Existing Tables; otherwise treat it as a plain column.

User Request:

{question}
"""