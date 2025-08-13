# apps/capacidad_carga.py
import streamlit as st
import numpy as np

def run():
    st.markdown("<center><h2>🧱 Capacidad de Carga - Método de Terzaghi</h2></center>", unsafe_allow_html=True)
    st.markdown("<center><h3>(Version de Prueba)</h3></center>", unsafe_allow_html=True)

    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")

    st.write("Este cálculo es para **zapatas cuadradas** en condiciones drenadas (φ > 0), sin factores de forma, inclinacion, ni profundidad.")

    with st.form("input_form"):
        col1, col2 = st.columns(2)
        with col1:
            #Geometria de la cientacion
            st.write("**Geometria de la cimentacion**")
            B = st.number_input("Ancho de zapata **B** (m)", min_value=0.1, value=1.0, step=0.1)
            L = st.number_input("Largo de la cimentacion **L** (m)", min_value=0.1, value=1.0, step=0.1)
            Df = st.number_input("Profundidad de desplante **Df** (m)", min_value=0.1, value=1.0, step=0.1)

            st.divider()

            #Datos del suelo
            st.write("**Datos del suelo**")
            gamma = st.number_input("Peso volumétrico del suelo **γ** (kN/m³)", min_value=10.0, value=18.0, step=0.1)
            c = st.number_input("Cohesión del suelo **c** (kPa)", min_value=0.0, value=0.0, step=1.0)
            phi = st.number_input("Ángulo de fricción interna **φ** (°)", min_value=0.0, max_value=45.0, value=30.0, step=1.0)

            st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")

        with col2:
            
            st.image("images/capcarga1.png")

            #Mostrar la ecuacion de capacidad de carga de terzagui
            st.latex(r"""
            q_u = c N_c + q N_q +  \frac{1}{2} \gamma B N_\gamma
            """)

            #Mostrar los factores de capacidad de carga de Terzaghi
            st.latex(r"""
            \begin{align*}
            
            N_{q} &=\frac{e^{2\left ( 3\pi /4-\phi /2 \right )tan\left ( \phi  \right )}}{2 cos ^{2} \left ( 45 + \frac{\phi }{2} \right )}\\
                    \\
                    
            N_c &= \frac{N_q - 1}{\tan \phi} \\
                    \\
                    
            N_{\gamma} &=\frac{1}{2}\left ( \frac{K_{p\gamma }}{cos^{2}(\phi' )}-1 \right )*tan(\phi' )\\
            
            \end{align*}
            """)
            #Agregar fuente bibliografica
            st.caption("Fuente: Terzaghi, K. (1943). 'Theoretical Soil Mechanics'. Wiley, New York.")
        submit = st.form_submit_button("CALCULAR", type="primary")

        st.divider()




    if submit:
        # Convertir a radianes
        phi_rad = np.radians(phi)


        # Coeficientes de Terzaghi
        Nq = np.exp(2*(3*np.pi/4-phi_rad/2)*np.tan(phi_rad))/(2*np.cos(np.pi/4+phi_rad/2)**2)
        Nc = (Nq - 1) / np.tan(phi_rad) if phi != 0 else 5.7  # Nc ≈ 5.7 para φ = 0
     
        # Diccionario de valores Ny (Nγ) según phi, calculados por De Kumbhojkar 1993 (para zapata cuadrada)
        ny_dict = {
            0: 0.0,
            1: 0.01,
            2: 0.04,
            3: 0.06,
            4: 0.10,
            5: 0.14,
            6: 0.20,
            7: 0.27,
            8: 0.35,
            9: 0.44,
            10: 0.56,
            11: 0.69,
            12: 0.85,
            13: 1.04,
            14: 1.26,
            15: 1.52,
            16: 1.82,
            17: 2.18,
            18: 2.59,
            19: 3.07,
            20: 3.64,
            21: 4.31,
            22: 5.09,
            23: 6.00,
            24: 7.08,
            25: 8.43,
            26: 9.84,
            27: 11.60,
            28: 13.70,
            29: 16.18,
            30: 19.13,
            31: 22.65,
            32: 26.87,
            33: 31.94,
            34: 38.04,
            35: 45.41,
            36: 54.36,
            37: 65.27,
            38: 78.61,
            39: 95.03,
            40: 115.31,
            41: 140.51,
            42: 171.99,
            43: 211.56,
            44: 261.60,
            45: 325.34,
            46: 407.11,
            47: 512.84,
            48: 650.67,
            49: 831.99,
            50: 1072.80

        }

        # Interpolación lineal si phi no está en el diccionario
        phi_keys = sorted(ny_dict.keys())
        if phi in ny_dict:
            Ny = ny_dict[phi]
        else:
            for i in range(len(phi_keys)-1):
                if phi_keys[i] < phi < phi_keys[i+1]:
                    # Interpolación lineal
                    Ny = ny_dict[phi_keys[i]] + (ny_dict[phi_keys[i+1]] - ny_dict[phi_keys[i]]) * (phi - phi_keys[i]) / (phi_keys[i+1] - phi_keys[i])
                    break
                else:
                    Ny = ny_dict[phi_keys[-1]]  # Si phi > max key

        # Cálculo de qu y qadm (FS = 3 por defecto)
        q = gamma * Df
        qu = c * Nc + q * Nq + 0.4 * gamma * B * Ny  # factor 0.4 para zapata cuadrada
        FS = 3.0
        qadm = qu / FS

        # Mostrar resultados
        st.subheader("📊 Resultados:")

        # Mostrar valores de N
        # with st.expander("📘 Valores de coeficientes de Terzaghi"):
        st.write(f"**Nc** = {Nc:.2f}")
        st.write(f"**Nq** = {Nq:.2f}")
        st.write(f"**Ny** = {Ny:.2f}")

        #Mostrar los valors de capacidad de carga
        st.success(f"Capacidad de carga última **qu = {qu:.2f} kPa**")
        st.info(f"Capacidad de carga admisible (FS=3) **qadm = {qadm:.2f} kPa**")
        


