import streamlit as st
import numpy as np

def run():
    st.markdown("<center><h2>🧱 Cálculo de Asentamientos Elásticos - Cimentación Superficial</h2></center>", unsafe_allow_html=True)
    st.markdown("<center><h3>(Version de Prueba)</h3></center>", unsafe_allow_html=True)

    st.markdown("<center><h5>Made by Geotecnia TerraNova</h5></center>", unsafe_allow_html=True)
    st.warning("⚠️ **Descargo de Responsabilidad:** Esta aplicación es una herramienta educativa y no reemplaza la evaluación de un ingeniero geotecnico calificado. Siempre consulta a un profesional para el diseño final.")

    col1, col2 = st.columns(2)

    #Funcion de Boussinesq rect al centro, esta z es desde la Df
    def bou_rect_c (q, L, B, z):
        m1 = L/B
        b = B/2
        n1 = z/b

        I4 = 2 / np.pi * ((m1*n1)/np.sqrt(1+m1**2+n1**2)*(1+m1**2+2*n1**2)/((1+n1**2)*(m1**2+n1**2))+np.asin(m1/(np.sqrt(m1**2+n1**2)*np.sqrt(1+n1**2))))

        Dsz = q * I4

        if Dsz < 0 : #Supone que el incremento de esfuerzos es representativo hasta la profundidad que llega el 10% de q y tambien evita errores si Dsz es negativo
            return 0
        else:
            return Dsz

    #Incremento de esfuerzos a diferentes profundidades
    def calculo_matrices(q, L, B, E):
        Matriz_z = [] #Profunididad
        Matriz_E = [] #modulo de young a la prof de calculo
        Matriz_Dsz = [] #Incremento de esfuerzos a la profundidad de calculo
        Matriz_Elastic_Settle = [] #Matriz de asentamientos en el suelo
        
        Delta_z = 0.1 #Valor para subdividir el medio
        prof_max = 8*B

        #Va a calcular los valores de cada valor de las matrices hasta llegar a la profundidad maxima
        z_actual = Delta_z
        s_acumulado = 0.0
        while z_actual < prof_max:
            Matriz_z.append(z_actual)
            
            E_actual = E #En el futuro este valor se puede hacer variar por estrato
            Matriz_E.append(E_actual)

            Dsz_actual = bou_rect_c(q, L, B, z_actual)
            Matriz_Dsz.append(Dsz_actual)

            Elastic_Settle_actual = (1 / E_actual) * Dsz_actual * Delta_z 

            s_acumulado= s_acumulado + Elastic_Settle_actual

            z_actual += np.round(Delta_z,2)


        return Matriz_z, Matriz_Dsz, Matriz_Elastic_Settle, s_acumulado

    


    with col1:
        st.header("Datos de entrada")

        B = st.number_input("Ancho de la cimentación (B) [m]", min_value=0.01, value=2.0, step=0.01)
        L = st.number_input("Longitud de la cimentación (L) [m]", min_value=0.01, value=4.0, step=0.01)
        q = st.number_input("Presión de contacto (q) [kPa]", min_value=0.0, value=100.0, step=0.1)
        Es = st.number_input("Módulo de elasticidad del suelo (Es) [kPa]", min_value=1.0, value=15000.0, step=100.0)

        # z = st.slider("Profundidad z", min_value=0.1, max_value= 6*B, step=0.1)


            
    with col2:
        # st.header("Cálculo del asentamiento elástico")
        st.info("Ajusta los parámetros y haz clic en 'CALCULAR'.")

        if st.button("CALCULAR", type="primary"):
            
            # Ds_cal = bou_rect_c(q, L, B, z)

            # st.write(f"Incremento de esfuerzos Δσz: {Ds_cal:.2f} kPa")


            #Con matrices
            Matriz_zcal, Matriz_Dsz, Matriz_Elastic_Settle, Asent_acum = calculo_matrices(q, L, B, Es)

            Asent_acum_cm = Asent_acum * 100

            import matplotlib.pyplot as plt

            fig, ax = plt.subplots()
            ax.plot(Matriz_Dsz, Matriz_zcal)
            ax.set_xlabel("Incremento de esfuerzos Δσz [kPa]")
            ax.set_ylabel("Profundidad [m]")
            ax.set_title("Distribución de Incremento de Esf. Verticales vs profundidad")
            ax.invert_yaxis()
            st.pyplot(fig)

            st.success(f"Asentamiento Total = {Asent_acum_cm:.2f} [cm]")



            
            
    