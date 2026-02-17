# 1. Builder (Construção) 
FROM python:3.13-slim AS builder

# Instala o 'uv' para gerenciar as dependências de forma rápida
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app
COPY pyproject.toml ./

# Instala as dependências no diretório do sistema
RUN uv pip install --system -r pyproject.toml

# 2. Estágio de Runtime (Execução)
FROM python:3.13-slim

WORKDIR /app

# Copia as bibliotecas do builder 
COPY --from=builder /usr/local/lib/python3.13/site-packages /usr/local/lib/python3.13/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin


# Copia o código da aplicação
COPY . .


# Criando o usuário
RUN useradd -m appuser

# Criamos a pasta e mudamos o dono
RUN mkdir -p /app/logs && chown -R appuser:appuser /app

# Mudamos para o usuário comum
USER appuser

# Porta que o flask irá usar
EXPOSE 5000
ENV FLASK_APP=app.main
ENV PYTHONUNBUFFERED=1

# Codigo que o container vai executar
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "2", "--timeout", "120", "app.main:app"]