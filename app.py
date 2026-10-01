import inspect
import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# ==========================================
# CONFIGURACIÓN DE LA PÁGINA
# ==========================================

st.set_page_config(
    page_title="Naviermetrics - Centro de Mando",
    layout="wide"
)

# Colocación del logo en la parte superior izquierda de la barra lateral
nombre_logo = "ChatGPT Image 1 oct 2026, 02_14_23 a.m..png"
st.sidebar.image(nombre_logo, use_container_width=True)

# ============================================================
# ESTILOS
# ============================================================

st.markdown("""
<style>
.main-title {
    font-size: 38px;
    font-weight: 800;
    color: #1E3A8A;
    margin-bottom: 0px;
}
.subtitle {
    font-size: 17px;
    color: #64748B;
    margin-top: 0px;
    margin-bottom: 25px;
}
.section-title {
    font-size: 25px;
    font-weight: 700;
    margin-top: 20px;
    margin-bottom: 10px;
}
.alert-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #FEF2F2;
    border: 1px solid #FECACA;
    color: #7F1D1D;
    margin-top: 15px;
    margin-bottom: 15px;
}
.success-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #F0FDF4;
    border: 1px solid #BBF7D0;
    color: #14532D;
    margin-top: 15px;
    margin-bottom: 15px;
}
.info-box {
    padding: 18px;
    border-radius: 10px;
    background-color: #EFF6FF;
    border: 1px solid #BFDBFE;
    color: #1E3A8A;
    margin-top: 15px;
    margin-bottom: 15px;
}
div[data-testid="stMetricValue"] {
    font-size: 28px;
}
</style>
""", unsafe_allow_html=True)


# ============================================================
# GREEN-API
# ============================================================

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


# ============================================================
# SESSION STATE
# ============================================================

for clave, valor in {
    "alerta_disparada": False,
    "log_alertas": [],
    "api_status": None,
    "ultimo_resultado": None,
}.items():
    if clave not in st.session_state:
        st.session_state[clave] = valor


# ============================================================
# ESTADO GREEN-API
# ============================================================

def obtener_estado_green_api():

    if GREEN_API is None:
        return {
            "ok": False,
            "estado": "configuracion_no_encontrada",
            "mensaje": "No se encontró la configuración de Green-API en st.secrets."
        }

    url = (
        f"{GREEN_API['api_url']}"
        f"/waInstance{GREEN_API['instance_id']}"
        f"/getStateInstance/{GREEN_API['api_token']}"
    )

    try:
        response = requests.get(url, timeout=15)

        try:
            data = response.json()
        except Exception:
            data = {}

        estado = data.get("stateInstance") if isinstance(data, dict) else None

        if response.status_code == 200:
            return {
                "ok": True,
                "estado": estado,
                "mensaje": f"Estado Green-API: {estado}"
            }

        return {
            "ok": False,
            "estado": estado,
            "mensaje": f"Green-API respondió HTTP {response.status_code}: {response.text}"
        }

    except requests.exceptions.Timeout:
        return {"ok": False, "estado": "timeout",
                "mensaje": "Tiempo de espera agotado al conectar con Green-API."}

    except requests.exceptions.ConnectionError:
        return {"ok": False, "estado": "connection_error",
                "mensaje": "No fue posible conectar con Green-API."}

    except Exception as e:
        return {"ok": False, "estado": "error",
                "mensaje": f"Error inesperado: {str(e)}"}


# ============================================================
# ENVIAR WHATSAPP
# ============================================================

def enviar_alerta_whatsapp(numero, mensaje):

    if GREEN_API is None:
        return {"ok": False, "mensaje": "Green-API no está configurada."}

    numero_limpio = "".join(c for c in str(numero) if c.isdigit())

    if not numero_limpio:
        return {"ok": False, "mensaje": "Número de WhatsApp inválido."}

    estado = obtener_estado_green_api()

    if not estado["ok"]:
        return {"ok": False, "mensaje": estado["mensaje"]}

    if estado["estado"] != "authorized":
        return {
            "ok": False,
            "mensaje": (
                "La instancia Green-API no está autorizada. "
                f"Estado actual: {estado['estado']}"
            )
        }

    url = (
        f"{GREEN_API['api_url']}"
        f"/waInstance{GREEN_API['instance_id']}"
        f"/sendMessage/{GREEN_API['api_token']}"
    )

    payload = {
        "chatId": f"{numero_limpio}@c.us",
        "message": mensaje
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=20
        )

        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code == 200:
            return {"ok": True, "mensaje": "Mensaje enviado correctamente.", "data": data}

        return {
            "ok": False,
            "mensaje": f"Green-API respondió HTTP {response.status_code}: {response.text}",
            "data": data
        }

    except requests.exceptions.Timeout:
        return {"ok": False, "mensaje": "Timeout enviando el mensaje a WhatsApp."}

    except requests.exceptions.ConnectionError:
        return {"ok": False, "mensaje": "No se pudo conectar con Green-API."}

    except Exception as e:
        return {"ok": False, "mensaje": f"Error enviando WhatsApp: {str(e)}"}


