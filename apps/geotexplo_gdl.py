
import streamlit as st


def run():

    # Configuración general
    st.set_page_config(page_title="Presupuesto Geotécnico", page_icon="📊")

    st.markdown("<center><h2>📊 Cálculadora de Exploración Geotécnica Guadalajara MEX", unsafe_allow_html=True)

    st.markdown("<center><h3>(Version de Prueba)</h3></center>", unsafe_allow_html=True)

    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")

    st.markdown("Para proyectos de hasta 2000 m2 y 10 niveles")


    # Ingreso de datos del proyecto
    st.subheader("📝 Datos del Proyecto")
    nombre_proyecto = st.text_input("Nombre del proyecto")
    ubicacion = st.selectbox("Ubicación", ["Guadalajara", "Zapopan"])
    area = st.number_input("Área de construcción (m²)", min_value=1, max_value=1000)
    niveles = st.number_input("Número de niveles", min_value=1, max_value= 10)

    st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")
    submit = st.button("CALCULAR", type="primary")



    # Cálculos simples
    if submit and area and niveles:
        
                #Determinar la profundidad de sondeos
        # NumeroDeNiveles = float(input('¿Cual es el NÚMERO DE NIVELES del proyecto? '))

        if niveles == 1:
            profundidad = 4
        elif niveles == 2:
            profundidad = 5
        elif niveles == 3:
            profundidad = 7
        elif niveles == 4 or 5:
            profundidad = 9
        elif niveles == 6 or 7:
            profundidad = 12
        elif niveles == 8 or 9:
            profundidad = 14
        elif niveles == 10:
            profundidad = 14
        else:
            profundidad = 'error'   

        
        #Numero de sondeos
        if 0 < area <= 100:
            num_sondeos = 1
        elif 100 < area <= 250:
            num_sondeos = 2
        elif 250 < area <=1000:
            num_sondeos = 3
        elif 1000 < area <=2000:
            num_sondeos = 4
        else:
            num_sondeos = 'error'


        

            
        # Ds_cal = bou_rect_c(q, L, B, z)

        #Tipo de sondeo
        tipo_sondeo = "SPT"
        
        st.header("🔍 Recomendación Técnica")
        st.write(f"Tipo de sondeo sugerido: {tipo_sondeo}")
        st.write(f"Número de sondeos: {num_sondeos}")
        st.write(f"Profundidad estimada por sondeo: {profundidad} m")

        # Precios base
        #precio_por_m = 1000
        #pu_laboratorio = 500
        #laboratorio = num_sondeos * profundidad * pu_laboratorio
        #movilizacion = 4000
        #informe = 5000
        #total_sondeo = num_sondeos * profundidad * precio_por_m
        #total = total_sondeo + laboratorio + movilizacion + informe

        st.header("💰 Cotizacion Estimada")
        st.write("📩Contáctenos a proyectos@geotecniaterranova.com")
        st.write("✅o por Whatsapp https://wa.link/vai3cy") 

          

        #st.write(f"Total sondeos: ${total_sondeo:,.0f} MXN, considerando {precio_por_m} MXN por m de profundidad")
        #st.write(f"Laboratorio: ${laboratorio:,.0f} MXN, considerando {pu_laboratorio} MXN por m de profundidad")
        #st.write(f"Movilizacion: ${movilizacion:,.0f} MXN")
        #st.write(f"Informe: ${informe:,.0f} MXN")
        #st.subheader(f"💰 Total: ${total:,.0f} MXN")

        