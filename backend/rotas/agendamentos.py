# ============================================================
# rotas/agendamentos.py — CRUD de agendamentos e upload de desenho
# Descrição: liga cliente e tatuador a uma data, hora e desenho opcional.
# ============================================================
from datetime import date, time
from decimal import Decimal
from pathlib import Path
from uuid import uuid4
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from pydantic import BaseModel, Field
from mysql.connector import IntegrityError
from database import obter_conexao
from seguranca import verificar_token

router = APIRouter(prefix="/agendamentos", tags=["Agendamentos"], dependencies=[Depends(verificar_token)])
PASTA_UPLOADS = Path(__file__).resolve().parents[1] / "uploads"
PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)
EXTENSOES_PERMITIDAS = {".png", ".jpg", ".jpeg", ".webp"}
LIMITE_BYTES = 5 * 1024 * 1024
class AgendamentoDados(BaseModel):
    idcliente: int = Field(gt=0)
    idtatuador: int = Field(gt=0)
    dataagendamento: date
    horaagendamento: time
    descricaotatuagem: Optional[str] = None
    valortatuagem: Optional[Decimal] = Field(default=None, ge=0, max_digits=10, decimal_places=2)
    status: Optional[str] = None

# Converte a hora para formato simples e padroniza a resposta da API.
def normalizar_agendamento(item):
    if item and item.get("horaagendamento"):
        item["horaagendamento"] = item["horaagendamento"].strftime("%H:%M")
    return item

# Lista agendamentos com os nomes do cliente e do tatuador.
@router.get("")
def listar_agendamentos():
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT a.*, c.nome AS cliente, t.nometatuador AS tatuador
            FROM agendamento a JOIN cliente c ON c.idcliente=a.idcliente
            JOIN tatuador t ON t.idtatuador=a.idtatuador ORDER BY a.dataagendamento, a.horaagendamento""")
        return [normalizar_agendamento(item) for item in cursor.fetchall()]
    finally: cursor.close(); conexao.close()

# Busca um agendamento pelo ID.
@router.get("/{idagendamento}")
def buscar_agendamento(idagendamento: int):
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT a.*, c.nome AS cliente, t.nometatuador AS tatuador
            FROM agendamento a JOIN cliente c ON c.idcliente=a.idcliente
            JOIN tatuador t ON t.idtatuador=a.idtatuador WHERE a.idagendamento=%s""", (idagendamento,))
        item=cursor.fetchone()
        if not item: raise HTTPException(404, "Agendamento não encontrado.")
        return normalizar_agendamento(item)
    finally: cursor.close(); conexao.close()

# Cadastra agendamento; o banco define status inicial como pendente.
@router.post("", status_code=201)
def criar_agendamento(dados: AgendamentoDados):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("INSERT INTO agendamento (idcliente, idtatuador, dataagendamento, horaagendamento, descricaotatuagem, valortatuagem) VALUES (%s,%s,%s,%s,%s,%s)", (dados.idcliente, dados.idtatuador, dados.dataagendamento, dados.horaagendamento, dados.descricaotatuagem, dados.valortatuagem))
        conexao.commit(); return {"mensagem":"Agendamento cadastrado.", "idagendamento":cursor.lastrowid}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "O cliente ou tatuador informado não existe.") from erro
    finally: cursor.close(); conexao.close()

# Atualiza dados e status de um agendamento.
@router.put("/{idagendamento}")
def atualizar_agendamento(idagendamento: int, dados: AgendamentoDados):
    status_atual = dados.status or "pendente"
    if status_atual not in {"pendente", "confirmado", "concluido", "cancelado"}:
        raise HTTPException(422, "Status inválido.")
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("UPDATE agendamento SET idcliente=%s, idtatuador=%s, dataagendamento=%s, horaagendamento=%s, descricaotatuagem=%s, valortatuagem=%s, status=%s WHERE idagendamento=%s", (dados.idcliente, dados.idtatuador, dados.dataagendamento, dados.horaagendamento, dados.descricaotatuagem, dados.valortatuagem, status_atual, idagendamento))
        if cursor.rowcount==0:
            cursor.execute("SELECT idagendamento FROM agendamento WHERE idagendamento=%s", (idagendamento,))
            if not cursor.fetchone(): raise HTTPException(404, "Agendamento não encontrado.")
        conexao.commit(); return {"mensagem":"Agendamento atualizado."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "O cliente ou tatuador informado não existe.") from erro
    finally: cursor.close(); conexao.close()

# Exclui um agendamento.
@router.delete("/{idagendamento}")
def excluir_agendamento(idagendamento: int):
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("DELETE FROM agendamento WHERE idagendamento=%s", (idagendamento,))
        if cursor.rowcount==0: raise HTTPException(404, "Agendamento não encontrado.")
        conexao.commit(); return {"mensagem":"Agendamento excluído."}
    finally: cursor.close(); conexao.close()

# Recebe uma imagem, valida tamanho e extensão, e grava seu caminho no agendamento.
@router.post("/{idagendamento}/desenho")
async def enviar_desenho(idagendamento: int, arquivo: UploadFile = File(...)):
    extensao = Path(arquivo.filename or "").suffix.lower()
    if extensao not in EXTENSOES_PERMITIDAS:
        raise HTTPException(415, "Formato inválido. Envie PNG, JPG, JPEG ou WEBP.")
    conteudo = await arquivo.read(LIMITE_BYTES + 1)
    if not conteudo:
        raise HTTPException(400, "O arquivo enviado está vazio.")
    if len(conteudo) > LIMITE_BYTES:
        raise HTTPException(413, "A imagem deve ter no máximo 5 MB.")
    nome_arquivo = f"{uuid4().hex}{extensao}"
    caminho = PASTA_UPLOADS / nome_arquivo
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        cursor.execute("SELECT desenhoaprovado FROM agendamento WHERE idagendamento=%s", (idagendamento,))
        item=cursor.fetchone()
        if not item: raise HTTPException(404, "Agendamento não encontrado.")
        # O nome é gerado pelo servidor; o nome enviado pelo usuário não vira caminho.
        caminho.write_bytes(conteudo)
        cursor.execute("UPDATE agendamento SET desenhoaprovado=%s WHERE idagendamento=%s", (f"/uploads/{nome_arquivo}", idagendamento))
        conexao.commit()
        return {"mensagem":"Desenho enviado com sucesso.", "desenhoaprovado":f"/uploads/{nome_arquivo}"}
    except Exception:
        conexao.rollback()
        if caminho.exists(): caminho.unlink()
        raise
    finally: cursor.close(); conexao.close()
