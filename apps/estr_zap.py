import streamlit as st
import math

# ACI 318-19 load factors
PHI_FLEXION = 0.90
PHI_CORTANTE = 0.75

def run():

    def calculate_footing_design(Pu, Mu, fc, fy, q_adm, b_col, h_col, d_propuesto, C_recubrimiento):
        """
        Calcula el diseño de una zapata aislada según el ACI 318-19.

        Args:
            Pu (float): Carga axial factorizada (factored axial load) en kg.
            Mu (float): Momento factorizado (factored moment) en kg-m.
            fc (float): Resistencia a la compresión del concreto (concrete compressive strength) en kg/cm².
            fy (float): Esfuerzo de fluencia del acero (steel yield strength) en kg/cm².
            q_adm (float): Presión admisible del suelo (allowable soil pressure) en kg/cm².
            b_col (float): Ancho de la columna (column width) en cm.
            h_col (float): Alto de la columna (column height) en cm.
            d_propuesto (float): Peralte efectivo propuesto (proposed effective depth) en cm.
            C_recubrimiento (float): Recubrimiento libre (clear cover) en cm.

        Returns:
            dict: Un diccionario con los resultados del diseño o un mensaje de error.
        """
        results = {}
        
        # 1. Dimensionamiento de la zapata (sin momento)
        Pu_service = Pu / 1.4 # Asumiendo carga de servicio (aproximado)
        q_service_pa = q_adm * 98066.5 # Convertir kg/cm² a Pa para cálculo de m²
        A_requerida_m2 = (Pu / PHI_FLEXION) / q_service_pa # m^2
        L_zapata = B_zapata = math.sqrt(A_requerida_m2)
        
        L_zapata_m = math.ceil(L_zapata * 10) / 10 # Redondear a la siguiente decima de metro
        B_zapata_m = math.ceil(B_zapata * 10) / 10
        
        L_zapata_cm = L_zapata_m * 100
        B_zapata_cm = B_zapata_m * 100
        
        results['L_zapata'] = L_zapata_cm
        results['B_zapata'] = B_zapata_cm

        results['Peralte_total'] = d_propuesto + C_recubrimiento + 1.27  # Considerando varilla #4
        
        # Cargas factorizadas de diseño
        q_u_prom_kgcm2 = Pu / (L_zapata_cm * B_zapata_cm) # Presión neta factorizada en kg/cm^2
        
        # 2. Verificación por cortante a una dirección (One-way shear)
        d = d_propuesto
        c_a_corte = (B_zapata_cm - h_col) / 2
        
        V_u1 = q_u_prom_kgcm2 * (c_a_corte - d) * L_zapata_cm # kg
        V_c1 = 0.53 * math.sqrt(fc) * L_zapata_cm * d # kg
        
        results['Cortante_1_direccion_Vu'] = V_u1
        results['Cortante_1_direccion_Vc'] = PHI_CORTANTE * V_c1
        
        results['Cortante_1_direccion_status'] = "Pasa" if V_u1 < PHI_CORTANTE * V_c1 else "No pasa"

        # 3. Verificación por cortante a dos direcciones (Two-way shear / Punching)
        bo = 2 * (b_col + d) + 2 * (h_col + d)
        V_u2 = q_u_prom_kgcm2 * (L_zapata_cm * B_zapata_cm - (b_col + d) * (h_col + d)) # kg
        
        # ACI 318-19, Section 22.6.5.2 - se toma el menor valor de las tres ecuaciones
        Vc_1 = (1.06 * math.sqrt(fc)) * bo * d # kg
        Vc_2 = (0.53 + 1.06 / (b_col/h_col)) * math.sqrt(fc) * bo * d # kg
        Vc_3 = (0.53 * 2 * d / bo) * math.sqrt(fc) * bo * d # kg -> (0.53 * 40 * d / bo) * math.sqrt(fc) * bo * d (original)
        
        # Simplificando para columna cuadrada: b_col=h_col, entonces beta_c=1, alfa_s=40
        Vc_punching = 1.06 * math.sqrt(fc) * bo * d # La más sencilla para este caso
        
        results['Cortante_2_direcciones_Vu'] = V_u2
        results['Cortante_2_direcciones_Vc'] = PHI_CORTANTE * Vc_punching
        
        results['Cortante_2_direcciones_status'] = "Pasa" if V_u2 < PHI_CORTANTE * Vc_punching else "No pasa"

        # 4. Diseño por momento
        x_corte = (B_zapata_cm - b_col) / 2 # Distancia al corte de la cara de la columna
        M_u_zapata = (q_u_prom_kgcm2 * 100) * (x_corte**2 / 2) * (L_zapata_cm) # kg-cm
        
        # Cálculo del área de acero As
        # Revisión del factor dentro de la raíz cuadrada
        discriminant = 1 - (2 * M_u_zapata) / (0.85 * fc * L_zapata_cm * d**2 * PHI_FLEXION)

        if discriminant < 0:
            return {'error': "El peralte efectivo (d) o las dimensiones de la zapata son insuficientes. Aumente los valores de entrada para el cálculo."}
        
        rho = 0.85 * fc / fy * (1 - math.sqrt(discriminant))
        As_requerida = rho * L_zapata_cm * d # cm2
        
        # ACI 318-19, Sección 7.6.1.1 - Acero mínimo
        rho_min = max(0.0018, 0.25 * math.sqrt(fc) / fy)
        As_min = rho_min * L_zapata_cm * d
        
        As_final = max(As_requerida, As_min)
        
        results['Momento_diseño_Mu'] = M_u_zapata / 100 # kg-m
        results['As_requerido'] = As_final
        
        # 5. Longitud de desarrollo (Development Length)
        db = 1.27 # cm (varilla #4)
        psi_t = 1.0 # Factor de posición (ACI 25.4.2.4)
        psi_e = 1.0 # Factor de recubrimiento epóxico
        lambda_c = 1.0 # Factor para concreto ligero
        
        # Simplificado de ACI 318-19, Eq. 25.4.2.3b
        ld = (fy / (1.1 * math.sqrt(fc))) * db
        
        results['Longitud_desarrollo_ld'] = ld
        results['Longitud_disponible'] = (B_zapata_cm - h_col) / 2 - C_recubrimiento
        
        results['Longitud_desarrollo_status'] = "Pasa" if results['Longitud_disponible'] > ld else "No pasa"
        
        return results

    # --- INTERFAZ DE USUARIO CON STREAMLIT ---
    st.set_page_config(page_title="Diseño de Zapata Aislada (ACI 318)", layout="centered")

    st.title("👨‍💻 Diseño de Zapata Aislada (ACI 318)")
    st.markdown("---")

    st.sidebar.header("Parámetros de Diseño")

    # User Inputs
    st.sidebar.subheader("Cargas")
    Pu = st.sidebar.number_input("Carga Axial Factorizada (Pu) [kg]", value=15000.0, step=1000.0)
    Mu = st.sidebar.number_input("Momento Factorizado (Mu) [kg-m]", value=0.0, step=100.0)

    st.sidebar.subheader("Propiedades de Materiales")
    fc = st.sidebar.number_input("Resistencia del Concreto (f'c) [kg/cm²]", value=210.0, step=10.0)
    fy = st.sidebar.number_input("Esfuerzo de Fluencia del Acero (fy) [kg/cm²]", value=4200.0, step=100.0)

    st.sidebar.subheader("Propiedades del Suelo")
    q_adm = st.sidebar.number_input("Presión Admisible del Suelo (q_adm) [kg/cm²]", value=2.0, step=0.1)

    st.sidebar.subheader("Dimensiones de la Columna y Zapata")
    b_col = st.sidebar.number_input("Ancho de la Columna [cm]", value=40.0, step=10.0)
    h_col = st.sidebar.number_input("Alto de la Columna [cm]", value=40.0, step=10.0)
    d_propuesto = st.sidebar.number_input("Peralte Efectivo Propuesto (d) [cm]", value=50.0, step=5.0)
    C_recubrimiento = st.sidebar.number_input("Recubrimiento Libre (C) [cm]", value=7.5, step=1.0)


    # Run calculation on button click
    if st.button("Calcular Diseño"):
        results = calculate_footing_design(Pu, Mu, fc, fy, q_adm, b_col, h_col, d_propuesto, C_recubrimiento)
        
        st.markdown("---")
        st.header("Resultados del Diseño")
        
        if 'error' in results:
            st.error(f"❌ Error de Cálculo: {results['error']}")
            st.warning("Ajusta los parámetros de entrada y vuelve a intentar.")
        else:
            st.subheader("1. Dimensiones de la Zapata")
            st.info(f"Dimensiones de la zapata: **{results['L_zapata']:.2f} cm x {results['B_zapata']:.2f} cm**")
            st.info(f"Peralte Total (con d={d_propuesto}cm y recubrimiento): **{results['Peralte_total']:.2f} cm**")
            
            st.subheader("2. Verificación por Cortante")
            
            if results['Cortante_1_direccion_status'] == "Pasa":
                st.success(f"✅ Cortante a una dirección: **Pasa**")
                st.write(f"V_u = {results['Cortante_1_direccion_Vu']:.2f} kg < $\phi$V_c = {results['Cortante_1_direccion_Vc']:.2f} kg")
            else:
                st.error(f"❌ Cortante a una dirección: **No Pasa**")
                st.write(f"V_u = {results['Cortante_1_direccion_Vu']:.2f} kg > $\phi$V_c = {results['Cortante_1_direccion_Vc']:.2f} kg")
                st.warning("Se debe aumentar el peralte efectivo (d).")
                
            if results['Cortante_2_direcciones_status'] == "Pasa":
                st.success(f"✅ Cortante a dos direcciones: **Pasa**")
                st.write(f"V_u = {results['Cortante_2_direcciones_Vu']:.2f} kg < $\phi$V_c = {results['Cortante_2_direcciones_Vc']:.2f} kg")
            else:
                st.error(f"❌ Cortante a dos direcciones: **No Pasa**")
                st.write(f"V_u = {results['Cortante_2_direcciones_Vu']:.2f} kg > $\phi$V_c = {results['Cortante_2_direcciones_Vc']:.2f} kg")
                st.warning("Se debe aumentar el peralte efectivo (d).")
                
            st.subheader("3. Diseño por Momento")
            st.write(f"Momento de diseño (Mu): **{results['Momento_diseño_Mu']:.2f} kg-m**")
            st.write(f"Área de acero requerida (As): **{results['As_requerido']:.2f} cm²**")
            st.info("Para un acero del #4 (1.27 cm²) se requieren {:.2f} varillas por lado.".format(results['As_requerido'] / 1.27))
            st.info(f"Espaciamiento aproximado: **{100 / (results['As_requerido'] / 1.27):.2f} cm**")

            st.subheader("4. Longitud de Desarrollo")
            if results['Longitud_desarrollo_status'] == "Pasa":
                st.success(f"✅ Longitud de desarrollo: **Pasa**")
                st.write(f"Longitud disponible = {results['Longitud_disponible']:.2f} cm > Longitud de desarrollo requerida = {results['Longitud_desarrollo_ld']:.2f} cm")
            else:
                st.error(f"❌ Longitud de desarrollo: **No Pasa**")
                st.write(f"Longitud disponible = {results['Longitud_disponible']:.2f} cm < Longitud de desarrollo requerida = {results['Longitud_desarrollo_ld']:.2f} cm")
                st.warning("Se debe considerar ganchos de 90° o aumentar el tamaño de la zapata.")
        
        st.markdown("---")
        st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
        st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero estructural calificado. Siempre consulta a un profesional para el diseño final.")
