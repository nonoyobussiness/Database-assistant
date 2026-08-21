'''def execute_sql(cursor, conn, sql):
    """
    Execute SQL and return (success, results_or_error).
    Handles SELECT separately from DML/DDL.
    To add result formatting (CSV, tables), modify this file.
    """
    try:
        cursor.execute(sql)

        if sql.upper().startswith("SELECT"):
            rows = cursor.fetchall()
            return True, rows
        else:
            conn.commit()
            return True, None

    except Exception as e:
        conn.rollback()
        return False, str(e)
        '''

import re


def execute_sql(cursor, conn, sql):
    """
    Execute SQL and return (success, results_or_error).
    Handles SELECT separately from DML/DDL.

    The LLM sometimes returns multiple statements in one response
    (e.g. one SELECT per table). psycopg2 only exposes fetchall()/
    description for the LAST statement in a single cursor.execute()
    call, so each statement is executed individually.

    For SELECTs, results_or_error is a list of "blocks", one per
    statement, each holding the table name, column names, and rows,
    so the caller can print a table/column header above each result
    set instead of one flat, unlabeled list of tuples.

    To add result formatting (CSV, tables), modify this file.
    """
    statements = [s.strip() for s in sql.split(";") if s.strip()]

    try:
        blocks = []
        saw_select = False

        for statement in statements:
            cursor.execute(statement)

            if statement.upper().startswith("SELECT"):
                saw_select = True
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()

                table_match = re.search(
                    r"FROM\s+([a-zA-Z_][a-zA-Z0-9_]*)",
                    statement,
                    re.IGNORECASE
                )
                table_name = table_match.group(1) if table_match else None

                blocks.append({
                    "table": table_name,
                    "columns": columns,
                    "rows": rows,
                })

        if saw_select:
            return True, blocks
        else:
            conn.commit()
            return True, None

    except Exception as e:
        conn.rollback()
        return False, str(e)
