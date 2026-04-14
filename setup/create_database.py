import sqlite3

conn = sqlite3.connect("database.db")

# funcionarios
conn.execute("""
CREATE TABLE IF NOT EXISTS funcionarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prontuario TEXT UNIQUE,
    nome TEXT
)
""")

# chaves
conn.execute("""
CREATE TABLE IF NOT EXISTS chaves (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo TEXT UNIQUE,
    bloco TEXT,
    andar TEXT
)
""")

# emprestimos
conn.execute("""
CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chave_id INTEGER,
    funcionario_id INTEGER,
    data_retirada TEXT,
    data_devolucao TEXT,
    devolvido INTEGER DEFAULT 0,
    FOREIGN KEY(chave_id) REFERENCES chaves(id),
    FOREIGN KEY(funcionario_id) REFERENCES funcionarios(id)
)
""")

conn.commit()
conn.close()

print("Banco criado com sucesso")