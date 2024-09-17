# Etapa 1: Build do Frontend (React com Vite)
FROM node:20.12.2-slim AS build-frontend

# Defina o diretório de trabalho para o build do frontend
WORKDIR /app/ui

# Copie os arquivos de package.json e package-lock.json para instalar dependências
COPY ./ui/package*.json ./

# Instale as dependências do frontend
RUN npm install

# Copie o restante dos arquivos do frontend e faça o build
COPY ./ui ./
RUN npm run build

# Etapa 2: Build da API Backend (FastAPI)
FROM python:3.12.6-slim AS build-backend

# Defina o diretório de trabalho para o backend
WORKDIR /app/api

# Copie os arquivos requirements.txt da API
COPY ./api/requirements.txt ./

# Instale as dependências da API FastAPI em um ambiente virtual
RUN python -m venv /opt/venv \
    && . /opt/venv/bin/activate \
    && pip install --upgrade pip \
    && pip install -r requirements.txt

# Certifique-se de que o ambiente virtual esteja ativado em cada execução
ENV PATH="/opt/venv/bin:$PATH"

# Copie o restante do código da API
COPY ./api ./

# Etapa 3: Imagem Nginx para servir Frontend + API (via proxy)
FROM nginx:alpine

# Copie a configuração do Nginx
COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf

# Copie os arquivos estáticos do build do frontend para o diretório padrão do Nginx
COPY --from=build-frontend /app/ui/dist /usr/share/nginx/html

# Exponha a porta 80 para o Nginx
EXPOSE 80

# Comando para rodar o Nginx (por padrão, o Nginx já executa)
CMD ["nginx", "-g", "daemon off;"]

# Etapa 4: Container para rodar a API (separado)
FROM python:3.12.6-slim AS backend-container

# Defina o diretório de trabalho para o backend
WORKDIR /app/api

# Copie o build do backend já preparado
COPY --from=build-backend /app/api /app/api

# Exponha a porta 8000
EXPOSE 8000

# Comando para iniciar a API FastAPI com Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
