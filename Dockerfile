# Etapa 1: Build do Frontend (React com Vite)
FROM node:20.12.2-slim AS build-frontend

WORKDIR /ui
COPY ./ui/package*.json ./
RUN npm ci
COPY ./ui ./
COPY ./ui/.env.example .env
RUN npm run build
RUN rm -rf node_modules

# Etapa 2: Imagem Nginx para servir Frontend + API (via proxy)
FROM nginx:alpine AS nginx-container

COPY ./nginx/nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build-frontend /ui/dist /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]

# Etapa 3: Container para rodar a API
FROM python:3.12.6-slim AS backend-builder

WORKDIR /api

# Copie requirements.txt e instale as dependências
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

COPY ./api/requirements.txt ./

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

FROM python:3.12.6-slim AS backend-container

WORKDIR /api

COPY --from=backend-builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=backend-builder /usr/local/bin /usr/local/bin

# Copie o código da API
COPY ./api ./

# Create non-root user
RUN useradd --create-home --shell /bin/bash apiuser && \
    chown -R apiuser:apiuser /api
USER apiuser

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

# Comando para iniciar a API FastAPI com Uvicorn
CMD ["python", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]