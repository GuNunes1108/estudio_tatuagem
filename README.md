# Estúdio de Tatuagem — projeto completo (Aulas 1–16)

Sistema web didático para gerenciar clientes, tatuadores, senioridades, estilos, agendamentos e usuários. Tecnologias: MySQL/XAMPP, Python/FastAPI, HTML, Bootstrap e JavaScript puro.

## Guia rápido: como entrar no sistema (Windows)

Siga esta ordem na primeira vez. **O login só funciona depois de criar a conta de administrador**; não existe usuário/senha padrão no projeto.

1. **Banco de dados:** abra o XAMPP e clique em Start ao lado de MySQL. Abra `http://localhost/phpmyadmin`, entre em Importar e selecione `banco/estudio_tatuagem.sql` deste projeto.
2. **Configurar backend:** abra o terminal na pasta `estudio_tatuagem-main\backend` (a pasta que contém `main.py`) e execute:

   ```powershell
   python -m venv .venv
   .venv\Scripts\Activate.ps1
   pip install -r requirements.txt
   Copy-Item .env.example .env
   ```

   Se o PowerShell bloquear a ativação, use o Prompt de Comando (CMD) e execute `.venv\Scripts\activate.bat`, ou continue sem ativar usando `.venv\Scripts\python.exe -m pip install -r requirements.txt`.

3. **Chave secreta:** gere uma chave no terminal com `python -c "import secrets; print(secrets.token_urlsafe(48))"`. Abra `backend/.env` e substitua o valor de `SECRET_KEY` pela chave gerada. No XAMPP padrão, deixe `DB_USER=root`, `DB_PASSWORD=` vazio; se você configurou senha no MySQL, preencha-a.
4. **Criar a conta de administrador:** ainda na pasta `backend`, com o ambiente virtual ativado, execute `python criar_admin.py`. Digite nome, e-mail e uma senha com pelo menos 10 caracteres duas vezes. A senha não aparece enquanto você digita; isso é normal.
5. **Ligar a API:** execute `uvicorn main:app --reload` no terminal da pasta `backend`. Deixe esse terminal aberto. Confira `http://localhost:8000/health`; deve aparecer `{"status":"ok","aplicacao":"Estúdio de Tatuagem"}`.
6. **Ligar o site:** abra um segundo terminal na pasta `estudio_tatuagem-main\frontend` e execute `python -m http.server 5500`. Deixe esse terminal aberto.
7. **Entrar:** abra `http://localhost:5500/login.html`, use o e-mail e a senha criados no passo 4 e clique em **Entrar**. Para cadastrar funcionários ou outros administradores, entre primeiro como administrador e acesse `http://localhost:5500/cadastro.html`.

### Se não conseguir entrar

- **“E-mail ou senha inválidos”**: confirme que criou o administrador no passo 4 e use exatamente o mesmo e-mail/senha.
- **Erro de conexão com a API**: confirme que o terminal do Uvicorn continua aberto e que `/health` abre.
- **Erro de conexão com MySQL**: confira se o MySQL está iniciado no XAMPP e se os dados de `backend/.env` correspondem aos do seu MySQL.
- **E-mail já cadastrado** ao criar admin: essa conta já existe; tente entrar com ela. Não apague o banco só para resolver o login.
- **Acesso negado ao cadastro**: a página `cadastro.html` é somente para administradores. Primeiro entre com a conta admin.

## Requisitos
- Python 3.10 ou mais recente
- XAMPP com MySQL ativo (ou outro MySQL compatível)
- Navegador moderno

## 1. Criar o banco
1. Abra o XAMPP e inicie o MySQL.
2. Entre no phpMyAdmin (`http://localhost/phpmyadmin`).
3. Importe `banco/estudio_tatuagem.sql` ou copie e execute seu conteúdo na aba SQL.

O script cria as tabelas e alguns dados demonstrativos. Ele usa `CREATE TABLE IF NOT EXISTS`, portanto não apaga tabelas já existentes.

## 2. Configurar e iniciar o backend
No terminal, entre na pasta `backend`:

```bash
python -m venv .venv
# Windows PowerShell:
.venv\Scripts\Activate.ps1
# Windows CMD:
.venv\Scripts\activate.bat
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

Copie `.env.example` para `.env` e ajuste os dados do MySQL. No XAMPP padrão, normalmente o usuário é `root` e a senha vazia.

Gere uma chave JWT segura e coloque-a em `SECRET_KEY` no `.env`:

```bash
python -c "import secrets; print(secrets.token_urlsafe(48))"
```

Crie o primeiro administrador de forma segura (o script pergunta a senha sem mostrá-la):

```bash
python criar_admin.py
```

Inicie a API:

```bash
uvicorn main:app --reload
```

- API: `http://localhost:8000`
- Documentação interativa: `http://localhost:8000/docs`
- Verificação: `http://localhost:8000/health`

## 3. Iniciar o frontend
Em outro terminal, na pasta `frontend`, execute:

```bash
python -m http.server 5500
```

Abra `http://localhost:5500`. A primeira tela é a página inicial. Faça login com o administrador que você criou.

> Para o primeiro login via interface, abra `http://localhost:5500/login.html`. A tela de cadastro de usuários (`cadastro.html`) exige uma conta administradora; não há cadastro público que conceda acesso ao sistema.

## Usuários e permissões
- `admin`: pode usar as telas de gestão e cadastrar usuários.
- `funcionario`: pode usar as telas de gestão, mas não pode cadastrar outros usuários.
- `cliente`: papel previsto no banco; as telas administrativas não são um portal de cliente nesta versão.

A API exige JWT nas rotas de gestão. O backend também verifica o tipo de usuário para proteger o cadastro de usuários. A validação de permissões mais finas por operação pode ser ampliada conforme as regras da escola.

## Estrutura
```text
banco/estudio_tatuagem.sql
backend/main.py
backend/database.py
backend/seguranca.py
backend/criar_admin.py
backend/rotas/{clientes,senioridade,tatuadores,agendamentos,estilos,usuarios,login}.py
backend/uploads/
frontend/{index,login,cadastro,dashboard,clientes,senioridade,estilos,tatuadores,agendamentos}.html
frontend/js/{config,auth,login,cadastro,clientes,senioridade,estilos,tatuadores,agendamentos,dashboard}.js
```

## Observações
- O `.env` e a pasta `.venv/` não devem ser enviados ao GitHub.
- O upload aceita imagens PNG, JPG, JPEG e WEBP com limite de 5 MB.
- Este é um projeto de aprendizagem para rodar localmente. Antes de publicar na internet, configure HTTPS, credenciais fortes, backups e controles adicionais.
