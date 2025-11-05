UEBAX: Plataforma de Análise de Comportamento
1. Sobre o Projeto
O presente projeto tem como objetivo desenvolver a plataforma UEBAX, uma solução voltada para o monitoramento e análise do comportamento de usuários e dispositivos em um ambiente computacional controlado.

A ferramenta foi desenvolvida como um projeto acadêmico para simular práticas adotadas em sistemas corporativos de segurança da informação (SI). Ela regista automaticamente as atividades dos usuários, aplica regras simples para identificar ações que fujam do padrão esperado (ex: logins fora do horário de trabalho) e apresenta os dados num dashboard interativo. O projeto oferece suporte à Perícia Computacional na coleta, preservação e análise de evidências digitais.

2. Visão Geral das Funcionalidades
O projeto é uma aplicação full-stack completa, dividida num backend (API) e num frontend (Cliente). Ele implementa 8 ecrãs funcionais:

Autenticação Segura (JWT):

Ecrã de Login (com geração de token JWT)

Ecrã de Cadastro (com validação de erros)

Botão de "Sair" (Logout) com "blacklisting" de tokens.

Recuperação de Conta (Fluxo de 3 Passos):

Ecrã para solicitar redefinição de senha (via e-mail).

Ecrã para verificação do token de 6 dígitos.

Ecrã para definir a nova senha.

Dashboard de Análise (Rota Protegida):

Ecrã Principal: Mostra 4 cards de estatísticas, um gráfico de linha interativo (Logins por Hora) e uma tabela de status de conexão.

Ecrã de Eventos: Um relatório completo com tabela de todos os eventos de usuário registados.

Ecrã de Alertas: Um relatório completo com tabela de todos os alertas de segurança gerados pelo motor de regras.

3. Tech Stack (Tecnologias Utilizadas)
Backend (A "Fábrica")
Python 3.12+

Django & Django Rest Framework (DRF): Para construir a API RESTful.

Simple JWT (JSON Web Tokens): Para autenticação e gestão de sessões.

django-cors-headers: Para permitir a comunicação segura entre o backend e o frontend.

SQLite3: Base de dados leve para desenvolvimento.

Frontend (A "Loja")
React 18+ (configurado com Vite)

React Router (v6): Para a navegação entre páginas e roteamento aninhado (no dashboard).

Chart.js (react-chartjs-2): Para a renderização do gráfico de linha interativo.

react-icons: Para os ícones da interface.

CSS Modules: Para estilização de componentes de forma isolada.

4. Instalação e Execução
Este é um projeto full-stack que corre em dois terminais separados.

Antes de Começar: Preparando o Repositório
Para que o projeto funcione noutra máquina (ou para o seu professor/recrutador), ele precisa de duas coisas:

1. O Ficheiro .gitignore (Obrigatório!)

Crie um ficheiro chamado .gitignore na raiz do projeto e cole o seguinte. Isto impedirá que você envie as suas node_modules (1865+ ficheiros) e a sua base de dados para o Git.

# --- Node.js / React (Vite) ---
node_modules/
dist/
.vite/
.env
.env.local

# --- Python / Django ---
venv/
env/
db.sqlite3
__pycache__/
*.pyc

# --- Ficheiros do SO ---
.DS_Store
Thumbs.db

Como Executar o Projeto
1. Clone o repositório:
git clone (https://github.com/Gabriel-Ls2/UEBAx.git)
cd uebax_project

2. Terminal 1: Iniciar o Backend (Django)

Este terminal será a sua "Fábrica" de dados.

# 1. Crie e ative um ambiente virtual
python -m venv venv
# No Windows:
./venv/Scripts/activate
# No Mac/Linux:
source venv/bin/activate

# 2. Instale as dependências do Python
pip install -r requirements.txt

# 3. Crie a sua base de dados 
python manage.py migrate

# 4. Inicie o servidor do backend
python manage.py runserver

O seu backend está agora a correr em http://127.0.0.1:8000

3. Terminal 2: Iniciar o Frontend (React)

Abra um segundo terminal. Este será a sua "Loja" (interface).

# 1. Instale as dependências do React 
npm install

# 2. Inicie o servidor de desenvolvimento do Vite
npm run dev

O seu frontend está agora a correr em http://localhost:5173

Lembrete de Configuração
CORS: O backend (Django) só aceitará pedidos do frontend se o http://localhost:5173 estiver na sua lista de permissões.

Verifique o ficheiro uebax_project/settings.py e garanta que CORS_ALLOWED_ORIGINS contém o URL do seu frontend.

Criação de Admin: Para ver os dados no painel admin do Django (/admin), crie um superusuário:
python manage.py createsuperuser