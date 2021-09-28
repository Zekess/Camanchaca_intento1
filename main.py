import streamlit as st
import pandas as pd
import base64
from Solver_codigos.get_instancias import CrearInstancias
from Solver_codigos.ExtendedWeek import solution_by_week
from time import time

# Parámetros/variables/funciones que se usarán:

st.set_page_config(layout="wide")
metodos = ['Calendarización desde Dotaciones', 'Calculo y comparación de nueva calendarización']
paginas_navegacion = ['Home', 'Instrucciones', metodos[0], metodos[1], 'About Us']
def xldownload(excel, name):
    data = open(excel, 'rb').read()
    b64 = base64.b64encode(data).decode('UTF-8')
    href = f'<a href="data:file/xls;base64,{b64}" download={name}>Descargar {name}</a>'
    return href
# ------------------------------------------------------------------------------------------------------------------


st.image('Imagenes_web/logo.png')

## Título

_, center, _ = st.columns((1, 2, 1))
center.markdown('# Asignación de Turnos.')

## Sidebar

with st.sidebar:
    st.image('Imagenes_web/logo.png')
    st.text('')
    st.text('')
    pag_navegacion_actual = st.radio('Navegar', paginas_navegacion)

# Página de bienvenida.
if pag_navegacion_actual == 'Home':
    '''
    ## Bienvenido/a.

    La interfaz para la ejecución del programa de __asignación de turnos__. Esta aplicación fue desarrollada
    en Surpoint Analytics SpA con el fin de facilitar el uso del _solver_ encargado de resolver el problema asignación
    de turnos.

    A la izquierda esá la barra de navegación. En _Instrucciones_ se encuentran los tutorailes para el uso de las
    diferentes herramientas de esta interfaz.        
    '''

# Página de instrucciones:
if pag_navegacion_actual == 'Instrucciones':
    st.header('Instrucciones.')
    '''
    Indique qué método desea revisar:
    '''
    metodo_instrucciones = st.selectbox('Seleccione método.', metodos)

    if metodo_instrucciones == metodos[0]:  # Instrucciones para el primer método
        '''
        Este método consiste de dos etapas. Primero recibe un archvo de dotaciones en formato excel y,
        a partir de este archivo, crea una instancia (archivo en formato excel) por cada ocupación y turno señalada
        en el archivo de dotaciones. Luego, por cada una de estas instancias, crea un archivo _solución_, que contiene
        la calendarización propuesta.

        __Entradas__: Sólo hay una entrada: el excel que se sube al presionar el _uploader_.
        '''

        st.file_uploader('Ejemplo de uploader:')

        '''
        Este excel de dotaciones debe tener tres hojas: Dotaciones, Parametros y Feriados. Cada una debe estar estructurada
        de la siguiente forma:

        __Dotaciones__:
        '''

        st.image('Imagenes_web/DotacionesEjemplo.jpg')

        '''
        __Parametros__:
        '''

        st.image('Imagenes_web/DotacionesEjemplo2.jpg')

        '''
        __Feriados__:
        '''

        st.image('Imagenes_web/DotacionesEjemplo3.jpg')

        '''
        Puede revisar el siguiente excel de dotaciones como ejemplo:
        '''

        st.markdown(xldownload('elementos_web/Dotaciones.xlsx', 'Dotaciones ejemplo'), unsafe_allow_html=True)
        '''
        Una vez cargado este archivo dotaciones, si todo salió bien, se desplegará una cuadro de mensaje como el siguiente: 
        '''
        st.success('Se ha cargado correctamente el excel de este metodo')
        '''
        Y además aparecerá una barra de carga que repsenta el progreso en la carga de los distintos turnos y cargos.

        Luego se desplegará una lista con todos los cargos y turnos obtenidos del archivo de entrada. En esta lista podrá marcar los cargos a los 
        cuales les quiera obtener una calendarización. Una vez seleccionados los cargos, deberá apretar el botón \'\'ejecutar solver\'\' para
        hacer correr el programa. Una vez terminada la ejecución, se desplegarán los resultados/calendarizaciones de cada cargo que haya
        seleccionado de tal forma que podrá inspeccionarlos y, si desea, descargar el excel con la calendarización.         
        '''

    elif metodo_instrucciones == metodos[1]:  # Instrucciones para el segundo metodo
        '''
        Este método consiste de una única etapa. Recibe un archvo descriptivo de un cargo en formato excel y,
        a partir de este archivo, crea un archivo _solución_, que contiene la calendarización propuesta para dicho cargo.
        Es decir, corresponde a la segunda etapa del método 1 pero utilizando un único cargo.

        __Entradas__: Sólo hay una entrada: el excel que se sube al presionar el _uploader_.
        '''

        st.file_uploader('Ejemplo de uploader:')

        '''
        Este excel, que debe corresponder a un único cargo, debe tener cuatro hojas: Parametros, Costos, Requerimientos y Feriados. Cada una debe estar estructurada
        de la siguiente forma:


        __Parametros__:
        '''

        st.image('Imagenes_web/InstanciaEjemplo1.jpg')

        '''
        __Costos__:
        '''

        st.image('Imagenes_web/InstanciaEjemplo2.jpg')

        '''
        __Requerimientos__:
        '''

        st.image('Imagenes_web/InstanciaEjemplo3.jpg')

        '''
        __Feriados__:
        '''

        st.image('Imagenes_web/InstanciaEjemplo4.jpg')

        '''
        Una vez cargado este escel, si todo salió bien, se desplegará una cuadro de mensaje como el siguiente: 
        '''
        st.success('Se ha cargado correctamente el excel de este metodo')
        '''
        Y además se desplegará el excel cargado. Antes de continuar, se recomienda revisar bien que el excel que se ha subido es el correcto.

        Luego, deberá apretar el botón \'\'ejecutar solver\'\' para hacer correr el programa. Una vez terminada la ejecución,
        se desplegará el resultado/calendarización del cargo que correspondiente de tal forma que podrá inspeccionarlo y, 
        si lo desea, descargar el excel con la calendarización.         
        '''

if pag_navegacion_actual == metodos[0]:
    st.header('Crear soluciones desde archivo de Dotaciones.')
    if 'key' not in st.session_state:
        st.session_state.key = 1
    excel_metodo1_uploader = st.file_uploader('Subir excel de dotaciones.', type="xlsx", key=st.session_state.key)

    if excel_metodo1_uploader is not None:
        st.success('Se cargó el excel exitosamente.')
        excel_metodo1 = pd.ExcelFile(excel_metodo1_uploader)
        if 'dict_excels' not in st.session_state:
            st.session_state.dict_excels = CrearInstancias(excel_metodo1)

    if 'dict_excels' in st.session_state:
        excels_names = list(st.session_state.dict_excels.keys())
        container_multiselect = st.container()
        check_all = st.checkbox('Seleccionar todos')
        if check_all:
            instancias_seleccionadas = container_multiselect.multiselect('Multiselect', excels_names, excels_names)
        else:
            instancias_seleccionadas = container_multiselect.multiselect('Multiselect', excels_names)
        if st.button('Ejecutar solver'):
            with st.spinner('Cargando calendarizaciones...'):
                total_soluciones = len(instancias_seleccionadas)
                barra_progreso_soluciones = st.progress(0)
                contador_soluciones = 0
                time_start = time()
                for xls_name in instancias_seleccionadas:
                    xls_writer = st.session_state.dict_excels[xls_name]
                    xls = pd.ExcelFile(xls_writer)
                    resultado_name, resultado_writer = solution_by_week(xls)
                    st.markdown(xldownload(resultado_writer, resultado_name), unsafe_allow_html=True)
                    contador_soluciones += 1
                    barra_progreso_soluciones.progress(contador_soluciones/total_soluciones)
                    time_stamp = time()-time_start
                    time_start = time_stamp
                    st.write(time_stamp)

    if st.button('Reset_all'):
        try:
            st.session_state.key += 1
        except:
            pass
        try:
            del (st.session_state.dict_excels)
        except:
            pass
        st.experimental_rerun()