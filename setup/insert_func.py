import sqlite3
import pandas as pd
import os

DATABASE = "../database.db"
ARQUIVO_XLS = "./servidores.xls"

def inserir_servidores():

    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()

    df = pd.read_excel(ARQUIVO_XLS)

    inseridos = 0
    ignorados = 0

    for _, row in df.iterrows():

        nome = str(row["SERVIDOR"]).strip()
        prontuario = str(row["PRONTUARIO"]).strip().upper()

        try:
            cursor.execute("""
                INSERT INTO funcionarios
                (prontuario, nome)
                VALUES (?, ?)
            """, (prontuario, nome))

            inseridos += 1

        except sqlite3.IntegrityError:
            ignorados += 1

    conn.commit()
    conn.close()

    print(f"Inseridos: {inseridos}")
    print(f"Ignorados: {ignorados}")

if __name__ == "__main__":
    inserir_servidores()