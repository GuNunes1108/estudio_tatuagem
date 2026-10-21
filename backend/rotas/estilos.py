# ============================================================
# rotas/estilos.py — CRUD de estilos de tatuagem
# Descrição: mantém a lista de estilos disponíveis no estúdio.
# ============================================================
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from mysql.connector import IntegrityError
from database import obter_conexao
from seguranca import verificar_token

router = APIRouter(prefix="/estilos", tags=["Estilos"], dependencies=[Depends(verificar_token)])
class EstiloDados(BaseModel):
    descricao: str = Field(min_length=1, max_length=50)

# Lista os estilos cadastrados.
@router.get("")
def listar_estilos():
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try: cursor.execute("SELECT * FROM estilo ORDER BY descricao"); return cursor.fetchall()
    finally: cursor.close(); conexao.close()

# Busca um estilo pelo ID.
@router.get("/{idestilo}")
def buscar_estilo(idestilo: int):
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM estilo WHERE idestilo=%s", (idestilo,)); item=cursor.fetchone()
        if not item: raise HTTPException(404, "Estilo não encontrado.")
        return item
    finally: cursor.close(); conexao.close()

# Cadastra um estilo novo.
@router.post("", status_code=201)
def criar_estilo(dados: EstiloDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("INSERT INTO estilo (descricao) VALUES (%s)", (dados.descricao.strip(),)); conexao.commit()
        return {"mensagem":"Estilo cadastrado.", "idestilo":cursor.lastrowid}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Esse estilo já existe.") from erro
    finally: cursor.close(); conexao.close()

# Atualiza a descrição de um estilo.
@router.put("/{idestilo}")
def atualizar_estilo(idestilo: int, dados: EstiloDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("UPDATE estilo SET descricao=%s WHERE idestilo=%s", (dados.descricao.strip(), idestilo))
        if cursor.rowcount==0:
            cursor.execute("SELECT idestilo FROM estilo WHERE idestilo=%s", (idestilo,))
            if not cursor.fetchone(): raise HTTPException(404, "Estilo não encontrado.")
        conexao.commit(); return {"mensagem":"Estilo atualizado."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Esse estilo já existe.") from erro
    finally: cursor.close(); conexao.close()

# Exclui um estilo e suas associações com tatuadores são removidas pelo banco.
@router.delete("/{idestilo}")
def excluir_estilo(idestilo: int):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("DELETE FROM estilo WHERE idestilo=%s", (idestilo,))
        if cursor.rowcount==0: raise HTTPException(404, "Estilo não encontrado.")
        conexao.commit(); return {"mensagem":"Estilo excluído."}
    finally: cursor.close(); conexao.close()
