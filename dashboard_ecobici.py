"""Tablero de recomendación de estaciones ECOBICI.
Ubicar en la raíz de Titulacion-CD y ejecutar: python -m streamlit run dashboard_ecobici.py
"""
from pathlib import Path

import geopandas as gpd
import numpy as np
import pandas as pd
import pydeck as pdk
from scipy.sparse import load_npz
import streamlit as st

from motor_ecobici import MotorEcobici


BASE = Path(__file__).resolve().parent
DATOS = BASE / 'Data' / 'Procesados' / 'Tablero'

st.set_page_config(page_title='Expansión ECOBICI', page_icon='🚲', layout='wide')


@st.cache_resource(show_spinner='Cargando datos de la optimización…')
def cargar():
    candidatas = gpd.read_file(DATOS / 'candidatas.gpkg').sort_values('idx_modelo').reset_index(drop=True)
    estaciones = gpd.read_file(DATOS / 'estaciones.gpkg')
    alcaldias = gpd.read_file(DATOS / 'alcaldias.gpkg')
    cobertura = load_npz(DATOS / 'matriz_cobertura.npz').tocsr()
    grafo = load_npz(DATOS / 'grafo.npz').tocsr()
    habitantes = np.load(DATOS / 'habitantes.npy')
    motor = MotorEcobici(candidatas, cobertura, habitantes, grafo)
    return motor, estaciones, alcaldias


st.title('🚲 Expansión óptima de ECOBICI')
st.caption('Herramienta exploratoria para comparar proyectos de instalación de nuevas estaciones en CDMX.')

try:
    motor, existentes, alcaldias = cargar()
except (FileNotFoundError, OSError, ValueError, KeyError) as exc:
    st.error('Faltan los datos exportados desde el notebook o están incompletos.')
    st.code(str(exc))
    st.info('Ejecuta la celda de exportación del notebook. Los archivos deben quedar en Data/Procesados/Tablero/.')
    st.stop()

nombres = sorted(motor.candidatas['alcaldia'].dropna().unique())
with st.sidebar:
    st.header('Configuración')
    k = st.number_input('Estaciones nuevas (K)', min_value=10, max_value=int(len(motor.ids)), value=10, step=1)
    alcaldia_ui = st.selectbox('Área geográfica', ['Toda CDMX'] + nombres)
    alcaldia = None if alcaldia_ui == 'Toda CDMX' else alcaldia_ui
    peso = st.slider('Peso de cobertura poblacional (%)', 0, 100, 65, 5)
    st.caption(f'Peso de demanda estimada: {100-peso}%.')
    estrategia = st.radio('Estrategia de conectividad', ['Mixta', 'Solo conectada'])
    tamano = st.selectbox('Mínimo de estaciones por nuevo núcleo', [5, 7, 10], index=0,
                          disabled=(estrategia == 'Solo conectada'))
    ejecutar = st.button('Calcular recomendaciones', type='primary', use_container_width=True)

if not ejecutar:
    st.info('Configura el escenario en la barra lateral y selecciona **Calcular recomendaciones**.')
    st.caption('Todos los criterios utilizan datos precalculados en el proyecto de titulación.')
    st.stop()

try:
    with st.spinner('Evaluando ubicaciones y conectividad…'):
        resultado = motor.optimizar(
            K=int(k), peso_cobertura=peso/100, alcaldia=alcaldia,
            estrategia=estrategia, minimo_nucleo=tamano,
        )
        resultado = motor.clasificar_componentes(resultado)
except (ValueError, RuntimeError) as exc:
    st.error(f'No fue posible construir el escenario: {exc}')
    st.stop()

poblacion = float(resultado['poblacion_adicional'].sum())
demanda = float(resultado['demanda_rf'].sum())
num_nucleos = int(resultado.loc[resultado['tipo_red'] == 'Núcleo independiente', 'componente'].nunique())

c1, c2, c3, c4 = st.columns(4)
c1.metric('Estaciones recomendadas', len(resultado))
c2.metric('Habitantes adicionales cubiertos', f'{poblacion:,.0f}')
c3.metric('Movimientos diarios estimados¹', f'{demanda:,.0f}')
c4.metric('Núcleos independientes', num_nucleos)

# Generar puntos para el mapa, preservando ID y la clasificación de red final.
seleccionadas = motor.candidatas.drop(columns=['demanda_rf']).merge(
    resultado,
    on='id_celda',
    validate='one_to_one'
)
seleccionadas = seleccionadas.to_crs('EPSG:4326')
existentes_mapa = existentes.to_crs('EPSG:4326')

