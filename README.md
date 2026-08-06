# Sistema de Controle de Chaves

Aplicação Flask para registrar a retirada e a devolução de chaves, usando SQLite.

## Requisitos e execução

Requer Python 3.8+ e Flask.

```bash
pip install flask
python app.py
```

Abra `http://127.0.0.1:5000` no navegador. Para criar uma base nova, execute antes:

```bash
python setup/create_database.py
python setup/insert_chaves.py
```

## Estrutura

```text
app.py                         # ponto de entrada do servidor
sistema_chaves/
  __init__.py                  # fábrica e configuração da aplicação Flask
  database.py                  # conexão com o SQLite
  routes.py                    # rotas HTTP e respostas da interface
  services/
    emprestimos.py             # regras de retirada, devolução e exportação
templates/                     # páginas HTML
static/                        # JavaScript, CSS e imagens
setup/                         # criação e carga inicial do banco
database.db                    # dados locais da aplicação
```

## Organização das responsabilidades

- `routes.py` não contém regras de negócio: recebe a requisição e chama o serviço adequado.
- `services/emprestimos.py` concentra as regras de funcionários, chaves e empréstimos. Novas regras do fluxo devem ser adicionadas aqui.
- `database.py` é o único ponto de definição da localização e abertura do banco.
- `app.py` somente inicializa o sistema, preservando o comando `python app.py`.

As URLs públicas continuam as mesmas: `/`, `/admin`, `/estado`, `/registrar`, `/info/<codigo>` e `/exportar`.
