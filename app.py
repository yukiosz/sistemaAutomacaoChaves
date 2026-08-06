from flask import Flask, render_template, request, jsonify, redirect, url_for, Response
import sqlite3
from datetime import datetime
import csv
import io
import re

app = Flask(__name__)

DATABASE = "database.db"


def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/admin")
def admin():
    return render_template("admin.html")

@app.route("/estado")
def estado():
    conn = get_db()

    dados = conn.execute("""
        SELECT c.codigo, f.nome
        FROM emprestimos e
        JOIN chaves c ON c.id = e.chave_id
        JOIN funcionarios f ON f.id = e.retirado_por
        WHERE e.data_devolucao IS NULL
    """).fetchall()

    conn.close()

    return jsonify([
        {"codigo": d["codigo"], "nome": d["nome"]}
        for d in dados
    ])

def normalizar_prontuario(valor):
    valor = valor.strip().upper()

    if re.match(r'^[A-Z]{2}[A-Z0-9]+$', valor):
        return {"tipo": "completo", "valor": valor[2:]}

    if valor.startswith("01100"):
        return {"tipo": "parcial", "valor": valor[5:]}

    return {"tipo": "completo", "valor": valor}


@app.route("/registrar", methods=["POST"])
def registrar():
    data = request.json

    prontuario_input = data["id"]
    codigo = data["chave"]
    tipo = data["tipo"]

    conn = get_db()

    # 🔎 NORMALIZAÇÃO DO PRONTUÁRIO
    info = normalizar_prontuario(prontuario_input)

    if info["tipo"] == "completo":
        funcionario = conn.execute(
            "SELECT * FROM funcionarios WHERE prontuario=?",
            (info["valor"],)
        ).fetchone()

    else:
        resultados = conn.execute(
            "SELECT * FROM funcionarios WHERE prontuario LIKE ?",
            (info["valor"] + "%",)
        ).fetchall()

        if len(resultados) == 0:
            funcionario = None

        elif len(resultados) > 1:
            conn.close()
            return jsonify({
                "status": "erro",
                "mensagem": "Múltiplos funcionários encontrados"
            })

        else:
            funcionario = resultados[0]

    # ❌ funcionário não encontrado
    if not funcionario:
        conn.close()
        return jsonify({
            "status": "erro",
            "mensagem": "Funcionário não encontrado"
        })

    # 🔎 busca chave
    chave = conn.execute(
        "SELECT * FROM chaves WHERE codigo=?",
        (codigo,)
    ).fetchone()

    if not chave:
        conn.close()
        return jsonify({
            "status": "erro",
            "mensagem": "Chave não encontrada"
        })

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # =========================
    # RETIRADA
    # =========================
    if tipo == "RETIRADA":

        ativo = conn.execute("""
            SELECT * FROM emprestimos
            WHERE chave_id=? AND data_devolucao IS NULL
        """, (chave["id"],)).fetchone()

        if ativo:
            conn.close()
            return jsonify({
                "status": "erro",
                "mensagem": "Chave não disponível"
            })

        conn.execute("""
            INSERT INTO emprestimos
            (chave_id, retirado_por, data_retirada)
            VALUES (?,?,?)
        """, (chave["id"], funcionario["id"], agora))

    # =========================
    # DEVOLUÇÃO
    # =========================
    else:

        emprestimo = conn.execute("""
            SELECT id
            FROM emprestimos
            WHERE chave_id=? AND data_devolucao IS NULL
        """, (chave["id"],)).fetchone()

        if not emprestimo:
            conn.close()
            return jsonify({
                "status": "erro",
                "mensagem": "Chave não está emprestada"
            })

        conn.execute("""
            UPDATE emprestimos
            SET devolvido_por=?, data_devolucao=?
            WHERE id=?
        """, (funcionario["id"], agora, emprestimo["id"]))

    conn.commit()
    conn.close()

    return jsonify({"status": "ok"})

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
        JOIN funcionarios f ON f.id = e.retirado_por
        WHERE c.codigo=? AND e.data_devolucao IS NULL
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


@app.route("/exportar")
def exportar():

    conn = get_db()

    dados = conn.execute("""
        SELECT 
            e.id,
            fr.prontuario as retirado_prontuario,
            fr.nome as retirado_nome,
            fd.prontuario as devolvido_prontuario,
            fd.nome as devolvido_nome,
            c.codigo,
            e.data_retirada,
            e.data_devolucao
        FROM emprestimos e
        JOIN funcionarios fr ON fr.id = e.retirado_por
        LEFT JOIN funcionarios fd ON fd.id = e.devolvido_por
        JOIN chaves c ON c.id = e.chave_id
        WHERE e.exportado = 0
        ORDER BY e.data_retirada
    """).fetchall()

    if not dados:
        conn.close()
        return redirect(url_for("index", msg="sem_dados"))

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')

    writer.writerow([
        "prontuario-retirada",
        "nome-retirada",
        "prontuario-devolucao",
        "nome-devolucao",
        "codigo-chave",
        "horario-retirada",
        "horario-devolucao"
    ])

    ids_exportados = []

    for row in dados:
        writer.writerow([
            row["retirado_prontuario"],
            row["retirado_nome"],
            row["devolvido_prontuario"] or "",
            row["devolvido_nome"] or "",
            row["codigo"],
            row["data_retirada"],
            row["data_devolucao"]
        ])
        ids_exportados.append(row["id"])

    conn.executemany(
        "UPDATE emprestimos SET exportado = 1 WHERE id = ?",
        [(i,) for i in ids_exportados]
    )

    conn.commit()
    conn.close()

    agora = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    nome_arquivo = f"emprestimos_{agora}.csv"

    return Response(
        u'\ufeff' + output.getvalue(),
        mimetype="text/csv; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename={nome_arquivo}"
        }
    )


if __name__ == "__main__":
    app.run(debug=True)
