# Etapa 1: Build do Frontend (React com Vite)
FROM node:20.12.2-slim AS build-frontend

WORKDIR /ui
COPY ./ui/package*.json ./
RUN npm install
COPY ./ui ./
RUN npm run build

# Etapa 2: Imagem Nginx para servir Frontend + API (via proxy)
FROM nginx:alpine AS nginx-container

COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-frontend /ui/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Etapa 3: Container para rodar a API
FROM python:3.12.6-slim AS backend-container

WORKDIR /api

# Copie requirements.txt e instale as dependências
COPY ./api/requirements.txt ./
RUN pip install --upgrade pip \
    && pip install -r requirements.txt

# Copie o código da API
COPY ./api ./

EXPOSE 8000

# Comando para iniciar a API FastAPI com Uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]