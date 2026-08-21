from ollama import chat
from config import LLM_MODEL


def stream_sql(prompt):
    """
    Stream SQL response from the LLM.
    To switch LLM providers, only this file needs to change.
    Returns the full SQL string after streaming.
    """
    response = chat(
        model=LLM_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True
    )

    sql = ""
    for chunk in response:
        token = chunk["message"]["content"]
        print(token, end="", flush=True)
        sql += token
    print()

    # Strip markdown code fences if present
    sql = sql.replace("```sql", "").replace("```", "").strip()
    return sql
