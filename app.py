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
    # obter ou inicializar a sessão do usuário
    session = cl.user_session.get("history", [])
    if len(session) == 0:
        session.append({"role": "system", "content": prompt})

    session.append({"role": "user", "content": message.content})
    response = client.chat.completions.create(model="gpt-4-turbo",
                                              messages=session)

    print(response)
    response_content = response.choices[0].message.content
    json_content = json.loads(response_content)

    assistant_message = json_content['message']
    session.append({"role": "assistant", "content": assistant_message})
    cl.user_session.set("history", session)
    await cl.Message(content=assistant_message).send()

    # Se houver query e chart, gerar o gráfico
    if 'query' in json_content and 'chart' in json_content:
        df = duckdb.sql(json_content['query']).df()
        fig = make_chart(df, **json_content['chart'])
        elements = [cl.Plotly(name="chart", figure=fig, display="inline")]
        await cl.Message(content="Aqui está o gráfico solicitado:", elements=elements).send()

    # Se houver apenas query, mostrar o dataframe
    elif 'query' in json_content and 'chart' not in json_content:
        df = duckdb.sql(json_content['query']).df()
        await cl.DataFrame(df, description="Dataframe from query")

