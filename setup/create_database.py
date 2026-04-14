import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# funcionários
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

# emprestimos (COM CONTROLE DE EXPORTAÇÃO)
cursor.execute("""
CREATE TABLE IF NOT EXISTS emprestimos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    funcionario_id INTEGER NOT NULL,
    chave_id INTEGER NOT NULL,
    data_retirada DATETIME NOT NULL,
    data_devolucao DATETIME,
    exportado INTEGER DEFAULT 0,
    FOREIGN KEY (funcionario_id) REFERENCES funcionarios(id),
    FOREIGN KEY (chave_id) REFERENCES chaves(id)
)
""")

conn.commit()
conn.close()

print("Banco de dados criado com sucesso.")