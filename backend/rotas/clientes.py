# ============================================================
# rotas/clientes.py — CRUD de clientes
# Descrição: lista, consulta, cadastra, atualiza e exclui clientes.
# ============================================================
from datetime import date
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from mysql.connector import IntegrityError, Error
from database import obter_conexao
from seguranca import verificar_token

router = APIRouter(prefix="/clientes", tags=["Clientes"], dependencies=[Depends(verificar_token)])

class ClienteCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    cpf: str = Field(pattern=r"^\d{11}$")
    telefone: Optional[str] = Field(default=None, max_length=20)
    datacadastro: Optional[date] = None
    cidade: Optional[str] = Field(default=None, max_length=100)
    uf: Optional[str] = Field(default=None, min_length=2, max_length=2)

    @field_validator("nome")
    @classmethod
    def validar_nome(cls, valor):
        # Impede que um nome formado apenas por espaços seja salvo.
        if not valor.strip():
            raise ValueError("O nome não pode ficar vazio.")
        return valor.strip()

# Lista os clientes em ordem alfabética.
@router.get("")
def listar_clientes():
    conexao = obter_conexao(); cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM cliente ORDER BY nome")
        return cursor.fetchall()
    finally:
        cursor.close(); conexao.close()

# Busca um cliente pelo identificador.
@router.get("/{idcliente}")
def buscar_cliente(idcliente: int):
    conexao = obter_conexao(); cursor = conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM cliente WHERE idcliente = %s", (idcliente,))
        cliente = cursor.fetchone()
        if not cliente: raise HTTPException(status_code=404, detail="Cliente não encontrado.")
        return cliente
    finally:
        cursor.close(); conexao.close()

# Insere um cliente usando parâmetros SQL para evitar injeção de SQL.
@router.post("", status_code=status.HTTP_201_CREATED)
def criar_cliente(cliente: ClienteCreate):
    conexao = obter_conexao(); cursor = conexao.cursor()
    try:
        cursor.execute("INSERT INTO cliente (nome, cpf, telefone, datacadastro, cidade, uf) VALUES (%s, %s, %s, %s, %s, %s)", (cliente.nome, cliente.cpf, cliente.telefone, cliente.datacadastro, cliente.cidade, cliente.uf))
        conexao.commit()
        return {"mensagem": "Cliente cadastrado com sucesso.", "idcliente": cursor.lastrowid}
    except IntegrityError as erro:
        conexao.rollback()
        raise HTTPException(status_code=409, detail="Este CPF já está cadastrado.") from erro
    finally:
        cursor.close(); conexao.close()

# Atualiza todos os campos editáveis de um cliente existente.
@router.put("/{idcliente}")
def atualizar_cliente(idcliente: int, cliente: ClienteCreate):
    conexao = obter_conexao(); cursor = conexao.cursor()
    try:
        cursor.execute("UPDATE cliente SET nome=%s, cpf=%s, telefone=%s, datacadastro=%s, cidade=%s, uf=%s WHERE idcliente=%s", (cliente.nome, cliente.cpf, cliente.telefone, cliente.datacadastro, cliente.cidade, cliente.uf, idcliente))
        if cursor.rowcount == 0:
            cursor.execute("SELECT idcliente FROM cliente WHERE idcliente=%s", (idcliente,))
            if not cursor.fetchone(): raise HTTPException(status_code=404, detail="Cliente não encontrado.")
        conexao.commit()
        return {"mensagem": "Cliente atualizado com sucesso."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(status_code=409, detail="O CPF informado já pertence a outro cliente.") from erro
    finally:
        cursor.close(); conexao.close()

# Exclui um cliente se ele não estiver referenciado por agendamentos.
@router.delete("/{idcliente}")
def excluir_cliente(idcliente: int):
    conexao = obter_conexao(); cursor = conexao.cursor()
    try:
        cursor.execute("DELETE FROM cliente WHERE idcliente=%s", (idcliente,))
        if cursor.rowcount == 0: raise HTTPException(status_code=404, detail="Cliente não encontrado.")
        conexao.commit(); return {"mensagem": "Cliente excluído com sucesso."}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(status_code=409, detail="Não é possível excluir: o cliente possui agendamentos vinculados.") from erro
    finally:
        cursor.close(); conexao.close()
