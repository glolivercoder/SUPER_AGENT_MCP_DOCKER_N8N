import sqlite3

DB_PATH = 'data/super_agent.db'

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("""
    SELECT config_value FROM configurations WHERE module_name = 'openrouter' AND config_key = 'api_key'
""")
row = cursor.fetchone()

if row:
    value = row[0]
    if value.startswith('ENCRYPTED:'):
        value = value[10:]
    print(f"API key salva no banco: {value}")
else:
    print("Nenhuma API key encontrada para openrouter no banco de dados.")

conn.close() 