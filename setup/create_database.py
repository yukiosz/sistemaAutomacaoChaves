import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# funcionarios
cursor.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prontuario TEXT UNIQUE NOT NULL,
    nome TEXT NOT NULL
)
""")

# chaves
cursor.execute("""
CREATE TABLE IF NOT EXISTS chaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE NOT NULL,
    bloco TEXT,
    andar TEXT
)
""")

# emprestimos (NOVO MODELO COM RETIRADA E DEVOLUÇÃO SEPARADAS)
cursor.execute("""
CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,

    chave_id INTEGER NOT NULL,

    retirado_por INTEGER NOT NULL,
    devolvido_por INTEGER,

    data_retirada DATETIME NOT NULL,
    data_devolucao DATETIME,

    exportado INTEGER DEFAULT 0,

    FOREIGN KEY (chave_id) REFERENCES chaves(id),
    FOREIGN KEY (retirado_por) REFERENCES funcionarios(id),
    FOREIGN KEY (devolvido_por) REFERENCES funcionarios(id)
)
""")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso.")