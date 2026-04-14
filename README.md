# Sistema de Controle de Chaves – Claviculário

Sistema web para controle de empréstimo e devolução de chaves com validação de funcionário, controle de disponibilidade e registro em banco de dados SQLite.

---

# Requisitos

* Python 3.8 ou superior
* Pip instalado
* Navegador web
* Leitor de código de barras (opcional)

---

# Estrutura do Projeto

```
claviculario/
│
├── app.py
│
├── setup/
│   ├── create_database.py
│   └── insert_chaves.py
│
├── templates/
│   └── index.html
│
└── static/
    ├── style.css
    ├── script.js
    └── images/
```

---

# Instalação

## 1. Instalar dependências

No terminal, dentro da pasta do projeto:

```
pip install flask
```

---

## 2. Criar banco de dados

Execute o script de criação:

```
python setup/create_database.py
```

Este comando irá criar o arquivo:

```
database.db
```

---

## 3. Inserir chaves no banco

Execute:

```
python setup/insert_chaves.py
```

Isso irá cadastrar todas as chaves disponíveis no sistema.

---

## 4. Inserir funcionários

Antes de utilizar o sistema, é necessário cadastrar funcionários no banco.

Exemplo:

```
INSERT INTO funcionarios (prontuario, nome)
VALUES ('SP123', 'João Silva');
```

Você pode usar:

* DB Browser for SQLite
* sqlite3 via terminal
* script Python

---

# Executar o sistema

Rodar o servidor:

```
python app.py
```

Abrir no navegador:

```
http://127.0.0.1:5000
```

---

# Fluxo de utilização

## Retirada

1. Ler código do funcionário
2. Ler código da chave
3. Pressionar ENTER (automático com leitor)
4. Chave fica vermelha

## Devolução

1. Ler código do funcionário
2. Ler código da chave
3. Pressionar botão DEVOLVER
4. Chave volta para verde

---

# Regras do sistema

* Funcionário deve existir no banco
* Chave deve existir no banco
* Chave não pode estar emprestada
* Apenas o funcionário que retirou pode devolver
* Data e hora são registradas automaticamente
* Clique na chave vermelha mostra detalhes do empréstimo

---

# Banco de Dados

Tabelas:

* funcionarios
* chaves
* emprestimos

---

# Observações

* O sistema funciona offline
* SQLite não necessita instalação
* Compatível com leitor de código de barras
* Interface otimizada para uso rápido

---

# Inicialização rápida

```
pip install flask
python setup/create_database.py
python setup/insert_chaves.py
python app.py
```

Abrir:

```
http://127.0.0.1:5000
```
