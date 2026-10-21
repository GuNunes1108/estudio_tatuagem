# Explicação detalhada do projeto — Aulas 1 a 16

Este documento acompanha o projeto implementado. A ideia é entender como os componentes trabalham juntos, não só copiar os arquivos.

## 1. Visão geral

O projeto tem três camadas:

1. **MySQL (`banco/estudio_tatuagem.sql`)** guarda os dados de forma persistente e aplica chaves primárias, únicas e estrangeiras.
2. **API FastAPI (`backend/`)** recebe requisições HTTP, valida dados, verifica login/permissões e conversa com o MySQL.
3. **Frontend (`frontend/`)** contém as páginas HTML, o Bootstrap para aparência e JavaScript com `fetch()` para chamar a API.

Fluxo de um cadastro: a pessoa preenche um formulário → JavaScript monta JSON → `fetch` envia POST → FastAPI valida o modelo Pydantic → rota executa SQL parametrizado → MySQL salva → API devolve JSON → frontend atualiza a tabela.

## 2. Como as 16 aulas aparecem no código

| Aula | Conceito | Onde está no projeto |
|---|---|---|
| 1 | API, REST, HTTP e JSON | `README.md`, endpoints no `backend/main.py` e rotas |
| 2 | Banco MySQL, tabelas e relacionamentos | `banco/estudio_tatuagem.sql` |
| 3 | Ambiente virtual e dependências | `backend/requirements.txt`, instruções deste README |
| 4 | Primeiro endpoint FastAPI | `backend/main.py`, rota `/health` |
| 5 | CRUD de clientes e conexão MySQL | `backend/database.py`, `backend/rotas/clientes.py` |
| 6 | HTML, JavaScript, Fetch e CORS | `frontend/clientes.html`, `frontend/js/clientes.js`, `backend/main.py` |
| 7 | Senioridade, tatuadores, FK e JOIN | `rotas/senioridade.py`, `rotas/tatuadores.py`, telas correspondentes |
| 8 | Agendamentos, duas FKs, data/hora e status | `rotas/agendamentos.py`, `frontend/agendamentos.html` |
| 9 | Upload de desenho aprovado | endpoint `/agendamentos/{id}/desenho`, pasta `backend/uploads/` |
| 10 | Estilos e relacionamento N:N | tabela `tatuador_estilo`, rotas de estilos e estilos do tatuador |
| 11 | Organização das rotas | cada funcionalidade tem seu módulo em `backend/rotas/` e `APIRouter` |
| 12 | Cadastro e hash de senha | `rotas/usuarios.py`, `criar_admin.py`, tabela `usuario` |
| 13 | Login JWT | `rotas/login.py`, `seguranca.py`, `frontend/login.html` |
| 14 | Rotas protegidas | `Depends(verificar_token)` em todos os grupos de gestão |
| 15 | Login, dashboard e logout | `frontend/login.html`, `dashboard.html`, `js/auth.js` |
| 16 | Autorização por tipo | `verificar_admin`, rota `/usuarios` e proteção de `cadastro.html` |

## 3. Banco de dados: tabelas e relações

- `cliente`: informações de contato. `idcliente` é a chave primária e `cpf` é único.
- `senioridade`: níveis como Júnior, Pleno e Sênior.
- `tatuador`: dados profissionais e `idsenioridade`, que aponta para `senioridade`.
- `estilo`: catálogo de estilos de tatuagem.
- `tatuador_estilo`: tabela de ligação entre tatuadores e estilos. A chave primária composta (`idtatuador`, `idestilo`) impede repetir o mesmo estilo para a mesma pessoa. Isso representa uma relação muitos-para-muitos (N:N).
- `agendamento`: liga um cliente e um tatuador a data, hora, descrição, valor, status e caminho opcional do desenho.
- `usuario`: login, hash da senha, tipo e vínculo opcional com cliente.

As chaves estrangeiras evitam que um agendamento aponte para um cliente/tatuador inexistente. A política `RESTRICT` impede apagar pessoas com agendamentos, preservando o histórico. As associações de estilo são removidas com `CASCADE` porque deixam de fazer sentido quando tatuador/estilo é apagado.

## 4. Backend arquivo por arquivo

### `backend/main.py`
É o ponto de entrada da API. Cria `FastAPI`, configura CORS para as origens locais, publica a pasta de uploads como `/uploads`, registra `/health` e inclui os módulos de rotas. A separação deixa o `main.py` curto e organizado.

