import plotly.graph_objects as go
import chainlit as cl
from openai import OpenAI
import os

# Configurar a chave da API da OpenAI
client = OpenAI(api_key='')  # Ou substitua pelo seu valor diretamente@cl.on_messageasync def handle_message(message: cl.Message):    if message.content.lower() == "mostrar gráfico":        # Cria a figura com Plotly        fig = go.Figure(            data=[go.Bar(y=[2, 1, 3])],            layout_title_text="Gráfico de Exemplo",        )        # Cria um elemento do Chainlit para exibir o gráfico        elements = [cl.Plotly(name="chart", figure=fig, display="inline")]        # Envia uma mensagem com o gráfico embutido        await cl.Message(content="Aqui está o gráfico solicitado:", elements=elements).send()    else:        # Chama a API do ChatGPT com GPT-4 usando a nova interface        response = client.chat.completions.create(            model="gpt-4-turbo",            messages=[                {"role": "system", "content": "Você é um assistente útil."},                {"role": "user", "content": message.content}            ]        )        # Extrai o conteúdo da resposta        content = response['choices'][0]['message']['content'].strip()        # Envia a resposta ao usuário


@cl.on_message
async def handle_message(message: cl.Message):
    if message.content.lower() == "mostrar gráfico":
        # Cria a figura com Plotly
        fig = go.Figure(
            data=[go.Bar(y=[2, 1, 3])],
            layout_title_text="Gráfico de Exemplo",
        )

        # Cria um elemento do Chainlit para exibir o gráfico
        elements = [cl.Plotly(name="chart", figure=fig, display="inline")]

        # Envia uma mensagem com o gráfico embutido
        await cl.Message(content="Aqui está o gráfico solicitado:", elements=elements).send()

    else:
        # Chama a API do ChatGPT com GPT-4 usando a nova interface
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "Você é um assistente útil."},
                {"role": "user", "content": message.content}
            ]
        )

        # Extrai o conteúdo da resposta
        content = response.choices[0].message.content.strip()

        # Envia a resposta ao usuário
        await cl.Message(content=content).send()
