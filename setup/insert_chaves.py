import sqlite3

chaves = [
"A401","A402","A405","A406","A407","A408",
"A501","A504","A505","A506","A507",
"B101","B102","B106","B107",
"B201","B202","B206","B207","B208","B209","B210",
"B404","B405",
"B501","B503","B505","B509",
"B511","B513","B515","B516"
]

conn = sqlite3.connect("database.db")

for c in chaves:
    bloco = c[0]
    andar = c[1]+"00"

    conn.execute(
        "INSERT OR IGNORE INTO chaves (codigo, bloco, andar) VALUES (?,?,?)",
        (c, bloco, andar)
    )

conn.commit()
conn.close()

print("Chaves inseridas")