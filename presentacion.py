import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np

# -------------------- CONFIGURACIÓN DE LA PÁGINA --------------------
st.set_page_config(
    page_title="Sistema de Evaluación de Llamadas | COE",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ==================== CSS PERSONALIZADO (PALETA CUN) ====================
st.markdown(
    """
    <style>
        /* Paleta CUN */
        :root {
            --cun-green: #22c55e;
            --cun-green-dark: #15804d;
            --cun-blue-dark: #0f172a;
            --cun-gray-medium: #334155;
            --cun-gray-light: #f1f5f9;
            --white: #ffffff;
        }

        /* Fondo general */
        .main .block-container {
            background-color: #f8fafc;
            padding: 2rem 3rem;
        }

        /* Títulos */
        h1, h2, h3, h4, h5 {
            font-family: 'Segoe UI', sans-serif;
            color: var(--cun-blue-dark);
        }
        .main-title {
            font-size: 2.5rem;
            font-weight: 900;
            color: var(--cun-blue-dark);
            border-left: 10px solid var(--cun-green);
            padding-left: 25px;
            margin-bottom: 1.5rem;
        }
        .section-title {
            font-size: 1.8rem;
            font-weight: 700;
            color: var(--cun-blue-dark);
            border-bottom: 3px solid #ffc107;
            padding-bottom: 10px;
            display: inline-block;
            margin-bottom: 1.5rem;
        }

        /* Tarjetas (cards) */
        .card-cun {
            background: var(--white);
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.08);
            border-left: 5px solid var(--cun-green);
            margin-bottom: 1.5rem;
            transition: transform 0.2s;
        }
        .card-cun:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 20px rgba(0,0,0,0.12);
        }
        .card-cun h3 {
            margin-top: 0;
            color: var(--cun-blue-dark);
        }
        .card-dark {
            background: var(--cun-blue-dark);
            color: white;
            padding: 1.5rem;
            border-radius: 12px;
            border-left: 5px solid var(--cun-green);
            margin-bottom: 1.5rem;
        }
        .card-dark h3 {
            color: white !important;
        }

        /* Sidebar personalizado */
        [data-testid="stSidebar"] {
            background-color: var(--cun-blue-dark) !important;
            padding: 2rem 1rem !important;
        }
        [data-testid="stSidebar"] * {
            color: #e2e8f0 !important;
            font-family: 'Segoe UI', sans-serif;
        }
        [data-testid="stSidebar"] .stRadio label {
            display: flex;
            align-items: center;
            gap: 10px;
            padding: 10px 16px;
            border-radius: 8px;
            font-weight: 600;
            font-size: 0.85rem;
            color: #94a3b8 !important;
            background: transparent;
            transition: all 0.3s ease;
            cursor: pointer;
            margin: 2px 0;
        }
        [data-testid="stSidebar"] .stRadio label:hover {
            background: rgba(255,255,255,0.05);
            color: white !important;
        }
        [data-testid="stSidebar"] .stRadio label > div:first-child {
            display: none !important;
        }
        [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] {
            background: rgba(34, 197, 94, 0.15) !important;
            color: var(--cun-green) !important;
            border-left: 3px solid var(--cun-green);
            border-radius: 0 8px 8px 0;
            padding-left: 13px;
        }
        [data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] * {
            color: var(--cun-green) !important;
        }

        /* Botones */
        .stButton button {
            background: var(--cun-blue-dark) !important;
            color: white !important;
            font-weight: 700 !important;
            border-radius: 30px !important;
            border: none !important;
            padding: 0.5rem 1.5rem !important;
            transition: all 0.3s ease !important;
        }
        .stButton button:hover {
            background: var(--cun-green) !important;
            transform: scale(1.02);
            box-shadow: 0 8px 20px rgba(34, 197, 94, 0.3);
        }

        /* Expanders */
        .streamlit-expanderHeader {
            font-weight: 700 !important;
            color: var(--cun-blue-dark) !important;
            background: var(--cun-gray-light) !important;
            border-radius: 8px !important;
        }

        /* Badges */
        .badge-pos {
            background: #d4edda; color: #155724; padding: 4px 14px; border-radius: 20px; font-weight: 700; display: inline-block;
        }
        .badge-neg {
            background: #f8d7da; color: #721c24; padding: 4px 14px; border-radius: 20px; font-weight: 700; display: inline-block;
        }
        .badge-cun {
            background: #22c55e; color: white; padding: 4px 14px; border-radius: 20px; font-weight: 700; display: inline-block;
        }
        .error-card {
            background: #fff5f5;
            border-left: 5px solid #dc3545;
            padding: 1rem;
            border-radius: 8px;
            margin-bottom: 1.5rem;
        }
        .error-card h4 {
            color: #dc3545;
            margin-top: 0;
        }
        .sql-block {
            background: #0f172a;
            color: #e2e8f0;
            padding: 1rem;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            font-size: 0.85rem;
            overflow-x: auto;
        }
        .status-solved {
            background: #d4edda; padding: 4px 14px; border-radius: 20px; font-weight: 700; color: #155724;
        }
        .status-progress {
            background: #fff3cd; padding: 4px 14px; border-radius: 20px; font-weight: 700; color: #856404;
        }
        .status-pending {
            background: #f8d7da; padding: 4px 14px; border-radius: 20px; font-weight: 700; color: #721c24;
        }
    </style>
""",
    unsafe_allow_html=True,
)

# ==================== BARRA LATERAL ====================
with st.sidebar:
    st.markdown(
        """
        <div style="text-align: center; margin-bottom: 30px;">
            <h2 style="color: #22c55e; font-weight: 900; margin:0;">🎓 CUN</h2>
            <p style="color: #94a3b8; font-size: 0.8rem; margin:0;">COE · Servicios Digitales</p>
        </div>
    """,
        unsafe_allow_html=True,
    )

    page = st.radio(
        label="Navegación",
        options=[
            "🏠 Portada",
            "⚙️ Flujo de Datos y Modelos",
            "🔴 Errores Identificados",
            "✅ Conclusiones",
        ],
        index=0,
        label_visibility="collapsed",
    )

    st.sidebar.markdown("---")
    st.sidebar.caption("👥 Hugo · David S. · Juan")
    st.sidebar.caption("📌 Presentación para David Barón")

# ==================== PÁGINAS ====================

# ---------- PÁGINA 1: PORTADA ----------
if page == "🏠 Portada":
    st.markdown(
        '<div class="main-title">📞 Sistema de Evaluación de Llamadas y Chats</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### *De la escucha reactiva al coaching predictivo*")
    st.markdown("---")

    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown(
            """
            <div class="card-cun" style="border-left-color: #0f172a;">
                <h3>🎯 El Problema que Resolvemos</h3>
                <ul>
                    <li><strong>Escala</strong>: No podemos escuchar el 100% de las llamadas manualmente.</li>
                    <li><strong>Objetividad</strong>: No tenemos métricas estandarizadas sobre los 7 pilares estratégicos.</li>
                    <li><strong>Capacitación</strong>: La retroalimentación a agentes se basa en corazonadas, no en datos masivos.</li>
                </ul>
            </div>
            <div class="card-cun" style="border-left-color: #22c55e; margin-top: 1.5rem;">
                <h3>💡 La Solución</h3>
                <p>Un sistema de <strong>4 modelos de Machine Learning</strong> que analiza el 100% de las interacciones, convierte el audio en datos accionables y se retroalimenta con el criterio humano de los coordinadores.</p>
            </div>
            <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 12px; margin-top: 1.5rem;">
                <h4 style="color: #0f172a;">🔄 Círculo Virtuoso</h4>
                <p style="font-size: 0.95rem; color: #334155;">
                <strong>Máquina califica</strong> → <strong>Coordinador revisa</strong> → <strong>Corrección humana</strong> → <strong>Data Science reentrena</strong> → <strong>Modelo mejora</strong> → <strong>Agentes venden más</strong>
                </p>
            </div>
        """,
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="card-dark">
                <h3>👥 Equipo Proyecto</h3>
                <p><strong>Hugo Alberto Bernal</strong><br>COE - Servicios Digitales</p>
                <p><strong>David Santiago Cerón</strong><br>COE - Servicios Digitales</p>
                <p><strong>Juan Francisco Garnica</strong><br>COE - Servicios Digitales</p>
                <hr style="border-color: #1e293b;">
                <p style="font-size: 0.85rem; color: #94a3b8;">Presentación para <strong style="color:white;">David Barón</strong></p>
            </div>
        """,
            unsafe_allow_html=True,
        )

# ---------- PÁGINA 2: FLUJO DE DATOS Y MODELOS ----------
elif page == "⚙️ Flujo de Datos y Modelos":
    st.markdown(
        '<div class="main-title">⚙️ Flujo de Datos y Modelos</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### El viaje de los datos: Desde el audio hasta el análisis")
    st.markdown("---")

    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(
            """
            <div style="background:#0f172a; color:white; padding:20px; border-radius:12px; text-align:center; height:120px;">
                <div style="font-size:2.5rem;">📞</div>
                <strong>Five9</strong><br><span style="font-size:0.7rem;">Audio de llamadas</span>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div style="display:flex; align-items:center; justify-content:center; height:120px; font-size:3rem; color:#22c55e;">➡️</div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div style="background:#0f172a; color:white; padding:20px; border-radius:12px; text-align:center; height:120px;">
                <div style="font-size:2.5rem;">🎙️</div>
                <strong>Whisper</strong><br><span style="font-size:0.7rem;">Audio → Texto JSON</span>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col4:
        st.markdown(
            """
            <div style="display:flex; align-items:center; justify-content:center; height:120px; font-size:3rem; color:#22c55e;">➡️</div>
        """,
            unsafe_allow_html=True,
        )
    with col5:
        st.markdown(
            """
            <div style="background:#22c55e; color:white; padding:20px; border-radius:12px; text-align:center; height:120px;">
                <div style="font-size:2.5rem;">🧠</div>
                <strong>4 Modelos</strong><br><span style="font-size:0.7rem;">Análisis completo</span>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("#### 🔍 Detalle Técnico (STT)")
    st.markdown(
        """
        - **Motor**: *Whisper Large V3* (OpenAI). Alta precisión en acentos latinos y jerga técnica.
        - **Salida**: Texto plano con marca de tiempo por cada frase, ID de agente, duración y resultado de venta (Sí/No).
    """
    )

    with st.expander("📝 Ejemplo de Transcripción (Mockup)"):
        st.code(
            """
        [00:00:15] Agente: Hola, ¿cómo estás? Te llamo para contarte sobre nuestra beca del 40%.
        [00:00:28] Cliente: Me interesa, pero he visto que la otra universidad tiene más programas virtuales.
        [00:00:45] Agente: Entiendo. Déjame contarte que nuestros convenios internacionales nos respaldan...
        """,
            language="text",
        )

    st.markdown("---")
    st.markdown(
        '<div class="section-title">🧠 Los 4 Modelos</div>', unsafe_allow_html=True
    )

    pilares = [
        "P1: Promesa",
        "P2: Beneficio",
        "P3: Respaldo",
        "P4: Beca",
        "P5: Diferenciación",
        "P6: Urgencia",
        "P7: Cierre",
    ]

    col1, col2 = st.columns(2)

    with col1:
        st.markdown(
            """
            <div class="card-cun">
                <h3>🏛️ Modelo 1: Estratégico (VSM)</h3>
                <p><em>Vector Space Model - Similitud semántica</em></p>
                <p>Representa los 7 pilares como vectores y calcula la similitud coseno con la transcripción.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        valores = [85, 45, 90, 30, 70, 95, 60]
        fig = go.Figure(
            data=go.Scatterpolar(
                r=valores,
                theta=pilares,
                fill="toself",
                marker=dict(color="#22c55e"),
                line=dict(color="#15803d", width=2),
            )
        )
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 100], color="#64748b"),
                angularaxis=dict(tickfont=dict(size=10, color="#0f172a")),
            ),
            showlegend=False,
            height=350,
            margin=dict(l=30, r=30, t=30, b=30),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<span class="badge-neg">🔴 Alerta: Pilares 2 (Beneficio) y 4 (Beca) por debajo del umbral</span>',
            unsafe_allow_html=True,
        )

    with col2:
        st.markdown(
            """
            <div class="card-cun">
                <h3>🤝 Modelo 2: Confianza (Teorema de Bayes)</h3>
                <p><em>Clasificador probabilístico de polaridad</em></p>
                <p>Estima P(Positivo|texto) y P(Negativo|texto) usando frecuencias de palabras.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=85,
                title={
                    "text": "Probabilidad de Sentimiento NEGATIVO",
                    "font": {"size": 14},
                },
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100], "tickfont": {"color": "#0f172a"}},
                    "bar": {"color": "#dc3545"},
                    "steps": [
                        {"range": [0, 40], "color": "#d4edda"},
                        {"range": [40, 70], "color": "#fff3cd"},
                        {"range": [70, 100], "color": "#f8d7da"},
                    ],
                    "threshold": {
                        "line": {"color": "#0f172a", "width": 4},
                        "thickness": 0.75,
                        "value": 85,
                    },
                },
            )
        )
        fig.update_layout(
            height=350,
            margin=dict(l=20, r=20, t=30, b=20),
            paper_bgcolor="rgba(0,0,0,0)",
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown(
            '<span class="badge-pos">📊 Confianza del clasificador: 92% (Margen alto)</span>',
            unsafe_allow_html=True,
        )

    col3, col4 = st.columns(2)

    with col3:
        st.markdown(
            """
            <div class="card-cun" style="border-left-color: #ffc107;">
                <h3>🔍 Modelo 3: Identificación</h3>
                <p><em>Diccionario comparativo de palabras clave</em></p>
                <p>Detecta entidades específicas (referidos, empresas, convenios) mediante patrones y reglas.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div style="background: #f1f5f9; padding: 15px; border-radius: 12px;">
                <span style="background: #22c55e; color: white; padding: 5px 14px; border-radius: 20px; margin: 4px; display: inline-block;">🏢 Convenio: Empresa X</span>
                <span style="background: #0f172a; color: white; padding: 5px 14px; border-radius: 20px; margin: 4px; display: inline-block;">👤 Referido: María G.</span>
                <span style="background: #dc3545; color: white; padding: 5px 14px; border-radius: 20px; margin: 4px; display: inline-block;">🏫 Competencia: Universidad Y</span>
                <span style="background: #ffc107; color: #0f172a; padding: 5px 14px; border-radius: 20px; margin: 4px; display: inline-block;">🎓 Beca Académica</span>
            </div>
        """,
            unsafe_allow_html=True,
        )
        st.caption(
            "La minería de reglas permite ajustar el diccionario sin reentrenar el modelo."
        )

    with col4:
        st.markdown(
            """
            <div class="card-cun" style="border-left-color: #ffc107;">
                <h3>📋 Modelo 4: Protocolo</h3>
                <p><em>Diccionario de objeciones + Adherencia al script</em></p>
                <p>Clasifica la objeción principal en 9 categorías y mide si el agente siguió el flujo esperado.</p>
            </div>
        """,
            unsafe_allow_html=True,
        )
        col_a, col_b = st.columns([3, 1])
        with col_a:
            st.progress(70, text="Adherencia al Script")
        with col_b:
            st.markdown(
                '<span class="badge-cun">🏷️ Económica</span>', unsafe_allow_html=True
            )

        with st.expander("📌 Ver 9 Categorías de Objeción"):
            st.markdown(
                """
            1. Económica / Costo  
            2. Falta de Tiempo  
            3. Competencia (otra universidad)  
            4. Desconfianza en la calidad  
            5. Indecisión / Necesito pensarlo  
            6. Distancia / Ubicación  
            7. Familiar / Apoyo familiar  
            8. Académica (programa no encaja)  
            9. Genérica / Otra
            """
            )

# ---------- PÁGINA 3: ERRORES IDENTIFICADOS ----------
elif page == "🔴 Errores Identificados":
    st.markdown(
        '<div class="main-title">🔴 Errores Identificados y Soluciones</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### *Análisis de los principales hallazgos en el proceso*")
    st.markdown("---")

    # Error 1
    st.markdown(
        """
        <div class="error-card">
            <h4>❌ Error 1: Cédulas vacías en COE.venta_contact_nuevo</h4>
            <p><strong>Problema:</strong> El campo <code>Cedula</code> queda como <code>'N/A'</code> porque el asesor no tiene cédula registrada en Kactus al momento del procesamiento.</p>
            <p><strong>Solución bidireccional:</strong></p>
            <ul>
                <li><strong>Hacia atrás</strong> (actualización histórica):</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.code(
        """
        UPDATE COE.venta_contact_nuevo
        SET Cedula = ?, Asesor = ?
        WHERE Correo = ? AND Fecha = ? AND Hora_Llamada = ? AND Cedula = 'N/A'
        """,
        language="sql",
    )
    st.markdown(
        """
        <ul>
            <li><strong>Hacia adelante</strong>: El script ya consulta Kactus y asigna la cédula correcta desde el inicio.</li>
        </ul>
        <p><span class="status-solved">✅ ESTADO: SOLUCIONADO</span></p>
        <p><strong>Acciones realizadas:</strong> Las cédulas se actualizan correctamente en ambos sentidos. Los nuevos registros ya llegan con cédula.</p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Error 2
    st.markdown(
        """
        <div class="error-card">
            <h4>❌ Error 2: Nulos en columna <code>fuente</code> de la tabla de chats</h4>
            <p><strong>Problema:</strong> La tabla <code>[ZOHO].[CRM].[Transcripciones_de_chat]</code> tiene registros con <code>fuente</code> NULL, 'NULL' (string) o vacío, lo que impide saber el origen del chat.</p>
            <p><strong>Consulta de detección:</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.code(
        """
        SELECT Visitor_phone_number, fuente
        FROM [ZOHO].[CRM].[Transcripciones_de_chat]
        WHERE fuente IS NULL
           OR UPPER(LTRIM(RTRIM(fuente))) = 'NULL'
           OR LTRIM(RTRIM(fuente)) = '';
        """,
        language="sql",
    )
    st.markdown(
        """
        <p><strong>Resultado:</strong> Se encontraron registros sin fuente.</p>
        <p><strong>Solución propuesta:</strong></p>
        <ul>
            <li>Revisar el proceso de captura de chats en ZOHO para garantizar que siempre se registre la fuente (web, WhatsApp, Facebook, etc.).</li>
            <li>Mientras tanto, etiquetar estos registros como "Fuente desconocida" en los reportes.</li>
        </ul>
        <p><span class="status-progress">🟡 ESTADO: EN PROCESO</span></p>
        <p><strong>Acciones en curso:</strong></p>
        <ul>
            <li>Se agenda reunión con <strong>Analista de Calidad • Servicio</strong> para evaluar si es posible rastrear los nulos y determinar su origen.</li>
            <li>Por ahora, estos registros no se mostrarán en el tablero para evitar distorsiones.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("---")

    # Error 3
    st.markdown(
        """
        <div class="error-card">
            <h4>❌ Error 3: Correos de asesores con cargos no comerciales</h4>
            <p><strong>Problema:</strong> En <code>COE.venta_contact_nuevo</code> hay registros de asesores con cargos que no están directamente relacionados con la venta (auxiliares de vinculaciones, rematrícula, cartera, etc.), distorsionando los indicadores.</p>
            <p><strong>Consulta de detección:</strong></p>
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.code(
        """
        SELECT
            h.CARGO,
            COUNT(*) AS Cantidad
        FROM COE.venta_contact_nuevo v
        LEFT JOIN kactus.historico_contratos h
            ON UPPER(LTRIM(RTRIM(v.Correo))) = UPPER(LTRIM(RTRIM(h.EMAIL_INSTITUCIONAL)))
        WHERE v.Fecha BETWEEN '2026-01-01' AND CAST(GETDATE() AS DATE)
        GROUP BY h.CARGO
        ORDER BY Cantidad DESC;
        """,
        language="sql",
    )
    st.markdown(
        """
        <p><strong>Resultados obtenidos:</strong></p>
        """,
        unsafe_allow_html=True,
    )
    data_cargos = {
        "CARGO": [
            "AUXILIAR GESTOR VINCULACIONES",
            "AUXILIAR GESTOR REMATRICULA",
            "AUXILIAR GESTOR DE CARTERA",
            "GESTOR DE VINCULACIONES",
            "ASESOR CONTACT CENTER",
            "DOC AUX T&T/V/TC/IDIOMAS/PROYECTOS ACADE",
            "AUXILIAR GESTOR DE PERMANENCIA",
            "NULL",
            "AUXILIAR VINCULACIONES BE",
            "DIRECTOR SERVICIOS DIGITALES",
            "ARTICULADOR ESTRATEGICO DE PLANEACION",
            "APRENDIZ",
            "ESPECIALISTA DE ANALITICA",
            "AUXILIAR GESTOR ESTABILIDAD",
            "CATALIZADOR FORMACION INTERNA",
            "MENTOR",
            "ANALISTA DATA MARSHALL",
        ],
        "Cantidad": [
            277514,
            32308,
            18821,
            6426,
            3850,
            1930,
            1772,
            169,
            73,
            48,
            18,
            8,
            8,
            8,
            7,
            2,
            1,
        ],
    }
    df_cargos = pd.DataFrame(data_cargos)
    st.dataframe(df_cargos, use_container_width=True)

    st.markdown(
        """
        <p><strong>Solución propuesta:</strong></p>
        <ol>
            <li><strong>Filtrar del análisis</strong> todos los cargos que no tengan relación directa con la venta (cargos administrativos, docentes, directivos, aprendices, etc.).</li>
            <li><strong>Crear un modelo exclusivo para REMATRICULA</strong>, ya que este proceso tiene condiciones y métricas diferentes a la venta de primer contacto.</li>
        </ol>
        <p><span class="status-progress">🟡 ESTADO: EN PROCESO</span></p>
        <p><strong>Acciones en curso:</strong></p>
        <ul>
            <li>Se inicia la limpieza de cargos: se identifican y depuran los que no corresponden a ventas de entrada.</li>
            <li>Consulta de referencia para revisar la tabla filtrada:</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )
    st.code(
        """
        SELECT * FROM COE.venta_contact_nuevo
        WHERE CARGO IN ('ASESOR CONTACT CENTER', 'GESTOR DE VINCULACIONES', ...)  -- cargos comerciales
        """,
        language="sql",
    )
    st.markdown(
        """
        <ul>
            <li>Se está diseñando la bandera para detectar REMATRICULA por palabras clave.</li>
        </ul>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        '<div class="section-title">🎯 Propuesta: Modelo Exclusivo para REMATRÍCULA</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        """
        <div class="card-cun" style="border-left-color: #ffc107;">
            <p><strong>Justificación:</strong> REMATRICULA tiene condiciones y métricas diferentes a la venta de primer contacto.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    data_comparativa = {
        "Aspecto": [
            "Pilares evaluados",
            "Métricas",
            "CALIFICACIÓN TOTAL",
            "Objeción principal",
        ],
        "Modelo actual (ventas)": [
            "P1-P7 (promesa, beneficio, entregables, garantía, regalos, precio, cierre)",
            "M1 (estratégico), M2 (confianza), M3 (identificación), M4 (protocolo)",
            "60% M1 + 15% M2 + 15% M3 + 10% M4",
            "Económica, tiempo, competencia, etc.",
        ],
        "Modelo REMATRICULA": [
            "Fidelización, Satisfacción previa, Disponibilidad de cupos, Facilidades de pago, Cierre de matrícula",
            "M2 (confianza), M4 (protocolo), M5 (historial académico), M6 (gestión de documentos)",
            "40% Fidelización + 20% Satisfacción + 20% Cupos + 20% Pago",
            "Carga académica, Horarios, Costo, Trámites pendientes",
        ],
    }
    df_comparativa = pd.DataFrame(data_comparativa)
    st.table(df_comparativa)

    st.markdown(
        """
        <p><strong>Implementación:</strong></p>
        <ul>
            <li>Bandera para detectar REMATRICULA (por cargo o palabras clave: "rematrícula", "continuar", "siguiente semestre").</li>
            <li>Resultados en misma tabla con campo <code>Tipo_Proceso</code> ('Venta' o 'Rematricula').</li>
        </ul>
        <p><strong>Beneficio:</strong> Indicadores más precisos para cada tipo de gestión.</p>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="background: #e2e8f0; padding: 1.5rem; border-radius: 12px;">
            <h4 style="color: #0f172a;">📌 Resumen de Estados</h4>
            <ul>
                <li><span class="status-solved">✅ SOLUCIONADO</span> Cédulas vacías</li>
                <li><span class="status-progress">🟡 EN PROCESO</span> Nulos en fuente (reunión con Analista de Calidad)</li>
                <li><span class="status-progress">🟡 EN PROCESO</span> Limpieza de cargos y modelo REMATRICULA</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )

# ---------- PÁGINA 4: CONCLUSIONES ----------
else:
    st.markdown(
        '<div class="main-title">✅ Conclusiones y Análisis de Resultados</div>',
        unsafe_allow_html=True,
    )
    st.markdown("### *Análisis de indicadores clave - Enero a Junio 2026*")
    st.markdown("---")

    # Datos de la tabla
    data_conclusiones = {
        "Indicador": [
            "Promesa",
            "Beneficio",
            "Garantía",
            "Regalos",
            "Precio",
            "Cierre",
        ],
        "Promedio Ene-Jun 2026": [43.54, 51.34, 48.86, 36.37, 41.94, 51.63],
        "Tendencia": [
            "➖ Estable",
            "⬇️ Descendente",
            "➖ Estable",
            "⬇️ Leve descenso",
            "➖ Estable",
            "⬇️ Descendente",
        ],
        "Análisis": [
            "Se mantiene entre el 43% y el 44% durante todo el semestre. No presenta variaciones importantes, lo que indica consistencia, aunque existe margen para incrementar su utilización.",
            "Inicia en **52,70%** y finaliza en **50,07%**, con una disminución de **2,63 puntos porcentuales**. Es el indicador que más cae durante el semestre, evidenciando una menor comunicación de los beneficios del programa.",
            "Mantiene un comportamiento muy uniforme, cercano al 49%, lo que refleja una adecuada utilización de argumentos de confianza y respaldo.",
            "Es el indicador con menor promedio del semestre. Además de ser el menos utilizado, muestra una ligera disminución entre enero y junio, representando una oportunidad clara de mejora.",
            "Permanece alrededor del 42% durante todo el período. Aunque no presenta una tendencia negativa marcada, tampoco evidencia mejoras sostenidas en el uso de argumentos relacionados con costos o facilidades de pago.",
            "Es el indicador con el mayor promedio general; sin embargo, disminuye de **51,84%** en enero a **50,71%** en junio. La reducción podría estar asociada con la caída en los argumentos de beneficio, afectando la efectividad del cierre comercial.",
        ],
    }
    df_conclusiones = pd.DataFrame(data_conclusiones)

    # Mostrar tabla con estilo mejorado
    st.dataframe(
        df_conclusiones,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Indicador": st.column_config.TextColumn("Indicador", width="small"),
            "Promedio Ene-Jun 2026": st.column_config.NumberColumn(
                "Promedio", format="%.2f%%", width="small"
            ),
            "Tendencia": st.column_config.TextColumn("Tendencia", width="small"),
            "Análisis": st.column_config.TextColumn("Análisis", width="large"),
        },
    )

    st.markdown("---")
    st.markdown("### 📊 Resumen de Hallazgos")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown(
            """
            <div style="background: #dc3545; color: white; padding: 1.2rem; border-radius: 12px; text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 900;">36.37%</div>
                <div style="font-size: 0.9rem;">🔴 <strong>Regalos</strong> (más bajo)</div>
                <div style="font-size: 0.8rem; margin-top: 5px;">Oportunidad de mejora clara</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col2:
        st.markdown(
            """
            <div style="background: #ffc107; color: #0f172a; padding: 1.2rem; border-radius: 12px; text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 900;">-2.63 p.p.</div>
                <div style="font-size: 0.9rem;">🟡 <strong>Beneficio</strong> (más descendente)</div>
                <div style="font-size: 0.8rem; margin-top: 5px;">Caída más pronunciada</div>
            </div>
        """,
            unsafe_allow_html=True,
        )
    with col3:
        st.markdown(
            """
            <div style="background: #22c55e; color: white; padding: 1.2rem; border-radius: 12px; text-align: center;">
                <div style="font-size: 1.8rem; font-weight: 900;">51.63%</div>
                <div style="font-size: 0.9rem;">🟢 <strong>Cierre</strong> (más alto)</div>
                <div style="font-size: 0.8rem; margin-top: 5px;">Aunque está descendiendo</div>
            </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown("---")
    st.markdown("### 🎯 Acciones Recomendadas")

    st.markdown(
        """
        <div style="background: #f1f5f9; padding: 1.5rem; border-radius: 12px;">
            <ul>
                <li><strong>Beneficio (↓ 2.63 p.p.)</strong>: Reforzar capacitación en comunicación de beneficios y ventajas del programa.</li>
                <li><strong>Regalos (36.37%)</strong>: Implementar estrategias para destacar bonos, descuentos y beneficios extra durante la llamada.</li>
                <li><strong>Cierre (↓)</strong>: Alinear la estrategia de cierre con la comunicación de beneficios para recuperar efectividad.</li>
                <li><strong>Promesa, Garantía y Precio</strong>: Mantener la consistencia y buscar pequeñas mejoras para elevar el promedio general.</li>
            </ul>
            <p style="margin-top: 1rem;"><strong>Conclusión general:</strong> El semestre muestra fortalezas en Cierre y Garantía, pero oportunidades claras en Beneficio y Regalos. Se recomienda un plan de acción focalizado para revertir las tendencias negativas.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("---")
    st.markdown(
        """
        <div style="text-align: center; padding: 1.5rem; background: #0f172a; border-radius: 12px; color: white;">
            <p style="font-size: 1.2rem; font-weight: 700; margin: 0;">
                De la escucha reactiva al coaching predictivo, impulsado por datos y retroalimentación humana.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )
