# apps/ensayo_triaxial.py
import streamlit as st
import numpy as np
import pandas as pd

def run():
    st.markdown("<center><h2>🧪 Ensayo Triaxial - Cálculo de c y φ</h2></center>", unsafe_allow_html=True)
    st.markdown("<center><h3>(Version de Prueba)</h3></center>", unsafe_allow_html=True)
    
    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")

    st.write("Introduce los valores de esfuerzo principal mayor (σ₁) y menor (σ₃) de **tres probetas** para calcular la envolvente de falla de Mohr-Coulomb.")
    st.caption("Nota: σ₃ es el esfuerzo de confinamiento y σ₁ es σ₃ mas el efuerzo desviador")

    st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")

    with st.form("triaxial_form"):
        st.subheader("Datos del ensayo")
        data = {
            "Probeta" : [1,2,3],
            "σ₃ (kPa)": [],
            "σ₁ (kPa)": []
        }

        for i in range(1, 4):
            col1, col2 = st.columns(2)

            with col1:

                sigma3 = col1.number_input(f"Probeta {i} - σ₃ (kPa)", key=f"sigma3_{i}", value=100 + i*50.0)
            with col2:
                sigma1 = col2.number_input(f"Probeta {i} - σ₁ (kPa)", key=f"sigma1_{i}", value=300 + i*100.0)
            data["σ₃ (kPa)"].append(sigma3)
            data["σ₁ (kPa)"].append(sigma1)

        submit = st.form_submit_button("CALCULAR", type="primary")

    if submit:
        df = pd.DataFrame(data)
        
        # Transformar a círculo de Mohr: c/φ mediante regresión lineal del plano de falla
        s3 = np.array(df["σ₃ (kPa)"])
        s1 = np.array(df["σ₁ (kPa)"])
        sigma_mean = (s1 + s3) / 2
        tau_max = (s1 - s3) / 2

        # Regresión lineal en el espacio st: tau = c + sigma * tan(φ)
        coeffs = np.polyfit(sigma_mean, tau_max, 1)
        m = coeffs[0] #m=sin(fi)
        b = coeffs[1] #b=c*cos(fi)
        phi_rad = np.arcsin(m)
        phi_deg = np.degrees(phi_rad)
        c = b / np.cos(phi_rad)


        ##### ----- Resultados
        st.divider()
        st.subheader("📊 Resultados:")
        col_res1, col_res2 = st.columns(2)

        #Los resultados se mostraran en 2 columnas, en la columna 1 la tabla de datos y en la columna 2  la grafica
        with col_res1:
            # Mostrar tabla
            st.write("📋 Tabla de datos:")
            st.dataframe(df, hide_index=True)

             # Resultados
            st.write(" Parametros de la envolvente Mohr - Coulomb:")
            st.success(f"Cohesión c = {c:.2f} kPa")
            st.success(f"Ángulo de fricción interna φ = {phi_deg:.2f}°")

        with col_res2:
            # Mostrar gráfica
            import matplotlib.pyplot as plt
        
            #Para la envolvente de falla
            x0 = 0
            y0 = c
            pendiente = np.tan(phi_rad)
            x_recta = np.linspace(x0, max(sigma_mean) * 1.4, 100)
    
            # Calcular y graficar los círculos de Mohr para cada par (σ₁, σ₃)
            circles = []
            for i in range(3):
                center = (data["σ₁ (kPa)"][i] + data["σ₃ (kPa)"][i]) / 2
                radius = (data["σ₁ (kPa)"][i] - data["σ₃ (kPa)"][i]) / 2
                theta = np.linspace(0, 2 * np.pi, 200)
                x = center + radius * np.cos(theta)
                y = radius * np.sin(theta)
                circles.append((x, y))        

            # Graficar los círculos en el mismo gráfico
            fig, ax = plt.subplots()
            for x, y   in circles:
                ax.plot(x, y, label = "Circulo de Mohr ")
            # ax.plot(sigma_mean, tau_max, 'o', label="Puntos experimentales")
            ax.plot(x_recta, pendiente * (x_recta - x0) + y0, 'r--', label="Envolvente de falla")
            ax.set_title("Círculos de Mohr y Envolvente de Mohr-Coulomb")
            ax.legend()

            # Asignar valores mínimo y máximo de los ejes
            ax.set_xlim(0, max(s1) * 1.1)
            ax.set_ylim(0, max(s1) / 1.4)

            # Definir nombres de ejes
            ax.set_xlabel("Esfuerzo normal")
            ax.set_ylabel("Esfuerzo cortante")
    


            st.pyplot(fig)