### `backend/database.py`
Lê o `.env` e abre conexões MySQL. A função `obter_conexao()` concentra os detalhes de host, porta, usuário e banco. Se a conexão falhar, devolve uma mensagem controlada sem expor a senha.

### `backend/seguranca.py`
- `obter_chave_secreta()` exige uma chave JWT configurada.
- `criar_token()` cria um token assinado com e-mail (`sub`), tipo e expiração.
- `verificar_token()` exige `Authorization: Bearer <token>`, confere assinatura e validade.
- `verificar_admin()` exige também o tipo `admin`.

Autenticação responde “quem é você?”; autorização responde “você pode fazer isso?”. O cadastro de usuários exige ambas as coisas.

### `backend/criar_admin.py`
É um utilitário de configuração inicial. Solicita senha sem exibi-la no terminal, verifica tamanho e confirmação, gera hash bcrypt e grava o usuário como `admin`. Isso evita uma rota pública que permita a qualquer visitante criar uma conta administrativa.

### `backend/rotas/clientes.py`
Implementa GET de lista, GET por ID, POST, PUT e DELETE. `ClienteCreate` é um modelo Pydantic que valida nome, CPF e limites dos campos. SQL usa `%s` com parâmetros separados; não concatena texto do usuário dentro do SQL. CPF duplicado vira erro HTTP 409 e cliente inexistente vira 404.

### `backend/rotas/senioridade.py`
CRUD simples da tabela `senioridade`. Uma senioridade usada por tatuadores não pode ser apagada; o banco impede e a API devolve 409.

### `backend/rotas/estilos.py`
CRUD do catálogo de estilos. As descrições são únicas. A exclusão remove automaticamente as associações correspondentes na tabela de ligação.

### `backend/rotas/tatuadores.py`
CRUD de tatuadores. O `JOIN` com `senioridade` mostra o nome do nível em vez de apenas o número. A rota `GET /tatuadores` também usa `GROUP_CONCAT` para listar os estilos. As rotas `GET /tatuadores/{id}/estilos` e `PUT /tatuadores/{id}/estilos` leem/substituem as relações N:N em uma transação.

### `backend/rotas/agendamentos.py`
CRUD de agendamentos com `JOIN` em cliente e tatuador. `normalizar_agendamento()` padroniza a hora para `HH:MM`. O cadastro inicial deixa o banco aplicar `status='pendente'`; na edição o status pode ser alterado. O upload aceita apenas extensões permitidas, limita o tamanho a 5 MB, gera nome aleatório e salva o caminho no registro.

### `backend/rotas/usuarios.py`
Recebe cadastro somente após `verificar_admin`. A senha é transformada em hash bcrypt antes de chegar ao SQL; a senha original nunca é salva. A API valida o tipo e o vínculo com cliente.

### `backend/rotas/login.py`
Busca a conta pelo e-mail, compara a senha digitada com o hash usando `bcrypt.checkpw()` e devolve um JWT. A mensagem de erro é igual para e-mail inexistente e senha incorreta, para não revelar qual conta existe.

### `backend/requirements.txt` e `backend/.env.example`
O primeiro declara bibliotecas; o segundo documenta as variáveis de ambiente necessárias. Copie `.env.example` para `.env`, gere a chave JWT e não envie o `.env` ao GitHub.

## 5. Frontend arquivo por arquivo

- `index.html`: landing page com apresentação e link para login.
- `login.html`: formulário de autenticação.
- `dashboard.html`: atalhos para as áreas de gestão e botão de sair.
- `cadastro.html`: formulário de criação de usuário, visível apenas para admin.
- `clientes.html`: formulário e tabela de clientes.
- `senioridade.html`: formulário e tabela de níveis de senioridade.
- `estilos.html`: formulário e tabela de estilos.
- `tatuadores.html`: formulário de tatuador, seletor de senioridade e checkboxes de estilos.
- `agendamentos.html`: formulário de sessão, status durante edição e campo de upload.
- `css/style.css`: ajustes visuais complementares ao Bootstrap.
- `js/config.js`: endereço base da API.
- `js/auth.js`: guarda token/usuário no `localStorage`, acrescenta `Authorization`, trata 401, faz logout e verifica papel de admin no frontend. Isso melhora a experiência, mas **a segurança real está no backend**, pois o navegador pode ser alterado.
- `js/login.js`: envia e-mail/senha, salva token e redireciona ao painel.
- `js/dashboard.js`: inicializa painel e esconde atalho de cadastro para não-admin.
- `js/cadastro.js`: chama a rota de usuário com token.
- `js/clientes.js`: carrega lista, cria, edita e exclui clientes.
- `js/senioridade.js`: operações de CRUD para senioridades.
- `js/estilos.js`: operações de CRUD para estilos.
- `js/tatuadores.js`: carrega opções, salva dados do tatuador e associa estilos.
- `js/agendamentos.js`: carrega clientes/tatuadores, salva sessões, envia arquivo com `FormData` e exibe link do desenho.

