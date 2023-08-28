import time
import pandas as pd
import numpy as np
import streamlit as st
import pydeck as pdk
import requests

from plotly import graph_objs as go
from pymongo import MongoClient
from datetime import datetime, timedelta


with st.sidebar:
    st.write("Seleções")

    # Selectbox para escolher a fazenda
    selected_farm = st.selectbox("Selecionar fazenda", ["Cristalina", "Unimar", "Univem sede"])

    # Selectbox para escolher o dispositivo de monitoramento
    selected_device = st.selectbox("Selecionar dispositivo", ["Boia Cristalina", "Boia Unimar", "Tanque Univem"])

    with st.spinner("Carregando informações..."):
        time.sleep(5)
    st.success("Pronto!")





API_KEY = 'cb5b30a4742c3ff08c5f2ffa90845071'
CITY = 'fartura'
URL = f'http://api.openweathermap.org/data/2.5/weather?q={CITY}&appid={API_KEY}&units=metric'

response = requests.get(URL)
weather_data = response.json()

cidade = weather_data['name']
pais = weather_data['sys']['country']
nuvens = weather_data['clouds']['all']

clima = weather_data['weather'][0]['main']
descricao = weather_data['weather'][0]['description']

pressao = weather_data['main']['pressure']
nivelMar = weather_data['main']['sea_level']
nivelTerra = weather_data['main']['grnd_level']

alvorada_timestamp = weather_data['sys']['sunrise']
crepusculo_timestamp = weather_data['sys']['sunset']

lat = weather_data['coord']['lat']
lon = weather_data['coord']['lon']

temperature = weather_data['main']['temp']
wind_speed = weather_data['wind']['speed']
humidity = weather_data['main']['humidity']

# Convertendo os timestamps em objetos de data e hora
alvorada_dt = datetime.utcfromtimestamp(alvorada_timestamp).strftime('%H:%M:%S')
crepusculo_dt = datetime.utcfromtimestamp(crepusculo_timestamp).strftime('%H:%M:%S')

col1, col2, col3 = st.columns(3)
col1.metric("Temperatura", f"{temperature} °C")
col2.metric("Velocidade do vento", f"{wind_speed} m/s")
col3.metric("Umidade", f"{humidity}%")
col1.metric('Cidade', cidade)
col2.metric('País', pais)
col3.metric('Nível de nuvens', nuvens)
col1.metric('Clima', clima)
col2.metric('Descrição', descricao)
col3.metric('Pressão Atmosférica',f'{pressao} Pa')
col1.metric('Nascer do Sol', alvorada_dt)  # Mostrar timestamp convertido
col2.metric('Por do Sol', crepusculo_dt)   # Mostrar timestamp convertido
col3.metric('Nível do mar', nivelMar)
col1.metric('Latitude', lat)
col2.metric('Longitude', lon)
col3.metric('Altitude', nivelTerra)


url = "https://api.thingspeak.com/channels/1854188/fields/1.json?results=1"

# Faça a solicitação GET à API do ThingSpeak
response = requests.get(url)

# Verifique se a solicitação foi bem-sucedida (código de status 200)
if response.status_code == 200:
    data = response.json()

    # Exiba os valores do campo 1
    for entry in data['feeds']:
        field_1_value = entry['field1']
        print(f"Valor do field 1: {field_1_value}")
else:
    print("Falha na solicitação. Código de status:", response.status_code)



def get_thingspeak_data(url):
    response = requests.get(url)
    data = response.json()

    for entry in data['feeds']:
        temperature_str = entry['field1']
        if temperature_str.strip() == "" or temperature_str is None:
            entry['field1'] = "0.00"

    return data



# Configurando a aplicação Streamlit
st.markdown("<h1 style='font-size: 24px;'>Gráfico de Temperatura em Tempo Real</h1>", unsafe_allow_html=True)

# Botão de atualização
if st.button("Atualizar gráfico", key="atualizar_btn"):
    data = get_thingspeak_data(url)

    temperature_values = []
    for entry in data['feeds']:
        temperature_str = entry['field1']
        try:
            temperature_float = float(temperature_str)
            temperature_values.append(temperature_float)
        except ValueError:
            temperature_values.append(0.00)

    formatted_dates = [entry['created_at'][5:16] for entry in data['feeds']]

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=formatted_dates, y=temperature_values, mode='lines+markers', name='Temperatura'))
    fig.update_xaxes(type='category')

    st.plotly_chart(fig, use_container_width=True)
    st.write("Gráfico atualizado!")

else:
    fig = go.Figure()
    st.plotly_chart(fig, use_container_width=True)

st.markdown("<style>div.stButton > button {font-size: 24px;}</style>", unsafe_allow_html=True)
st.write("Clique no botão 'Atualizar' para buscar os últimos dados.")










