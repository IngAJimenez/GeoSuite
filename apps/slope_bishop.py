import streamlit as st
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# --- FÓRMULA Y LÓGICA DEL MÉTODO DE BISHOP SIMPLIFICADO ---
#
# El Factor de Seguridad (FS) se calcula con la siguiente fórmula iterativa:
#
#           Σ [ (c' * b + (W - u * b) * tan(φ')) / m_α ]
# FS = ----------------------------------------------------
#                      Σ(W * sinα)
#
# donde:
# m_α = cos(α) + (sin(α) * tan(φ') / FS)
#
# Debido a que FS aparece en ambos lados, se requiere un proceso iterativo.
#
# Variables:
# c'   : Cohesión efectiva del suelo
# φ'   : Ángulo de fricción interna efectivo
# γ    : Peso unitario del suelo
# W    : Peso de cada dovela
# α    : Ángulo en la base de cada dovela
# b    : Ancho de la base de cada dovela
# u    : Presión de poros en la base de la dovela (simplificado con ru)
# ru   : Coeficiente de presión de poros (u / (γ * h))

def run():


    def calculate_bishop_fs(
        cohesion, friction_angle, unit_weight, slope_height, slope_angle,
        circle_center_x, circle_center_y, circle_radius, num_slices, ru
    ):
        """
        Calcula el Factor de Seguridad (FS) para la estabilidad de un talud
        utilizando el método de Bishop Simplificado.

        Retorna:
            - El Factor de Seguridad final.
            - Un DataFrame de pandas con los detalles de cada dovela.
            - Los datos geométricos para la gráfica.
        """
        # Convertir ángulos a radianes para los cálculos
        phi_rad = np.deg2rad(friction_angle)
        beta_rad = np.deg2rad(slope_angle)

        # --- 1. Definir la geometría del talud y del círculo de falla ---
        slope_toe_x = slope_height / np.tan(beta_rad)

        # Puntos de intersección del círculo con la superficie del terreno
        y_crest = slope_height
        try:
            x_intersect_crest = circle_center_x - np.sqrt(circle_radius**2 - (y_crest - circle_center_y)**2)
        except ValueError:
            st.error("Error: El círculo de falla no intersecta la cresta del talud. Ajusta los parámetros del círculo.")
            return None, None, None

        m_slope = -np.tan(beta_rad)
        c_slope = slope_height
        A = 1 + m_slope**2
        B = 2 * (m_slope * c_slope - m_slope * circle_center_y - circle_center_x)
        C = circle_center_x**2 + c_slope**2 - 2 * c_slope * circle_center_y + circle_center_y**2 - circle_radius**2
        discriminant = B**2 - 4 * A * C
        if discriminant < 0:
            st.error("Error: El círculo de falla no intersecta la cara del talud. Ajusta los parámetros del círculo.")
            return None, None, None
        x_intersect_slope1 = (-B + np.sqrt(discriminant)) / (2 * A)
        x_intersect_slope2 = (-B - np.sqrt(discriminant)) / (2 * A)
        y_intersect_slope1 = m_slope * x_intersect_slope1 + c_slope
        x_intersect_toe = x_intersect_slope1 if 0 < y_intersect_slope1 < slope_height else x_intersect_slope2

        # --- 2. Dividir la masa deslizante en dovelas (rebanadas) ---
        slice_width = (x_intersect_toe - x_intersect_crest) / num_slices
        slice_data = []

        # --- 3. Proceso iterativo para encontrar el FS ---
        fs_assumed = 1.5
        tolerance = 0.001
        max_iterations = 100

        for i in range(max_iterations):
            numerator_sum = 0
            denominator_sum = 0
            temp_slice_details = []

            for j in range(num_slices):
                x_left = x_intersect_crest + j * slice_width
                x_right = x_left + slice_width
                x_mid = (x_left + x_right) / 2

                if x_mid < slope_toe_x:
                    y_top = slope_height
                else:
                    y_top = m_slope * x_mid + c_slope

                if (circle_radius**2 - (x_mid - circle_center_x)**2) < 0: continue
                y_base = circle_center_y - np.sqrt(circle_radius**2 - (x_mid - circle_center_x)**2)

                slice_height = y_top - y_base
                if slice_height < 0: continue

                alpha = np.arctan2(circle_center_y - y_base, x_mid - circle_center_x) - np.pi/2
                W = (slice_height * slice_width) * unit_weight
                u = ru * unit_weight * slice_height
                b = slice_width / np.cos(alpha)

                m_alpha = np.cos(alpha) + (np.sin(alpha) * np.tan(phi_rad) / fs_assumed)
                
                # Componentes de fuerza
                driving_force = W * np.sin(alpha)
                cohesive_resisting_force = cohesion * b
                frictional_resisting_force = (W - u * b) * np.tan(phi_rad)
                
                numerator_slice = (cohesive_resisting_force + frictional_resisting_force) / m_alpha

                numerator_sum += numerator_slice
                denominator_sum += driving_force

                # Guardar datos detallados para la tabla en la última iteración
                if i == max_iterations - 1 or abs(fs_assumed - (numerator_sum / denominator_sum if denominator_sum != 0 else 1)) < tolerance:
                    temp_slice_details.append({
                        "Dovela": j + 1,
                        "Peso W (kN/m)": W,
                        "Ángulo α (°)": np.rad2deg(alpha),
                        "Fuerza Actuante (W*sinα)": driving_force,
                        "Resistencia Cohesiva (c*b)": cohesive_resisting_force,
                        "Resistencia Friccional ((W-ub)tanφ')": frictional_resisting_force,
                        "Numerador FS": numerator_slice,
                    })

            if denominator_sum == 0:
                fs_calculated = float('inf')
            else:
                fs_calculated = numerator_sum / denominator_sum

            if abs(fs_calculated - fs_assumed) < tolerance:
                slice_data = temp_slice_details
                break
            fs_assumed = fs_calculated
        else:
            st.warning(f"El cálculo no convergió después de {max_iterations} iteraciones.")

        geom_data = {
            "slope_height": slope_height, "slope_angle": slope_angle, "slope_toe_x": slope_toe_x,
            "circle_center_x": circle_center_x, "circle_center_y": circle_center_y, "circle_radius": circle_radius,
            "x_intersect_crest": x_intersect_crest, "x_intersect_toe": x_intersect_toe,
            "num_slices": num_slices, "slice_width": slice_width
        }
        return fs_calculated, pd.DataFrame(slice_data), geom_data

    def plot_slope(geom_data):
        """Genera una gráfica del talud, el círculo de falla y las dovelas."""
        if not geom_data: return None
        fig, ax = plt.subplots(figsize=(10, 7))
        H, beta, toe_x = geom_data["slope_height"], geom_data["slope_angle"], geom_data["slope_toe_x"]
        center_x, center_y, radius = geom_data["circle_center_x"], geom_data["circle_center_y"], geom_data["circle_radius"]
        x_crest_start, x_toe_end = geom_data["x_intersect_crest"], geom_data["x_intersect_toe"]
        crest_x_limit, toe_x_limit = -H / 2, toe_x + H / 2
        ax.plot([crest_x_limit, 0], [H, H], 'g-', label="Superficie del Terreno")
        ax.plot([0, toe_x], [H, 0], 'g-')
        ax.plot([toe_x, toe_x_limit], [0, 0], 'g-')
        failure_circle = plt.Circle((center_x, center_y), radius, fill=False, color='r', linestyle='--', label="Círculo de Falla")
        ax.add_patch(failure_circle)
        ax.plot(center_x, center_y, 'r+', markersize=10, label="Centro del Círculo")
        for j in range(geom_data["num_slices"]):
            x_left = x_crest_start + j * geom_data["slice_width"]
            ax.axvline(x=x_left, color='gray', linestyle=':', linewidth=0.8)
        ax.axvline(x=x_toe_end, color='gray', linestyle=':', linewidth=0.8, label="Dovelas")
        ax.set_aspect('equal', adjustable='box')
        ax.set_xlabel("Distancia Horizontal (m)"); ax.set_ylabel("Distancia Vertical (m)")
        ax.set_title("Análisis de Estabilidad de Talud - Método de Bishop")
        ax.legend(); ax.grid(True, linestyle='--', alpha=0.6)
        ax.set_xlim(min(crest_x_limit, center_x - radius) - 1, max(toe_x_limit, center_x ) + 1)
        ax.set_ylim(min(0, center_y - radius) - 1, max(H, center_y ) + 1)
        return fig

    # --- INTERFAZ DE USUARIO CON STREAMLIT ---
    st.markdown("<center><h2>⛰️ Calculadora de Estabilidad de Taludes</h2></center>", unsafe_allow_html=True)
    st.markdown("<center><h3>(Version de Prueba)</h3></center>", unsafe_allow_html=True)
    
    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")

    st.header("Método de Bishop Simplificado")
    st.markdown("Esta aplicación calcula el **Factor de Seguridad (FS)** para un talud de suelo homogéneo. Introduce los parámetros.")

    #Hacer 2 columnas una para los parametros y otra para los calculos
    tab_param1, tab_param2 = st.columns(2)

    with tab_param1:
        st.header("Parámetros de Entrada")
        tab1, tab2, tab3 = st.tabs([ "Geometría", "Suelo", "Círculo de Falla"])

        with tab1:
            H = st.number_input("Altura del Talud, H (m)", 1.0, value=10.0, step=0.5, format="%.2f")
            beta = st.slider("Ángulo del Talud, β (°)", 10.0, 90.0, value=45.0, step=1.0)

        with tab2:
            c = st.number_input("Cohesión, c' (kPa)", 0.0, value=10.0, step=0.5, format="%.2f")
            phi = st.number_input("Ángulo de Fricción, φ' (°)", 0.0, 45.0, value=30.0, step=0.5, format="%.2f")
            gamma = st.number_input("Peso Unitario, γ (kN/m³)", 10.0, 25.0, value=16.0, step=0.1, format="%.2f")
            ru = st.slider("Coeficiente de Presión de Poros, ru", 0.0, 0.6, value=0.0, step=0.05, help="ru = u / (γ * h). ru=0 significa talud seco.")

        with tab3:
            st.info("Define un círculo de falla de prueba.")
            R = st.number_input("Radio del Círculo, R (m)", min_value=H, value=15.0, step=0.5, format="%.2f")
            Xc = st.number_input("Coordenada X del Centro (m)", value=5.0, step=0.5, format="%.2f")
            Yc = st.number_input("Coordenada Y del Centro (m)", value=18.0, step=0.5, format="%.2f")
            n_slices = st.slider("Número de Dovelas", 10, 100, value=30, step=5)

    with tab_param2:
        if st.button("CALCULAR", type="primary"):
            if R <= abs(H - Yc):
                st.error("El radio es demasiado pequeño. El círculo no puede intersectar la cresta. Aumenta R o ajusta Yc.")
            else:
                fs, slice_df, geom_data = calculate_bishop_fs(c, phi, gamma, H, beta, Xc, Yc, R, n_slices, ru)
                if fs is not None:
                    st.subheader("Resultados del Análisis")
                    col1, col2 = st.columns([1, 2])
                    with col1:
                        st.metric(label="Factor de Seguridad (FS)", value=f"{fs:.3f}")
                        if fs < 1.0: st.error("¡Peligro! Talud inestable (FS < 1.0)")
                        elif fs < 1.5: st.warning("Precaución. FS bajo (1.0 ≤ FS < 1.5)")
                        else: st.success("Talud estable (FS ≥ 1.5)")
                    with col2:
                        st.write("**Visualización del Talud y Círculo de Falla**")
                        fig = plot_slope(geom_data)
                        if fig: st.pyplot(fig)

                    # st.markdown("---")
                    # st.subheader("Detalles del Cálculo por Dovela")
                    # st.info("La suma de la columna 'Numerador FS' dividida por la suma de 'Fuerza Actuante' da como resultado el Factor de Seguridad.")
                    
                    # # --- MODIFICACIÓN CLAVE: MOSTRAR EL DATAFRAME DETALLADO ---
                    # st.dataframe(slice_df.style.format({
                    #     "Peso W (kN/m)": "{:.2f}",
                    #     "Ángulo α (°)": "{:.2f}",
                    #     "Fuerza Actuante (W*sinα)": "{:.2f}",
                    #     "Resistencia Cohesiva (c*b)": "{:.2f}",
                    #     "Resistencia Friccional ((W-ub)tanφ')": "{:.2f}",
                    #     "Numerador FS": "{:.2f}"
                    # }))
                else:
                    st.error("No se pudo completar el cálculo. Revisa los parámetros del círculo de falla.")
        else:
            st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")