Nos formulários, `fetch()` é assíncrono. `await` espera a resposta, `response.ok` identifica respostas HTTP de sucesso, e `response.json()` converte o corpo JSON em objeto JavaScript. Ao exibir texto vindo da API, o código usa `textContent` nas tabelas para reduzir o risco de injeção de HTML.

## 6. Métodos HTTP e exemplos

| Método | Exemplo | O que faz |
|---|---|---|
| GET | `/clientes` | lista clientes |
| GET | `/clientes/1` | busca o cliente 1 |
| POST | `/clientes` | cria cliente |
| PUT | `/clientes/1` | atualiza cliente 1 |
| DELETE | `/clientes/1` | exclui cliente 1, se não houver dependências |
| POST | `/login` | valida credenciais e devolve token |
| POST | `/usuarios` | cria usuário, somente admin |
| POST | `/agendamentos/1/desenho` | envia imagem associada ao agendamento 1 |

Use `http://localhost:8000/docs` para experimentar as rotas. Primeiro faça login em `/login`, copie `access_token`, clique em **Authorize** e informe `Bearer SEU_TOKEN` (ou só o token, conforme o campo de autorização apresentado). A API pode devolver `401` se não houver token ou ele tiver expirado, e `403` se a conta não for admin ao cadastrar usuário.

## 7. Por que alguns detalhes foram implementados assim?

- **SQL parametrizado:** evita que os dados digitados sejam interpretados como parte do comando SQL.
- **Hash bcrypt:** o banco guarda um resumo de senha, não a senha em texto legível.
- **JWT com expiração:** o token não vale para sempre.
- **CORS restrito às origens locais:** evita aceitar chamadas de qualquer site durante o desenvolvimento.
- **Nome aleatório para upload:** impede que o nome enviado pelo usuário escolha o caminho de gravação.
- **Limite de upload:** reduz risco de arquivos grandes ocuparem todo o espaço.
- **Chaves estrangeiras:** mantêm a consistência entre registros relacionados.
- **`try/finally` para conexões:** fecha cursor e conexão mesmo se a consulta falhar.

## 8. Limites conhecidos e próximos passos

É uma aplicação educacional local. Antes de produção, seria necessário HTTPS, política de senha e recuperação, limitação de tentativas de login, logs/auditoria, proteção CSRF conforme a estratégia de sessão, validação real do conteúdo de imagens (não apenas extensão), gestão de tokens/revogação, testes automatizados, migrações de banco e controles de autorização mais específicos por ação. O token guardado em `localStorage` é simples para a aula, mas tem riscos se houver vulnerabilidade XSS. O tipo `cliente` existe no banco e no cadastro administrativo, mas não tem um portal próprio nesta versão.

## 9. Checklist para testar

1. MySQL ativo e script SQL importado.
2. `.env` criado com banco e `SECRET_KEY` válida.
3. Dependências instaladas no ambiente virtual.
4. `python criar_admin.py` executado.
5. API iniciada com `uvicorn main:app --reload`.
6. `GET /health` responde `{"status":"ok"...}`.
7. Frontend iniciado com `python -m http.server 5500` dentro de `frontend/`.
8. Login de admin funciona e abre o painel.
9. CRUD de clientes, senioridade, estilos e tatuadores funciona.
10. Agendamento pode ser criado e imagem anexada.
11. Criar usuário como admin funciona; como funcionário, deve retornar 403.
12. Logout apaga token e volta para o login.

## 10. Comentários removidos do JavaScript e sua origem

Para deixar os arquivos JavaScript mais limpos, os comentários que estavam dentro deles foram removidos. Eles eram anotações explicativas e títulos de seções; não eram comandos executados pelo navegador. Abaixo está o mapa de onde cada anotação veio e o que explicava. Os caminhos são relativos à pasta `estudio_tatuagem/`.

### `frontend/js/agendamentos.js`

