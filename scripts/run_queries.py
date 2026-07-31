import sqlite3

conn = sqlite3.connect("data/processed/bluestock_mf.db")
cursor = conn.cursor()

with open("sql/queries.sql", "r") as f:
    lines = f.readlines()

# Strip full-line comments before splitting
clean_lines = [line for line in lines if not line.strip().startswith("--")]
sql_script = "".join(clean_lines)

queries = [q.strip() for q in sql_script.split(";") if q.strip()]

for i, query in enumerate(queries, 1):
    try:
        cursor.execute(query)
        rows = cursor.fetchall()
        for row in rows[:5]:
            print(row)
        print(f"({len(rows)} total rows)")
    except Exception as e:
        print(f"ERROR: {e}")

conn.close()