### Análise da Eficiência no Atendimento do SP156: Um Estudo sobre Disparidades De Atendimentos Regionais

Este estudo tem como objetivo explorar a base de dados dos chamados, identificando padrões de atendimento em diferentes regiões e tipos de serviço. O foco do projeto é o desenvolvimento de um chatbot que facilita a visualização dos dados, gerando gráficos e dashboards automaticamente. Essa ferramenta interativa permite que os usuários explorem métricas como a distribuição dos chamados, taxas de atendimento e tempo médio de resposta, oferecendo uma maneira prática e visual de interpretar as informações disponíveis.


### Diagrama da Solução
![](misc/Diagrama.png)

#### Recursos:
- ETL;
- Scraping;
- Particionamento Hive;
- Engenharia de Prompt;
- Leitura dos dados com DuckDB;
- Elaboração de resposta Personalizada com ChatGPT;
- Elaboração de queries para DuckDB ler partição HIVE com auxilio do ChatGPT;
- Elaboração de gráficos no Streamlit com auxilio do ChatGPT.

### Implantação
- Adicione a chave da openai api como variável de ambiente:
```bash
echo 'export OPENAI_API_KEY="sua-chave-da-api"' >> ~/.bashrc
source ~/.bashrc

```
- Execute o comando abaixo para criar a imagem:
```bash
docker build --build-arg OPENAI_API_KEY=$OPENAI_API_KEY -t chat .
```
- Execute o comando abaixo para executar a imagem:
```bash
docker run -p 8501:8501 chat
```
- Também é possível executar a solução sem buildar imagem no docker com os comandos:
```bash
pip install -r requirements.txt
streamlit run app.py
```
