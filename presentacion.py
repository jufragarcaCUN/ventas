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

    .insight-card-pct {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #3182CE;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        margin-bottom: 15px;
    }
    .insight-card-pct:hover {
        transform: translateY(-3px);
        box-shadow: 0 8px 15px rgba(49, 130, 206, 0.15);
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
        cursor: pointer;
    }
    </style>
""",
    unsafe_allow_html=True,
)

st.title("🎯 Análisis de Objeciones COE - CUN")
st.markdown("### *Informe de Auditoría y Control de Llamadas Operativas*")
st.markdown("---")

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

    # ==================== BARRA LATERAL CON FILTROS ====================
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

        # ==================== TARJETAS DE INDICADORES GENERALES ====================
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

        # ==================== SECCIÓN DE VOLÚMENES ABSOLUTOS ====================
        st.subheader("📊 Análisis General por Volúmenes Absolutos (Cantidad Directa)")
        
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
            legend=dict(title="<b>Programas Académicos</b>", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
        )
        st.plotly_chart(fig_abs, use_container_width=True)

        # Tabla de distribución absoluta usando barras nativas estilizadas
        st.markdown("##### 🛑 Distribución del Motivo de Pérdida en Volumen Directo")
        st.dataframe(
            df_obj_totales,
            column_config={
                "Tipo de Objeción": "Categoría de Objeción",
                "Total": st.column_config.ProgressColumn(
                    "Volumen de Llamadas",
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

        # ==================== 4. SECCIÓN: INSIGHTS TEXTUALES ABSOLUTOS ====================
        if not df_obj_totales.empty:
            mayor_objecion = df_obj_totales.iloc[0]["Tipo de Objeción"]
            cantidad_mayor = df_obj_totales.iloc[0]["Total"]
            porcentaje_sobre_caidas = (cantidad_mayor / total_llamadas_filtradas) * 100

            df_mayor_obj = df_filtrado[df_filtrado[col_objecion_cat] == mayor_objecion]
            prog_afectado = df_mayor_obj[col_programa].value_counts().idxmax() if not df_mayor_obj.empty else "N/A"

            col_ins1, col_ins2 = st.columns(2)
            with col_ins1:
                st.markdown(
                    f"""
                    <div class="insight-card">
                        <h3>🔴 Análisis de Barreras Críticas en Volumen</h3>
                        <ul>
                            <li><b>Mayor fuga en llamadas:</b> La objeción <b>'{mayor_objecion}'</b> es la que más volumen absoluto genera en la sala, con <b>{cantidad_mayor:,} casos</b> ({porcentaje_sobre_caidas:.1f}% del total general).</li>
                            <li><b>Carrera con más registros:</b> <b>{prog_afectado}</b> es quien más suma unidades en esta métrica.</li>
                        </ul>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            with col_ins2:
                st.markdown(
                    """
                    <div class="insight-card">
                        <h3>📌 Nota del Líder COE</h3>
                        <p>Los volúmenes absolutos nos indican dónde está la mayor masa de llamadas de la CUN, pero pueden invisibilizar la gravedad de las objeciones en carreras de nicho o menor tamaño.</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

        st.markdown("---")

        # ==================== 5. ACORDEÓN COMPLETO: ANÁLISIS PORCENTUAL POR PROGRAMA ====================
        with st.expander("📊 ANÁLISIS PORCENTUAL POR PROGRAMA (Normalización de Impacto Actualizado)"):
            st.markdown("### 🔍 ¿Qué analiza esta sección?")
            st.markdown("""
            *Esta pestaña equilibra la balanza. Aquí cada programa académico calcula su distribución internamente sobre el **100% de sus propias llamadas caídas**.*
            *Evita que las carreras masivas tapen los problemas críticos de las carreras pequeñas. **¡Aquí medimos tasas de fricción real!***
            """)
            
            # 1. Calcular los porcentajes internos por carrera
            # Agrupamos por Programa y Objeción para contar
            df_pct_base = df_filtrado.groupby([col_programa, col_objecion_cat]).size().reset_index(name="Conteo")
            
            # Sacamos los totales de cada carrera individual
            df_totales_por_carrera = df_filtrado[col_programa].value_counts().reset_index()
            df_totales_por_carrera.columns = [col_programa, "Total_Carrera"]
            
            # Cruzamos y calculamos el porcentaje relativo de cada objeción en esa carrera específica
            df_pct_final = pd.merge(df_pct_base, df_totales_por_carrera, on=col_programa)
            df_pct_final["Porcentaje del Programa"] = (df_pct_final["Conteo"] / df_pct_final["Total_Carrera"]) * 100
            
            # Ordenamos para la gráfica
            df_pct_ranking = df_pct_final.groupby(col_objecion_cat)["Porcentaje del Programa"].mean().reset_index()
            df_pct_ranking = df_pct_ranking.sort_values(by="Porcentaje del Programa", ascending=False)

            # 2. Gráfica de Barras Apiladas al 100% (Enfoque Relativo usando escala azul institucional)
            fig_pct = px.bar(
                df_pct_final,
                x="Porcentaje del Programa",
                y=col_objecion_cat,
                color=col_programa,
                orientation="h",
                color_discrete_sequence=px.colors.sequential.Blues_r,
                category_orders={col_objecion_cat: df_pct_ranking[col_objecion_cat].tolist()},
                labels={"Porcentaje del Programa": "Porcentaje Interno de Impacto (%)", col_objecion_cat: "Categoría de Objeción"}
            )
            fig_pct.update_layout(
                yaxis={"categoryorder": "total ascending"},
                margin=dict(l=220, r=20, t=20, b=20),
                height=500,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(title="<b>Distribución por Carrera</b>", orientation="v", yanchor="top", y=1, xanchor="left", x=1.02)
            )
            st.plotly_chart(fig_pct, use_container_width=True)

            # 3. Tabla de Datos Porcentual Estilizada
            st.markdown("##### 📈 Tabla de Fricción Relativa (% Promedio de Afectación)")
            df_tabla_pct = df_pct_final.groupby(col_objecion_cat).agg(
                Porcentaje_Promedio=("Porcentaje del Programa", "mean"),
                Carrera_Mas_Golpeada=(col_programa, lambda x: df_pct_final.loc[x.index].sort_values(by="Porcentaje del Programa", ascending=False).iloc[0][col_programa]),
                Porcentaje_Maximo=("Porcentaje del Programa", "max")
            ).reset_index().sort_values(by="Porcentaje_Promedio", ascending=False)

            st.dataframe(
                df_tabla_pct,
                column_config={
                    "col_objecion_cat": "Categoría de Objeción",
                    "Porcentaje_Promedio": st.column_config.NumberColumn("Fricción Promedio", format="%.2f %%"),
                    "Carrera_Mas_Golpeada": "Programa con Mayor Fricción",
                    "Porcentaje_Maximo": st.column_config.ProgressColumn("Impacto Máximo Local", format="%.2f %%", min_value=0, max_value=100, color="blue")
                },
                use_container_width=True,
                hide_index=True
            )

            # 4. Insights Porcentuales Dinámicos
            if not df_tabla_pct.empty:
                peor_obj_pct = df_tabla_pct.iloc[0][col_objecion_cat]
                promedio_peor = df_tabla_pct.iloc[0]["Porcentaje_Promedio"]
                carrera_critica = df_tabla_pct.iloc[0]["Carrera_Mas_Golpeada"]
                max_critico = df_tabla_pct.iloc[0]["Porcentaje_Maximo"]

                col_pct_ins1, col_pct_ins2 = st.columns(2)
                with col_pct_ins1:
                    st.markdown(
                        f"""
                        <div class="insight-card-pct">
                            <h3>🔵 Hallazgo Relativo Crítico (Tasas de Rebote)</h3>
                            <ul>
                                <li><b>Alerta Máxima Proporcional:</b> Analizando los porcentajes internos, la objeción de <b>'{peor_obj_pct}'</b> lidera con un índice de fricción promedio del <b>{promedio_peor:.2f}%</b> entre todos los programas.</li>
                                <li><b>Punto de Dolor Localizado:</b> El programa académico donde esta objeción es más destructiva es <b>{carrera_critica}</b>, representando un impresionante <b>{max_critico:.2f}%</b> de sus llamadas totales caídas.</li>
                            </ul>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_pct_ins2:
                    st.markdown(
                        f"""
                        <div class="insight-card-pct">
                            <h3>💡 Plan de Acción Comercial COE</h3>
                            <p>¡Atención! Aunque la carrera <b>{carrera_critica}</b> tenga pocas llamadas en volumen absoluto, el <b>{max_critico:.2f}%</b> de sus cierres se están perdiendo exclusivamente por <b>{peor_obj_pct}</b>. Se sugiere cambiar urgentemente el script comercial enfocado en este nicho para evitar la muerte del programa en el embudo.</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

        st.markdown("---")

        # ==================== 6. SECCIÓN: TABLA GLOSARIO EXPLICATIVO FIJO ====================
        st.subheader("📖 Glosario Técnico: Definición de Objeciones en Sala")
        st.markdown("Matriz conceptual interactiva utilizada para estandarizar la tipificación dentro del COE de la CUN:")
        
        html_glosario = "<table class='glosario-tabla'><thead><tr><th>Categoría de Objeción</th><th>Significado Comercial / ¿Qué significa en la llamada?</th></tr></thead><tbody>"
        for item in glosario_data:
            html_glosario += f"<tr><td><b>{item['cat']}</b></td><td>{item['significado']}</td></tr>"
        html_glosario += "</tbody></table>"
        
        st.markdown(html_glosario, unsafe_allow_html=True)

    else:
        st.warning("⚠️ No existen llamadas reales con datos comerciales válidos para los filtros seleccionados.")
else:
    st.error(f"❌ El archivo Excel no contiene datos válidos o no se detectó en la ruta: `{RUTA_REAL_EXCEL}`.")
