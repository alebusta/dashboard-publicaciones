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

st.title("Temas")

st.write(
    """Temas de publicaciones y divisiones autoras"""
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

def grafico_temas_division_interactivo(df, rango_temas=(0, 25), colores_division=None):

    # Calcular la frecuencia de cada tema y división
    frecuencia = df_filtrado.groupby(['temas', 'division']).size().reset_index(name='frecuencia')

    # Obtener los temas ordenados por frecuencia
    temas_ordenados = frecuencia.groupby('temas')['frecuencia'].sum().sort_values(ascending=False)

    # Obtener los temas dentro del rango especificado
    temas_rango = temas_ordenados.reset_index()['temas'][rango_temas[0]:rango_temas[1]]

    # Filtrar los datos para los temas en el rango
    frecuencia = frecuencia[frecuencia['temas'].isin(temas_rango)]

    # Crear un diccionario que mapee cada división a un color específico
    colores_division_dict = {'ASUNTOS DE GÉNERO': '#E999FF','Brasilia': '#24A215', 'Bogotá': '#968783',
                             'Buenos Aires': '#A0D1F8','CEPAL':'#1698FE','COMERCIO INTERNACIONAL E INTEGRACIÓN':'#104E7F',
                             'DESARROLLO ECONÓMICO':'#F50D2D','DESARROLLO PRODUCTIVO Y EMPRESARIAL':'#8D29E1',
                             'DESARROLLO SOCIAL':'#060DF7','DESARROLLO SOSTENIBLE Y ASENTAMIENTOS HUMANOS':'#88FF01',
                             'ESTADÍSTICAS':'#FF7012','Interdivisional':'#514F4B','México': '#8CFFAC', 'Montevideo': '#F7E8AD',
                             'PLANIFICACIÓN PARA EL DESARROLLO': '#F3FA0B', 'POBLACIÓN Y DESARROLLO': '#FFC300',
                             'RECURSOS NATURALES':'#8A4B2E','Revista':'#FF4BC9','Puerto España':'#EC936F',
                             'Washington': '#DFDDDC',
                            }

    # Crear el gráfico interactivo
    fig = px.bar(frecuencia, x='temas', y='frecuencia', color='division', barmode='stack',
                 color_discrete_map=colores_division_dict)

    # Ordenar los temas de mayor a menor frecuencia
    fig.update_xaxes(categoryorder='total descending')

    # Personalizar el diseño del gráfico
    fig.update_layout(title='Frecuencia de temas por unidad organizacional',
                      xaxis_title='Temas',
                      yaxis_title='Cantidad de publicaciones',
                      legend_title='Unidad organizacional',
                      xaxis_tickangle=-45,
                      width=1100,
                      height=800)

    # Mostrar el gráfico y conteo
    #numero_resultados = temas_ordenados.shape[0] ##number of availables rows
    #st.markdown(f'*Total temas:{numero_resultados}*') ## sale como un titulo que dice cuantos resultados tiene para ese filtro

    st.plotly_chart(fig)

   
# Ejemplo de uso
grafico_temas_division_interactivo(df, rango_temas=(0, 151))


design.footer()