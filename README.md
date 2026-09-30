# TaskFlow --- Gerenciador de Tarefas

Aplicação web full-stack para gerenciamento de tarefas, desenvolvida
para demonstrar integração entre Angular, FastAPI e PostgreSQL/Supabase.

## Demonstração

-   **Aplicação:** https://task-flow-silk-beta.vercel.app
-   **Login:** https://task-flow-silk-beta.vercel.app/login
-   **Dashboard:** https://task-flow-silk-beta.vercel.app/dashboard
-   **API:** https://taskflow-kwys.onrender.com
-   **Documentação interativa:** https://taskflow-kwys.onrender.com/docs
-   **Health check:** https://taskflow-kwys.onrender.com/health
-   **Verificação do banco:**
    https://taskflow-kwys.onrender.com/health/db
-   **Repositório:** https://github.com/josiamiranda3/TaskFlow

## Sobre o projeto

O TaskFlow é uma aplicação de gerenciamento de tarefas com frontend
Angular, API REST em FastAPI, persistência de dados em
PostgreSQL/Supabase e autenticação via Supabase Auth. O frontend e o
backend são publicados separadamente, respectivamente na Vercel e no
Render.

## Funcionalidades

-   Cadastro e autenticação de usuários.
-   Login com e-mail e senha.
-   Validação dos campos obrigatórios.
-   Mensagens de erro para credenciais inválidas ou falhas de conexão.
-   Indicador de carregamento durante o login.
-   Dashboard para visualizar e gerenciar tarefas.
-   Criação, edição, conclusão e exclusão de tarefas, conforme
    disponível na versão atual.
-   Organização por prioridades, prazos e filtros, caso esses recursos
    já estejam implementados na versão publicada.
-   Persistência dos dados.
-   Documentação interativa da API por Swagger UI/OpenAPI.
-   Interface web responsiva.

> Revise a lista de funcionalidades antes de publicar e remova os itens
> que ainda não estiverem disponíveis na versão implantada.

## Tecnologias

**Frontend** - Angular - TypeScript - HTML - SCSS/CSS - Angular Router e
formulários Angular

**Backend** - Python - FastAPI - API REST - OpenAPI/Swagger UI - CORS

**Dados e autenticação** - PostgreSQL - Supabase - Supabase Auth

**Ferramentas e deploy** - Git e GitHub - Visual Studio Code - Vercel
(frontend) - Render (backend)

## Arquitetura

``` text
Navegador
   |
   +--> Frontend Angular (Vercel)
   |        |
   |        +--> Supabase Auth (autenticação)
   |
   +--> API FastAPI (Render)
              |
              +--> PostgreSQL / Supabase
```

## Estrutura principal

``` text
TaskFlow/
├── backend/       # API em Python/FastAPI
├── frontend/      # Aplicação Angular
└── README.md      # Documentação do projeto
```

A estrutura interna pode variar conforme os módulos e arquivos
existentes no repositório.

## Como executar localmente

### Pré-requisitos

-   Git
-   Python compatível com o backend
-   Node.js e npm compatíveis com a versão do Angular
-   Projeto Supabase configurado

### 1. Clonar o repositório

``` bash
git clone https://github.com/josiamiranda3/TaskFlow.git
cd TaskFlow
```

### 2. Backend

``` bash
cd backend
python -m venv .venv
```

No Git Bash do Windows:

``` bash
source .venv/Scripts/activate
```

No PowerShell:

``` powershell
.venv\Scripts\Activate.ps1
```

Instale as dependências:

``` bash
pip install -r requirements.txt
```

Configure as variáveis exigidas pelo backend conforme a configuração do
projeto. Não publique senhas, tokens ou credenciais no GitHub.

Se a aplicação estiver exposta como `app` em `app/main.py`, inicie com:

``` bash
uvicorn app.main:app --reload
```

A API normalmente estará em `http://127.0.0.1:8000`, com documentação em
`http://127.0.0.1:8000/docs`.

### 3. Frontend

Em outro terminal:

``` bash
cd frontend
npm install
```

Confira `src/environments/environment.ts` para confirmar que a URL da
API de desenvolvimento aponta para `http://127.0.0.1:8000`.

Inicie o Angular:

``` bash
npm start
```

Se o projeto não tiver um script `start`, use:

``` bash
npx ng serve
```

A aplicação normalmente estará em `http://localhost:4200`.

## Configuração e segurança

-   A configuração de produção do Angular utiliza a URL pública da API
    hospedada no Render.
-   A configuração de desenvolvimento utiliza a API local.
-   Configure CORS apenas para as origens necessárias.
-   No frontend, utilize somente a chave pública apropriada do Supabase;
    nunca exponha a chave `service_role`.
-   Não versione arquivos `.env`, senhas, tokens privados ou credenciais
    do banco.
-   Confirme as políticas de Row Level Security (RLS) e as permissões de
    acesso aos dados por usuário.
-   Configure segredos nos ambientes de hospedagem, e não diretamente no
    código.

## Checklist de validação

-   [ ] Cadastro de usuário.
-   [ ] Login com credenciais válidas.
-   [ ] Mensagem de erro para credenciais inválidas.
-   [ ] Logout e persistência/expiração da sessão.
-   [ ] Criar, editar, concluir e excluir tarefas.
-   [ ] Verificar persistência após atualizar a página.
-   [ ] Testar filtros, prioridades e prazos, se implementados.
-   [ ] Confirmar a comunicação entre frontend e API em produção.
-   [ ] Verificar o comportamento quando a API ou o banco estiver
    indisponível.

Documente comandos de testes automatizados somente depois de confirmar
que eles existem no repositório e que funcionam.

## Melhorias futuras

-   Ampliar a cobertura de testes automatizados.
-   Melhorar logs, tratamento de erros e monitoramento.
-   Adicionar pipeline de CI/CD.
-   Incluir capturas de tela e decisões arquiteturais.
-   Evoluir busca, filtros e paginação conforme a necessidade.

## Objetivo do projeto

Projeto de portfólio voltado a demonstrar conhecimentos práticos em
desenvolvimento full-stack, APIs REST, integração com banco de dados,
autenticação, versionamento e publicação de aplicações web.

## Autor

**Josias Miranda Oliveira de Lima**

-   GitHub: https://github.com/josiamiranda3
-   Repositório: https://github.com/josiamiranda3/TaskFlow
