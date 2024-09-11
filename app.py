import plotly.graph_objects as go
import chainlit as cl
from openai import OpenAI
import os
import json
import duckdb
from src.charts import make_chart


client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
with open('prompts/intro.txt', encoding='utf-8', mode='r') as txt:
    prompt = txt.read()

# msg handler
@cl.on_message
async def handle_message(message: cl.Message):
    # manter logica de chat com sessão
    session = cl.user_session.get("history", [])
    session.append({"role": "user", "content": message.content})

    if not session:
        session.append({"role": "system", "content": prompt})

    response = client.chat.completions.create(model="gpt-4-turbo",
                                              messages=session)

    # Extrai o conteúdo da resposta
    print(response.choices[0].message.content.strip())
    json_content = json.loads(response.choices[0].message.content.strip())
    session.append({"role": "assistant", "content": json_content['message']})
    
    cl.user_session.set("history", session)
    await cl.Message(content=json_content['message']).send()

    if 'query' in json_content and 'chart' in json_content:
        df = duckdb.sql(json_content['query']).df()
        fig = make_chart(df, **json_content['chart'])
        elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
        await cl.Message(content="Aqui está o gráfico solicitado:", elements=elements).send()

    elif 'query' in json_content and 'chart' not in json_content:
        df = duckdb.sql(json_content['query']).df()
        await cl.Text(content=f"Dataframe:\n{df}")