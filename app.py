import plotly.graph_objects as go
import streamlit as st
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

MAX_TOKENS = 4096
RESERVED_TOKENS = 500

def count_tokens(messages, model="gpt-4-turbo"):
    encoding = tiktoken.encoding_for_model(model)
    return sum(len(encoding.encode(msg["content"])) for msg in messages)

def get_messages_for_api(session):
    return [{'role': msg['role'], 'content': msg['content']} for msg in session]

def call_openai_api(session, max_attempts=5):
    messages_for_api = get_messages_for_api(session)
    for attempt in range(max_attempts):
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo",
                messages=messages_for_api,
                response_format={"type": "json_object"}
            )
            logging.info(f"Resposta API: {response}")
            response_content = response.choices[0].message.content
            return json.loads(response_content)
        except json.JSONDecodeError:
            logging.warning("API não respondeu no formato esperado. Tentando novamente...")
            messages_for_api.append({"role": "system", "content": f'RESPONDA NESTE FORMATO: {json_example}'})
        except Exception as e:
            st.error(f"Ocorreu um erro ao chamar a API do OpenAI: {str(e)}")
            return {"message": "Erro: ERRO DE API."}
    st.error("Não foi possível obter uma resposta válida da API do OpenAI após várias tentativas.")
    return {"message": "Erro: ERRO DE API."}

def process_message(session, json_content):
    query = json_content.get('query')
    chart_config = json_content.get('chart')

    # Armazenar dados para exibição posterior
    assistant_data = {}

    if query:
        assistant_data['query'] = query  # Armazena a consulta
        try:
            query_executavel = query.replace('database.parquet', 'database/*/*/*/*.parquet').replace("`", '"')
            df = duckdb.sql(query_executavel).df()

            if chart_config:
                fig = make_chart(df, **chart_config)
                assistant_data['chart'] = fig
            else:
                assistant_data['dataframe'] = df
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar a consulta ou gerar o gráfico: {str(e)}")
            assistant_data['error'] = str(e)
    # Adicionar os dados ao histórico
    if assistant_data:
        # Encontrar a última mensagem do assistente e adicionar os dados
        for msg in reversed(session):
            if msg['role'] == 'assistant' and 'data' not in msg:
                msg['data'] = assistant_data
                break

def main():
    st.sidebar.image("static/logo.png", use_column_width=True)
    
    sidebar_text = """
    ### Assistente 156 Prefeitura de São Paulo
    Esta aplicação visa analisar a base de 
    dados pública dos chamados do SP156 da 
    Prefeitura de São Paulo, buscando identificar
    padrões no atendimento dos chamados em 
    diferentes regiões e tipos de serviços.

    ### Desenvolvido por:
    - Vitor Ozols
    - Mario Matienzo
    - Renan Milochi
    - Sergio Augusto
    """

    st.sidebar.markdown(sidebar_text)
    if st.sidebar.button("Reiniciar Conversa"):
        st.session_state['history'] = []
        st.session_state['history'].append({"role": "system", "content": prompt})
        st.rerun()
    
    contatos = """
    ### Contatos
    2110167@aluno.univesp.br, 2101355@aluno.univesp.br, 2011094@aluno.univesp.br, 2106972@aluno.univesp.br 
    """
    st.sidebar.markdown(contatos)

    st.title("Assistente 156 Prefeitura de São Paulo")
    
    if 'history' not in st.session_state:
        st.session_state['history'] = []
        st.session_state['history'].append({"role": "system", "content": prompt})

    session = st.session_state['history']

    # Exibir o histórico de mensagens
    for message in session:
        if message['role'] == 'user':
            with st.chat_message("user"):
                st.write(message['content'])
        elif message['role'] == 'assistant':
            with st.chat_message("assistant"):
                st.write(message['content'])
                # Verificar se há dados adicionais
                if 'data' in message:
                    assistant_data = message['data']
                    if 'query' in assistant_data:
                        st.markdown(f"```sql\n{assistant_data['query']}\n```")
                    if 'chart' in assistant_data:
                        st.write("Aqui está o gráfico solicitado:")
                        st.plotly_chart(assistant_data['chart'], use_container_width=True)
                    elif 'dataframe' in assistant_data:
                        st.write(assistant_data['dataframe'])
                    if 'error' in assistant_data:
                        st.error(f"Erro: {assistant_data['error']}")

    # Obter entrada do usuário usando st.chat_input
    user_input = st.chat_input("Digite sua mensagem")
    if user_input:
        # Exibir a mensagem do usuário
        with st.chat_message("user"):
            st.write(user_input)
        session.append({"role": "user", "content": user_input})

        # Garantir que o número de tokens não ultrapasse o limite
        session_for_api = get_messages_for_api(session)
        while count_tokens(session_for_api) > (MAX_TOKENS - RESERVED_TOKENS):
            if len(session) > 1:
                session.pop(1)
                session_for_api = get_messages_for_api(session)
            else:
                break

        # Chamar a API do OpenAI
        try:
            json_content = call_openai_api(session)
            assistant_message = json_content.get('message', '')

            # Adicionar a resposta do assistente ao histórico
            session.append({"role": "assistant", "content": assistant_message})
            st.session_state['history'] = session

            # Processar a mensagem (gráficos, consultas, etc.)
            process_message(session, json_content)
        except Exception as e:
            st.error(f"Ocorreu um erro ao processar sua mensagem: {str(e)}")
        
        # Recarregar a interface para exibir novos dados
        st.rerun()

if __name__ == "__main__":
    main()
