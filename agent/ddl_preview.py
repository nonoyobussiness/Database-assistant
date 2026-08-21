import re


def _split_top_level(body):
    """
    Split a CREATE TABLE column-definition body on commas that are
    NOT inside parentheses (so REFERENCES table(col) isn't split).
    """
    parts = []
    depth = 0
    current = ""

    for ch in body:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1

        if ch == "," and depth == 0:
            parts.append(current.strip())
            current = ""
        else:
            current += ch

    if current.strip():
        parts.append(current.strip())

    return parts


def _describe_column(col_def):
    """
    Turn one column definition string into a short human-readable
    description, tagging primary keys and foreign keys.
    """
    col_name = col_def.split()[0].strip('"')
    col_lower = col_def.lower()

    if "primary key" in col_lower:
        return f"  - {col_name} (Primary Key)"

    ref_match = re.search(r"REFERENCES\s+\"?(\w+)\"?\s*\(\"?(\w+)\"?\)", col_def, re.IGNORECASE)
    if ref_match:
        return f"  - {col_name} (Foreign Key -> {ref_match.group(1)}.{ref_match.group(2)})"

    if "not null" in col_lower:
        return f"  - {col_name} (required, NOT NULL)"

    return f"  - {col_name}"


def preview_create_table(sql):
    """
    Returns a human-readable preview of a CREATE TABLE statement,
    or None if it couldn't be parsed.
    """
    match = re.search(
        r"CREATE TABLE\s+\"?(\w+)\"?\s*\((.*)\)\s*;?\s*$",
        sql, re.IGNORECASE | re.DOTALL
    )
    if not match:
        return None

    table_name = match.group(1)
    columns = _split_top_level(match.group(2))

    lines = [f"This will CREATE a new table '{table_name}' with columns:"]
    lines.extend(_describe_column(col) for col in columns)
    return "\n".join(lines)


def preview_alter_table(sql):
    """
    Returns a human-readable preview of an ALTER TABLE statement,
    or None if no recognizable sub-action was found.
    """
    table_match = re.search(r"ALTER TABLE\s+\"?(\w+)\"?", sql, re.IGNORECASE)
    if not table_match:
        return None
    table_name = table_match.group(1)

    lines = [f"This will ALTER table '{table_name}':"]
    found_action = False

    rename_match = re.search(
        r"RENAME COLUMN\s+\"?(\w+)\"?\s+TO\s+\"?(\w+)\"?",
        sql, re.IGNORECASE
    )
    if rename_match:
        found_action = True
        lines.append(f"  - Rename column '{rename_match.group(1)}' to '{rename_match.group(2)}'")

    for name, col_type in re.findall(
        r"ADD COLUMN\s+\"?(\w+)\"?\s+([\w()]+)", sql, re.IGNORECASE
    ):
        found_action = True
        lines.append(f"  - Add column '{name}' of type {col_type}")

    for name in re.findall(r"DROP COLUMN\s+\"?(\w+)\"?", sql, re.IGNORECASE):
        found_action = True
        lines.append(f"  - Drop column '{name}' (existing data in this column will be LOST)")

    for name, new_type in re.findall(
        r"ALTER COLUMN\s+\"?(\w+)\"?\s+TYPE\s+([\w()]+)", sql, re.IGNORECASE
    ):
        found_action = True
        lines.append(f"  - Change column '{name}' type to {new_type}")

    for constraint_name, ref_table, ref_col in re.findall(
        r"ADD CONSTRAINT\s+\"?(\w+)\"?\s+FOREIGN KEY\s*\([^)]*\)\s*REFERENCES\s+\"?(\w+)\"?\s*\(\"?(\w+)\"?\)",
        sql, re.IGNORECASE
    ):
        found_action = True
        lines.append(f"  - Add foreign key constraint '{constraint_name}' -> {ref_table}.{ref_col}")

    if not found_action:
        return None

    return "\n".join(lines)


def preview_ddl(sql):
    """
    Dispatches to the right preview generator based on the
    statement's DDL type. Returns None if the statement type
    isn't CREATE/ALTER or couldn't be parsed for preview.
    """
    sql_upper = sql.upper().strip()

    if sql_upper.startswith("CREATE TABLE"):
        return preview_create_table(sql)
    elif sql_upper.startswith("ALTER TABLE"):
        return preview_alter_table(sql)

    return None