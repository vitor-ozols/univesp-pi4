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

# Controle de tokens
MAX_TOKENS = 4096 
RESERVED_TOKENS = 500

def count_tokens(messages, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return sum(len(encoding.encode(msg["content"])) for msg in messages)

def call_openai_api(session, max_attempts=5):
    for attempt in range(max_attempts):
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=session,
            response_format={"type": "json_object"}
        )
        logging.info(f"Resposta API: {response}")
        response_content = response.choices[0].message.content
        try:
            return json.loads(response_content)
        except json.JSONDecodeError:
            logging.warning("API não respondeu no formato esperado. Tentando novamente...")
            session.append({"role": "system", "content": f'RESPONDA NESTE FORMATO: {json_example}'})
    return {"message": "Erro: ERRO DE API."}

async def send_chart(df, chart_config):
    fig = make_chart(df, **chart_config)
    await cl.Message(content="Aqui está o gráfico solicitado:", elements=[cl.Plotly(name="chart", figure=fig, display="inline")]).send()

async def process_message(session, json_content):
    assistant_message = json_content.get('message')
    if assistant_message:
        await cl.Message(content=assistant_message).send()

    query = json_content.get('query')
    chart_config = json_content.get('chart')
    return_df = json_content.get('return_df')

    if query:
        query = query.replace('database.parquet', 'database/*/*/*/*.parquet').replace("`", '"')
        df = duckdb.sql(query).df()

        if chart_config:
            await send_chart(df, chart_config)
        else:
            await cl.Message(content=df.to_markdown()).send()
    
    elif return_df:
        df = duckdb.sql(json_content['query']).df()
        session.append({"role": "system", "content": df.to_markdown()})
        new_json_content = call_openai_api(session)
        await process_message(session, new_json_content)

@cl.on_message
async def handle_message(message: cl.Message):
    session = cl.user_session.get("history", [])

    if not session:
        session.append({"role": "system", "content": prompt})

    session.append({"role": "user", "content": message.content})

    # Garantir que o número de tokens não ultrapasse o limite
    while count_tokens(session) > (MAX_TOKENS - RESERVED_TOKENS):
        if len(session) > 1:
            session.pop(1)
        else:
            break

    json_content = call_openai_api(session)
    session.append({"role": "assistant", "content": json_content.get('message', '')})
    cl.user_session.set("history", session)

    await process_message(session, json_content)