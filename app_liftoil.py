import streamlit as st
import pandas as pd
import plotly.express as px
import streamlit.components.v1 as components
import os  # <-- AGREGA ESTA LÍNEA AQUÍ ARRIBA
import lasio
import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Estilo HTML y CSS para títulos y subtítulos con degradado en las letras (azul eléctrico y gris)
st.markdown("""
<style>
.title {
    font-size: 36px;
    font-weight: bold;
    background: linear-gradient(100deg, #02AC66, #C0C0C0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: black; /* Cambio realizado */
}

.subheader {
    font-size: 24px;
    font-weight: bold;
    background: linear-gradient(180deg, #00008B, #C0C0C0);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    color: black; /* Cambio realizado */
}

</style>
""", unsafe_allow_html=True)


# Título principal bloqueado contra traductores automáticos (se corrige el typo de SOLTUNIONS a SOLUTIONS si lo deseas)
st.markdown('<h1 class="title notranslate" translate="no">LIFTOIL SOLUTIONS SAC</h1>', unsafe_allow_html=True)

secciones = [
    "🏠 Inicio",
    "Compresor Oil & Gas"
]

seccion = st.sidebar.selectbox("Selecciona una sección", secciones)

if seccion == "🏠 Inicio":
    st.title("Aplicación de Pruebas con Compresor Reciprocante Externo (CRE)")
    st.image("CRE.png")
    st.write("Aquí mostraremos los pozos que cuentan con telemtría")

# Código del Reloj Estilizado para la Barra Lateral
with st.sidebar:
    st.write("---")  # Línea divisoria
    
    # HTML y CSS adaptado para coincidir con la imagen
    reloj_html = """
    <div style="
        font-family: 'Source Sans Pro', sans-serif;
        text-align: center;
        background: linear-gradient(135deg, #02382c, #065442); /* Degradé verde oscuro */
        padding: 12px 20px;
        border-radius: 20px; /* Bordes muy redondeados tipo píldora */
        box-shadow: inset 0 1px 3px rgba(255,255,255,0.1);
        margin: 10px auto;
        width: 85%;
    ">
        <!-- Título superior en dorado suave -->
        <div style="color: #cbd5e1; font-size: 14px; margin-bottom: 4px; font-weight: 500;">
            Hora del navegador:
        </div>
        <!-- Contenedor del reloj dinámico -->
        <div id="reloj" style="color: #facc15; font-size: 18px; font-weight: bold; letter-spacing: 0.5px;">
            --:--:--
        </div>
    </div>

    <script>
    function actualizarReloj() {
        const ahora = new Date();
        // Formato de hora local de 12 horas con a. m. / p. m.
        document.getElementById("reloj").innerText = ahora.toLocaleTimeString('es-ES', { 
            hour: '2-digit', 
            minute: '2-digit', 
            second: '2-digit', 
            hour12: true 
        });
    }
    setInterval(actualizarReloj, 1000);
    actualizarReloj(); // Carga inmediata
    </script>
    """
    
    # Renderizar el componente web dentro del sidebar
    components.html(reloj_html, height=100)

# Configura aquí el nombre exacto de tu archivo local
RUTA_ARCHIVO = r"VII..xlsx"

st.write("### Pozos en Evaluación")

# Verificar si el archivo realmente existe en la carpeta del script
if os.path.exists(RUTA_ARCHIVO):
    es_excel = RUTA_ARCHIVO.endswith('.xlsx')
    pozo_seleccionado = None
    
    # Lógica para leer múltiples hojas si es un archivo Excel local
    if es_excel:
        excel_file = pd.ExcelFile(RUTA_ARCHIVO)
        hojas = excel_file.sheet_names
        pozo_seleccionado = st.selectbox("Selecciona el pozo (hoja) que deseas visualizar:", hojas)
        datos = pd.read_excel(RUTA_ARCHIVO, sheet_name=pozo_seleccionado)
    else:
        datos = pd.read_csv(RUTA_ARCHIVO)
    
    st.write("### Vista previa de los datos")
    st.write(datos)
    
    st.write("### Gráficando Variables")
    
    # 2. Definir variables por defecto y opcionales
    variables_defecto = ["Presion salida [PSI]", "Presion succion [PSI]"]
    variables_opcionales = [
        "Frecuencia del motor  [Hz]",        
    ]
    
    todas_las_columnas = variables_defecto + variables_opcionales
    
    # Asegurar que solo se muestren opciones que realmente existan en el archivo cargado
    opciones_disponibles = [col for col in todas_las_columnas if col in datos.columns]
    defectos_disponibles = [col for col in variables_defecto if col in datos.columns]
    
    # 3. Selector múltiple dinámico
    columnas_seleccionadas = st.multiselect(
        "Selecciona las variables que deseas visualizar en la gráfica:",
        options=opciones_disponibles,
        default=defectos_disponibles
    )
    
    # 4. Validar y graficar con formato Melt (Largo)
    if columnas_seleccionadas:
        try:
            # Transformación segura: une las columnas seleccionadas bajo una columna "Variable"
            # NOTA: Asegúrate de que la columna "Fecha" exista con esa mayúscula exacta en tu Excel
            datos_melt = datos.melt(
                id_vars=["Fecha"], 
                value_vars=columnas_seleccionadas,
                var_name="Variable", 
                value_name="Medicion"
            )
            
            mapa_colores = {
                "Presion salida [PSI]": "green",
                "Presion succion [PSI]": "red",
                "Frecuencia del motor  [Hz]": "blue"                
            }
            
            # Título dinámico según el pozo seleccionado
            titulo_grafica = f"Historial de Parámetros de Operación - {pozo_seleccionado}" if es_excel else "Historial de Parámetros de Operación"
            
            # Graficamos usando las nuevas columnas generadas por .melt()
            figura = px.line(
                datos_melt, 
                x="Fecha", 
                y="Medicion",
                color="Variable",  
                title=titulo_grafica,
                markers=True,
                color_discrete_map=mapa_colores
            )
            
            figura.update_layout(
                xaxis_title="Fecha de Registro",
                yaxis_title="Valor / Medición",
                legend_title="Variables"
            )
            
            st.plotly_chart(figura, use_container_width=True)
            
        except Exception as e:
            st.error(f"Error al procesar la gráfica: {e}")
            st.info("💡 Si el error menciona 'KeyError: Fecha', es porque la columna de fecha en tu Excel se llama distinto (ej. 'FECHA' o 'fecha'). Modifícala en la línea id_vars=['Fecha'].")
    else:
        st.warning("Por favor, selecciona al menos una variable para mostrar la gráfica.")

else:
    # Este bloque ahora queda limpio y aislado solo para cuando NO se encuentra el archivo físico
    st.error(f"❌ No se encontró el archivo '{RUTA_ARCHIVO}' en el directorio de la aplicación. Por favor, verifica el nombre y la ubicación.")

