# ============================================================
# database.py — conexão com o banco MySQL
# Descrição: lê as configurações do .env e abre conexões seguras.
# Uso: importar obter_conexao nas rotas da API.
# ============================================================
import os
import mysql.connector
from dotenv import load_dotenv
from fastapi import HTTPException

load_dotenv()

# Abre uma conexão nova usando as configurações do ambiente.
def obter_conexao():
    try:
        return mysql.connector.connect(
            host=os.getenv("DB_HOST", "127.0.0.1"),
            port=int(os.getenv("DB_PORT", "3306")),
            user=os.getenv("DB_USER", "root"),
            password=os.getenv("DB_PASSWORD", ""),
            database=os.getenv("DB_NAME", "estudio_tatuagem"),
            charset="utf8mb4",
            collation="utf8mb4_unicode_ci",
            connection_timeout=5,
        )
    except mysql.connector.Error as erro:
        # Não devolve senha nem detalhes internos do servidor ao navegador.
        raise HTTPException(status_code=503, detail="Não foi possível conectar ao MySQL. Confira se o serviço está ativo e se o .env está correto.") from erro
