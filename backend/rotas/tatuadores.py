# ============================================================
# rotas/tatuadores.py — CRUD de tatuadores e relação com estilos
# Descrição: gerencia tatuadores, senioridade e estilos dominados.
# ============================================================
from datetime import date
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from mysql.connector import IntegrityError
from database import obter_conexao
from seguranca import verificar_token

router = APIRouter(prefix="/tatuadores", tags=["Tatuadores"], dependencies=[Depends(verificar_token)])
class TatuadorDados(BaseModel):
    nometatuador: str = Field(min_length=1, max_length=100)
    cpf: str = Field(pattern=r"^\d{11}$")
    email: Optional[str] = Field(default=None, max_length=100)
    telefone: Optional[str] = Field(default=None, max_length=20)
    datacontratacao: Optional[date] = None
    idsenioridade: int = Field(gt=0)
class EstilosTatuadorDados(BaseModel):
    estilos: List[int]

# Lista tatuadores com o nome da senioridade e dos estilos associados.
@router.get("")
def listar_tatuadores():
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT t.*, s.nome AS senioridade,
            COALESCE(GROUP_CONCAT(DISTINCT e.descricao ORDER BY e.descricao SEPARATOR ', '), '') AS estilos
            FROM tatuador t JOIN senioridade s ON s.idsenioridade=t.idsenioridade
            LEFT JOIN tatuador_estilo te ON te.idtatuador=t.idtatuador
            LEFT JOIN estilo e ON e.idestilo=te.idestilo
            GROUP BY t.idtatuador ORDER BY t.nometatuador""")
        return cursor.fetchall()
    finally: cursor.close(); conexao.close()

# Busca um tatuador por ID com seu nível de senioridade.
@router.get("/{idtatuador}")
def buscar_tatuador(idtatuador: int):
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT t.*, s.nome AS senioridade FROM tatuador t JOIN senioridade s ON s.idsenioridade=t.idsenioridade WHERE t.idtatuador=%s", (idtatuador,)); item=cursor.fetchone()
        if not item: raise HTTPException(404, "Tatuador não encontrado.")
        return item
    finally: cursor.close(); conexao.close()

# Cadastra um tatuador e devolve seu ID para relacionar estilos depois.
@router.post("", status_code=201)
def criar_tatuador(dados: TatuadorDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("INSERT INTO tatuador (nometatuador, cpf, email, telefone, datacontratacao, idsenioridade) VALUES (%s,%s,%s,%s,%s,%s)", (dados.nometatuador.strip(), dados.cpf, dados.email, dados.telefone, dados.datacontratacao, dados.idsenioridade))
        conexao.commit(); return {"mensagem":"Tatuador cadastrado.", "idtatuador":cursor.lastrowid}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "CPF duplicado ou senioridade inexistente.") from erro
    finally: cursor.close(); conexao.close()

# Atualiza os dados de um tatuador existente.
@router.put("/{idtatuador}")
def atualizar_tatuador(idtatuador: int, dados: TatuadorDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("UPDATE tatuador SET nometatuador=%s, cpf=%s, email=%s, telefone=%s, datacontratacao=%s, idsenioridade=%s WHERE idtatuador=%s", (dados.nometatuador.strip(), dados.cpf, dados.email, dados.telefone, dados.datacontratacao, dados.idsenioridade, idtatuador))
        if cursor.rowcount==0:
            cursor.execute("SELECT idtatuador FROM tatuador WHERE idtatuador=%s", (idtatuador,))
            if not cursor.fetchone(): raise HTTPException(404, "Tatuador não encontrado.")
        conexao.commit(); return {"mensagem":"Tatuador atualizado."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "CPF duplicado ou senioridade inexistente.") from erro
    finally: cursor.close(); conexao.close()

# Exclui um tatuador quando não há agendamentos vinculados.
@router.delete("/{idtatuador}")
def excluir_tatuador(idtatuador: int):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("DELETE FROM tatuador WHERE idtatuador=%s", (idtatuador,))
        if cursor.rowcount==0: raise HTTPException(404, "Tatuador não encontrado.")
        conexao.commit(); return {"mensagem":"Tatuador excluído."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Não é possível excluir: o tatuador possui agendamentos.") from erro
    finally: cursor.close(); conexao.close()

# Lista os estilos já associados a um tatuador.
@router.get("/{idtatuador}/estilos")
def listar_estilos_tatuador(idtatuador: int):
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT idestilo FROM tatuador_estilo WHERE idtatuador=%s", (idtatuador,))
        return [item["idestilo"] for item in cursor.fetchall()]
    finally: cursor.close(); conexao.close()

# Substitui a lista de estilos de um tatuador em uma transação.
@router.put("/{idtatuador}/estilos")
def salvar_estilos_tatuador(idtatuador: int, dados: EstilosTatuadorDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("SELECT idtatuador FROM tatuador WHERE idtatuador=%s", (idtatuador,))
        if not cursor.fetchone(): raise HTTPException(404, "Tatuador não encontrado.")
        conexao.start_transaction()
        cursor.execute("DELETE FROM tatuador_estilo WHERE idtatuador=%s", (idtatuador,))
        for idestilo in sorted(set(dados.estilos)):
            cursor.execute("INSERT INTO tatuador_estilo (idtatuador, idestilo, dataestilo) VALUES (%s,%s,%s)", (idtatuador, idestilo, date.today()))
        conexao.commit(); return {"mensagem":"Estilos do tatuador atualizados."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "Um ou mais IDs de estilo não existem.") from erro
    finally: cursor.close(); conexao.close()
