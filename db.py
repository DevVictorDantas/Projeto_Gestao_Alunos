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
from typing import Optional
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

def executar_sql(sql, params=None, fetchone=False):
  with psycopg2.connect(**CONFIG) as con, con.cursor() as cur:
    cur.execute(sql, params)
    sql_limpo = sql.strip().upper()
    
    if sql_limpo.startswith(("CREATE", "INSERT", "UPDATE", "DELETE", "DROP")):
      con.commit()
      
      if sql_limpo.startswith("DELETE"):
        return cur.rowcount > 0
      
      return "Alteração realizada com sucesso"
    
    else:
      if fetchone:
          return  cur.fetchone()   
      else:
          return  cur.fetchall()
    

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
  lista_alunos = executar_sql(sql)
  print(lista_alunos)
  
# TODO: buscar_aluno(aluno_id)
#   SELECT de um aluno por id. Devolva None se não existir.

def buscar_aluno(id):
  sql = "SELECT nome, idade, matricula FROM alunos WHERE id = %s;"       
  aluno = executar_sql(sql, (id,))
  print(aluno)
  
# TODO: atualizar_aluno(id, **campos)
#   UPDATE parcial: atualize só os campos recebidos. Dica: nomes de coluna
#   podem entrar por f-string (são do seu código); VALORES vão com %s.

def atualizar_aluno(
  id: int, 
  nome: Optional[str] = None, 
  idade: Optional[int] = None, 
  matricula: Optional[str] = None, 
  media: Optional[float] = None
  ):  
  
  campos_atualizados = {
    "nome": nome,
    "idade": idade,
    "matricula": matricula,
    "media": media
  }
  
  campos_validos = {k: v for k, v in campos_atualizados.items() if v is not None}
  if not campos_validos:
    print("Nenhuma informação do aluno foi alterada")
    return False
  
  partes = [f"{campo} = %s" for campo in campos_validos.keys()]
  partes_sql = ", ".join(partes)
  
  sql = f"UPDATE alunos SET {partes_sql} WHERE id= %s;"
  
  entrada = list(campos_validos.values()) + [id]
  
  executar_sql(sql, entrada)

# TODO: excluir_aluno(id)
#   DELETE por id. Devolva True/False (dica: cur.rowcount > 0).

def excluir_aluno(id):
  sql = "DELETE FROM alunos WHERE id = %s;"
  executar_sql(sql, (id,))
  

# --------------------------------------------------------------------------
# CRUD de DISCIPLINAS  (Desafio 2)
# --------------------------------------------------------------------------
# TODO: inserir_disciplina, listar_disciplinas, buscar_disciplina,
#       excluir_disciplina — espelhando o CRUD de alunos.
def inserir_disciplina(nome, carga_horaria):
  sql = "INSERT INTO disciplinas (nome, carga_horaria) VALUES (%s, %s);"
  executar_sql(sql, (nome, carga_horaria))
  
def listar_disciplinas():
  sql = "SELECT * FROM disciplinas ORDER BY id ASC"
  lista_disciplinas = executar_sql(sql)
  print(lista_disciplinas)
  
def buscar_disciplina(id):
  sql = "SELECT nome, carga_horaria FROM disciplinas WHERE id = %s"       
  disciplina = executar_sql(sql, (id,))
  print(disciplina)
  
def atualizar_disciplina(
  id: int, 
  nome: Optional[str] = None, 
  carga_horaria: Optional[int] = None
):  
  
  campos_atualizados = {
    "nome": nome,
    "carga": carga_horaria
  }
  
  campos_validos = {k: v for k, v in campos_atualizados.items() if v is not None}
  if not campos_validos:
    print("Nenhuma informação do aluno foi alterada")
    return False
  
  partes = [f"{campo} = %s" for campo in campos_validos.keys()]
  partes_sql = ", ".join(partes)
  
  sql = f"UPDATE disciplinas SET {partes_sql} WHERE id= %s;"
  
  entrada = list(campos_validos.values()) + [id]
  
  executar_sql(sql, entrada)  
  
def excluir_disciplina(id):
  sql = "DELETE FROM disciplinas WHERE id = %s;"
  executar_sql(sql, (id,))

# --------------------------------------------------------------------------
# MATRÍCULAS — relacionamento aluno <-> disciplina  (Desafio 3)
# --------------------------------------------------------------------------
# TODO: matricular(aluno_id, disciplina_id)
#   INSERT na tabela matriculas. Dica: "ON CONFLICT DO NOTHING" evita erro se
#   a matrícula já existir.
#
def matricular_aluno(aluno_id, disciplina_id):
  sql = "INSERT INTO matriculas (aluno_id, disciplina_id) VALUES (%s, %s) ON CONFLICT DO NOTHING;"
  executar_sql(sql, (aluno_id, disciplina_id))
  
# TODO: disciplinas_do_aluno(aluno_id)
#   Liste as disciplinas em que o aluno está matriculado. Dica: use JOIN entre
#   disciplinas e matriculas.
def disciplinas_do_aluno(aluno_id):
  sql = "SELECT disciplinas.nome FROM matriculas JOIN disciplinas ON disciplinas.id = matriculas.disciplina_id WHERE matriculas.aluno_id = %s;"
  disciplinas_matriculadas = executar_sql(sql, (aluno_id,))
  print(disciplinas_matriculadas)