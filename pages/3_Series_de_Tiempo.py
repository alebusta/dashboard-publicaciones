import streamlit as st
import design
import pandas as pd
import plotly.express as px
import ast
import plotly.graph_objs as go

# Llamar los estilos personalizados
design.local_css("styles.css")

#Llamar al logo del encabezado
design.header()

st.title('Series de tiempo')




excel_file = 'divisiones_2015-2024_04.xlsx' #Nombre archivo a importar  'xlsx' hace referencia a excel

sheet_name = 'Sheet1' #la hoja de excel que voy a importar

df_tot = pd.read_excel(excel_file, #importo el archivo excel
                   sheet_name = sheet_name) #le digo cual hoja necesito

df = df_tot[df_tot['Sustantivo']=='SI']

df['temas'] = df['cepal.topicSpa'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)

df_temas = df.explode('temas')

# Agrupación por tipo
df_agrupado = df.groupby(['tipo_gr','dc.year']).count()[['dc.identifier.uri']] #que me agrupe por CALIFICACION y me cuente por los datos de  EDAD PERSONA ENCUESTADA
# Renombrar el índice y restablecer el índice del DataFrame
df_agrupado = df_agrupado.rename_axis(index={'tipo_gr': 'Tipo'}).reset_index()
# Renombrar la columna 'dc.identifier.uri' a 'Cantidad'
df_agrupado = df_agrupado.rename(columns={'dc.identifier.uri': 'Cantidad'})

# Agrupación por division
div_agrupado = df.groupby(['division','dc.year']).count()[['dc.identifier.uri']] #que me agrupe por CALIFICACION y me cuente por los datos de  EDAD PERSONA ENCUESTADA
# Renombrar el índice y restablecer el índice del DataFrame
div_agrupado = div_agrupado.rename_axis(index={'division': 'Tipo'}).reset_index()
# Renombrar la columna 'dc.identifier.uri' a 'Cantidad'
div_agrupado = div_agrupado.rename(columns={'dc.identifier.uri': 'Cantidad'})

# Agrupación por temas
tem_agrupado = df_temas.groupby(['temas','dc.year']).count()[['dc.identifier.uri']] #que me agrupe por CALIFICACION y me cuente por los datos de  EDAD PERSONA ENCUESTADA
# Renombrar el índice y restablecer el índice del DataFrame
tem_agrupado = tem_agrupado.rename_axis(index={'temas': 'Tipo'}).reset_index()
# Renombrar la columna 'dc.identifier.uri' a 'Cantidad'
tem_agrupado = tem_agrupado.rename(columns={'dc.identifier.uri': 'Cantidad'})

top_2023= list(tem_agrupado[tem_agrupado['dc.year']==2023].sort_values(by='Cantidad', ascending=False)[:15]['Tipo'])
top_2015= list(tem_agrupado[tem_agrupado['dc.year']==2015].sort_values(by='Cantidad', ascending=False)[:15]['Tipo'])

# Datos  
data = df_agrupado[df_agrupado['dc.year']<2024]
data2 = div_agrupado[div_agrupado['dc.year']<2024]
data3 = tem_agrupado[(tem_agrupado['Tipo'].isin(top_2023))&(tem_agrupado['dc.year']<2024)]
data4 = tem_agrupado[(tem_agrupado['Tipo'].isin(top_2015))&(tem_agrupado['dc.year']<2024)]
data_tot = data.groupby(['dc.year']).sum()[['Cantidad']]
 

# Función para crear el gráfico de series de tiempo
def plot_time_series(data):
    # Agregar una columna adicional que indique la serie total
    
    fig = px.line(data, x='dc.year', y='Cantidad', color='Tipo', height=550, width=800, labels={'dc.year':'Año'}) 
    
    # Agregar funcionalidad de resaltado
    fig.update_traces(selector=dict(mode='event', event='click'), hoverinfo='all', mode='lines')
    #fig.update_layout(legend=dict(traceorder='reversed'))
    # Agregar la serie total al gráfico
    #fig.add_scatter(x=data['dc.year'], y=data_tot['Cantidad'], mode='lines', name='Total', line=dict(color='black', dash='dot'))
    return fig
 
# Aplicación de Streamlit
def main():
    
    st.subheader("Publicaciones por tipo de documento")
    st.plotly_chart(plot_time_series(data))

    st.subheader("Publicaciones por unidad organizacional")
    st.plotly_chart(plot_time_series(data2))

    st.subheader("Evolución 15 temas más frecuentes en 2023")
    st.plotly_chart(plot_time_series(data3))

    st.subheader("Evolución 15 temas más frecuentes en 2015")
    st.plotly_chart(plot_time_series(data4))

if __name__ == '__main__':
    main()


    # Obtener la lista única de temas
temas_list = tem_agrupado['Tipo'].unique()

# Multiselect para seleccionar los temas
selected_temas = st.multiselect("Selecciona los temas", temas_list, default=temas_list[:3])

# Filtrar el DataFrame basado en los temas seleccionados
filtered_df = tem_agrupado[tem_agrupado['Tipo'].isin(selected_temas)&(tem_agrupado['dc.year']<2024)]

# Crear el gráfico de línea
fig = go.Figure()

for tema in selected_temas:
    tema_data = filtered_df[filtered_df['Tipo'] == tema]
    fig.add_trace(go.Scatter(x=tema_data['dc.year'], y=tema_data['Cantidad'], mode='lines', name=tema))

# Configurar el diseño del gráfico
fig.update_layout(title='Evolución de temas seleccionados', xaxis_title='Año', yaxis_title='Cantidad', width=800, height=500)

# Mostrar el gráfico en Streamlit
st.plotly_chart(fig)

design.footer()