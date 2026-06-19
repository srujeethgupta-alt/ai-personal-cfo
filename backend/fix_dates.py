import sqlite3

DB='ai_money_manager.db'
conn=sqlite3.connect(DB)
c=conn.cursor()
changed=0
checks=[('investments',['start_date','maturity_date']),('loans',['start_date','end_date']),('goals',['target_date']),('expenses',['expense_date'])]
for table,cols in checks:
    for col in cols:
        try:
            c.execute(f"SELECT id, {col} FROM {table} WHERE {col}='' OR {col}='NULL'")
            rows=c.fetchall()
            print(f"{table}.{col} -> {len(rows)} rows with empty/NULL string")
            if rows:
                c.execute(f"UPDATE {table} SET {col}=NULL WHERE {col}='' OR {col}='NULL'")
                changed += c.rowcount
        except Exception as e:
            print('error', table, col, e)
conn.commit()
conn.close()
print('Total changed:', changed)
