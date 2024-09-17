import plotly.graph_objects as go
import chainlit as cl
from openai import OpenAI
import os
import json
import duckdb
from src.charts import make_chart
import tiktoken
import logging

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s",
                    handlers=[logging.StreamHandler()])

client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

with open('prompts/intro.txt', encoding='utf-8', mode='r') as txt:
    prompt = txt.read()

with open('prompts/json_example.txt', encoding='utf-8', mode='r') as txt_json:
    json_example = txt_json.read()

# controle de tokens
MAX_TOKENS = 4096 
RESERVED_TOKENS = 500

def count_tokens(messages, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    num_tokens = sum(len(encoding.encode(msg["content"])) for msg in messages)
    return num_tokens


def api_message_handler(session, max_attempts=5, attempts=0):    
    while attempts < max_attempts:
        response = client.chat.completions.create(model="gpt-4-turbo",
                                                  messages=session,
                                                  response_format={"type": "json_object"})
        logging.info(f"Resposta API: {response}")
        response_content = response.choices[0].message.content
        try:
            json_content = json.loads(response_content)
            return json_content
        except json.JSONDecodeError:
            logging.info(f"Resposta API: API NÃO RESPONDEU NO FORMATO ESPERADO")
            session.append({"role": "system", "content": f'RESPONDA NESTE FORMATO: {json_example}'})
        attempts += 1
    return {"message": "Erro: ERRO DE API."}

# func para fazer graficos
async def send_chart(df, chart_config):
    fig = make_chart(df, **chart_config)
    elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
    await cl.Message(content="Aqui está o gráfico solicitado:", elements=elements).send()


@cl.on_message
async def handle_message(message: cl.Message):

    session = cl.user_session.get("history", [])
    if len(session) == 0:
        session.append({"role": "system", "content": prompt})

    session.append({"role": "user", "content": message.content})

    while count_tokens(session) > (MAX_TOKENS - RESERVED_TOKENS):
        if len(session) > 1:
            session.pop(1)
        else:
            break

    json_content = api_message_handler(session=session)

    assistant_message = json_content['message']
    session.append({"role": "assistant", "content": assistant_message})
    cl.user_session.set("history", session)

    if 'message' in json_content:
        await cl.Message(content=assistant_message).send()

    # se houver uma query e um gráfico, gerar o gráfico
    if 'query' in json_content and 'chart' in json_content:
        query = json_content['query'].replace('database.parquet', 'database/*/*/*/*.parquet')
        df = duckdb.sql(query).df()
        await send_chart(df, json_content['chart'])

    # se houver apenas a query, mostrar df em MD
    elif 'query' in json_content and 'chart' not in json_content:
        df = duckdb.sql(json_content['query']).df()
        df_md = df.to_markdown()
        await cl.Message(content=df_md).send()

    elif 'return_df' in json_content:
        df = duckdb.sql(json_content['query']).df()
        df_md = df.to_markdown()
        session.append({"role": "system", "content": df_md})
        #api_message_handler()

#TODO melhorar a lógica, ainda ta fraca
"""
Adicionar lógica para alimentar o chat com dados da tabela, tipo um distinc
"""