data = get_thingspeak_data(url)
# Extrair o valor da temperatura (supondo que a temperatura está no campo 'field1')
temperature_value = float(data['feeds'][0]['field1'])

# Criar o gráfico gauge com cor de fundo translúcida
fig = go.Figure(go.Indicator(
    mode="gauge+number",
    value=temperature_value,
    domain={'x': [0, 1], 'y': [0, 1]},
    title={'text': "Temperatura", 'font': {'size': 24}},
    #delta={'reference': 10, 'increasing': {'color': "green"}},
    gauge={
        'axis': {'range': [None, 40], 'tickwidth': 1, 'tickcolor': "gray"},
        'bar': {'color': "dodgerblue"},
        'bgcolor': "gray",
        'borderwidth': 4,
        'bordercolor': "gray",
        'steps': [
            {'range': [0, 20], 'color': 'aliceblue'},
            {'range': [20, 25], 'color': 'green'},
            {'range': [25, 30], 'color': 'orange'},
            {'range': [30,40], 'color': 'red' }
            ],
        'threshold': {
            'line': {'color': "gray", 'width': 4},
            'thickness': 0.75,
            'value': 35}}))

fig.update_layout(paper_bgcolor="rgba(0, 0, 0, 0)", font={'color': "gray", 'family': "Arial"})

# Exibir o gráfico no Streamlit
st.plotly_chart(fig, use_container_width=True)



def main():
    st.title("Chatbot Link")

    if st.button("Tire suas dúvidas sobre tilapicultura com nosso ChatBot"):
        st.markdown(
            '<iframe src="https://www.chatbase.co/chatbot-iframe/-3vx_mANpiqJxw_iCJQUv" width="100%" style="height: 100%; min-height: 700px" frameborder="0"></iframe>',
            unsafe_allow_html=True
        )

if __name__ == "__main__":
    main()



url = "https://api.thingspeak.com/channels/1854188/fields/1.json?results=1"
response = requests.get(url)
data = response.json()

# Extract temperature from each entry, handling empty strings
temperatures = []
for entry in data['feeds']:
    if 'field1' in entry and entry['field1']:  # Check if 'field1' exists and is not empty
        try:
            temperature = float(entry['field1'])
            temperatures.append(temperature)
        except ValueError:
            pass

# Coordenadas fictícias da Fazenda Cristalina (substitua pelas coordenadas reais)
fazenda_cristalina_coords = (-23.4000, -49.5300)

# Check the type of 'data'
print(type(data))

# Create a DataFrame for chart data
chart_data = pd.DataFrame({
    'lat': [fazenda_cristalina_coords[0]] * len(temperatures),
    'lon': [fazenda_cristalina_coords[1]] * len(temperatures),
    'temperature': temperatures
})

# Create a PyDeck chart using Streamlit
st.pydeck_chart(pdk.Deck(
    map_style=None,
    initial_view_state=pdk.ViewState(
        latitude=fazenda_cristalina_coords[0],
        longitude=fazenda_cristalina_coords[1],
        zoom=11,
        pitch=50,
    ),
    layers=[
        pdk.Layer(
            'HexagonLayer',
            data=chart_data,
            get_position='[lon, lat]',
            radius=200,
            elevation_scale=4,
            elevation_range=[0, 650],
            pickable=True,
            extruded=True,
        ),
        pdk.Layer(
            'ScatterplotLayer',
            data=chart_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
        ),
    ],
))




def get_temperature_data(start_date, end_date):
    # Substitua a string de conexão do MongoDB pela sua própria URL
    uri = "mongodb+srv://carlos:<Jal406477>@acquacluster.4ooae.mongodb.net/?retryWrites=true&w=majority"

    # Crie uma instância do cliente MongoDB
    client = MongoClient(uri)

    # Acesse o banco de dados e a coleção desejados
    db = client["acquacluster"]
    collection = db["sensor"]

    # Consulta ao banco de dados
    query = {
        "timestamp": {"$gte": start_date, "$lte": end_date}
    }
    results = collection.find(query)

    # Converta os resultados em um DataFrame do pandas
    temperature_data = pd.DataFrame(list(results))

    # Feche a conexão com o MongoDB
    client.close()

    return temperature_data


# Título da aplicação
st.title("Sistema de Consulta de Temperatura")

# Sidebar para selecionar datas
st.sidebar.header("Filtros")
start_date = st.sidebar.date_input("Data de início", datetime.now() - timedelta(days=7))
end_date = st.sidebar.date_input("Data de término", datetime.now())

# Obtenha os dados de temperatura usando a função criada
temperature_data = get_temperature_data(start_date, end_date)

# Exibição do histórico
st.write("### Histórico de Temperaturas")
st.write(temperature_data)

# Restante do código (exportação, impressão, etc.)
# ...

# Botão para imprimir
if st.button("Imprimir Tabela"):
    st.write("### Tabela de Temperaturas")
    st.dataframe(temperature_data)
