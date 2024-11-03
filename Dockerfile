FROM python:3.10-slim

# Defina a variável de ambiente para a chave da API do OpenAI
ARG OPENAI_API_KEY
ENV OPENAI_API_KEY=${OPENAI_API_KEY}

# Defina o diretório de trabalho
WORKDIR /app

# Copie o arquivo de requisitos e instale as dependências
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copie o restante dos arquivos necessários
COPY database/ ./database/
COPY prompts/ ./prompts/
COPY src/ ./src/
COPY static/ ./static/
COPY app.py ./app.py
COPY . .

# Exponha a porta que o Streamlit usará
EXPOSE 8501

# Comando para executar a aplicação Streamlit
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
