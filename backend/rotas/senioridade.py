# ============================================================
# rotas/senioridade.py — CRUD de senioridades
# Descrição: mantém os níveis de experiência dos tatuadores.
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from mysql.connector import IntegrityError
from database import obter_conexao
from seguranca import verificar_token

router = APIRouter(prefix="/senioridade", tags=["Senioridade"], dependencies=[Depends(verificar_token)])
class SenioridadeDados(BaseModel):
    nome: str = Field(min_length=1, max_length=50)

# Lista os níveis de senioridade.
@router.get("")
def listar_senioridades():
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM senioridade ORDER BY idsenioridade")
        return cursor.fetchall()
    finally: cursor.close(); conexao.close()

# Busca um nível pelo ID.
@router.get("/{idsenioridade}")
def buscar_senioridade(idsenioridade: int):
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM senioridade WHERE idsenioridade=%s", (idsenioridade,)); item=cursor.fetchone()
        if not item: raise HTTPException(404, "Senioridade não encontrada.")
        return item
    finally: cursor.close(); conexao.close()

# Cadastra uma senioridade nova.
@router.post("", status_code=201)
def criar_senioridade(dados: SenioridadeDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("INSERT INTO senioridade (nome) VALUES (%s)", (dados.nome.strip(),)); conexao.commit()
        return {"mensagem":"Senioridade cadastrada.", "idsenioridade":cursor.lastrowid}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Já existe uma senioridade com esse nome.") from erro
    finally: cursor.close(); conexao.close()

# Atualiza o nome de uma senioridade.
@router.put("/{idsenioridade}")
def atualizar_senioridade(idsenioridade: int, dados: SenioridadeDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("UPDATE senioridade SET nome=%s WHERE idsenioridade=%s", (dados.nome.strip(), idsenioridade))
        if cursor.rowcount==0:
            cursor.execute("SELECT idsenioridade FROM senioridade WHERE idsenioridade=%s", (idsenioridade,))
            if not cursor.fetchone(): raise HTTPException(404, "Senioridade não encontrada.")
        conexao.commit(); return {"mensagem":"Senioridade atualizada."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Já existe uma senioridade com esse nome.") from erro
    finally: cursor.close(); conexao.close()

# Exclui a senioridade somente se nenhum tatuador a utilizar.
@router.delete("/{idsenioridade}")
def excluir_senioridade(idsenioridade: int):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("DELETE FROM senioridade WHERE idsenioridade=%s", (idsenioridade,))
        if cursor.rowcount==0: raise HTTPException(404, "Senioridade não encontrada.")
        conexao.commit(); return {"mensagem":"Senioridade excluída."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Não é possível excluir: existem tatuadores usando esta senioridade.") from erro
    finally: cursor.close(); conexao.close()
