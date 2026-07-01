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

# Inyección de CSS para la UI de nivel gerencial aplicando la identidad CUN
st.markdown(
    """
    <style>
    :root {
        --primary-color: #1E5D2F;
        --bg-color: #F4F6F7;
    }
    
    .stApp {
        background-color: var(--bg-color);
    }
    
    h1, h2, h3, h4 {
        color: #1E5D2F !important;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        font-weight: 700;
    }
    
    div[data-testid="stMetricValue"] {
        color: #1E5D2F !important;
        font-weight: bold;
        font-size: 2rem !important;
    }
    
    div[data-testid="stMetricLabel"] {
        color: #4A5568 !important;
        font-size: 0.95rem !important;
    }

    .insight-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #1E5D2F;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }

    .insight-card-pct {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 8px;
        border-left: 5px solid #2B6CB0;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }

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
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 Análisis de Objeciones COE - CUN")
st.markdown("### *Informe Clínico de Auditoría y Control de Procesos Operativos*")
st.markdown("---")

RUTA_REAL_EXCEL = "carreras_homologadas_1.xlsx"

# ==================== 2. MATRIZ DE CONFIGURACIÓN CONCEPTUAL ====================
glosario_data = [
    {"cat": "Económica", "significado": "El contacto manifiesta falta de liquidez, objeta el costo de la matrícula o requiere alternativas de financiación especiales durante el contacto."},
    {"cat": "Tiempo/Flexibilidad", "significado": "El contacto reporta incompatibilidad horaria con su jornada laboral activa, alta carga operacional o indisponibilidad de tiempo."},
    {"cat": "Confianza/Legalidad", "significado": "El contacto expresa dudas explícitas sobre la acreditación institucional, validez del título ante el Ministerio de Educación o códigos SNIES."},
    {"cat": "Metodología", "significado": "El contacto manifiesta resistencia o apatía hacia el modelo educativo propuesto, limitaciones técnicas o problemas de conectividad."},
    {"cat": "Terceros", "significado": "El contacto indica ausencia de autonomía en la toma de decisiones, postergando la resolución a la consulta con familiares o jefes directos."},
    {"cat": "Competencia", "significado": "El contacto declara estar en proceso de evaluación o comparación activa frente a la oferta académica y aranceles de otras instituciones."},
    {"cat": "Documentación/Requisitos", "significado": "El contacto reporta retrasos en la expedición o entrega de soportes obligatorios (ICFES, actas de grado, certificados de notas)."},
    {"cat": "Ubicación/Sedes", "significado": "El contacto argumenta barreras geográficas por distancia hacia los centros de servicio físico o restricciones de movilidad urbana."},
    {"cat": "Desinterés/Aplazamiento", "significado": "El contacto solicita voluntariamente diferir el proceso de admisión para periodos futuros o desiste explícitamente del interés comercial."}
]

# ==================== 3. PROCESAMIENTO Y DEPURACIÓN DE REGISTROS ====================
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

    # ==================== FILTROS ESTRATÉGICOS ====================
    st.sidebar.header("🔍 Criterios de Filtrado")

    lista_programas = sorted(df[col_programa].unique())
    opciones_prog = ["Todos"] + lista_programas
    prog_sel_raw = st.sidebar.multiselect("Programa Académico:", options=opciones_prog, default=["Todos"])

    lista_modalidades = sorted(df[col_modalidad].dropna().astype(str).unique())
    opciones_mod = ["Todos"] + lista_modalidades
    mod_sel_raw = st.sidebar.multiselect("Modalidad:", options=opciones_mod, default=["Todos"])

    lista_ciudades = sorted(df[col_ciudad].dropna().astype(str).unique())
    opciones_ciu = ["Todos"] + lista_ciudades
    ciu_sel_raw = st.sidebar.multiselect("Ubicación Geográfica:", options=opciones_ciu, default=["Todos"])

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
            rango_fechas_str = f"{fecha_min.strftime('%d/%m/%Y')} al {fecha_max.strftime('%d/%m/%Y')}" if pd.notna(fecha_min) else "Periodo Dinámico"
        else:
            rango_fechas_str = "Periodo Dinámico"

        # ==================== BALANCES MÉTRICOS CONTROLADOS ====================
        total_llamadas_filtradas = len(df_filtrado)
        total_universo_llamadas = 144000
        porcentaje_penetracion = (total_llamadas_filtradas / total_universo_llamadas) * 100
        total_categorias = df_filtrado[col_objecion_cat].nunique()

        st.markdown("#### Resumen Ejecutivo General")
        kpi_top1, kpi_top2, kpi_top3 = st.columns(3)
        with kpi_top1:
            st.metric(label="📊 Muestra Auditada Bajo Filtro", value=f"{total_llamadas_filtradas:,}")
        with kpi_top2:
            st.metric(label="📞 Universo Operativo de Control", value=f"{total_universo_llamadas:,}")
        with kpi_top3:
            st.metric(label="📅 Horizonte Temporal Evaluado", value=rango_fechas_str)

        kpi_bot1, kpi_bot2 = st.columns(2)
        with kpi_bot1:
            st.metric(label="📉 Tasa de Cobertura del Análisis", value=f"{porcentaje_penetracion:.2f}%")
        with kpi_bot2:
            st.metric(label="⚠️ Tipologías Activas en Sala", value=total_categorias)

        st.markdown("---")

        # ==================== EVALUACIÓN POR MUESTRA ABSOLUTA ====================
        st.subheader("📈 Análisis de Distribución por Volúmenes Absolutos")
        st.markdown("*Representación de la carga neta de interacciones fallidas ordenadas por volumen total.*")
        
        df_obj_totales = df_filtrado[col_objecion_cat].value_counts().reset_index()
        df_obj_totales.columns = ["Tipo de Objeción", "Total"]

        df_desglose = df_filtrado.groupby([col_objecion_cat, col_programa]).size().reset_index(name="Cantidad de Llamadas")
        df_desglose.columns = ["Tipo de Objeción", "Programa Académico", "Cantidad de Llamadas"]

        cun_green_scale = ["#E8F5E9", "#C8E6C9", "#A5D6A7", "#81C784", "#66BB6A", "#4CAF50", "#43A047", "#388E3C", "#2E7D32", "#1E5D2F"]

        fig_abs = px.bar(
            df_desglose,
            x="Cantidad de Llamadas",
            y="Tipo de Objeción",
            color="Programa Académico",
            orientation="h",
            color_discrete_sequence=cun_green_scale,
            category_orders={"Tipo de Objeción": df_obj_totales["Tipo de Objeción"].tolist()}
        )
        fig_abs.update_layout(
            yaxis={"categoryorder": "total ascending"},
            margin=dict(l=220, r=20, t=20, b=20),
            height=500,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            legend=dict(title="<b>Programa Académico</b>", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_abs, use_container_width=True)

        st.markdown("##### 🛑 Consolidado de Incidencias en Volumen Directo")
        st.dataframe(
            df_obj_totales,
            column_config={
                "Tipo de Objeción": "Categoría de Objeción",
                "Total": st.column_config.ProgressColumn(
                    "Volumen Corpóreo de Llamadas",
                    format="%d",
                    min_value=0,
                    max_value=int(df_obj_totales["Total"].max()),
                    color="green"
                ),
            },
            use_container_width=True,
            hide_index=True
        )

        st.markdown("---")

        # ==================== INSIGHTS GERENCIALES ABSOLUTOS DIRECTOS ====================
        if not df_obj_totales.empty:
            mayor_objecion = df_obj_totales.iloc[0]["Tipo de Objeción"]
            cantidad_mayor = df_obj_totales.iloc[0]["Total"]
            
            df_mayor_obj = df_filtrado[df_filtrado[col_objecion_cat] == mayor_objecion]
            prog_afectado = df_mayor_obj[col_programa].value_counts().idxmax() if not df_mayor_obj.empty else "N/A"
            cantidad_prog_afectado = df_mayor_obj[col_programa].value_counts().max() if not df_mayor_obj.empty else 0

            # Encontrar el programa con más volumen absoluto general de llamadas caídas y ver su objeción principal
            prog_top_general = df_filtrado[col_programa].value_counts().idxmax()
            df_prog_top = df_filtrado[df_filtrado[col_programa] == prog_top_general]
            peor_obj_prog_top = df_prog_top[col_objecion_cat].value_counts().idxmax()
            cant_peor_obj_prog_top = df_prog_top[col_objecion_cat].value_counts().max()

            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3>📋 Diagnóstico Directo de Objeciones</h3>
                        <ul>
                            <li>La objeción con mayor volumen general es <b>{mayor_objecion}</b> ({cantidad_mayor:,} llamadas), y el programa que más interacciones aporta a esta categoría es <b>{prog_afectado}</b> con <b>{cantidad_prog_afectado:,}</b> casos.</li>
                            <li>En el programa con mayor cantidad de llamadas fallidas (<b>{prog_top_general}</b>), la mayoría de los contactos tiene objeciones por <b>{peor_obj_prog_top}</b> (<b>{cant_peor_obj_prog_top:,}</b> llamadas).</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_ins2:
                st.markdown(
                    """
                    <div class="insight-card">
                        <h3>📌 Nota de Lectura</h3>
                        <p>Esta sección expone los datos de forma directa basados en el conteo total de la sala, reflejando principalmente el comportamiento de los programas con mayor cantidad de aspirantes registrados.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ==================== 5. ACORDEÓN: EVALUACIÓN RELATIVA NORMALIZADA ====================
        with st.expander("📊 ANÁLISIS PORCENTUAL POR PROGRAMA (Normalización de Impacto Relativo)"):
            st.markdown("### 🔍 Métricas Distribucionales Internas")
            st.markdown("""
            *Esta sección calcula la proporción interna de cada objeción calculada exclusivamente sobre el **100% de los registros correspondientes a cada programa específico**.*
            """)
            
            # Procesamiento matricial relativo
            df_pct_base = df_filtrado.groupby([col_programa, col_objecion_cat]).size().reset_index(name="Conteo")
            df_totales_por_carrera = df_filtrado[col_programa].value_counts().reset_index()
            df_totales_por_carrera.columns = [col_programa, "Total_Carrera"]
            
            df_pct_final = pd.merge(df_pct_base, df_totales_por_carrera, on=col_programa)
            df_pct_final["Porcentaje del Programa"] = (df_pct_final["Conteo"] / df_pct_final["Total_Carrera"]) * 100
            
            df_pct_ranking = df_pct_final.groupby(col_objecion_cat)["Porcentaje del Programa"].mean().reset_index()
            df_pct_ranking = df_pct_ranking.sort_values(by="Porcentaje del Programa", ascending=False)

            # Gráfica de distribución proporcional al 100%
            fig_pct = px.bar(
                df_pct_final,
                x="Porcentaje del Programa",
                y=col_objecion_cat,
                color=col_programa,
                orientation="h",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                category_orders={col_objecion_cat: df_pct_ranking[col_objecion_cat].tolist()},
                labels={"Porcentaje del Programa": "Participación Relativa por Programa (%)", col_objecion_cat: "Categoría de Objeción"}
            )
            fig_pct.update_layout(
                yaxis={"categoryorder": "total ascending"},
                margin=dict(l=220, r=20, t=20, b=20),
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(title="<b>Programa Académico</b>", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            st.plotly_chart(fig_pct, use_container_width=True)

            st.markdown("##### 📈 Matriz de Fricción Relativa (% Promedio Ponderado)")
            df_tabla_pct = df_pct_final.groupby(col_objecion_cat).agg(
                Porcentaje_Promedio=("Porcentaje del Programa", "mean"),
                Carrera_Mas_Golpeada=(col_programa, lambda x: df_pct_final.loc[x.index].sort_values(by="Porcentaje del Programa", ascending=False).iloc[0][col_programa]),
                Porcentaje_Maximo=("Porcentaje del Programa", "max")
            ).reset_index().sort_values(by="Porcentaje_Promedio", ascending=False)

            st.dataframe(
                df_tabla_pct,
                column_config={
                    "col_objecion_cat": "Categoría de Objeción",
                    "Porcentaje_Promedio": st.column_config.NumberColumn("Fricción Promedio Inter-Programa", format="%.2f %%"),
                    "Carrera_Mas_Golpeada": "Unidad de Máxima Exposición",
                    "Porcentaje_Maximo": st.column_config.ProgressColumn("Desviación Crítica Local", format="%.2f %%", min_value=0, max_value=100, color="blue")
                },
                use_container_width=True,
                hide_index=True
            )

            # Insights descriptivos porcentuales directos y sencillos
            if not df_tabla_pct.empty:
                peor_obj_pct = df_tabla_pct.iloc[0][col_objecion_cat]
                carrera_critica = df_tabla_pct.iloc[0]["Carrera_Mas_Golpeada"]
                max_critico = df_tabla_pct.iloc[0]["Porcentaje_Maximo"]

                col_pct_ins1, col_pct_ins2 = st.columns(2)
                with col_pct_ins1:
                    st.markdown(
                        f"""
                        <div class="insight-card-pct">
                            <h3>🔍 Análisis de Impacto por Programa</h3>
                            <ul>
                                <li>El programa con mayor impacto porcentual por una sola objeción es <b>{carrera_critica}</b>, donde la mayoría de sus aspirantes desiste por <b>{peor_obj_pct}</b>, representando el <b>{max_critico:.2f}%</b> de sus casos particulares.</li>
                                <li>Al evaluar proporcionalmente cada carrera, la categoría que se repite con mayor consistencia porcentual alta como motivo principal de no-cierre es <b>{peor_obj_pct}</b>.</li>
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_pct_ins2:
                    st.markdown(
                        f"""
                        <div class="insight-card-pct">
                            <h3>📊 Comportamiento Relativo</h3>
                            <p>Esta perspectiva permite ver qué objeción domina el comportamiento interno de cada carrera de forma independiente, aislando el impacto del tamaño o volumen total de estudiantes de la misma.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # ==================== 6. MARCO CONCEPTUAL ESTÁNDAR ====================
        st.subheader("📖 Matriz Operativa de Tipificación")
        st.markdown("Estructura conceptual estándar utilizada para la auditoría y control homogéneo de las interacciones dentro de la mesa de control del COE:")
        
        html_glosario = "<table class='glosario-tabla'><thead><tr><th>Categoría de Objeción</th><th>Definición Operativa e Incidencia Institucional</th></tr></thead><tbody>"
        for item in glosario_data:
            html_glosario += f"<tr><td><b>{item['cat']}</b></td><td>{item['significado']}</td></tr>"
        html_glosario += "</tbody></table>"
        
        st.markdown(html_glosario, unsafe_allow_html=True)

    else:
        st.warning("⚠️ No se identificaron registros concurrentes bajo los criterios de filtrado seleccionados.")
else:
    st.error(f"❌ Error en la lectura del repositorio o ausencia de datos válidos en la estructura física: `{RUTA_REAL_EXCEL}`.")
