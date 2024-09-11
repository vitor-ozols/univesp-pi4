import plotly.graph_objects as go
import chainlit as cl
from openai import OpenAI
import os
import json


# Configurar a chave da API da OpenAI
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Função para lidar com mensagens
@cl.on_message
async def handle_message(message: cl.Message):
    # Recupera o histórico de mensagens da sessão do usuário
    session = cl.user_session.get("history", [])

    # Adiciona a mensagem atual ao histórico
    session.append({"role": "user", "content": message.content})

    # Se o usuário pedir para mostrar o gráfico
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
        # Adiciona as instruções do sistema no início da conversa
        if not session:
            session.append({"role": "system", "content": "Você é um assistente útil."})

        # Chama a API do ChatGPT com GPT-4 usando a nova interface
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=session  # Passa o histórico da conversa
        )

        # Extrai o conteúdo da resposta
        content = response.choices[0].message.content.strip()

        # Adiciona a resposta do assistente ao histórico
        session.append({"role": "assistant", "content": content})

        # Atualiza o histórico na sessão do usuário
        cl.user_session.set("history", session)

        # Envia a resposta ao usuário
        await cl.Message(content=content).send()
