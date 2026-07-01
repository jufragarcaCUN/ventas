import os
import warnings
import pandas as pd
import streamlit as st
import plotly.express as px

# Ocultar advertencias de formato
warnings.filterwarnings("ignore")

# ==================== 1. CONFIGURACIÓN DE LA INTERFAZ Y ESTILO INSTITUCIONAL CUN ====================
st.set_page_config(
    page_title="Análisis de Objeciones COE", page_icon="🎯", layout="wide"
)

# Inyección de CSS Avanzado para mejorar la UI/UX y aplicar la identidad CUN
st.markdown(
    """
    <style>
    /* Variables globales */
    :root {
        --primary-color: #1E5D2F;
        --bg-color: #F4F6F7;
    }
    
    /* Fondo de la app */
    .stApp {
        background-color: var(--bg-color);
    }
    
    /* Estilos de títulos institucionales */
    h1, h2, h3, h4 {
        color: #1E5D2F !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
    }
    
    /* Formateo de Tarjetas KPI */
    div[data-testid="stMetricValue"] {
        color: #1E5D2F !important;
        font-weight: bold;
        font-size: 2rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #4A5568 !important;
        font-size: 0.95rem !important;
    }

    /* Contenedor estilizado para Insights con efecto Hover */
    .insight-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #1E5D2F;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    .insight-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(30, 93, 47, 0.15);
    }

    /* Estilización del Glosario HTML */
    .glosario-tabla {
        width: 100%;
        border-collapse: collapse;
        background-color: white;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
    }
    .glosario-tabla th {
        background-color: #1E5D2F;
        color: white;
        text-align: left;
        padding: 12px 15px;
        font-size: 1rem;
    }
    .glosario-tabla td {
        padding: 12px 15px;
        border-bottom: 1px solid #E2E8F0;
        color: #2D3748;
        font-size: 0.92rem;
    }
    .glosario-tabla tr:hover {
        background-color: #EDF7ED;
        cursor: pointer;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 Análisis de Objeciones COE - CUN")
st.markdown("### *Informe de Auditoría y Control de Llamadas Operativas*")
st.markdown("---")

# Ruta relativa corregida para GitHub/Streamlit Cloud
RUTA_REAL_EXCEL = "carreras_homologadas_1.xlsx"

# ==================== 2. DATA DEL GLOSARIO REAL DE LLAMADAS ====================
glosario_data = [
    {"cat": "Económica", "significado": "El contacto manifiesta falta de dinero, objeta el costo del semestre o solicita opciones de financiación especiales durante la llamada."},
    {"cat": "Tiempo/Flexibilidad", "significado": "El contacto reporta cruces de horarios con turnos laborales rotativos, altas cargas en su puesto actual o falta de tiempo disponible durante la llamada."},
    {"cat": "Confianza/Legalidad", "significado": "El contacto expresa dudas explícitas sobre la validez del título ante el Ministerio de Educación o exige códigos SNIES en la llamada."},
    {"cat": "Metodología", "significado": "El contacto manifiesta apatía o resistencia abierta al modelo educativo propuesto, problemas técnicos o de conectividad."},
    {"cat": "Terceros", "significado": "El contacto indica en la llamada que no tiene autonomía para decidir y que debe consultar la decisión económica con familiares o jefes."},
    {"cat": "Competencia", "significado": "El contacto manifiesta que está evaluando o comparando activamente frente a ofertas y costos de otras instituciones del mercado."},
    {"cat": "Documentación/Requisitos", "significado": "El contacto reporta en la llamada retrasos en la entrega de requisitos obligatorios (ICFES, actas de grado, certificados de notas)."},
    {"cat": "Ubicación/Sedes", "significado": "El contacto argumenta barrera geográfica por distancia excesiva hacia las sedes físicas o problemas de transporte urbano."},
    {"cat": "Desinterés/Aplazamiento", "significado": "El contacto solicita voluntariamente aplazar el contacto para periodos futuros o manifiesta desinterés definitivo con la llamada."}
]

# ==================== 3. CARGA Y LIMPIEZA DE DATOS BASURA ====================
@st.cache_data
def cargar_y_limpiar_excel(ruta):
    if os.path.exists(ruta):
        data = pd.read_excel(ruta)

        if "fecha" in data.columns:
            data["fecha"] = pd.to_datetime(data["fecha"], errors="coerce")

        col_prog = "programa_homologado_lista"
        col_obj = "Objecion_Detectada"

        data = data.dropna(subset=[col_prog, col_obj])
        data[col_prog] = data[col_prog].astype(str).str.strip()
        data[col_obj] = data[col_obj].astype(str).str.strip()

        textos_basura = ["otro / por verificar", "otro", "no registrado", "por verificar", "", "nan", "none"]
        data = data[
            (~data[col_prog].str.lower().isin(textos_basura))
            & (~data[col_obj].str.lower().isin(textos_basura))
        ]
        return data
    return None

df = cargar_y_limpiar_excel(RUTA_REAL_EXCEL)

if df is not None and not df.empty:
    col_programa = "programa_homologado_lista"
    col_modalidad = "modalidad_limpia"
    col_ciudad = "ciudad"
    col_objecion_cat = "Objecion_Detectada"

    # ==================== BARRA LATERAL CON LA OPCIÓN FÍSICA "TODOS" ====================
    st.sidebar.header("🔍 Filtros de Venta")

    lista_programas = sorted(df[col_programa].unique())
    opciones_prog = ["Todos"] + lista_programas
    prog_sel_raw = st.sidebar.multiselect("Filtrar por Programa:", options=opciones_prog, default=["Todos"])

    lista_modalidades = sorted(df[col_modalidad].dropna().astype(str).unique())
    opciones_mod = ["Todos"] + lista_modalidades
    mod_sel_raw = st.sidebar.multiselect("Filtrar por Modalidad:", options=opciones_mod, default=["Todos"])

    lista_ciudades = sorted(df[col_ciudad].dropna().astype(str).unique())
    opciones_ciu = ["Todos"] + lista_ciudades
    ciu_sel_raw = st.sidebar.multiselect("Filtrar por Ciudad:", options=opciones_ciu, default=["Todos"])

    prog_sel = lista_programas if "Todos" in prog_sel_raw or not prog_sel_raw else prog_sel_raw
    mod_sel = lista_modalidades if "Todos" in mod_sel_raw or not mod_sel_raw else mod_sel_raw
    ciu_sel = lista_ciudades if "Todos" in ciu_sel_raw or not ciu_sel_raw else ciu_sel_raw

    df_filtrado = df[
        (df[col_programa].isin(prog_sel)) & 
        (df[col_modalidad].isin(mod_sel)) & 
        (df[col_ciudad].isin(ciu_sel))
    ]

    if not df_filtrado.empty:
        if "fecha" in df_filtrado.columns:
            fecha_min = df_filtrado["fecha"].min()
            fecha_max = df_filtrado["fecha"].max()
            rango_fechas_str = f"{fecha_min.strftime('%d/%m/%Y')} al {fecha_max.strftime('%d/%m/%Y')}" if pd.notna(fecha_min) else "Filtro Dinámico"
        else:
            rango_fechas_str = "Filtro Dinámico"

        # ==================== TARJETAS DE INDICADORES ====================
        total_llamadas_filtradas = len(df_filtrado)
        total_universo_llamadas = 144000
        porcentaje_penetracion = (total_llamadas_filtradas / total_universo_llamadas) * 100
        total_categorias = df_filtrado[col_objecion_cat].nunique()

        st.markdown("#### Resumen Ejecutivo General")
        kpi_top1, kpi_top2, kpi_top3 = st.columns(3)
        with kpi_top1:
            st.metric(label="📊 Llamadas Analizadas con Filtro", value=f"{total_llamadas_filtradas:,}")
        with kpi_top2:
            st.metric(label="📞 Universo Total Operativo", value=f"{total_universo_llamadas:,}")
        with kpi_top3:
            st.metric(label="📅 Rango de Fechas Evaluado", value=rango_fechas_str)

        kpi_bot1, kpi_bot2 = st.columns(2)
        with kpi_bot1:
            st.metric(label="📉 Tasa de Penetración de Análisis", value=f"{porcentaje_penetracion:.2f}%")
        with kpi_bot2:
            st.metric(label="⚠️ Tipos de Objeción en Sala", value=total_categorias)

        st.markdown("---")

        # ==================== GRÁFICA ENFOQUE TOTAL EN OBJECIONES (VERDES CUN) ====================
        st.subheader("📈 Ranking Global de Objeciones y Programas Afectados")
        
        df_obj_totales = df_filtrado[col_objecion_cat].value_counts().reset_index()
        df_obj_totales.columns = ["Tipo de Objeción", "Total"]

        df_desglose = df_filtrado.groupby([col_objecion_cat, col_programa]).size().reset_index(name="Cantidad de Llamadas")
        df_desglose.columns = ["Tipo de Objeción", "Programa Académico", "Cantidad de Llamadas"]

        # Paleta de degradados exclusivamente basada en el verde institucional de la CUN (#1E5D2F)
        cun_green_scale = ["#E8F5E9", "#C8E6C9", "#A5D6A7", "#81C784", "#66BB6A", "#4CAF50", "#43A047", "#388E3C", "#2E7D32", "#1E5D2F"]

        fig = px.bar(
            df_desglose,
            x="Cantidad de Llamadas",
            y="Tipo de Objeción",
            color="Programa Académico",
            orientation="h",
            color_discrete_sequence=cun_green_scale,
            category_orders={"Tipo de Objeción": df_obj_totales["Tipo de Objeción"].tolist()}
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=220, r=20, t=20, b=20),
            height=550,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(title="<b>Programas Académicos</b>", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ==================== DISTRIBUCIÓN DE OBJECIONES REALES (TABLA ESTILIZADA CON GRADIENTE) ====================
        st.subheader("🛑 Distribución del Motivo de Pérdida en Llamadas")
        st.markdown("*Esta tabla se pinta dinámicamente con degradados verdes según el volumen de pérdidas:*")
        
        top_objeciones = df_filtrado[col_objecion_cat].value_counts().reset_index()
        top_objeciones.columns = ["Categoría de Objeción", "Volumen de Llamadas"]
        
        # Muestra la tabla de datos usando un mapa de color interactivo de Pandas basado en verdes
        st.dataframe(
            top_objeciones.style.background_gradient(cmap="Greens", subset=["Volumen de Llamadas"]),
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # ==================== 4. SECCIÓN: INSIGHTS TEXTUALES CON HOVER EFECT ====================
        st.subheader("💡 Insights Operativos del Cruce de Llamadas")

        if not top_objeciones.empty:
            mayor_objecion = top_objeciones.iloc[0]["Categoría de Objeción"]
            cantidad_mayor = top_objeciones.iloc[0]["Volumen de Llamadas"]
            porcentaje_sobre_caidas = (cantidad_mayor / total_llamadas_filtradas) * 100

            df_mayor_obj = df_filtrado[df_filtrado[col_objecion_cat] == mayor_objecion]
            prog_afectado = df_mayor_obj[col_programa].value_counts().idxmax() if not df_mayor_obj.empty else "N/A"

            if mayor_objecion == "Tiempo/Flexibilidad":
                recomendacion_comercial = "Se requiere evaluar estrategias de flexibilización horaria, promoción activa de la modalidad virtual o reestructuración de los speechs de seguimiento."
            elif mayor_objecion == "Económica":
                recomendacion_comercial = "Se requiere articulación inmediata con el área de cartera o convenios de financiación para mitigar la deserción telefónica."
            else:
                recomendacion_comercial = "Se requiere revisar las mallas curriculares del programa afectado o capacitar a los asesores de la sala."

            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3>🔴 Análisis de Barreras Críticas en Sala</h3>
                        <ul>
                            <li><b>Principal obstáculo detectado:</b> La categoría de objeción <b>'{mayor_objecion}'</b> es el motivo número uno por el cual fracasan los closures telefónicos, acumulando un volumen de <b>{cantidad_mayor:,} llamadas</b> (un <b>{porcentaje_sobre_caidas:.1f}%</b> del total filtrado).</li>
                            <li><b>Programa de la CUN más afectado:</b> El programa académico con mayor vulnerabilidad actual es <b>{prog_afectado}</b>.</li>
                            <li><i>👉 {recomendacion_comercial}</i></li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_ins2:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3>📞 Métricas Operativas del COE</h3>
                        <ul>
                            <li><b>Volumen de Esfuerzo:</b> Sobre el universo base de <b>{total_universo_llamadas:,} llamadas</b>, el cruce actual consolida <b>{total_llamadas_filtradas:,} llamadas</b> analizadas en los registros reales.</li>
                            <li><b>Tasa de Penetración del Análisis:</b> El porcentaje de llamadas procesadas respecto al volumen total se ubica en el <b>{porcentaje_penetracion:.2f}%</b>.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ==================== 5. SECCIÓN: GLOSARIO EXPLICATIVO EN HTML MAQUETADO ====================
        st.subheader("📖 Glosario Técnico: Definición de Objeciones en Sala")
        st.markdown("Matriz conceptual interactiva utilizada para estandarizar la tipificación dentro del COE de la CUN (pasa el cursor por encima):")
        
        # Construcción de tabla responsiva en HTML puro con hover personalizado en CSS
        html_glosario = "<table class='glosario-tabla'><thead><tr><th>Categoría de Objeción</th><th>Significado Comercial / ¿Qué significa en la llamada?</th></tr></thead><tbody>"
        for item in glosario_data:
            html_glosario += f"<tr><td><b>{item['cat']}</b></td><td>{item['significado']}</td></tr>"
        html_glosario += "</tbody></table>"
        
        st.markdown(html_glosario, unsafe_allow_html=True)

    else:
        st.warning("⚠️ No existen llamadas reales con datos comerciales válidos para los filtros seleccionados.")
else:
    st.error(f"❌ El archivo Excel no contiene datos válidos o no se detectó en la ruta: `{RUTA_REAL_EXCEL}`.")
