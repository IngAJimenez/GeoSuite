# apps/presiones_tierra.py
import streamlit as st
import numpy as np
import matplotlib.pyplot as plt

def run():

    st.markdown("<center><h2>🧱 Presiones de Tierra - Método de Rankine</h2></center>", unsafe_allow_html=True)
    st.markdown("<center><h3>(Version de Prueba)</h3></center>", unsafe_allow_html=True)
    
    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")

    st.write("Calcula las presiones activas y pasivas para suelos sin cohesión (c=0), muro vertical y terreno horizontal.")

    st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")
    
    with st.form("rankine_form"):
        gamma = st.number_input("Peso volumétrico del suelo γ (kN/m³)", min_value=10.0, value=18.0, step=0.1)
        phi = st.number_input("Ángulo de fricción interna φ (°)", min_value=0.0, max_value=45.0, value=30.0, step=1.0)
        H = st.number_input("Altura del muro H (m)", min_value=0.1, value=3.0, step=0.1)

        submit = st.form_submit_button("CALCULAR", type="primary")

    if submit:
        phi_rad = np.radians(phi)

        # Coeficientes de Rankine
        Ka = np.tan(np.radians(45 - phi / 2)) ** 2
        K0 = 1 - np.sin(phi_rad)
        Kp = np.tan(np.radians(45 + phi / 2)) ** 2

        # Presiones en la base del muro
        pa = Ka * gamma * H
        p0 = K0 * gamma * H
        pp = Kp * gamma * H

        # Fuerza total (triángulo): P = 0.5 * Ka * γ * H²
        Pa = 0.5 * Ka * gamma * H**2
        P0 = 0.5 * K0 * gamma * H**2
        Pp = 0.5 * Kp * gamma * H**2


        col1, col2 = st.columns([1,2])
        
        with col1:
            st.subheader("📊 Resultados:")
            st.write(f"Coeficiente activo (Ka): **{Ka:.3f}**")
            st.write(f"Coeficiente en reposp (K0): **{K0:.3f}**")
            st.write(f"Coeficiente pasivo (Kp): **{Kp:.3f}**")

            st.divider()

            st.write(f"Presión activa en la base: **{pa:.2f} kPa**")
            st.write(f"Presión en reposo en la base: **{p0:.2f} kPa**")
            st.write(f"Presión pasiva en la base: **{pp:.2f} kPa**")

            st.divider()

            st.write(f"Fuerza activa total (Pa): **{Pa:.2f} kN/m**")
            st.write(f"Fuerza en reposo total (P0): **{P0:.2f} kN/m**")
            st.write(f"Fuerza pasiva total (Pp): **{Pp:.2f} kN/m**")

            st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")

        with col2:
            # Gráfico
            z = np.linspace(0, H, 100)
            sigma_a = Ka * gamma * z
            sigma_h0 = K0 * gamma * z
            sigma_p = Kp * gamma * z

            fig, ax = plt.subplots()
            ax.plot(sigma_a, z, label="Presión Activa", color='red')
            ax.plot(sigma_h0, z, label="Presión en Reposo", color='green')
            ax.plot(sigma_p, z, label="Presión Pasiva", color='blue')
            ax.set_xlabel("Presión (kPa)")
            ax.set_ylabel("Profundidad (m)")
            ax.invert_yaxis()
            ax.legend()
            ax.grid(True)
            st.pyplot(fig)
