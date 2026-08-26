"""
CAMADA DE BANCO (db.py)  —  ESQUELETO, implemente você mesmo
============================================================

Esta é a ÚNICA parte do projeto que "fala SQL". As rotas (main.py) nunca
escrevem SQL: elas chamam as funções daqui. Essa separação em camadas é o
coração do módulo.

REGRA DE OURO (segurança): os VALORES que vêm do cliente vão SEMPRE como %s
+ tupla de parâmetros. Nunca concatene dados do usuário na string SQL
(isso abre SQL Injection).

Ordem sugerida de implementação:
  1. Configuração + conectar()      -> abrir conexão com o PostgreSQL
  2. criar_tabelas()                -> criar alunos, disciplinas, matriculas
  3. CRUD de alunos                 -> inserir / listar / buscar / atualizar / excluir
  4. CRUD de disciplinas            (Desafio 2)
  5. matrículas + JOIN              (Desafio 3)

O modelo de dados (as 3 tabelas) está definido em `esquema.sql` — use como
referência ao escrever criar_tabelas().
"""

# DICA — bibliotecas que você provavelmente vai usar:
#   import os
#   import psycopg2
#   from psycopg2.extras import RealDictCursor   # faz o banco devolver dict, não tupla
#   from dotenv import load_dotenv               # lê o arquivo .env
import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
# TODO: carregue as variáveis do .env (load_dotenv) e monte um CONFIG lendo
#       DB_HOST, DB_NAME, DB_USER, DB_PASSWORD (dica: os.getenv com um padrão).

load_dotenv() 

CONFIG = {
  "host": os.getenv("DB_HOST"),
  "database": os.getenv("DB_NAME"),
  "user": os.getenv("DB_USER"),
  "password": os.getenv("DB_PASSWORD"),
  "port": os.getenv("DB_PORT"),
}

# TODO: def conectar():
#   Abra e devolva uma conexão psycopg2 usando o CONFIG.
#   Dica: passe cursor_factory=RealDictCursor para as linhas virem como dicts.
def conectar():
  conexao = psycopg2.connect(
    host = CONFIG["host"],
    database = CONFIG["name"],
    user = CONFIG["user"],
    password = CONFIG["password"],
    port = CONFIG["port"],
    cursor_factory=RealDictCursor
  )
  return conexao

def executar_sql(sql, params=None):
  with psycopg2.connect(**CONFIG) as con, con.cursor() as cur:
    
    sql_limpo = sql.strip().upper()    

    if sql_limpo.startswith(("INSERT")):
      cur.execute(sql, params)
    else:
      cur.execute(sql)
    
    if sql_limpo.startswith(("CREATE", "INSERT", "UPDATE", "DELETE", "DROP")):
      con.commit()
      return "Alteração realizada com sucesso"
    else:
      dados = cur.fetchall()
      print("Os alunos são: ", dados)
      return dados

# TODO: def criar_tabelas():
#   Crie as 3 tabelas com "CREATE TABLE IF NOT EXISTS ..." (veja esquema.sql).
#   Esta função é chamada no startup da API (main.py).
def criar_tabelas():
  sql = """ CREATE TABLE IF NOT EXISTS alunos (
    id        SERIAL PRIMARY KEY,
    nome      VARCHAR(100) NOT NULL,
    idade     INTEGER,
    matricula VARCHAR(20) UNIQUE NOT NULL,
    media     NUMERIC(4,2) DEFAULT 0
  );

    CREATE TABLE IF NOT EXISTS disciplinas (
    id            SERIAL PRIMARY KEY,
    nome          VARCHAR(100) NOT NULL UNIQUE,
    carga_horaria INTEGER NOT NULL
  );

    CREATE TABLE IF NOT EXISTS matriculas (
    id            SERIAL PRIMARY KEY,   
    aluno_id      INTEGER REFERENCES alunos(id) ON DELETE CASCADE,
    disciplina_id INTEGER REFERENCES disciplinas(id) ON DELETE CASCADE,
    UNIQUE (aluno_id, disciplina_id)     -- mesma matrícula só uma vez
  );"""
  executar_sql(sql)

# --------------------------------------------------------------------------
# CRUD de ALUNOS
# --------------------------------------------------------------------------
# TODO: inserir_aluno(nome, idade, matricula, media=0)
#   INSERT na tabela alunos. Dica: use "RETURNING *" para já receber de volta
#   a linha criada (com o id gerado pelo banco).

def inserir_aluno(nome, idade, matricula, media=0):
  sql = "INSERT INTO alunos (nome, idade, matricula, media) VALUES (%s, %s, %s, %s) RETURNING *"
  executar_sql(sql, (nome, idade, matricula, media))
#
# TODO: listar_alunos()
#   SELECT de todos os alunos, ordenados por id.
#   (Fazer aceitar filtros é o Desafio 1 — comece simples.)

def listar_alunos():
  sql = "SELECT * FROM alunos ORDER BY id ASC"
  executar_sql(sql)
  
# TODO: buscar_aluno(aluno_id)
#   SELECT de um aluno por id. Devolva None se não existir.

def buscar_aluno(aluno_id):
  sql = "SELECT * FROM alunos WHERE aluno_id = %s"
  dados_aluno = (aluno_id) 
  return aluno

  executar_sql(sql, aluno_id)
  
# TODO: atualizar_aluno(aluno_id, **campos)
#   UPDATE parcial: atualize só os campos recebidos. Dica: nomes de coluna
#   podem entrar por f-string (são do seu código); VALORES vão com %s.

#def atualizar_aluno(aluno_id):
  

# TODO: excluir_aluno(aluno_id)
#   DELETE por id. Devolva True/False (dica: cur.rowcount > 0).


# --------------------------------------------------------------------------
# CRUD de DISCIPLINAS  (Desafio 2)
# --------------------------------------------------------------------------
# TODO: inserir_disciplina, listar_disciplinas, buscar_disciplina,
#       excluir_disciplina — espelhando o CRUD de alunos.


# --------------------------------------------------------------------------
# MATRÍCULAS — relacionamento aluno <-> disciplina  (Desafio 3)
# --------------------------------------------------------------------------
# TODO: matricular(aluno_id, disciplina_id)
#   INSERT na tabela matriculas. Dica: "ON CONFLICT DO NOTHING" evita erro se
#   a matrícula já existir.
#
# TODO: disciplinas_do_aluno(aluno_id)
#   Liste as disciplinas em que o aluno está matriculado. Dica: use JOIN entre
#   disciplinas e matriculas.
