import sqlite3

# Conectar a tu SQLite
conn = sqlite3.connect("datos.db")
cursor = conn.cursor()

# Abrir archivo para escribir todo en SQL
with open("dump.sql", "w", encoding="utf-8") as f:
    for line in conn.iterdump():
        f.write(f"{line}\n")

conn.close()
print("dump.sql creado con éxito ✅")