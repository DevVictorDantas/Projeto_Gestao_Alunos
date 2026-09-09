"""
CAMADA DE ROTAS (main.py)  —  ESQUELETO, implemente você mesmo
==============================================================

É o "cardápio" da API: cada rota é um endpoint. Mantenha as rotas FINAS —
elas só devem:
  1. receber/validar a entrada (via schemas do Pydantic);
  2. chamar UMA função do db.py;
  3. traduzir o resultado em resposta HTTP (status code + corpo).

Nenhuma regra de negócio ou SQL mora aqui.

Depois de implementar, rode (com o venv ativado e o PostgreSQL no ar):
    uvicorn main:app --reload
E explore em: http://127.0.0.1:8000/docs
"""

# DICA — o que você vai importar:
from typing import List
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import RedirectResponse
from psycopg2.errors import UniqueViolation   # para tratar duplicidade
import db
#from schemas import AlunoEntrada, AlunoAtualizacao, AlunoSaida  # e disciplinas


# TODO: crie a aplicação -> app = FastAPI(title="Gestão de Alunos")
#       (a variável PRECISA se chamar `app` — é o que o uvicorn procura.)
app = FastAPI(title="Gestão de Alunos", version="0.1.0")

# TODO: registre o startup para criar as tabelas:
#   @app.on_event("startup")
#   def ao_iniciar():
#       db.criar_tabelas()
@app.on_event("startup")
def ao_iniciar():
    db.criar_tabelas()

# TODO: GET /  -> uma mensagem de boas-vindas (ex.: aponte para /docs).
@app.get("/", include_in_schema=False)
def redirecionar_docs():
    return RedirectResponse(url="/docs")


# ========================= ALUNOS =========================
# Verbo/rota/status que você deve implementar (o "coração" do REST):
#
#   POST   /alunos            -> 201 Created; devolva o objeto criado.
#                                Trate matrícula duplicada com 409 Conflict
#                                (except UniqueViolation).
#   GET    /alunos            -> 200; lista. (Filtros = Desafio 1.)
#   GET    /alunos/{id}       -> 200 com o aluno, ou 404 se não existir.
#   PATCH  /alunos/{id}       -> 200; atualização parcial. Dica:
#                                payload.model_dump(exclude_unset=True).
#   DELETE /alunos/{id}       -> 204 No Content; 404 se não existir.
#
# Lembre: use response_model=AlunoSaida e status_code=status.HTTP_201_CREATED etc.
@app.get("/alunos")
def listar_alunos():
    return db.listar_alunos()

# ========================= DISCIPLINAS (Desafio 2) =========================
# POST /disciplinas (201, 409 se duplicado) · GET /disciplinas (200) ·
# DELETE /disciplinas/{id} (204, 404 se não existir).


# ========================= MATRÍCULAS (Desafio 3) =========================
# POST /alunos/{aluno_id}/matricular/{disciplina_id}
#      -> 404 se aluno OU disciplina não existir; senão matricula.
# GET  /alunos/{aluno_id}/disciplinas
#      -> lista as disciplinas do aluno (usa db.disciplinas_do_aluno / JOIN).
