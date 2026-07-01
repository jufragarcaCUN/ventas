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

st.markdown(
    """
    <style>
    :root {
        --primary-color: #1E5D2F;
    }
    .reportview-container, .stApp {
        background: #F4F6F7;
    }
    h1, h2, h3 {
        color: #1E5D2F !important; /* Verde Institucional CUN */
    }
    div[data-testid="stMetricValue"] {
        color: #1E5D2F !important;
    }
    .stButton>button {
        background-color: #1E5D2F;
        color: white;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 Análisis de Objeciones COE - CUN")
st.markdown("### *Informe de Auditoría y Control de Llamadas Operativas*")
st.markdown("---")

RUTA_REAL_EXCEL = "carreras_homologadas_1.xlsx"

# ==================== 2. TABLA EXPLICATIVA (GLOSARIO REAL DE LLAMADAS) ====================
glosario_data = {
    "Categoría de Objeción": [
        "Económica",
        "Tiempo/Flexibilidad",
        "Confianza/Legalidad",
        "Metodología",
        "Terceros",
        "Competencia",
        "Documentación/Requisitos",
        "Ubicación/Sedes",
        "Desinterés/Aplazamiento",
    ],
    "Significado Comercial / ¿Qué significa en la llamada?": [
        "El contacto manifiesta falta de dinero, objeta el costo del semestre o solicita opciones de financiación especiales durante la llamada.",
        "El contacto reporta cruces de horarios con turnos laborales rotativos, altas cargas en su puesto actual o falta de tiempo disponible durante la llamada.",
        "El contacto expresa dudas explícitas sobre la validez del título ante el Ministerio de Educación o exige códigos SNIES en la llamada.",
        "El contacto manifiesta apatía o resistencia abierta al modelo educativo propuesto, problemas técnicos o de conectividad.",
        "El contacto indica en la llamada que no tiene autonomía para decidir y que debe consultar la decisión económica con familiares o jefes.",
        "El contacto manifiesta que está evaluando o comparando activamente frente a ofertas y costos de otras instituciones del mercado.",
        "El contacto reporta en la llamada retrasos en la entrega de requisitos obligatorios (ICFES, actas de grado, certificados de notas).",
        "El contacto argumenta barrera geográfica por distancia excesiva hacia las sedes físicas o problemas de transporte urbano.",
        "El contacto solicita voluntariamente aplazar el contacto para periodos futuros o manifiesta desinterés definitivo con la llamada.",
    ],
}
df_glosario = pd.DataFrame(glosario_data)


# ==================== 3. CARGA Y LIMPIEZA DE DATOS BASURA ====================
@st.cache_data
def cargar_y_limpiar_excel(ruta):
    if os.path.exists(ruta):
        data = pd.read_excel(ruta)

        # Convertir fechas si existen
        if "fecha" in data.columns:
            data["fecha"] = pd.to_datetime(data["fecha"], errors="coerce")

        # Definición de columnas clave
        col_prog = "programa_homologado_lista"
        col_obj = "Objecion_Detectada"

        # Limpieza de nulos iniciales
        data = data.dropna(subset=[col_prog, col_obj])

        # Volvemos todo string y minúsculas temporalmente para limpiar sin importar cómo venga escrito
        data[col_prog] = data[col_prog].astype(str).str.strip()
        data[col_obj] = data[col_obj].astype(str).str.strip()

        # Filtro duro: Eliminamos de raíz cualquier registro que contenga estos textos basura
        textos_basura = [
            "otro / por verificar",
            "otro",
            "no registrado",
            "por verificar",
            "",
            "nan",
            "none",
        ]

        data = data[
            (~data[col_prog].str.lower().isin(textos_basura))
            & (~data[col_obj].str.lower().isin(textos_basura))
        ]

        return data
    return None


df = cargar_y_limpiar_excel(RUTA_REAL_EXCEL)

if df is not None and not df.empty:
    # Columnas estandarizadas del archivo de llamadas
    col_programa = "programa_homologado_lista"
    col_modalidad = "modalidad_limpia"
    col_ciudad = "ciudad"
    col_objecion_cat = "Objecion_Detectada"

    # ==================== BARRA LATERAL CON LA OPCIÓN FÍSICA "TODOS" ====================
    st.sidebar.header("🔍 Filtros de Venta")

    # Filtro 1: Programas Académicos (Ya limpios)
    lista_programas = sorted(df[col_programa].unique())
    opciones_prog = ["Todos"] + lista_programas
    prog_sel_raw = st.sidebar.multiselect(
        "Filtrar por Programa:", options=opciones_prog, default=["Todos"]
    )

    # Filtro 2: Modalidades
    lista_modalidades = sorted(df[col_modalidad].dropna().astype(str).unique())
    opciones_mod = ["Todos"] + lista_modalidades
    mod_sel_raw = st.sidebar.multiselect(
        "Filtrar por Modalidad:", options=opciones_mod, default=["Todos"]
    )

    # Filtro 3: Ciudades
    lista_ciudades = sorted(df[col_ciudad].dropna().astype(str).unique())
    opciones_ciu = ["Todos"] + lista_ciudades
    ciu_sel_raw = st.sidebar.multiselect(
        "Filtrar por Ciudad:", options=opciones_ciu, default=["Todos"]
    )

    # Lógica de asignación para la opción "Todos"
    prog_sel = (
        lista_programas if "Todos" in prog_sel_raw or not prog_sel_raw else prog_sel_raw
    )
    mod_sel = (
        lista_modalidades if "Todos" in mod_sel_raw or not mod_sel_raw else mod_sel_raw
    )
    ciu_sel = (
        lista_ciudades if "Todos" in ciu_sel_raw or not ciu_sel_raw else ciu_sel_raw
    )

    # Filtrado final enfocado únicamente en los cruces reales analizados
    df_filtrado = df[
        (df[col_programa].isin(prog_sel))
        & (df[col_modalidad].isin(mod_sel))
        & (df[col_ciudad].isin(ciu_sel))
    ]

    # PROCESAMIENTO EXCLUSIVO DE DATOS VALIDADOS
    if not df_filtrado.empty:

        # Rango de fechas dinámico sobre lo que cruzó
        if "fecha" in df_filtrado.columns:
            fecha_min = df_filtrado["fecha"].min()
            fecha_max = df_filtrado["fecha"].max()
            if pd.notna(fecha_min) and pd.notna(fecha_max):
                rango_fechas_str = f"{fecha_min.strftime('%d/%m/%Y')} al {fecha_max.strftime('%d/%m/%Y')}"
            else:
                rango_fechas_str = "Filtro Dinámico Cruzado"
        else:
            rango_fechas_str = "Filtro Dinámico Cruzado"

        # ==================== TARJETAS DE INDICADORES (MÉTRICAS DEL CRUCE REAL) ====================
        total_llamadas_filtradas = len(df_filtrado)
        total_universo_llamadas = 144000  # Universo base operativo
        porcentaje_penetracion = (
            total_llamadas_filtradas / total_universo_llamadas
        ) * 100
        total_categorias = df_filtrado[col_objecion_cat].nunique()

        st.markdown("#### Resumen Ejecutivo General")
        kpi_top1, kpi_top2, kpi_top3 = st.columns(3)
        with kpi_top1:
            st.metric(
                label="📊 Llamadas Analizadas con Filtro",
                value=f"{total_llamadas_filtradas:,}",
            )
        with kpi_top2:
            st.metric(
                label="📞 Universo Total Operativo",
                value=f"{total_universo_llamadas:,}",
            )
        with kpi_top3:
            st.metric(label="📅 Rango de Fechas Evaluado", value=rango_fechas_str)

        kpi_bot1, kpi_bot2 = st.columns(2)
        with kpi_bot1:
            st.metric(
                label="📉 Tasa de Penetración de Análisis",
                value=f"{porcentaje_penetracion:.2f}%",
            )
        with kpi_bot2:
            st.metric(label="⚠️ Tipos de Objeción en Sala", value=total_categorias)

        st.markdown("---")

        # ==================== GRÁFICA INTERACTIVA HORIZONTAL REESTRUCTURADA ====================
        st.subheader("📈 Distribución de Objeciones por Top 10 Programas Académicos")

        # Identificar los 10 programas con más llamadas caídas primero
        top_10_prog_nombres = df_filtrado[col_programa].value_counts().head(10).index

        # Filtrar el dataframe solo para esos 10 programas y agrupar por Programa + Objeción
        df_top_grafica = df_filtrado[df_filtrado[col_programa].isin(top_10_prog_nombres)]
        df_agrupado = (
            df_top_grafica.groupby([col_programa, col_objecion_cat])
            .size()
            .reset_index(name="Cantidad de Llamadas")
        )
        df_agrupado.columns = ["Nombre del Programa", "Tipo de Objeción", "Cantidad de Llamadas"]

        # Gráfica horizontal apilada (Muestra las objeciones reales dentro de cada barra)
        fig = px.bar(
            df_agrupado,
            x="Cantidad de Llamadas",
            y="Nombre del Programa",
            color="Tipo de Objeción",
            orientation="h",
            color_discrete_sequence=px.colors.sequential.Greens_r, # Degradados verdes institucionales
            labels={"Tipo de Objeción": "Objeción Detectada"}
        )

        fig.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=320, r=20, t=20, b=20),  # Espacio para los nombres largos de carreras
            height=650,
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # ==================== DISTRIBUCIÓN DE OBJECIONES REALES ====================
        st.subheader("🛑 Distribución del Motivo de Pérdida en Llamadas")
        top_objeciones = df_filtrado[col_objecion_cat].value_counts().reset_index()
        top_objeciones.columns = ["Categoría de Objeción", "Volumen de Llamadas"]
        st.dataframe(top_objeciones, use_container_width=True, hide_index=True)

        st.markdown("---")

        # ==================== 4. SECCIÓN: INSIGHTS TEXTUALES DEL CRUCE DE LLAMADAS ====================
        st.subheader("💡 Insights Operativos del Cruce de Llamadas")

        if not top_objeciones.empty:
            mayor_objecion = top_objeciones.iloc[0]["Categoría de Objeción"]
            cantidad_mayor = top_objeciones.iloc[0]["Volumen de Llamadas"]
            porcentaje_sobre_caidas = (cantidad_mayor / total_llamadas_filtradas) * 100

            df_mayor_obj = df_filtrado[df_filtrado[col_objecion_cat] == mayor_objecion]
            prog_afectado = (
                df_mayor_obj[col_programa].value_counts().idxmax()
                if not df_mayor_obj.empty
                else "N/A"
            )

            if mayor_objecion == "Tiempo/Flexibilidad":
                recomendacion_comercial = "Se requiere evaluar estrategias de flexibilización horaria, promoción activa de la modal virtual o reestructuración de los speechs de seguimiento."
            elif mayor_objecion == "Económica":
                recomendacion_comercial = "Se requiere articulación con el área de cartera o convenios de financiación para mitigar la deserción telefónica."
            else:
                recomendacion_comercial = "Se requiere revisar las mallas curriculares del programa afectado o capacitar a los asesores de la sala."

            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.markdown(f"""
                ### **Análisis de Barreras Críticas en Sala**
                * 🔴 **Principal obstáculo detectado:** La categoría de objeción **'{mayor_objecion}'** es el motivo número uno por el cual fracasan los closures telefónicos, acumulando un volumen de **{cantidad_mayor:,} llamadas** (un **{porcentaje_sobre_caidas:.1f}%** de las llamadas analizadas).
                * 🎓 **Programa académico de la CUN más afectado:** El programa académico con mayor vulnerabilidad es **{prog_afectado}**. *{recomendacion_comercial}*
                """)
            with col_ins2:
                st.markdown(f"""
                ### **Métricas Operativas del COE**
                * 📞 **Volumen de Esfuerzo:** Sobre el universo base de **{total_universo_llamadas:,} llamadas**, el cruce actual consolida **{total_llamadas_filtradas:,} llamadas** analizadas en los registros reales.
                * 📉 **Tasa de Penetración del Análisis:** El porcentaje de llamadas procesadas respecto al volumen total se ubica en el **{porcentaje_penetracion:.2f}%**.
                """)

        st.markdown("---")

        # ==================== 5. SECCIÓN: TABLA GLOSARIO EXPLICATIVO FIJO ====================
        st.subheader("📖 Glosario Técnico: Definición de Objeciones en Sala")
        st.markdown(
            "Matriz conceptual fija utilizada para estandarizar la tipificación y auditoría de llamadas dentro del COE de la CUN:"
        )
        st.table(df_glosario)

    else:
        st.warning(
            "⚠️ No existen llamadas reales con datos comerciales válidos para los filtros seleccionados."
        )

else:
    st.error(
        f"❌ El archivo Excel no contiene datos válidos o no se detectó en la ruta: `{RUTA_REAL_EXCEL}`."
    )
