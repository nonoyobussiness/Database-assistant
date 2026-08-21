# Add new blocked commands or custom rules here
'''
BLOCKED_COMMANDS = [
    "DROP DATABASE",
    "TRUNCATE",
]

DDL_COMMANDS = [
    "CREATE TABLE",
    "ALTER TABLE",
    "DROP TABLE",
]


def validate_sql(sql):
    """
    Returns (is_valid, reason).
    Add new validation rules here as the project grows.
    """
    sql_upper = sql.upper()

    for cmd in BLOCKED_COMMANDS:
        if cmd in sql_upper:
            return False, cmd

    if sql_upper.startswith("DELETE") and "WHERE" not in sql_upper:
        return False, "DELETE WITHOUT WHERE"

    return True, "OK"


def extract_table_name(question):
    """Extract table name from natural language question."""
    words = question.lower().split()
    for i, word in enumerate(words):
        if word == "table" and i + 1 < len(words):
            return words[i + 1]
    return None


def is_ddl(sql):
    """Returns True if the SQL is a DDL statement that requires a RAG update."""
    sql_upper = sql.upper()
    return any(sql_upper.startswith(cmd) for cmd in DDL_COMMANDS)


def is_drop(sql):
    return sql.upper().startswith("DROP TABLE")


def is_select(sql):
    return sql.upper().startswith("SELECT")
'''

# Add new blocked commands or custom rules here

BLOCKED_COMMANDS = [
    "DROP DATABASE",
    "TRUNCATE",
]

DDL_COMMANDS = [
    "CREATE TABLE",
    "ALTER TABLE",
    "DROP TABLE",
]


def validate_sql(sql):
    """
    Returns (is_valid, reason).
    Add new validation rules here as the project grows.
    """
    sql_upper = sql.upper()

    for cmd in BLOCKED_COMMANDS:
        if cmd in sql_upper:
            return False, cmd

    if sql_upper.startswith("DELETE") and "WHERE" not in sql_upper:
        return False, "DELETE WITHOUT WHERE"

    return True, "OK"


def extract_table_name(question):
    """Extract table name from natural language question."""
    words = question.lower().split()
    for i, word in enumerate(words):
        if word == "table" and i + 1 < len(words):
            return words[i + 1]
    return None


def is_ddl(sql):
    """Returns True if the SQL is a DDL statement that requires a RAG update."""
    sql_upper = sql.upper()
    return any(sql_upper.startswith(cmd) for cmd in DDL_COMMANDS)


def is_drop(sql):
    return sql.upper().startswith("DROP TABLE")


def is_create(sql):
    return sql.upper().startswith("CREATE TABLE")


def is_alter(sql):
    return sql.upper().startswith("ALTER TABLE")


def is_select(sql):
    return sql.upper().startswith("SELECT")