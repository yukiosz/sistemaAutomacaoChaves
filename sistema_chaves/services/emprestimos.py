import csv
import io
import re
import sqlite3
from datetime import datetime


def normalizar_prontuario(valor):
    valor = valor.strip().upper()

    if re.match(r'^[A-Z]{2}[A-Z0-9]+$', valor):
        return {"tipo": "completo", "valor": valor[2:]}

    if valor.startswith("01100"):
        return {"tipo": "parcial", "valor": valor[5:]}

    return {"tipo": "completo", "valor": valor}


def listar_chaves_emprestadas(conn):
    dados = conn.execute("""
        SELECT c.codigo, f.nome
        FROM emprestimos e
        JOIN chaves c ON c.id = e.chave_id
        JOIN funcionarios f ON f.id = e.retirado_por
        WHERE e.data_devolucao IS NULL
    """).fetchall()

    return [{"codigo": dado["codigo"], "nome": dado["nome"]} for dado in dados]


def buscar_funcionario(conn, prontuario_input):
    info = normalizar_prontuario(prontuario_input)

    if info["tipo"] == "completo":
        return conn.execute(
            "SELECT * FROM funcionarios WHERE prontuario=?", (info["valor"],)
        ).fetchone(), None

    resultados = conn.execute(
        "SELECT * FROM funcionarios WHERE prontuario LIKE ?", (info["valor"] + "%",)
    ).fetchall()

    if not resultados:
        return None, None
    if len(resultados) > 1:
        return None, "Múltiplos funcionários encontrados"
    return resultados[0], None


def cadastrar_funcionario(conn, prontuario, nome):
    prontuario = (prontuario or "").strip().upper()
    nome = (nome or "").strip()

    if not prontuario or not nome:
        return {"status": "erro", "mensagem": "Informe o prontuário e o nome do funcionário."}

    try:
        conn.execute(
            "INSERT INTO funcionarios (prontuario, nome) VALUES (?, ?)",
            (prontuario, nome),
        )
        conn.commit()
    except sqlite3.IntegrityError as erro:
        # A restrição UNIQUE do banco evita prontuários duplicados.
        if "UNIQUE constraint failed" in str(erro):
            return {"status": "erro", "mensagem": "Já existe um funcionário com esse prontuário."}
        raise

    return {"status": "ok", "mensagem": "Funcionário cadastrado com sucesso."}


def registrar_emprestimo(conn, dados):
    funcionario, erro = buscar_funcionario(conn, dados["id"])
    if erro:
        return {"status": "erro", "mensagem": erro}
    if not funcionario:
        return {"status": "erro", "mensagem": "Funcionário não encontrado"}

    chave = conn.execute(
        "SELECT * FROM chaves WHERE codigo=?", (dados["chave"],)
    ).fetchone()
    if not chave:
        return {"status": "erro", "mensagem": "Chave não encontrada"}

    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    if dados["tipo"] == "RETIRADA":
        ativo = conn.execute("""
            SELECT id FROM emprestimos
            WHERE chave_id=? AND data_devolucao IS NULL
        """, (chave["id"],)).fetchone()

        if ativo:
            return {"status": "erro", "mensagem": "Chave não disponível"}

        conn.execute("""
            INSERT INTO emprestimos (chave_id, retirado_por, data_retirada)
            VALUES (?,?,?)
        """, (chave["id"], funcionario["id"], agora))
    else:
        emprestimo = conn.execute("""
            SELECT id FROM emprestimos
            WHERE chave_id=? AND data_devolucao IS NULL
        """, (chave["id"],)).fetchone()

        if not emprestimo:
            return {"status": "erro", "mensagem": "Chave não está emprestada"}

        conn.execute("""
            UPDATE emprestimos
            SET devolvido_por=?, data_devolucao=?
            WHERE id=?
        """, (funcionario["id"], agora, emprestimo["id"]))

    conn.commit()
    return {"status": "ok"}


def detalhes_emprestimo(conn, codigo):
    dado = conn.execute("""
        SELECT c.codigo, f.nome, f.prontuario, e.data_retirada
        FROM emprestimos e
        JOIN chaves c ON c.id = e.chave_id
        JOIN funcionarios f ON f.id = e.retirado_por
        WHERE c.codigo=? AND e.data_devolucao IS NULL
    """, (codigo,)).fetchone()

    if not dado:
        return {}

    return {
        "chave": dado["codigo"], "nome": dado["nome"],
        "id": dado["prontuario"], "data": dado["data_retirada"],
    }


def exportar_emprestimos(conn, somente_nao_exportados=True):
    filtro_exportacao = "WHERE e.exportado = 0" if somente_nao_exportados else ""
    dados = conn.execute(f"""
        SELECT e.id, fr.prontuario AS retirado_prontuario,
               fr.nome AS retirado_nome, fd.prontuario AS devolvido_prontuario,
               fd.nome AS devolvido_nome, c.codigo, e.data_retirada, e.data_devolucao
        FROM emprestimos e
        JOIN funcionarios fr ON fr.id = e.retirado_por
        LEFT JOIN funcionarios fd ON fd.id = e.devolvido_por
        JOIN chaves c ON c.id = e.chave_id
        {filtro_exportacao}
        ORDER BY e.data_retirada
    """).fetchall()

    if not dados:
        return None

    output = io.StringIO()
    writer = csv.writer(output, delimiter=';')
    writer.writerow([
        "prontuario-retirada", "nome-retirada", "prontuario-devolucao",
        "nome-devolucao", "codigo-chave", "horario-retirada", "horario-devolucao",
    ])

    for dado in dados:
        writer.writerow([
            dado["retirado_prontuario"], dado["retirado_nome"],
            dado["devolvido_prontuario"] or "", dado["devolvido_nome"] or "",
            dado["codigo"], dado["data_retirada"], dado["data_devolucao"],
        ])

    if somente_nao_exportados:
        conn.executemany(
            "UPDATE emprestimos SET exportado = 1 WHERE id = ?",
            [(dado["id"],) for dado in dados],
        )
        conn.commit()

    nome_arquivo = datetime.now().strftime("emprestimos_%Y-%m-%d_%H-%M-%S.csv")
    return output.getvalue(), nome_arquivo
