FROM python:3.12-slim

WORKDIR /app

# Instala dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copia tudo para o container
COPY . .

# Instala todas as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Verifica se o modelo existe
RUN if [ -f "modelo_gradient_boosting.pkl" ]; then \
        echo "✅ Modelo encontrado"; \
    else \
        echo "❌ Modelo não encontrado"; \
        exit 1; \
    fi

EXPOSE 5000 8501

# O comando será sobrescrito pelo docker-compose
CMD ["python", "app.py"]