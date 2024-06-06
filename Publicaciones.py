import pandas as pd
import streamlit as st
import design
import plotly.express as px

# Llamar los estilos personalizados
design.local_css("styles.css")

#Llamar al logo del encabezado
design.header()


st.title('Producción de publicaciones sustantivas CEPAL')


#st.set_page_config(page_title="Publicaciones CEPAL") # Nombre para configurar la pagina web
#st.header('Producción Publicaciones Sustantivas CEPAL') #Va a ser el titulo de la pagina

## ---------  CONTENIDO ---------- ##

excel_file = 'divisiones_2015-2024_06_06.xlsx' #Nombre archivo a importar  'xlsx' hace referencia a excel

sheet_name = 'Sheet1' #la hoja de excel que voy a importar

df_tot = pd.read_excel(excel_file, #importo el archivo excel
                   sheet_name = sheet_name) #le digo cual hoja necesito

df = df_tot[df_tot['Sustantivo']=='SI']


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

numero_resultados = df[mask].shape[0] ##number of availables rows
st.markdown(f'*Resultados Disponibles:{numero_resultados}*') ## sale como un titulo que dice cuantos resultados tiene para ese filtro

#una nueva agrupacion

df_agrupado = df[mask].groupby(['tipo_gr','dc.year']).count()[['dc.identifier.uri']] #que me agrupe por CALIFICACION y me cuente por los datos de  EDAD PERSONA ENCUESTADA
df_agrupado =df_agrupado.rename(columns={'dc.identifier.uri': 'Cantidad'})
df_agrupado =df_agrupado.reset_index()



df_filtrado = df[mask]

#pivot para reporte
# Crear la pivot table
pivot_table = pd.pivot_table(df_filtrado, 
                              index='tipo_gr',  # Columna para las filas
                              columns='dc.year',  # Columna para las columnas
                              values='dc.identifier.uri',  # Columna a contar
                              aggfunc='count',  # Función de agregación (en este caso, contar)
                              fill_value=0)  # Valor para los campos vacíos

#st.dataframe(pivot_table)


df_divisiones = df_filtrado.groupby(['division'], as_index = False)['dc.identifier.uri'].count() #hago un tipo de TABLA DINAMICA para agrupar los datos de una mejor manera, lo que hago aqui es que por cada EPS, me cuente la cantidad de personas encuestadas***

df_years = df_filtrado.groupby(['dc.year'], as_index = False)['dc.identifier.uri'].count().rename(columns={'dc.identifier.uri': 'Cantidad'})

# Gráfico de líneas para la serie de tiempo


line_chart = px.line(df_years,
                   title = 'Evolución de producción de documentos', 
                   x='dc.year',
                   y='Cantidad',
                   text ='Cantidad',
                   labels={'dc.year':'Año'}
                   )

# Ajustar la posición del texto para que esté un poco por encima de cada punto
line_chart.update_traces(textposition='top center')


st.plotly_chart(line_chart) #mostrar el grafico de barras en streamlit


#Crear un grafico de torta (pie chart)

pie_chart = px.pie(df_divisiones, #tomo el dataframe2
                   title = 'Distribución por unidad organizacional', #El titulo
                   values = 'dc.identifier.uri',##columna
                   names = 'division',
                   height = 600
                   ) ## para verlo por EPS --> Colores

st.plotly_chart(pie_chart) # de esta forma se va a mostrar el dataframe en Streamlit

#Crear un gráfico de barras


bar_chart = px.bar(df_agrupado,
                   title = 'Publicaciones por tipo de documento', 
                   x='tipo_gr',
                   y='Cantidad',
                   text =None,
                   color = df_agrupado['dc.year'].astype(str),
                   barmode='stack',
                   color_discrete_sequence=px.colors.sequential.algae,
                   height = 550,
                   labels={'tipo_gr': 'Tipo de documento', 'dc.year':'Año'}
                   )
# Mostrar el gráfico
bar_chart.update_layout(legend_title_text='Año')

totales = df_agrupado.groupby('tipo_gr').sum()


for i, row in totales.iterrows():
    bar_chart.add_annotation(x=i, y=totales['Cantidad'][i],
                       text=str(totales['Cantidad'][i]),
                       font=dict(color='black', size=12),
                       showarrow=False,
                       yshift=5)

st.plotly_chart(bar_chart) #mostrar el grafico de barras en streamlit



st.write("<h2 style='font-weight: bold; font-size: 18px;'>Detalle de publicaciones</h2>", unsafe_allow_html=True)

st.dataframe(
    df_filtrado[['dc.title','dc.identifier.uri','division']],
    column_config={
        "dc.title": "Título",
        "dc.identifier.uri": st.column_config.LinkColumn("Enlace"),
        "division": "División"        
    },
    hide_index=True,
    width=900,
)
###### -------- FIN DE CONTENIDO -----------####

design.footer()