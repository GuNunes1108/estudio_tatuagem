# ============================================================
# rotas/usuarios.py — cadastro de usuários (somente admin)
# Descrição: cria usuários com senha em hash, sem cadastro público.
# ============================================================
import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field
from mysql.connector import IntegrityError
from database import obter_conexao
from seguranca import verificar_admin

router = APIRouter(prefix="/usuarios", tags=["Usuários"], dependencies=[Depends(verificar_admin)])
class UsuarioCreate(BaseModel):
    nome: str = Field(min_length=1, max_length=100)
    email: EmailStr
    senha: str = Field(min_length=10, max_length=72)
    tipo: str = Field(pattern=r"^(admin|funcionario|cliente)$")
    idcliente: int | None = Field(default=None, gt=0)

# Cria usuário guardando apenas o hash bcrypt da senha.
@router.post("", status_code=201)
def criar_usuario(dados: UsuarioCreate):
    hash_senha = bcrypt.hashpw(dados.senha.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    conexao=obter_conexao(); cursor=conexao.cursor()
    try:
        if dados.tipo == "cliente" and dados.idcliente is None:
            raise HTTPException(422, "Para usuário do tipo cliente, informe idcliente.")
        if dados.tipo != "cliente" and dados.idcliente is not None:
            raise HTTPException(422, "idcliente só deve ser informado para usuários do tipo cliente.")
        cursor.execute("INSERT INTO usuario (nome,email,senha,tipo,idcliente) VALUES (%s,%s,%s,%s,%s)", (dados.nome.strip(), dados.email.lower(), hash_senha, dados.tipo, dados.idcliente))
        conexao.commit(); return {"mensagem":"Usuário cadastrado com sucesso.", "idusuario":cursor.lastrowid}
    except IntegrityError as erro:
        conexao.rollback(); raise HTTPException(409, "E-mail já cadastrado ou cliente vinculado inexistente.") from erro
    finally: cursor.close(); conexao.close()
