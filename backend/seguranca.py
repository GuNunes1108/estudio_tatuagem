# ============================================================
# seguranca.py — autenticação JWT e autorização por tipo
# Descrição: valida o token e oferece uma dependência exclusiva para admin.
# ============================================================
import os
from datetime import datetime, timedelta, timezone
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

load_dotenv()
_esquema_bearer = HTTPBearer(auto_error=False)
ALGORITMO = "HS256"

# Retorna a chave secreta e interrompe a inicialização se ela não foi configurada.
def obter_chave_secreta():
    chave = os.getenv("SECRET_KEY", "")
    if len(chave) < 32 or "COLOQUE_UMA_CHAVE" in chave:
        raise RuntimeError("Configure SECRET_KEY no arquivo backend/.env com uma chave aleatória longa.")
    return chave

# Cria um JWT assinado com e-mail, tipo e prazo de expiração do usuário.
def criar_token(email: str, tipo: str):
    minutos = int(os.getenv("ACCESS_TOKEN_MINUTES", "60"))
    agora = datetime.now(timezone.utc)
    payload = {"sub": email, "tipo": tipo, "iat": agora, "exp": agora + timedelta(minutes=minutos)}
    return jwt.encode(payload, obter_chave_secreta(), algorithm=ALGORITMO)

# Confere assinatura e validade do token enviado no cabeçalho Authorization.
def verificar_token(credenciais: HTTPAuthorizationCredentials = Depends(_esquema_bearer)):
    if credenciais is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Faça login para acessar este recurso.", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(credenciais.credentials, obter_chave_secreta(), algorithms=[ALGORITMO])
        if not payload.get("sub"):
            raise jwt.InvalidTokenError("Token sem usuário")
        return payload
    except jwt.ExpiredSignatureError as erro:
        raise HTTPException(status_code=401, detail="Sua sessão expirou. Entre novamente.", headers={"WWW-Authenticate": "Bearer"}) from erro
    except (jwt.InvalidTokenError, RuntimeError) as erro:
        raise HTTPException(status_code=401, detail="Token inválido. Entre novamente.", headers={"WWW-Authenticate": "Bearer"}) from erro

# Permite a operação apenas quando o token válido pertence a um administrador.
def verificar_admin(payload: dict = Depends(verificar_token)):
    if payload.get("tipo") != "admin":
        raise HTTPException(status_code=403, detail="Apenas administradores podem realizar esta operação.")
    return payload