# ============================================================
# CONSTRUIR MENSAJE
# ============================================================

def construir_mensaje_alerta(incidente, dias, costo_diario, impacto_financiero):

    fecha = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

    mensaje = (
        "🚨 Naviermetrics — ALERTA DE OBRA\n\n"
        "Proyecto: Centro de Mando Inmobiliario\n\n"
        f"Fecha:\n{fecha}\n\n"
        f"INCIDENCIA DETECTADA:\n{incidente}\n\n"
        f"Duración estimada:\n{dias} día(s)\n\n"
        f"Costo diario estimado:\nRD$ {costo_diario:,.2f}\n\n"
        f"IMPACTO FINANCIERO ESTIMADO:\nRD$ {impacto_financiero:,.2f}\n\n"
        "Estado:\n⚠️ Requiere revisión y validación.\n\n"
        "Sistema:\nNaviermetrics\nAnalítica inteligente para construcción.\n\n"
        "Esta alerta corresponde a un evento detectado por el sistema y debe ser "
        "validada por el responsable autorizado antes de adoptar medidas "
        "contractuales o legales."
    )

    return mensaje


# ============================================================
# REGISTRAR ALERTA
# ============================================================

def registrar_alerta(incidente, dias, costo_diario, impacto, resultado_whatsapp):

    registro = {
        "Fecha": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Incidencia": incidente,
        "Días": dias,
        "Costo diario": costo_diario,
        "Impacto": impacto,
        "WhatsApp": "ENVIADO" if resultado_whatsapp.get("ok") else "NO ENVIADO"
    }

    st.session_state.log_alertas.insert(0, registro)


# ============================================================
# HEADER
# ============================================================

st.markdown('<div class="main-title">Naviermetrics</div>', unsafe_allow_html=True)

st.markdown(
    '<div class="subtitle">Centro de Mando Inmobiliario y Legal — República Dominicana</div>',
    unsafe_allow_html=True
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.header("⚙️ Configuración")

    st.markdown("### WhatsApp")

    numero_whatsapp = st.text_input(
        "Número receptor",
        value="18092728026",
        help="Número completo con código de país, sin +, espacios ni guiones."
    )

    st.divider()

    st.markdown("### Parámetros financieros")

    costo_diario = st.number_input(
        "Costo estimado por día (RD$)",
        min_value=0.0,
        value=4500.0,
        step=500.0
    )

    st.divider()

    st.markdown("### Conectividad")

    if st.button("🔌 Verificar Green-API"):
        st.session_state.api_status = obtener_estado_green_api()

    if st.session_state.api_status:

        estado_api = st.session_state.api_status

        if estado_api["ok"]:
            if estado_api["estado"] == "authorized":
                st.success("GREEN-API AUTORIZADA")
            else:
                st.warning(f"Estado: {estado_api['estado']}")
        else:
            st.error(estado_api["mensaje"])

    else:
        st.info("Presiona 'Verificar Green-API' para comprobar la conexión.")


# ============================================================
# VIDEO
# ============================================================

st.markdown(
    '<div class="section-title">📹 Monitoreo en Vivo e Ingesta Analítica</div>',
    unsafe_allow_html=True
)

st.video(VIDEO_URL)

st.caption(
    "Feed de video utilizado como demostración del sistema de analítica visual Naviermetrics."
)


# ============================================================
# DETECCIÓN
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">🚨 Motor de Detección de Incidencias</div>',
    unsafe_allow_html=True
)

col1, col2 = st.columns(2)

with col1:
    incidente = st.selectbox(
        "Tipo de incidencia detectada",
        [
            "Ingreso no autorizado",
            "Actividad fuera de horario",
            "Ausencia de personal",
            "Riesgo de seguridad",
            "Interrupción de actividad",
            "Acumulación de materiales",
            "Vehículo no autorizado",
            "Incidencia contractual"
        ]
    )

with col2:
    dias = st.slider(
        "Duración estimada de la incidencia",
        min_value=1,
        max_value=30,
        value=3
    )


# ============================================================
# IMPACTO FINANCIERO
# ============================================================

impacto_financiero = costo_diario * dias

st.markdown(
    '<div class="info-box"><b>Impacto financiero estimado</b><br>'
    f'RD$ {impacto_financiero:,.2f}</div>',
    unsafe_allow_html=True
)


# ============================================================
# PROTOCOLO
# ============================================================

st.markdown("### ⚖️ Protocolo de validación")

activar_protocolo = st.checkbox("Activar protocolo de alerta y notificación")


