from flask import Blueprint, Response, jsonify, redirect, render_template, request, url_for

from .database import get_db
from .services.emprestimos import (
    detalhes_emprestimo,
    exportar_emprestimos,
    listar_chaves_emprestadas,
    registrar_emprestimo,
)


web = Blueprint("web", __name__)


@web.route("/")
def index():
    return render_template("index.html")


@web.route("/admin")
def admin():
    return render_template("admin.html")


@web.route("/estado")
def estado():
    conn = get_db()
    try:
        return jsonify(listar_chaves_emprestadas(conn))
    finally:
        conn.close()


@web.route("/registrar", methods=["POST"])
def registrar():
    conn = get_db()
    try:
        return jsonify(registrar_emprestimo(conn, request.json))
    finally:
        conn.close()


@web.route("/info/<codigo>")
def info(codigo):
    conn = get_db()
    try:
        return jsonify(detalhes_emprestimo(conn, codigo))
    finally:
        conn.close()


@web.route("/exportar")
def exportar():
    conn = get_db()
    try:
        resultado = exportar_emprestimos(conn)
    finally:
        conn.close()

    if not resultado:
        return redirect(url_for("web.index", msg="sem_dados"))

    conteudo, nome_arquivo = resultado
    return Response(
        "\ufeff" + conteudo,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )
