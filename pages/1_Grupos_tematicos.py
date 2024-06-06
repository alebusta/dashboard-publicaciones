import streamlit as st
import design
import pandas as pd
import numpy as np
import ast
import plotly.express as px 
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.io as pio

st.set_page_config(page_title="Grupos temáticos", page_icon="📈")

# Llamar los estilos personalizados
design.local_css("styles.css")

#Llamar al logo del encabezado
design.header()


st.title("Grupos temáticos")
st.sidebar.header("Grupos temáticos")
st.write(
    """En esta sección se presenta cuales son los temas que abordan las publicaciones de CEPAL, a partir de los metadatos (tópicos CEPAL)"""
)

excel_file = 'divisiones_2015-2024_06_06.xlsx' #Nombre archivo a importar  'xlsx' hace referencia a excel

sheet_name = 'Sheet1' #la hoja de excel que voy a importar

df_tot = pd.read_excel(excel_file, #importo el archivo excel
                   sheet_name = sheet_name) #le digo cual hoja necesito

df = df_tot[df_tot['Sustantivo']=='SI']


df['temas'] = df['cepal.topicSpa'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)

df_temas = df.explode('temas')

## Hasta aquí el df base, ahora se requiere hacer un filtro para manipular los datos,

#Crear una lista con los parametros de una columna

division = df['division'].unique().tolist() # se crea una lista unica de la columna Division
tipo = df['tipo_gr'].unique().tolist() # se crea una lista unica de la columna tipo de documento
year = df['dc.year'].unique().tolist() # se crea una lista unica de la columna año

#Crear slider en el sidebar
st.sidebar.title('Filtrar datos')

#Crear un slider de edad

year_selector = st.sidebar.slider('Seleccionar años:',
                          min_value = min(year), #el valor minimo va a ser el valor mas pequeño que encuentre dentro de la columna EDAD PERSONA ENCUESTADA
                          max_value = max(year),#el valor maximo va a ser el valor mas grande que encuentre dentro de la columna EDAD PERSONA ENCUESTADA
                          value = (min(year),max(year))) #que tome desde el minimo, hasta el maximo


#crear multiselectores

#Agregar opción Todas
division_all = ['Todas'] + division
tipo_all = ['Todos'] + tipo

division_selector = st.sidebar.multiselect('Divisiones:',
                                 division_all,
                                 default = 'Todas')
# Si "todas" está seleccionada, seleccionar todas las demás divisiones
if 'Todas' in division_selector:
    division_selector = division

tipo_selector = st.sidebar.multiselect('Tipo de documentos:',
                                       tipo_all,
                                       default = 'Todos')
# Si "Todos" está seleccionada, seleccionar todas las demás divisiones
if 'Todos' in tipo_selector:
    tipo_selector = tipo


                                       
#Ahora necesito que esos selectores y slider me filtren la informacion

mask = (df['dc.year'].between(*year_selector))&(df['division'].isin(division_selector))&(df['tipo_gr'].isin(tipo_selector))

#mi df_temas filtrados por el mask
df_filtrado = df_temas[mask]

# Calcular la frecuencia de cada tema y división
tem_div = df_filtrado.groupby(['temas']).size().reset_index(name='frecuencia')

clusters = pd.read_excel('Clusters.xlsx', sheet_name = 'g3')

tem_div = pd.merge(tem_div, clusters, on='temas', how='left')

numero_resultados = tem_div.shape[0] ##number of availables rows
st.markdown(f'*Total temas:{numero_resultados}*') ## sale como un titulo que dice cuantos resultados tiene para ese filtro

#st.dataframe(tem_div)

# Obtén la lista ordenada de clusters
clusters_ordenados = sorted(tem_div['Cluster'].unique()) 

# Guarda los colores originales  
original_colors = {
    '1. Desarrollo económico': '#E41B1C',
    '2. Desarrollo social': '#377EB8',
    '3. Sustentabilidad ambiental y gestión de recursos naturales': '#4DAF4A',
    '4. Desarrollo productivo, innovación y aprovechamiento tecnológico': '#984EA3',
    '5. Institucionalidad, gobernanza y temas transversales': '#FF7F00'
}
                   
# Crear un DataFrame para cada categoría
data_frames = {cluster: tem_div[tem_div['Cluster'] == cluster] for cluster in tem_div['Cluster'].unique()}

# Crear una figura de dispersión para cada categoría
graf = make_subplots(rows=1, cols=1, shared_xaxes=True, shared_yaxes=True)

# Lista para mantener el orden de las trazas
ordered_traces = []

for cluster in clusters_ordenados:
    data_frame = data_frames[cluster]
    text_info = [
        f'Subject: {valor}<br>Publicaciones: {frec}' for valor, frec in zip(data_frame['temas'], 
                                                                                             data_frame['frecuencia']                                                                                             
                                                                           )
    ]
    trace = go.Scatter(
        x=data_frame['Item'], 
        y=data_frame['frecuencia'],
        mode='markers',
        name=cluster,
        text=text_info,
        hoverinfo='text',
        visible=True,  # Hacer visible por defecto
        marker=dict(
            color=original_colors[cluster],
            size=12,
            line=dict(
                width=2,
                color='white'
            ),
            opacity=0.6
        )
    )
    graf.add_trace(trace)
    ordered_traces.append(trace)

# Configura la figura   
graf.update_layout(
    title="Distribución Temática de las Publicaciones",
    height=800,
    width=800, 
    showlegend=True,
    legend=dict(
        x=0.5,
        y=-0.7,
        traceorder='normal',  # Ordenar por el orden de clusters_ordenados
        orientation='h',
        bgcolor='rgba(255, 255, 255, 0.6)',
        xanchor='center',  # Anclaje horizontal al centro
        yanchor='bottom',  # Anclaje vertical en la parte inferior
    )
)

# Configura la interacción con la leyenda
graf.update_layout(legend=dict(itemclick='toggleothers', traceorder='normal'))


st.plotly_chart(graf)


## Gráfico de barras


# Crear el gráfico interactivo
bar = px.bar(tem_div.sort_values('Cluster'), x='temas', y='frecuencia', color = 'Cluster', color_discrete_map = original_colors,
             opacity=0.6)


# Ordenar los temas de mayor a menor frecuencia
bar.update_xaxes(categoryorder='total descending')

# Personalizar el diseño del gráfico
bar.update_layout(title='Frecuencia de temas en publicaciones',
                      #xaxis_title='Temas',
                      yaxis_title='Número de publicaciones',
                      #legend_title='División',
                      xaxis_tickangle=-45,
                      width=800,
                      height=800,
                      showlegend=True,
                      legend=dict(
                        title='Grupo temático',
                        x=0.5,
                        y=-0.7,
                        #traceorder='normal',  # Ordenar por el orden de clusters_ordenados
                        orientation='h',
                        bgcolor='rgba(255, 255, 255, 0.6)',
                        xanchor='center',  # Anclaje horizontal al centro
                        yanchor='bottom'  # Anclaje vertical en la parte inferior
                        )
    )

st.plotly_chart(bar)

tema_df = tem_div.loc[tem_div['frecuencia'].idxmax(), 'temas']

st.subheader('Listado de publicaciones a partir de un tema seleccionado')


tema = tem_div['temas'].unique().tolist() # se crea una lista unica de la columna Division

tema_selector = st.selectbox('Seleccionar tema:', tema, index=tema.index(tema_df))


# Crea un contenedor vacío para el dataframe
df_container = st.empty()


# Dentro del contenedor, crea el dataframe
with df_container.container():
    # Código para crear el dataframe filtrado por tema_selector
    df_filtrado_tema = df_filtrado[df_filtrado['temas']==tema_selector][['dc.title','dc.identifier.uri','temas','dc.year','division']]
    st.write("Publicaciones: ", len(df_filtrado_tema))
    st.dataframe(df_filtrado_tema)

# Actualiza el dataframe dentro del contenedor cuando el tema_selector cambia

with df_container.container():
    df_filtrado_tema = df_filtrado[df_filtrado['temas']==tema_selector][['dc.title','dc.identifier.uri','dc.year','division','temas']]
    st.write("Publicaciones: ", len(df_filtrado_tema))  
    st.dataframe(df_filtrado_tema,
                   column_config={
        "dc.title": "Título",
        "dc.identifier.uri": st.column_config.LinkColumn("Enlace"),
        "dc.year": "Año",
        "division": "División"    
    },
    hide_index=True,
    width=900,)


    design.footer()
   