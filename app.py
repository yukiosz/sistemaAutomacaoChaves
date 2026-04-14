from flask import Flask, render_template, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = "database.db"

def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/estado")
def estado():
    conn = get_db()

    dados = conn.execute("""
        SELECT c.codigo
        FROM emprestimos e
        JOIN chaves c ON c.id = e.chave_id
        WHERE e.devolvido = 0
    """).fetchall()

    conn.close()

    return jsonify([d["codigo"] for d in dados])


@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.json

    prontuario = data["id"]
    codigo = data["chave"]
    tipo = data["tipo"]

    conn = get_db()

    funcionario = conn.execute(
        "SELECT * FROM funcionarios WHERE prontuario=?",
        (prontuario,)
    ).fetchone()

    if not funcionario:
        return jsonify({
            "status":"erro",
            "mensagem":"Funcionário não encontrado"
        })

    chave = conn.execute(
        "SELECT * FROM chaves WHERE codigo=?",
        (codigo,)
    ).fetchone()

    if not chave:
        return jsonify({
            "status":"erro",
            "mensagem":"Chave não encontrada"
        })

    if tipo == "RETIRADA":

        ativo = conn.execute("""
            SELECT * FROM emprestimos
            WHERE chave_id=? AND devolvido=0
        """,(chave["id"],)).fetchone()

        if ativo:
            return jsonify({
                "status":"erro",
                "mensagem":"Chave não disponível"
            })

        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        conn.execute("""
            INSERT INTO emprestimos
            (chave_id, funcionario_id, data_retirada, devolvido)
            VALUES (?,?,?,0)
        """,(chave["id"], funcionario["id"], agora))

    else:
        agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        emprestimo = conn.execute("""
            SELECT e.id, f.prontuario
            FROM emprestimos e
            JOIN funcionarios f ON f.id = e.funcionario_id
            WHERE e.chave_id=? AND e.devolvido=0
        """,(chave["id"],)).fetchone()

        if not emprestimo:
            return jsonify({
                "status":"erro",
                "mensagem":"Chave não está emprestada"
            })

        if emprestimo["prontuario"] != prontuario:
            return jsonify({
                "status":"erro",
                "mensagem":"Prontuário difere do informado na retirada da chave"
            })

        conn.execute("""
            UPDATE emprestimos
            SET devolvido=1, data_devolucao=?
            WHERE id=?
        """,(agora, emprestimo["id"]))

    conn.commit()
    conn.close()

    return jsonify({"status":"ok"})


@app.route("/info/<codigo>")
def info(codigo):

    conn = get_db()

    dado = conn.execute("""
        SELECT 
            c.codigo,
            f.nome,
            f.prontuario,
            e.data_retirada
        FROM emprestimos e
        JOIN chaves c ON c.id = e.chave_id
        JOIN funcionarios f ON f.id = e.funcionario_id
        WHERE c.codigo=? AND e.devolvido=0
    """,(codigo,)).fetchone()

    conn.close()

    if not dado:
        return jsonify({})

    return jsonify({
        "chave": dado["codigo"],
        "nome": dado["nome"],
        "id": dado["prontuario"],
        "data": dado["data_retirada"]
    })


if __name__ == "__main__":
    app.run(debug=True)
