import streamlit as st
import design
import pandas as pd
from pyvis.network import Network
import ast
import tempfile


st.set_page_config(page_title="Redes", page_icon="📈")

# Llamar los estilos personalizados
design.local_css("styles.css")

#Llamar al logo del encabezado
design.header()


st.title("Redes")

st.write(
    """Redes temáticas y organizacionales"""
)

excel_file = 'divisiones_2015-2024_04.xlsx' #Nombre archivo a importar  'xlsx' hace referencia a excel

sheet_name = 'Sheet1' #la hoja de excel que voy a importar

df_tot = pd.read_excel(excel_file, #importo el archivo excel
                   sheet_name = sheet_name) #le digo cual hoja necesito

df = df_tot[df_tot['Sustantivo']=='SI']


df['temas'] = df['cepal.topicSpa'].apply(lambda x: ast.literal_eval(x) if isinstance(x, str) and x.startswith('[') else x)

df_temas = df.explode('temas')

df_temas['temas'] = df_temas['temas'].replace('RECURSOS NATURALES', 'REC NATURALES')



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
                          value = (max(year),max(year))) #que tome desde el minimo, hasta el maximo


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
frecuencia = df_filtrado.groupby(['temas', 'division']).size().reset_index(name='frecuencia')

# Obtener los temas ordenados por frecuencia
temas_ordenados = frecuencia.groupby('temas')['frecuencia'].sum().sort_values(ascending=False)


# Función para crear la visualización de la red
def create_network_visualization(df):
    # Crear un objeto Network de pyvis
    net = Network(directed=False, height='700px')

    # Desactivar la simulación física por defecto
    net.toggle_physics(True)

    
    net.show_buttons(filter_=['physics'])

    # Crear conjuntos para almacenar temas y divisiones únicas
    temas_set = set()
    divisiones_set = set()

    # Agregar nodos y bordes al grafo
    for index, row in df.iterrows():
        tema = row['temas']
        division = row['division']
        frecuencia = row['frecuencia']
        
        # Agregar nodos de temas y divisiones al grafo
        net.add_node(tema, color='blue')
        net.add_node(division, color='red')

        # Agregar los nombres de temas y divisiones al conjunto respectivo
        temas_set.add(tema)
        divisiones_set.add(division)
        
        # Verificar si uno de los nodos es un tema y el otro es una división antes de agregar el borde
        if isinstance(tema, str) and isinstance(division, str):
            # Agregar borde entre tema y división con el ancho de acuerdo a la frecuencia
            net.add_edge(tema, division, width=frecuencia/20)

    # Guardar la visualización en un archivo HTML temporal
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
    temp_file.close()
    net.save_graph(temp_file.name)
    
    # Mostrar la visualización inicial en Streamlit
    st.components.v1.html(open(temp_file.name, "r").read(), height=800)
    
    # Crear menú de selección en Streamlit
    selected_option = st.selectbox("Seleccione una opción:", sorted(list(temas_set)))#.union(divisiones_set)))
    
    # Actualizar la visualización cuando el usuario seleccione una opción
    if selected_option:
        # Crear un nuevo objeto Network solo con los nodos y bordes relacionados con la opción seleccionada
        selected_net = Network(directed=False, height='500px')

        for index, row in df.iterrows():
            tema = row['temas']
            division = row['division']
            if selected_option == tema or selected_option == division:
                selected_net.add_node(tema, color='blue')
                selected_net.add_node(division, color='red')
                selected_net.add_edge(tema, division, width=row['frecuencia']/20)
        
        # Guardar la visualización actualizada en un archivo HTML temporal
        temp_file_selected = tempfile.NamedTemporaryFile(delete=False, suffix=".html")
        temp_file_selected.close()
        selected_net.save_graph(temp_file_selected.name)
        
        # Mostrar la visualización actualizada en Streamlit
        st.components.v1.html(open(temp_file_selected.name, "r").read(), height=600)



create_network_visualization(frecuencia)

design.footer()