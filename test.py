import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import pydeck as pdk

#x = st.slider('x')
#st.write(x, 'square is', x * x)

DATE_TIME = "date/time"
DATA_URL = ("http://s3-us-west-2.amazonaws.com/streamlit-demo-data/uber-raw-data-sep14.csv.gz")

st.title("Toma de Uber en Nueva York")
st.markdown(
    """
    Primera app con Streamlit, tomado de la demo donde se muestra las tomas de taxi de Uber
    en Nueva York. 

    El deslizador se usa para elegir una hora del d{ia y ver loc cambios en los graficos.
    El codigo fuente original esta en: 
    [Ver codigo fuente](https://github.com/streamlit/demo-uber-nyc-pickups/blob/master/app.py)
    """
    )

@st.cache(persist = True)
def cargar_datos(nrows):
    datos = pd.read_csv(DATA_URL, nrows = nrows)
    lowercase = lambda x: str(x).lower()
    datos.rename(lowercase, axis = "columns", inplace = True)
    datos[DATE_TIME] =  pd.to_datetime(datos[DATE_TIME])
    return datos

datos = cargar_datos(100000) # Define cuantas filas del arcivo de datos se cargaran a la funcion cargar_datos

hora = st.slider("Horas a visualizar", 0, 23) # Desde las 00:00 a las 23:00

datos = datos[datos[DATE_TIME].dt.hour == hora]

st.subheader("Datos Geograficos entre %i:00 y %i:00" % (hora, (hora + 1) % 24))
punto_medio = (np.average(datos["lat"]), np.average(datos["lon"]))

st.write(pdk.Deck(
    map_style = "mapbox://styles/mapbox/light-v9",
    initial_view_state = {
    "latitude": punto_medio[0],
    "longitude": punto_medio[1],
    "zoom": 11,
    "pitch":50,
    },
    layers = [
        pdk.Layer(
            "HexagonLayer",
            data=datos,
            get_position=["lon", "lat"],
            radius=100,
            elevation_scale=4,
            elevation_range=[0, 1000],
            pickable=True,
            extruded=True,
        ),
    ],
))

st.subheader("Desgloce por minuto entre %i:00 y %i:00" % (hora, (hora + 1)%24))
filtered = datos[
    (datos[DATE_TIME].dt.hour >= hora) & (datos[DATE_TIME].dt.hour < (hora + 1))
]
hist = np.histogram(filtered[DATE_TIME].dt.minute, bins=60, range=(0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "pickups":hist})

st.altair_chart(alt.Chart(chart_data)
    .mark_area(
        interpolate='step-after',
        ).encode(
        x=alt.X("minute:Q", scale=alt.Scale(nice=False)),
        y=alt.Y("pickups:Q"),
        tooltip=['minute', 'pickups']
        ), use_container_width=True
    )

if st.checkbox("Ver datos en bruto", False):
    st.subheader("Datos en bruto por minuto entre %i:00 y %i:00" % (hora, (hora + 1)%24))
    st.write(datos)