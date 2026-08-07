from functools import wraps

from flask import Blueprint, Response, flash, jsonify, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash

from .database import get_db
from .services.emprestimos import (
    detalhes_emprestimo,
    cadastrar_funcionario,
    exportar_emprestimos,
    listar_chaves_emprestadas,
    registrar_emprestimo,
)


web = Blueprint("web", __name__)


def exige_admin(view):
    @wraps(view)
    def protegida(*args, **kwargs):
        if "admin_id" not in session:
            return redirect(url_for("web.admin"))
        return view(*args, **kwargs)
    return protegida


@web.route("/")
def index():
    return render_template("index.html")


@web.route("/admin", methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        prontuario = request.form.get("prontuario", "").strip().upper()
        senha = request.form.get("senha", "")
        conn = get_db()
        try:
            administrador = conn.execute(
                "SELECT * FROM administradores WHERE prontuario = ?", (prontuario,)
            ).fetchone()
        finally:
            conn.close()

        if administrador and check_password_hash(administrador["senha_hash"], senha):
            session.clear()
            session["admin_id"] = administrador["id"]
            session["admin_nome"] = administrador["nome"]
            return redirect(url_for("web.painel_admin"))
        flash("Prontuário ou senha inválidos.", "erro")

    if "admin_id" in session:
        return redirect(url_for("web.painel_admin"))
    return render_template("admin_login.html")


@web.route("/admin/painel")
@exige_admin
def painel_admin():
    return render_template("admin.html", nome_admin=session.get("admin_nome"))


@web.route("/admin/funcionarios", methods=["POST"])
@exige_admin
def cadastrar_novo_funcionario():
    conn = get_db()
    try:
        resultado = cadastrar_funcionario(
            conn, request.form.get("prontuario"), request.form.get("nome")
        )
    finally:
        conn.close()
    flash(resultado["mensagem"], "sucesso" if resultado["status"] == "ok" else "erro")
    return redirect(url_for("web.painel_admin"))


@web.route("/admin/sair", methods=["POST"])
@exige_admin
def sair_admin():
    session.clear()
    return redirect(url_for("web.admin"))


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
@exige_admin
def exportar():
    conn = get_db()
    try:
        resultado = exportar_emprestimos(conn, somente_nao_exportados=True)
    finally:
        conn.close()

    if not resultado:
        flash("Não há novos registros para exportar.", "erro")
        return redirect(url_for("web.painel_admin"))

    conteudo, nome_arquivo = resultado
    return Response(
        "\ufeff" + conteudo,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )


@web.route("/exportar/todos")
@exige_admin
def exportar_todos():
    conn = get_db()
    try:
        resultado = exportar_emprestimos(conn, somente_nao_exportados=False)
    finally:
        conn.close()

    if not resultado:
        flash("Não há registros para exportar.", "erro")
        return redirect(url_for("web.painel_admin"))

    conteudo, nome_arquivo = resultado
    return Response(
        "\ufeff" + conteudo,
        mimetype="text/csv; charset=utf-8",
        headers={"Content-Disposition": f"attachment; filename={nome_arquivo}"},
    )
