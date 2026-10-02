import streamlit as st
import pandas as pd
import requests
from datetime import datetime
import os

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="Naviermetrics - Centro de Mando",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# ESTILOS (Negro + Azules + Blanco)
# ==========================================
st.markdown("""
<style>
    .stApp {
        background-color: #0B1120;
        color: #E2E8F0;
    }
    [data-testid="stSidebar"] {
        background-color: #020617;
        border-right: 1px solid #1E3A8A;
    }
    .main-title {
        font-size: 42px;
        font-weight: 800;
        color: #60A5FA;
        margin-bottom: 0px;
    }
    .subtitle {
        font-size: 18px;
        color: #94A3B8;
        margin-top: 4px;
        margin-bottom: 25px;
    }
    .section-title {
        font-size: 24px;
        font-weight: 700;
        color: #93C5FD;
        margin-top: 10px;
        margin-bottom: 15px;
    }
    .module-title {
        font-size: 16px;
        font-weight: 700;
        color: #F1F5F9;
        margin-top: 12px;
        margin-bottom: 6px;
    }
    .module-desc {
        font-size: 13px;
        color: #94A3B8;
        margin-bottom: 12px;
    }
    .stButton > button {
        background: linear-gradient(90deg, #1E40AF, #3B82F6);
        color: white;
        border: none;
        border-radius: 10px;
        font-weight: 600;
    }
    .stButton > button:hover {
        background: linear-gradient(90deg, #2563EB, #60A5FA);
        box-shadow: 0 0 20px rgba(59, 130, 246, 0.5);
    }
    div[data-testid="stMetricValue"] {
        color: #60A5FA;
        font-size: 26px;
    }
    .success-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #052E16;
        border: 1px solid #16A34A;
        color: #BBF7D0;
    }
    .alert-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #450A0A;
        border: 1px solid #DC2626;
        color: #FECACA;
    }
    .info-box {
        padding: 16px;
        border-radius: 12px;
        background-color: #0C1A3A;
        border: 1px solid #1E40AF;
        color: #BFDBFE;
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# GREEN-API
# ==========================================
def cargar_green_api():
    try:
        cfg = st.secrets["green_api"]
        return {
            "api_url": str(cfg["api_url"]).strip().rstrip("/"),
            "instance_id": str(cfg["instance_id"]).strip(),
            "api_token": str(cfg["api_token"]).strip()
        }
    except Exception:
        return None

GREEN_API = cargar_green_api()
VIDEO_URL = "https://www.youtube.com/watch?v=5_dFmyQN3TY"
NUMERO_WHATSAPP = "18092728026"

def obtener_estado_green_api():
    if GREEN_API is None:
        return {"ok": False, "estado": "configuracion_no_encontrada", "mensaje": "No se encontró Green-API en secrets."}
    url = f"{GREEN_API['api_url']}/waInstance{GREEN_API['instance_id']}/getStateInstance/{GREEN_API['api_token']}"
    try:
        response = requests.get(url, timeout=15)
        data = response.json() if response.status_code == 200 else {}
        estado = data.get("stateInstance")
        if response.status_code == 200:
            return {"ok": True, "estado": estado, "mensaje": f"Estado: {estado}"}
        return {"ok": False, "estado": estado, "mensaje": f"HTTP {response.status_code}"}
    except Exception as e:
        return {"ok": False, "estado": "error", "mensaje": str(e)}

def enviar_alerta_whatsapp(numero, mensaje):
    if GREEN_API is None:
        return {"ok": False, "mensaje": "Green-API no configurada."}
    numero_limpio = "".join(c for c in str(numero) if c.isdigit())
    if not numero_limpio:
        return {"ok": False, "mensaje": "Número inválido."}
    estado = obtener_estado_green_api()
    if not estado["ok"] or estado["estado"] != "authorized":
        return {"ok": False, "mensaje": estado["mensaje"]}
    url = f"{GREEN_API['api_url']}/waInstance{GREEN_API['instance_id']}/sendMessage/{GREEN_API['api_token']}"
    payload = {"chatId": f"{numero_limpio}@c.us", "message": mensaje}
    try:
        response = requests.post(url, json=payload, headers={"Content-Type": "application/json"}, timeout=20)
        if response.status_code == 200:
            return {"ok": True, "mensaje": "Mensaje enviado correctamente.", "data": response.json()}
        return {"ok": False, "mensaje": f"HTTP {response.status_code}: {response.text}"}
    except Exception as e:
        return {"ok": False, "mensaje": str(e)}

# ==========================================
# SESSION STATE
# ==========================================
if "pagina_actual" not in st.session_state:
    st.session_state.pagina_actual = "home"
if "api_status" not in st.session_state:
    st.session_state.api_status = None

# ==========================================
# SIDEBAR
# ==========================================
with st.sidebar:
    logo_path = "ChatGPT Image 1 oct 2026, 02_14_23 a.m..png"
    if os.path.exists(logo_path):
        st.image(logo_path, use_container_width=True)
    else:
        st.markdown("### 🏗️ Naviermetrics")

    st.markdown("---")
    st.markdown("### ⚙️ Configuración")
    st.markdown(f"**WhatsApp:** `{NUMERO_WHATSAPP}`")

    if st.button("🔌 Verificar Green-API"):
        st.session_state.api_status = obtener_estado_green_api()

    if st.session_state.api_status:
        if st.session_state.api_status["ok"] and st.session_state.api_status["estado"] == "authorized":
            st.success("GREEN-API AUTORIZADA")
        else:
            st.warning(st.session_state.api_status["mensaje"])

    st.markdown("---")
    if st.button("🏠 Volver al Inicio"):
        st.session_state.pagina_actual = "home"
        st.rerun()

# ==========================================
# PÁGINA HOME
# ==========================================
if st.session_state.pagina_actual == "home":

    st.markdown('<div class="main-title">Naviermetrics</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Centro de Mando Integral para Proyectos de Construcción — RD · PR · Panamá</div>', unsafe_allow_html=True)

    st.markdown('<div class="section-title">📹 Monitoreo en Vivo e Ingesta Analítica</div>', unsafe_allow_html=True)
    st.video(VIDEO_URL)
    st.caption("Feed de demostración. Aquí irá Digifort cuando tengas la licencia.")

    st.markdown("---")
    st.markdown('<div class="section-title">🚀 Módulos del Centro de Mando</div>', unsafe_allow_html=True)

    modulos = [
        {"id": "overview", "titulo": "Dashboard Principal", "desc": "KPIs globales, avance y alertas críticas", "img": "images/01_overview.png"},
        {"id": "monitoreo", "titulo": "Monitoreo Visual", "desc": "Cámaras, analytics y evidencias Digifort", "img": "images/02_monitoreo.png"},
        {"id": "financiero", "titulo": "Módulo Financiero", "desc": "Presupuesto, flujo de caja y gastos", "img": "images/03_financiero.png"},
        {"id": "contratistas", "titulo": "Contratistas", "desc": "Control de proveedores y desempeño", "img": "images/04_contratistas.png"},
        {"id": "legal", "titulo": "Legal & Cumplimiento", "desc": "Leyes RD/PR/Panamá + alertas legales", "img": "images/05_legal.png"},
        {"id": "comercial", "titulo": "Comercial / Avances", "desc": "Reportes visuales para stakeholders", "img": "images/06_comercial.png"},
        {"id": "materiales", "titulo": "Control de Materiales", "desc": "Inventario y consumo en obra", "img": "images/07_materiales.png"},
        {"id": "talento", "titulo": "Talento Humano", "desc": "Asistencia, evaluaciones y contratos", "img": "images/08_talento.png"},
        {"id": "reportes", "titulo": "Reportes PDF", "desc": "Informes profesionales descargables", "img": "images/09_reportes.png"},
        {"id": "contratos", "titulo": "Plantillas de Contratos", "desc": "Trabajo vs Prestación de Servicios", "img": "images/10_contratos.png"},
    ]

    for i in range(0, len(modulos), 5):
        cols = st.columns(5)
        for j, col in enumerate(cols):
            if i + j < len(modulos):
                m = modulos[i + j]
                with col:
                    if os.path.exists(m["img"]):
                        st.image(m["img"], use_container_width=True)
                    else:
                        st.markdown(f"<div style='height:140px;background:#1E293B;border-radius:12px;display:flex;align-items:center;justify-content:center;color:#64748B;'>Imagen</div>", unsafe_allow_html=True)
                    
                    st.markdown(f"<div class='module-title'>{m['titulo']}</div>", unsafe_allow_html=True)
                    st.markdown(f"<div class='module-desc'>{m['desc']}</div>", unsafe_allow_html=True)
                    
                    if st.button("Entrar →", key=f"btn_{m['id']}", use_container_width=True):
                        st.session_state.pagina_actual = m["id"]
                        st.rerun()

# ==========================================
# MÓDULOS
# ==========================================
else:
    pagina = st.session_state.pagina_actual

    if st.button("← Volver al Inicio"):
        st.session_state.pagina_actual = "home"
        st.rerun()

    st.markdown("---")

    # -------------------- LEGAL --------------------
    if pagina == "legal":
        st.markdown('<div class="main-title">Legal & Cumplimiento</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Leyes de Construcción y Conexas — RD · PR · Panamá</div>', unsafe_allow_html=True)

        leyes = {
            "DO": [
                {"codigo": "Ley 160-21", "nombre": "Ministerio de Vivienda, Hábitat y Edificaciones (MIVED)", "categoria": "Institucional", "riesgo": "Alto", "resumen": "Crea el MIVED y establece el marco rector de vivienda y edificaciones en RD."},
                {"codigo": "Código de Construcción RD", "nombre": "Código de Construcción de la República Dominicana", "categoria": "Código Técnico", "riesgo": "Crítico", "resumen": "Requisitos mínimos de diseño, seguridad estructural, sismo y habitabilidad."},
                {"codigo": "Ley 687-82", "nombre": "Reglamentación Técnica de Ingeniería y Arquitectura", "categoria": "Técnico", "riesgo": "Alto", "resumen": "Sistema de reglamentos técnicos para proyectos de ingeniería y arquitectura."},
                {"codigo": "Ley 16-92", "nombre": "Código de Trabajo", "categoria": "Laboral", "riesgo": "Alto", "resumen": "Regula relaciones laborales, jornadas, despidos y derechos de los trabajadores."},
                {"codigo": "Ley 64-00", "nombre": "Ley General sobre Medio Ambiente y Recursos Naturales", "categoria": "Ambiental", "riesgo": "Alto", "resumen": "Obligaciones ambientales, estudios de impacto y permisos."},
                {"codigo": "Ley 87-01", "nombre": "Sistema Dominicano de Seguridad Social", "categoria": "Laboral/SS", "riesgo": "Medio", "resumen": "Aportes obligatorios a la Seguridad Social."},
            ],
            "PR": [
                {"codigo": "PRBC 2018", "nombre": "Puerto Rico Building Code 2018 (Act 109-2018)", "categoria": "Código Técnico", "riesgo": "Crítico", "resumen": "Código de construcción basado en IBC 2018. Incluye requisitos sísmicos y de huracanes."},
                {"codigo": "Ley 161-2009", "nombre": "Reforma del Proceso de Permisos (OGPe)", "categoria": "Permisos", "riesgo": "Crítico", "resumen": "Crea la Oficina de Gerencia de Permisos y unifica trámites de construcción."},
                {"codigo": "Ley 16-1975", "nombre": "Ley de Seguridad y Salud en el Trabajo (PROSHA)", "categoria": "Seguridad", "riesgo": "Crítico", "resumen": "Normas de seguridad ocupacional equivalentes o superiores a OSHA federal."},
                {"codigo": "Ley 416-2004", "nombre": "Ley de Política Pública Ambiental", "categoria": "Ambiental", "riesgo": "Alto", "resumen": "Marco ambiental de Puerto Rico + requisitos EPA (NPDES, etc.)."},
                {"codigo": "Ley 80-1976", "nombre": "Ley de Despido Injustificado", "categoria": "Laboral", "riesgo": "Alto", "resumen": "Protección contra despidos sin justa causa e indemnizaciones."},
                {"codigo": "Ley 379-1948", "nombre": "Jornada de Trabajo y Horas Extras", "categoria": "Laboral", "riesgo": "Medio", "resumen": "Jornada diaria de 8 horas; extras a partir de la 9ª hora del día."},
            ],
            "PA": [
                {"codigo": "Ley 67-2015", "nombre": "Medidas de Seguridad en la Industria de la Construcción", "categoria": "Seguridad", "riesgo": "Crítico", "resumen": "Obliga a designar Oficial(es) de Seguridad Ocupacional según monto y riesgo de la obra."},
                {"codigo": "Decreto 2-2008", "nombre": "Seguridad, Salud e Higiene en la Construcción", "categoria": "Seguridad", "riesgo": "Crítico", "resumen": "Reglamento detallado de seguridad en obras de construcción."},
                {"codigo": "Acuerdo 281/2016 + 110/2025", "nombre": "Permisos de Construcción (DOYC)", "categoria": "Permisos", "riesgo": "Crítico", "resumen": "Proceso de permisos de construcción en el Distrito de Panamá. Vigencia 5 años."},
                {"codigo": "Ley 15-1959", "nombre": "Ejercicio de Ingeniería y Arquitectura (JTIA)", "categoria": "Profesional", "riesgo": "Alto", "resumen": "Regula el ejercicio profesional y crea la Junta Técnica de Ingeniería y Arquitectura."},
                {"codigo": "Ley 226-2021", "nombre": "Normas de Diseño y Edificación", "categoria": "Código Técnico", "riesgo": "Alto", "resumen": "Marco general de normas de diseño y edificación en Panamá."},
                {"codigo": "Código de Trabajo", "nombre": "Código de Trabajo de Panamá (disposiciones de construcción)", "categoria": "Laboral", "riesgo": "Alto", "resumen": "Normas laborales especiales para la actividad de construcción."},
            ]
        }

        pais = st.selectbox("Selecciona el país", ["República Dominicana", "Puerto Rico", "Panamá"])
        codigo_pais = {"República Dominicana": "DO", "Puerto Rico": "PR", "Panamá": "PA"}[pais]

        st.markdown(f"### Leyes vigentes en **{pais}**")

        for ley in leyes[codigo_pais]:
            color = {"Crítico": "#DC2626", "Alto": "#F59E0B", "Medio": "#3B82F6"}.get(ley["riesgo"], "#94A3B8")
            with st.expander(f"**{ley['codigo']}** — {ley['nombre']}  |  Riesgo: {ley['riesgo']}"):
                st.markdown(f"**Categoría:** {ley['categoria']}")
                st.markdown(f"**Resumen:** {ley['resumen']}")
                st.markdown(f"<span style='color:{color}; font-weight:700;'>Nivel de riesgo: {ley['riesgo']}</span>", unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("### 🚨 Generar Alerta Legal")

        col1, col2 = st.columns(2)
        with col1:
            tipo_alerta = st.selectbox("Tipo de alerta", [
                "Vencimiento de permiso de construcción",
                "Falta de Oficial de Seguridad",
                "Incumplimiento de jornada laboral",
                "Ausencia de EPP detectada",
                "Vencimiento de póliza / fianza",
                "Requisito ambiental pendiente"
            ])
        with col2:
            dias = st.number_input("Días restantes / impacto", min_value=0, value=7)

        if st.button("Enviar Alerta Legal por WhatsApp", type="primary"):
            mensaje = (
                f"⚖️ *Naviermetrics — ALERTA LEGAL*\n\n"
                f"País: {pais}\n"
                f"Tipo: {tipo_alerta}\n"
                f"Días / impacto: {dias}\n\n"
                f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
                f"Se requiere revisión inmediata del abogado del proyecto.\n"
                f"Sistema: Naviermetrics Legal Module"
            )
            resultado = enviar_alerta_whatsapp(NUMERO_WHATSAPP, mensaje)
            if resultado["ok"]:
                st.markdown('<div class="success-box"><b>✓ Alerta legal enviada por WhatsApp</b></div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="alert-box"><b>Error:</b> {resultado["mensaje"]}</div>', unsafe_allow_html=True)

    # -------------------- CONTRATOS --------------------
    elif pagina == "contratos":
        st.markdown('<div class="main-title">Plantillas de Contratos</div>', unsafe_allow_html=True)
        st.markdown('<div class="subtitle">Contrato de Trabajo vs Contrato de Prestación de Servicios</div>', unsafe_allow_html=True)

        tipo_contrato = st.radio(
            "Tipo de contrato",
            ["Contrato de Trabajo (relación de dependencia)", "Contrato de Prestación de Servicios (independiente)"],
            horizontal=True
        )

        pais_contrato = st.selectbox("País del contrato", ["República Dominicana", "Puerto Rico", "Panamá"])

        st.markdown("---")
        col1, col2 = st.columns(2)
        with col1:
            nombre = st.text_input("Nombre completo")
            cedula = st.text_input("Cédula / ID")
            cargo = st.text_input("Cargo o servicio", value="Oficial de Seguridad")
        with col2:
            fecha_inicio = st.date_input("Fecha de inicio")
            fecha_fin = st.date_input("Fecha de terminación (opcional)")
            salario = st.number_input("Salario / Honorarios", min_value=0.0, value=25000.0, step=1000.0)

        if st.button("Generar Plantilla", type="primary"):
            if "Trabajo" in tipo_contrato:
                plantilla = f"""
CONTRATO DE TRABAJO

Entre [EMPRESA] y {nombre} (Cédula/ID: {cedula})

1. Objeto: Prestación de servicios como {cargo} bajo subordinación.
2. País: {pais_contrato}
3. Remuneración: {salario:,.2f}
4. Inicio: {fecha_inicio.strftime('%d/%m/%Y')}
5. Terminación: Se regirá por el Código de Trabajo de {pais_contrato}.
6. Seguridad Social: Aportes obligatorios a cargo de la empresa.

Firmas:
_________________________          _________________________
Empresa                            Trabajador
"""
            else:
                plantilla = f"""
CONTRATO DE PRESTACIÓN DE SERVICIOS

Entre [EMPRESA] y {nombre} (Cédula/ID: {cedula})

1. Objeto: Servicios independientes de {cargo} (sin subordinación).
2. País: {pais_contrato}
3. Honorarios: {salario:,.2f} (contra factura)
4. Inicio: {fecha_inicio.strftime('%d/%m/%Y')}
5. Este contrato NO genera relación laboral ni derecho a prestaciones.
6. El Prestador es responsable de su propia seguridad y herramientas.

Firmas:
_________________________          _________________________
Empresa                            Prestador
"""
            st.code(plantilla)
            st.download_button("📥 Descargar plantilla", plantilla, file_name="contrato.txt")

    # -------------------- OTROS MÓDULOS --------------------
    else:
        st.markdown(f'<div class="main-title">{pagina.upper()}</div>', unsafe_allow_html=True)
        st.info(f"El módulo **{pagina}** está en construcción.")
