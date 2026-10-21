# ============================================================
# rotas/login.py — login e emissão de token JWT
# Descrição: valida credenciais e devolve um token assinado.
# ============================================================
import bcrypt
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr, Field
from database import obter_conexao
from seguranca import criar_token

router = APIRouter(prefix="/login", tags=["Autenticação"])
class LoginDados(BaseModel):
    email: EmailStr
    senha: str = Field(min_length=1, max_length=72)

# Confere e-mail e senha e retorna um JWT quando as credenciais são válidas.
@router.post("")
def fazer_login(dados: LoginDados):
    conexao=obter_conexao(); cursor=conexao.cursor(dictionary=True)
    try:
        cursor.execute("SELECT idusuario, nome, email, senha, tipo FROM usuario WHERE email=%s", (dados.email.lower(),))
        usuario=cursor.fetchone()
        senha_correta = bool(usuario) and bcrypt.checkpw(dados.senha.encode("utf-8"), usuario["senha"].encode("utf-8"))
        if not senha_correta:
            raise HTTPException(status_code=401, detail="E-mail ou senha inválidos.")
        token=criar_token(usuario["email"], usuario["tipo"])
        return {"access_token":token, "token_type":"bearer", "usuario":{"nome":usuario["nome"], "email":usuario["email"], "tipo":usuario["tipo"]}}
    finally: cursor.close(); conexao.close()