- **Inicialização do CRUD de agendamentos** — indicava o começo da configuração da tela de agendamentos.
- **Carregamento de clientes e tatuadores** — explicava o preenchimento dos campos de seleção usados no formulário.
- **Listagem de agendamentos** — indicava a montagem da tabela com os nomes relacionados e os links dos desenhos aprovados.
- **Montagem do JSON** — identificava a preparação dos dados para criar ou editar um agendamento.
- **Salvamento e envio da imagem** — explicava que os dados do agendamento são salvos e o arquivo é enviado em uma segunda requisição.
- **Edição e exclusão** — indicava a lógica acionada pelos botões para carregar um registro ou removê-lo.

### `frontend/js/auth.js`

- **Funções compartilhadas de autenticação** — título geral do arquivo.
- **Leitura do token** — explicava a recuperação do token salvo depois do login.
- **Leitura dos dados do usuário** — indicava a recuperação dos dados básicos guardados no navegador.
- **Logout** — explicava a remoção do token e dos dados do usuário ao sair.
- **Proteção de páginas para visitantes** — indicava o redirecionamento para a tela de login quando não existe token.
- **Restrição da tela de cadastro** — explicava a verificação do tipo de usuário antes de permitir abrir o cadastro de usuários.
- **Requisições protegidas** — indicava o envio do token e o tratamento de uma sessão expirada.
- **Cabeçalho do usuário** — explicava a exibição do nome e do tipo de usuário nas páginas.

### `frontend/js/cadastro.js`

- **Proteção e cadastro de usuários** — identificava a proteção da tela e o envio do formulário para criar um usuário.
- **Vínculo com cliente** — explicava que o campo de vínculo com cliente aparece apenas quando o tipo de conta escolhido é cliente.

### `frontend/js/clientes.js`

- **Proteção da página** — indicava a verificação de autenticação antes de usar a tela de clientes.
- **Carregamento da tabela** — explicava a busca dos clientes na API e a construção das linhas da tabela.
- **Limpeza do formulário** — indicava a preparação do formulário para um novo cadastro.
- **Cadastro ou atualização** — explicava como o formulário decide entre criar um cliente ou atualizar um existente.
- **Eventos de editar e excluir** — indicava o tratamento dos botões nas linhas da tabela.

### `frontend/js/config.js`

- **Configuração central da API** — identificava o arquivo que guarda o endereço base da API.
- **Alteração do endereço** — orientava a mudar a constante se a API fosse executada em outro endereço.

### `frontend/js/dashboard.js`

- **Inicialização do painel** — explicava a preparação do dashboard e a exibição de atalhos conforme o tipo de usuário.

### `frontend/js/estilos.js`

- **Inicialização do CRUD de estilos** — indicava a configuração da tela de estilos.
- **Listagem de estilos** — explicava a consulta e exibição dos estilos cadastrados.
- **Criação ou atualização** — indicava o envio do formulário para criar ou editar um estilo.
- **Edição ou exclusão** — identificava a lógica dos botões para editar ou excluir estilos.

### `frontend/js/login.js`

- **Processamento do login** — indicava a função responsável por enviar as credenciais e tratar a resposta da API.

### `frontend/js/senioridade.js`

- **Inicialização do CRUD de senioridades** — indicava a configuração da tela de níveis de experiência.
- **Listagem** — explicava a consulta dos níveis cadastrados.
- **Criação ou atualização** — identificava o salvamento de uma senioridade nova ou editada.
- **Botões de edição e exclusão** — indicava o tratamento das ações disponíveis para cada nível.

### `frontend/js/tatuadores.js`

- **Inicialização do CRUD de tatuadores** — indicava a configuração da tela de tatuadores.
- **Carregamento das opções** — explicava a busca das senioridades e dos estilos para preencher o formulário.
- **Listagem de tatuadores** — indicava a exibição dos tatuadores, seus níveis de experiência e estilos.
- **Leitura do formulário** — identificava a coleta dos valores preenchidos pelo usuário.
- **Salvamento e associação de estilos** — explicava que os dados do tatuador são salvos e os estilos são associados em seguida.
- **Edição ou exclusão** — indicava as ações de carregar os dados para edição ou remover um tatuador.

**Observação:** os comentários removidos eram apenas explicações em texto. A intenção foi manter as instruções do código disponíveis neste documento sem deixar esses comentários entre as linhas de JavaScript. Os comentários dos arquivos Python e de outros componentes não foram alterados nesta etapa.

