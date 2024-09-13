import plotly.graph_objects as go
import chainlit as cl
from openai import OpenAI
import os
import json
import duckdb
from src.charts import make_chart
import tiktoken
import logging

# Configuração do logging
logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.StreamHandler()])

# Inicializa o cliente da API OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Carrega o prompt inicial de um arquivo
with open('prompts/intro.txt', encoding='utf-8', mode='r') as txt:
    prompt = txt.read()

# Definição do limite de tokens para GPT-4 Turbo
MAX_TOKENS = 4096 
RESERVED_TOKENS = 500

# Função para contar o número de tokens
def count_tokens(messages, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = sum(len(encoding.encode(msg["content"])) for msg in messages)
    return num_tokens

# Função para chamar a API e lidar com respostas que não venham em JSON
def api_message_handler(session, max_attempts=5):
    attempts = 0
    while attempts < max_attempts:
        response = client.chat.completions.create(model="gpt-4-turbo",
                                                  messages=session)
        logging.info(f"Resposta API: {response}")
        response_content = response.choices[0].message.content
        try:
            json_content = json.loads(response_content)
            return json_content
        except json.JSONDecodeError:
            session.append({"role": "system", "content": 'RESPOSTA NÃO VEIO EM JSON'})
        attempts += 1
    # Se o limite de tentativas for alcançado
    return {"message": "Erro: Não foi possível obter uma resposta válida em JSON."}

# Função para gerar e enviar gráficos
async def send_chart(df, chart_config):
    fig = make_chart(df, **chart_config)
    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
    await cl.Message(content="Aqui está o gráfico solicitado:", elements=elements).send()

# Função principal para tratar mensagens
@cl.on_message
async def handle_message(message: cl.Message):
    # Obter ou inicializar a sessão do usuário
    session = cl.user_session.get("history", [])
    if len(session) == 0:
        session.append({"role": "system", "content": prompt})

    # Adiciona a mensagem do usuário à sessão
    session.append({"role": "user", "content": message.content})

    # Remove mensagens antigas para controle de tokens
    while count_tokens(session) > (MAX_TOKENS - RESERVED_TOKENS):
        if len(session) > 1:
            session.pop(1)
        else:
            break

    # Chama a API da OpenAI e processa a resposta
    json_content = api_message_handler(session=session)

    assistant_message = json_content['message']
    session.append({"role": "assistant", "content": assistant_message})
    cl.user_session.set("history", session)
    await cl.Message(content=assistant_message).send()

    # Se houver uma query e um gráfico, gerar o gráfico
    if 'query' in json_content and 'chart' in json_content:
        query = json_content['query'].replace('database.parquet', 'database/*/*/*/*.parquet')
        df = duckdb.sql(query).df()
        await send_chart(df, json_content['chart'])

    # Se houver apenas a query, exibir o dataframe em formato Markdown
    elif 'query' in json_content and 'chart' not in json_content:
        df = duckdb.sql(json_content['query']).df()
        df_md = df.to_markdown()
        await cl.Message(content=df_md).send()