seleccionadas['lon'] = seleccionadas.geometry.x
seleccionadas['lat'] = seleccionadas.geometry.y
existentes_mapa['lon'] = existentes_mapa.geometry.x
existentes_mapa['lat'] = existentes_mapa.geometry.y

seleccionadas['color'] = seleccionadas['tipo_red'].map({
    'Conectada a ECOBICI': [243, 140, 65],
    'Núcleo independiente': [28, 163, 128]
})

# Una vista en torno a las recomendaciones, o de la alcaldía solicitada.
if alcaldia is None:
    lon0, lat0 = float(seleccionadas['lon'].mean()), float(seleccionadas['lat'].mean())
    zoom = 11
else:
    territorio = alcaldias.loc[alcaldias['alcaldia'] == alcaldia].to_crs('EPSG:4326')
    centro = territorio.geometry.union_all().centroid
    lon0, lat0, zoom = float(centro.x), float(centro.y), 11.5

capas = []
if alcaldia is not None:
    capas.append(pdk.Layer(
        'GeoJsonLayer', data=territorio.__geo_interface__,
        stroked=True, filled=True, get_fill_color=[75, 110, 130, 12],
        get_line_color=[49, 78, 102, 190], line_width_min_pixels=2,
    ))
capas.extend([
    pdk.Layer('ScatterplotLayer', data=existentes_mapa[['lon', 'lat']],
              get_position='[lon, lat]', get_fill_color=[44, 114, 175, 150],
              get_radius=70, radius_min_pixels=2, pickable=False),
    pdk.Layer('ScatterplotLayer',
              data=seleccionadas[['lon', 'lat', 'id_celda', 'poblacion_adicional',
                                  'demanda_rf', 'tipo_red', 'componente', 'color']],
              get_position='[lon, lat]', get_fill_color='color',
              get_radius=170, radius_min_pixels=7, pickable=True,
              get_line_color=[30, 30, 30], stroked=True, line_width_min_pixels=1),
])

st.pydeck_chart(pdk.Deck(
    layers=capas,
    initial_view_state=pdk.ViewState(latitude=lat0, longitude=lon0, zoom=zoom, pitch=0),
    tooltip={'html': '<b>Cuadrícula {id_celda}</b><br/>{tipo_red} — grupo {componente}'
                     '<br/>Población marginal: {poblacion_adicional}'
                     '<br/>Movimientos predichos: {demanda_rf}',
             'style': {'backgroundColor': '#1D2936', 'color': 'white'}},
    map_style='https://basemaps.cartocdn.com/gl/positron-gl-style/style.json',
), use_container_width=True, height=520)

st.caption('🔵 ECOBICI existente  ·  🟠 Nuevas estaciones conectadas a ECOBICI  ·  🟢 Nuevos núcleos independientes')

st.subheader('Ubicaciones recomendadas')
columnas = ['id_celda', 'componente', 'tipo_red', 'poblacion_adicional',
            'demanda_rf', 'infra_ciclista_500m', 'dist_ecobici_min', 'alcaldia']
st.dataframe(
    seleccionadas[columnas].rename(columns={
        'id_celda': 'Cuadrícula', 'componente': 'Grupo', 'tipo_red': 'Conectividad',
        'poblacion_adicional': 'Población adicional', 'demanda_rf': 'Movimientos/día¹',
        'infra_ciclista_500m': 'Infraestructura ciclista (m)',
        'dist_ecobici_min': 'Distancia a ECOBICI (m)', 'alcaldia': 'Alcaldía',
    }),
    hide_index=True, use_container_width=True,
)

# CSV independiente de geometrías; añade lat/lon para abrir en otros programas.
exportar = seleccionadas.drop(columns=['geometry', 'color']).copy()
st.download_button(
    'Descargar recomendaciones (CSV)',
    data=exportar.to_csv(index=False).encode('utf-8-sig'),
    file_name='recomendaciones_ecobici.csv', mime='text/csv',
)

st.caption('¹ Suma de predicciones individuales de Random Forest, no viajes adicionales garantizados. '
           'Cobertura: puntos representativos de manzanas dentro de 500 m en línea recta; '
           'conectividad: distancias euclidianas, no rutas verificadas. '
           'La selección utiliza una heurística y no garantiza un óptimo global.')
