import argparse
import getpass
import sqlite3

from werkzeug.security import generate_password_hash


def criar_administrador(prontuario, nome, senha):
    conn = sqlite3.connect("database.db")
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS administradores (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                prontuario TEXT UNIQUE NOT NULL,
                nome TEXT NOT NULL,
                senha_hash TEXT NOT NULL
            )
        """)
        conn.execute(
            "INSERT INTO administradores (prontuario, nome, senha_hash) VALUES (?, ?, ?)",
            (prontuario.strip().upper(), nome.strip(), generate_password_hash(senha)),
        )
        conn.commit()
    finally:
        conn.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cadastra um administrador no banco local.")
    parser.add_argument("prontuario")
    parser.add_argument("nome")
    args = parser.parse_args()
    senha = getpass.getpass("Senha do administrador: ")
    if not senha:
        raise SystemExit("A senha não pode ser vazia.")
    criar_administrador(args.prontuario, args.nome, senha)
    print("Administrador cadastrado com sucesso.")
