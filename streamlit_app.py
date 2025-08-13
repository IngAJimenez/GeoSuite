# main.py
import streamlit as st
# import streamlit_authenticator as stauth
# import yaml
# from yaml.loader import SafeLoader


# Navegación después del login
from streamlit_option_menu import option_menu

st.set_page_config(page_title="GeoSuite", layout="wide")

with st.sidebar:
    selected = option_menu(
        menu_title="GeoSuite",
        options=["Inicio", "Capacidad de carga Terzaghi", "Asentamiento elastico", "Exploracion GDL", "Ensayo triaxial", "Presion de tierras", "Slope Bishop"],
        icons=["house"],
        default_index=0,
    )

if selected == "Inicio":
    st.markdown("<center><h2>GeoSuite (VERSION DE PRUEBA)</h2></center>", unsafe_allow_html=True)
    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")
   
    #Dos Columnas
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Bienvenidos a Geosuite**")
        st.write("Tu herramienta confiable para cálculos geotécnicos. ¡Comencemos!")
        st.write("Selecciona en la barra lateral la herramienta que desees utilizar y presiona el boton CALCULAR")
        st.write("Agradecemos la retroalimentacion y comentarios a proyectos@geotecniaterranova.com")
        st.write("Tambien puedes contactarnos por Whatsapp en este codigo QR")
        # st.image("images/FLYER GTN AGO24_.jpg")
        # from apps import dashboard_inicio
        # dashboard_inicio.run()

    with col2:
        st.image("images/ContactWSTNR.jpg")


elif selected == "Capacidad de carga Terzaghi":
    from apps import capacidad_carga
    capacidad_carga.run()

elif selected == "Ensayo triaxial":
    from apps import ensayo_triaxial

    ensayo_triaxial.run()

elif selected == "Presion de tierras":
    from apps import presiones_tierra
    presiones_tierra.run()

elif selected == "Asentamiento elastico":
    from apps import settlement
    settlement.run()


elif selected == "Slope Bishop":
    from apps import slope_bishop
    slope_bishop.run()

elif selected == "Exploracion GDL":
    from apps import geotexplo_gdl
    geotexplo_gdl.run()

# elif selected == "Slope Bishop Opt":
#     from apps import slope_bishop_opt
#     slope_bishop_opt.run()

# elif selected == "Estructural Zapata":
#     from apps import estr_zap
#     estr_zap.run()