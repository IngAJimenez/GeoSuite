# apps/dashboard_inicio.py
import streamlit as st
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

def run():
    # --- Cargar configuración desde el archivo YAML ---
    with open('apps/config/config.yaml') as file:
        config = yaml.load(file, Loader=SafeLoader)

    # --- Inicializar el autenticador ---
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days'],
        # config['preauthorized']
    )

    # --- Renderizar el widget de login ---
    login_result = authenticator.login('main')
    # st.write(login_result)
    if login_result:
        name, authentication_status, username = login_result
    else:
        st.warning("Inicio de sesión.")
        # st.stop()

    # --- Lógica de la aplicación ---

    if st.session_state["authentication_status"]:
        # --- PÁGINA PRINCIPAL (CONTENIDO PROTEGIDO) ---
        st.sidebar.title(f'Bienvenido, *{st.session_state["name"]}*')
        authenticator.logout('Cerrar sesión', 'sidebar')

        st.title('Aplicación Segura 🔐')
        st.write('Has accedido al contenido exclusivo.')
        
        # 

    elif st.session_state["authentication_status"] is False:
        st.error('Usuario/contraseña incorrectos')
    elif st.session_state["authentication_status"] is None:
        st.warning('Por favor, introduce tu usuario y contraseña')