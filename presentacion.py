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
st.markdown("### *Informe de Auditoría y Control de Llamadas Operativas*")
st.markdown("---")

RUTA_REAL_EXCEL = "carreras_homologadas_1.xlsx"

# ==================== 2. MATRIZ DE CONFIGURACIÓN CONCEPTUAL ====================
glosario_data = [
    {"cat": "Económica", "significado": "El contacto manifiesta falta de liquidez, objeta el costo de la matrícula o requiere alternativas de financiación especiales."},
    {"cat": "Tiempo/Flexibilidad", "significado": "El contacto reporta incompatibilidad horaria con su jornada laboral activa o indisponibilidad de tiempo."},
    {"cat": "Confianza/Legalidad", "significado": "El contacto expresa dudas explícitas sobre la acreditación institucional o códigos SNIES."},
    {"cat": "Metodología", "significado": "El contacto manifiesta resistencia hacia el modelo educativo propuesto, limitaciones técnicas o problemas de conectividad."},
    {"cat": "Terceros", "significado": "El contacto indica ausencia de autonomía en la toma de decisiones (debe consultar con familiares o jefes)."},
    {"cat": "Competencia", "significado": "El contacto declara estar en proceso de comparación frente a la oferta y aranceles de otras instituciones."},
    {"cat": "Documentación/Requisitos", "significado": "El contacto reporta retrasos en la expedición o entrega de soportes obligatorios (ICFES, actas de grado)."},
    {"cat": "Ubicación/Sedes", "significado": "El contacto argumenta barreras geográficas por distancia hacia los centros de servicio físico."},
    {"cat": "Desinterés/Aplazamiento", "significado": "El contacto solicita aplazar el proceso para periodos futuros o desiste explícitamente."}
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

        # ==================== BALANCES MÉTRICOS ====================
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
        st.subheader("📈 Distribución por Volúmenes Absolutos")
        
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

        # ==================== INSIGHTS ABSOLUTOS RE-ESTRUCTURADOS (DIRECTOS) ====================
        if len(df_obj_totales) >= 2:
            # Datos de la objeción #1
            obj_1 = df_obj_totales.iloc[0]["Tipo de Objeción"]
            cant_1 = df_obj_totales.iloc[0]["Total"]
            df_m1 = df_filtrado[df_filtrado[col_objecion_cat] == obj_1]
            prog_m1 = df_m1[col_programa].value_counts().idxmax()
            cant_prog_m1 = df_m1[col_programa].value_counts().max()

            # Datos de la objeción #2
            obj_2 = df_obj_totales.iloc[1]["Tipo de Objeción"]
            cant_2 = df_obj_totales.iloc[1]["Total"]
            df_m2 = df_filtrado[df_filtrado[col_objecion_cat] == obj_2]
            prog_m2 = df_m2[col_programa].value_counts().idxmax()
            cant_prog_m2 = df_m2[col_programa].value_counts().max()

            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3>📊 Distribución General de Datos</h3>
                        <ul>
                            <li>La objeción con mayor volumen es <b>{obj_1}</b> ({cant_1:,} llamadas), concentrándose principalmente en el programa <b>{prog_m1}</b> con <b>{cant_prog_m1:,}</b> casos.</li>
                            <li>La segunda objeción con mayor registro es <b>{obj_2}</b> ({cant_2:,} llamadas), acumulando su mayor cantidad en el programa <b>{prog_m2}</b> con <b>{cant_prog_m2:,}</b> casos.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_ins2:
                # Encontrar el programa con más volumen absoluto general y ver su objeción número uno
                prog_top_general = df_filtrado[col_programa].value_counts().idxmax()
                df_prog_top = df_filtrado[df_filtrado[col_programa] == prog_top_general]
                peor_obj_prog_top = df_prog_top[col_objecion_cat].value_counts().idxmax()
                cant_peor_obj_prog_top = df_prog_top[col_objecion_cat].value_counts().max()
                
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3>📈 Mayor Foco de Pérdida Directa</h3>
                        <ul>
                            <li>El programa que registra la mayor cantidad neta de llamadas caídas en la sala es <b>{prog_top_general}</b>, y su principal motivo de pérdida es la objeción por <b>{peor_obj_prog_top}</b> con un volumen de <b>{cant_peor_obj_prog_top:,}</b> casos.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ==================== 5. ACORDEÓN: EVALUACIÓN RELATIVA NORMALIZADA ====================
        with st.expander("📊 ANÁLISIS PORCENTUAL POR PROGRAMA (Impacto Relativo Proporcional)"):
            st.markdown("### 🔍 Datos Distribucionales Internos")
            
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

            st.markdown("##### 📈 Matriz de Fricción Proporcional por Carrera")
            df_tabla_pct = df_pct_final.groupby(col_objecion_cat).agg(
                Porcentaje_Promedio=("Porcentaje del Programa", "mean"),
                Carrera_Mas_Golpeada=(col_programa, lambda x: df_pct_final.loc[x.index].sort_values(by="Porcentaje del Programa", ascending=False).iloc[0][col_programa]),
                Porcentaje_Maximo=("Porcentaje del Programa", "max")
            ).reset_index().sort_values(by="Porcentaje_Promedio", ascending=False)

            st.dataframe(
                df_tabla_pct,
                column_config={
                    "col_objecion_cat": "Categoría de Objeción",
                    "Porcentaje_Promedio": st.column_config.NumberColumn("Fricción Promedio General", format="%.2f %%"),
                    "Carrera_Mas_Golpeada": "Programa con Mayor Fricción Interna",
                    "Porcentaje_Maximo": st.column_config.ProgressColumn("Impacto Máximo Local (%)", format="%.2f %%", min_value=0, max_value=100, color="blue")
                },
                use_container_width=True,
                hide_index=True
            )

            # Insights descriptivos porcentuales directos y sencillos
            if not df_tabla_pct.empty:
                # Ordenar el df_pct_final de mayor a menor para encontrar los impactos relativos más altos y puros
                df_impactos_puros = df_pct_final.sort_values(by="Porcentaje del Programa", ascending=False)
                
                carrera_pct_1 = df_impactos_puros.iloc[0][col_programa]
                obj_pct_1 = df_impactos_puros.iloc[0][col_objecion_cat]
                val_pct_1 = df_impactos_puros.iloc[0]["Porcentaje del Programa"]

                carrera_pct_2 = df_impactos_puros.iloc[1][col_programa] if len(df_impactos_puros) > 1 else "N/A"
                obj_pct_2 = df_impactos_puros.iloc[1][col_objecion_cat] if len(df_impactos_puros) > 1 else "N/A"
                val_pct_2 = df_impactos_puros.iloc[1]["Porcentaje del Programa"] if len(df_impactos_puros) > 1 else 0

                col_pct_ins1, col_pct_ins2 = st.columns(2)
                with col_pct_ins1:
                    st.markdown(
                        f"""
                        <div class="insight-card-pct">
                            <h3>🔍 Programas con Mayor Concentración Porcentual</h3>
                            <ul>
                                <li>En el programa <b>{carrera_pct_1}</b>, el <b>{val_pct_1:.2f}%</b> de sus llamadas caídas se concentran exclusivamente bajo la objeción de <b>{obj_pct_1}</b>.</li>
                                <li>Para el programa <b>{carrera_pct_2}</b>, la objeción que genera mayor impacto proporcional interno es <b>{obj_pct_2}</b>, acumulando el <b>{val_pct_2:.2f}%</b> de sus motivos de no-cierre.</li>
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_pct_ins2:
                    peor_transversal_pct = df_tabla_pct.iloc[0][col_objecion_cat]
                    prom_transversal_pct = df_tabla_pct.iloc[0]["Porcentaje_Promedio"]
                    st.markdown(
                        f"""
                        <div class="insight-card-pct">
                            <h3>📈 Impacto Proporcional Dominante</h3>
                            <ul>
                                <li>Al evaluar de forma independiente el 100% de cada carrera, la categoría que promedia el mayor nivel de afectación interna en el portafolio evaluado es <b>{peor_transversal_pct}</b> con un índice del <b>{prom_transversal_pct:.2f}%</b>.</li>
                            </ul>
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