# ============================================================
# EJECUTAR
# ============================================================

if st.button("🚨 EJECUTAR DETECCIÓN Y NOTIFICACIÓN",type="primary"):

    if not activar_protocolo:

        st.warning(
            "Debes activar el protocolo de alerta antes de ejecutar la notificación."
        )

    elif not numero_whatsapp.strip():

        st.error("Debes introducir un número de WhatsApp.")

    else:

        mensaje_alerta = construir_mensaje_alerta(
            incidente=incidente,
            dias=dias,
            costo_diario=costo_diario,
            impacto_financiero=impacto_financiero
        )

        with st.spinner("Enviando notificación..."):
            resultado = enviar_alerta_whatsapp(
                numero=numero_whatsapp,
                mensaje=mensaje_alerta
            )

        st.session_state.alerta_disparada = True
        st.session_state.ultimo_resultado = resultado

        registrar_alerta(
            incidente=incidente,
            dias=dias,
            costo_diario=costo_diario,
            impacto=impacto_financiero,
            resultado_whatsapp=resultado
        )

        if resultado["ok"]:

            st.markdown(
                '<div class="success-box"><b>✓ ALERTA EJECUTADA</b><br>'
                'La incidencia fue registrada y la notificación fue enviada por WhatsApp.</div>',
                unsafe_allow_html=True
            )
            st.success(resultado["mensaje"])

        else:

            st.markdown(
                '<div class="alert-box"><b>⚠️ ALERTA REGISTRADA — WHATSAPP NO ENVIADO</b><br>'
                'La incidencia fue procesada, pero la notificación no pudo ser enviada.</div>',
                unsafe_allow_html=True
            )
            st.error(resultado["mensaje"])


# ============================================================
# RESULTADO DE COMUNICACIÓN
# ============================================================

if st.session_state.ultimo_resultado:

    st.markdown("### 📡 Resultado de comunicación")

    ultimo = st.session_state.ultimo_resultado

    if ultimo.get("ok"):

        st.success("WhatsApp: mensaje enviado correctamente.")

        if ultimo.get("data"):
            with st.expander("Ver respuesta de Green-API"):
                st.json(ultimo["data"])

    else:
        st.warning("WhatsApp: no se pudo completar el envío.")


# ============================================================
# DASHBOARD
# ============================================================

st.divider()

st.markdown(
    '<div class="section-title">📊 Dashboard de Control</div>',
    unsafe_allow_html=True
)

total_alertas = len(st.session_state.log_alertas)

total_impacto = sum(r["Impacto"] for r in st.session_state.log_alertas)

c1, c2, c3, c4 = st.columns(4)

with c1:
    st.metric("Alertas generadas", total_alertas)

with c2:
    st.metric("Impacto acumulado", f"RD$ {total_impacto:,.0f}")

with c3:
    st.metric("Índice de certeza", "94%")

with c4:
    st.metric(
        "Sistema",
        "ACTIVO" if st.session_state.alerta_disparada else "MONITOREANDO"
    )


# ============================================================
# TABLA
# ============================================================

if st.session_state.log_alertas:

    st.markdown("### 📋 Registro de incidencias")

    df_alertas = pd.DataFrame(st.session_state.log_alertas)

    st.dataframe(df_alertas, hide_index=True, **ANCHO)

else:

    st.info("No existen incidencias registradas durante esta sesión.")


# ============================================================
# AUDITORÍA
# ============================================================

st.markdown("### 🔎 Trazabilidad y auditoría")

st.write(
    "Naviermetrics registra el evento detectado, la fecha, duración estimada, "
    "impacto financiero y estado de la notificación. Los eventos detectados "
    "por el sistema deben ser revisados y validados por el responsable "
    "autorizado antes de adoptar decisiones contractuales, administrativas o legales."
)


# ============================================================
# INFORMACIÓN TÉCNICA
# ============================================================

with st.expander("ℹ️ Información técnica"):

    st.markdown(
        """
**Naviermetrics** — Plataforma demostrativa de monitoreo y analítica aplicada a proyectos de construcción.

**Componentes:** Streamlit · Python · Green-API · YouTube · Pandas

**Flujo:**
Video → Analítica / detección → Incidencia → Evaluación → Registro → Notificación WhatsApp → Validación humana
        """
    )


# ============================================================
# REINICIAR
# ============================================================

st.divider()

if st.button("🔄 Reiniciar sesión", **ANCHO):

    st.session_state.alerta_disparada = False
    st.session_state.log_alertas = []
    st.session_state.api_status = None
    st.session_state.ultimo_resultado = None

    st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div style="text-align:center; margin-top:30px;">
    <small>Naviermetrics — Construction Intelligence & Monitoring</small>
    </div>
    """,
    unsafe_allow_html=True
)
