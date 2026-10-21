# ============================================================
# main.py — aplicação principal do Estúdio de Tatuagem
# Descrição: configura CORS, arquivos de upload e rotas da API.
# Como rodar: uvicorn main:app --reload (dentro de backend/).
# ============================================================
import os
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from rotas import clientes, senioridade, tatuadores, agendamentos, estilos, usuarios, login

load_dotenv()
app = FastAPI(title="API — Estúdio de Tatuagem", version="1.0.0", description="API didática para administrar um estúdio de tatuagem.")
origens = [origem.strip() for origem in os.getenv("FRONTEND_ORIGINS", "http://localhost:5500,http://127.0.0.1:5500").split(",") if origem.strip()]
app.add_middleware(CORSMiddleware, allow_origins=origens, allow_credentials=False, allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"], allow_headers=["Authorization", "Content-Type"])
PASTA_UPLOADS = Path(__file__).resolve().parent / "uploads"
PASTA_UPLOADS.mkdir(parents=True, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=PASTA_UPLOADS), name="uploads")

# Endpoint simples para verificar se a API iniciou.
@app.get("/health", tags=["Sistema"])
def verificar_saude():
    return {"status": "ok", "aplicacao": "Estúdio de Tatuagem"}

# Registra cada grupo de rotas, mantendo a documentação organizada.
app.include_router(login.router)
app.include_router(clientes.router)
app.include_router(senioridade.router)
app.include_router(estilos.router)
app.include_router(tatuadores.router)
app.include_router(agendamentos.router)
app.include_router(usuarios.router)
