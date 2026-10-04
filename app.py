# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import os
import datetime
import pandas as pd

st.set_page_config(page_title="MacroChile", page_icon="🔥", layout="centered")

# --- TEMA VISUAL PERSONALIZADO (oscuro, estilo app fitness premium) ---
def aplicar_estilo():
    st.markdown("""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Sora:wght@600;700;800&family=Inter:wght@400;500;600&display=swap');

        html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

        .stApp { background: #10141A; color: #E7ECF3; }

        section[data-testid="stSidebar"] {
            background: #171D26;
            border-right: 1px solid #262E3A;
        }

        h1, h2, h3 { font-family: 'Sora', sans-serif; letter-spacing: -0.01em; color: #F4F6F9; }

        p, span, label, li { color: #C7CEDA; }

        /* --- Header / logo de marca --- */
        .mc-hero {
            display: flex; align-items: center; gap: 14px;
            padding: 6px 0 18px 0;
            border-bottom: 1px solid #262E3A;
            margin-bottom: 22px;
        }
        .mc-hero-icon {
            width: 46px; height: 46px; flex-shrink: 0;
            display: flex; align-items: center; justify-content: center;
            border-radius: 12px;
            background: linear-gradient(135deg, #E3B341, #F2C761);
            box-shadow: 0 4px 14px rgba(227, 179, 65, 0.25);
        }
        .mc-hero-title {
            font-family: 'Sora', sans-serif; font-weight: 800;
            font-size: 1.7rem; color: #F4F6F9; margin: 0; line-height: 1.1;
        }
        .mc-hero-sub {
            font-family: 'Inter', sans-serif; color: #8A93A3;
            font-size: 0.85rem; margin: 3px 0 0 0;
        }

        /* --- Botones --- */
        .stButton>button {
            background: #1B2130; color: #E7ECF3;
            border: 1px solid #2C3444; border-radius: 10px;
            font-weight: 600; transition: all .15s ease;
        }
        .stButton>button:hover { border-color: #E3B341; color: #E3B341; }

        /* --- Métricas y tarjetas --- */
        div[data-testid="stMetric"] {
            background: #171D26; border: 1px solid #262E3A;
            border-radius: 14px; padding: 14px 16px;
        }
        div[data-testid="stExpander"] {
            background: #171D26; border: 1px solid #262E3A !important;
            border-radius: 12px;
        }
        div[data-testid="stForm"] {
            background: #171D26; border: 1px solid #262E3A;
            border-radius: 14px; padding: 18px;
        }

        /* --- Inputs --- */
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
            background: #1B2130 !important; border: 1px solid #2C3444 !important;
            color: #E7ECF3 !important; border-radius: 8px;
        }

        /* --- Ocultar branding genérico de Streamlit --- */
        #MainMenu { visibility: hidden; }
        footer { visibility: hidden; }
        </style>
    """, unsafe_allow_html=True)

def mostrar_logo(subtitulo=""):
    st.markdown(f"""
        <div class="mc-hero">
            <div class="mc-hero-icon">
                <svg width="24" height="24" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                    <path d="M12 2C12 2 7 7.5 7 12.5C7 15.5 9 18 12 18C15 18 17 15.5 17 12.5C17 11 16.3 9.8 15.5 9C15.7 10 15.3 11 14.5 11.5C14.8 10 14 8 12 6C12.3 7.5 11.5 8.5 10.5 9.5C9.3 10.7 9 12 9 13"
                    stroke="#10141A" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"/>
                </svg>
            </div>
            <div>
                <p class="mc-hero-title">MacroChile</p>
                <p class="mc-hero-sub">{subtitulo}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)

aplicar_estilo()

# --- ARCHIVO DE PERSISTENCIA ---
ARCHIVO_DATOS = os.path.join(os.path.dirname(__file__), "datos_usuarios.json")

def cargar_todos_los_datos():
    if os.path.exists(ARCHIVO_DATOS):
        try:
            with open(ARCHIVO_DATOS, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def guardar_todos_los_datos(datos):
    try:
        with open(ARCHIVO_DATOS, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.error(f"No se pudo guardar tu información en disco: {e}")

# --- ESTADO DE SESIÓN GOOGLE ---
usuario_email = None
usuario_nombre = None
if hasattr(st, "user") and st.user.is_logged_in:
    usuario_email = st.user.email
    usuario_nombre = st.user.get("name", usuario_email)

# Base de datos global de alimentos
base_datos_global = {
    "fideos carozzi": {"calorias": 318, "proteinas": 11.6},
    "carne en tiras": {"calorias": 108, "proteinas": 22.7},
    "carne molida": {"calorias": 168, "proteinas": 19.0},
    "bistec posta paleta": {"calorias": 108, "proteinas": 24.4},
    "leche chocolate": {"calorias": 75, "proteinas": 3.1},
    "leche blanca": {"calorias": 33, "proteinas": 3.1},
    "mani sin sal": {"calorias": 621, "proteinas": 25.8},
    "mani salado": {"calorias": 596, "proteinas": 28.1},
    "cereal colacao": {"calorias": 405, "proteinas": 7.4},
    "atun en aceite": {"calorias": 133, "proteinas": 24.7},
    "atun en agua": {"calorias": 87, "proteinas": 21.1},
    "arroz": {"calorias": 325, "proteinas": 6.2},
    "pollo": {"calorias": 165, "proteinas": 31.0},
    "huevo": {"calorias": 155, "proteinas": 13.0},
    "score guarana": {"calorias": 48, "proteinas": 0.0},
    "coca cola": {"calorias": 32, "proteinas": 0.0},
    "avena": {"calorias": 389, "proteinas": 16.9},
    "pan hallulla": {"calorias": 296, "proteinas": 8.5},
    "pan marraqueta": {"calorias": 270, "proteinas": 8.0},
    "papas cocidas": {"calorias": 87, "proteinas": 1.9},
    "camote": {"calorias": 86, "proteinas": 1.6},
    "lentejas": {"calorias": 116, "proteinas": 9.0},
    "yogurt griego": {"calorias": 97, "proteinas": 10.0},
    "mantequilla mix": {"calorias": 542, "proteinas": 0.2},
    "queso mantecoso": {"calorias": 356, "proteinas": 23.0},
    "pizza espanola lider": {"calorias": 244, "proteinas": 11.0},
    "pizza salame lider": {"calorias": 265, "proteinas": 12.0}
}

# --- INICIALIZAR SESSION STATES ---
for key, default in [
    ("alimentos_personalizados", {}),
    ("comidas_registradas_por_usuario", {}),
    ("comidas_registradas_invitado", []),
    ("registro_peso_por_usuario", {}),
    ("registro_peso_invitado", []),
    ("idioma", None),
    ("es_chileno", None),
    ("modo_presupuesto", False),
    ("onboarding_completado", False),
    ("setup_peso", 75.0),
    ("setup_altura", 175.0),
    ("setup_sexo", "Masculino"),
    ("setup_edad", 18),
    ("setup_peso_ideal", 70.0),
    ("setup_plazo", "corto"),
    ("setup_usar_agua_pasos", True),
    ("setup_nivel_actividad", "Hago un poco / Me ejercito 2 veces a la semana"),
    ("setup_activar_cheat", False),
    ("setup_cheat_extra", 5000),
    ("setup_presupuesto_diario", 6000),
    ("presupuesto_tipo_comida", "Desayuno / Once"),
]:
    if key not in st.session_state:
        st.session_state[key] = default

if usuario_email and st.session_state.get("datos_cargados_para") != usuario_email:
    todos_los_datos = cargar_todos_los_datos()
    datos_usuario = todos_los_datos.get(usuario_email, {})
    st.session_state.alimentos_personalizados[usuario_email] = datos_usuario.get("alimentos_personalizados", {})
    st.session_state.comidas_registradas_por_usuario[usuario_email] = datos_usuario.get("comidas_registradas", [])
    st.session_state.registro_peso_por_usuario[usuario_email] = datos_usuario.get("registro_peso", [])
    if "configuracion_usuario" in datos_usuario:
        cfg = datos_usuario["configuracion_usuario"]
        st.session_state.setup_peso = cfg.get("peso", 75.0)
        st.session_state.setup_altura = cfg.get("altura", 175.0)
        st.session_state.setup_sexo = cfg.get("sexo", "Masculino")
        st.session_state.setup_edad = cfg.get("edad", 18)
        st.session_state.setup_peso_ideal = cfg.get("peso_ideal", 70.0)
        st.session_state.setup_plazo = cfg.get("plazo", "corto")
        st.session_state.setup_usar_agua_pasos = cfg.get("usar_agua_pasos", True)
        st.session_state.setup_nivel_actividad = cfg.get("nivel_actividad", "Hago un poco / Me ejercito 2 veces a la semana")
        st.session_state.setup_activar_cheat = cfg.get("activar_cheat", False)
        st.session_state.setup_cheat_extra = cfg.get("cheat_extra", 5000)
        st.session_state.modo_presupuesto = cfg.get("modo_presupuesto", False)
        st.session_state.setup_presupuesto_diario = cfg.get("presupuesto_diario", 6000)
        st.session_state.onboarding_completado = True
    st.session_state.datos_cargados_para = usuario_email

def guardar_datos_usuario_actual():
    if not usuario_email:
        return
    todos_los_datos = cargar_todos_los_datos()
    todos_los_datos[usuario_email] = {
        "alimentos_personalizados": st.session_state.alimentos_personalizados.get(usuario_email, {}),
        "comidas_registradas": st.session_state.comidas_registradas_por_usuario.get(usuario_email, []),
        "registro_peso": st.session_state.registro_peso_por_usuario.get(usuario_email, []),
        "configuracion_usuario": {
            "peso": st.session_state.setup_peso,
            "altura": st.session_state.setup_altura,
            "sexo": st.session_state.setup_sexo,
            "edad": st.session_state.setup_edad,
            "peso_ideal": st.session_state.setup_peso_ideal,
            "plazo": st.session_state.setup_plazo,
            "usar_agua_pasos": st.session_state.setup_usar_agua_pasos,
            "nivel_actividad": st.session_state.setup_nivel_actividad,
            "activar_cheat": st.session_state.setup_activar_cheat,
            "cheat_extra": st.session_state.setup_cheat_extra,
            "modo_presupuesto": st.session_state.modo_presupuesto,
            "presupuesto_diario": st.session_state.setup_presupuesto_diario
        }
    }
    guardar_todos_los_datos(todos_los_datos)

# Referencias activas
if usuario_email:
    if usuario_email not in st.session_state.alimentos_personalizados:
        st.session_state.alimentos_personalizados[usuario_email] = {}
    if usuario_email not in st.session_state.comidas_registradas_por_usuario:
        st.session_state.comidas_registradas_por_usuario[usuario_email] = []
    if usuario_email not in st.session_state.registro_peso_por_usuario:
        st.session_state.registro_peso_por_usuario[usuario_email] = []
    alimentos_propios = st.session_state.alimentos_personalizados[usuario_email]
    lista_comidas = st.session_state.comidas_registradas_por_usuario[usuario_email]
    registro_peso = st.session_state.registro_peso_por_usuario[usuario_email]
else:
    alimentos_propios = {}
    lista_comidas = st.session_state.comidas_registradas_invitado
    registro_peso = st.session_state.registro_peso_invitado

# --- PASO 1: SELECCIÓN DE IDIOMA Y LOGIN ---
if st.session_state.idioma is None:
    mostrar_logo("Select your language / Selecciona tu idioma")
    st.write("Por favor, elige tu idioma para continuar:")

    col_lang1, col_lang2 = st.columns(2)
    with col_lang1:
        if st.button("🇪🇸 Español", use_container_width=True):
            st.session_state.idioma = "es"
            st.rerun()
    with col_lang2:
        if st.button("🇺🇸 English (US)", use_container_width=True):
            st.session_state.idioma = "en"
            st.rerun()

    st.markdown("---")
    st.write("¿Tienes una cuenta de Google y quieres desbloquear tu menú y perfil guardado para siempre?")
    if usuario_email:
        st.success(f"✅ Ya iniciaste sesión como **{usuario_nombre}** ({usuario_email})")
        if st.button("Cerrar sesión"):
            st.logout()
    else:
        st.button("🔐 Iniciar sesión con Google", use_container_width=True, on_click=st.login)
        st.caption("Google valida tu identidad. Esta app nunca ve ni guarda tu contraseña.")
    st.stop()

# --- PASO 2: NACIONALIDAD Y MODO PRESUPUESTO ---
if st.session_state.es_chileno is None and st.session_state.idioma == "es":
    mostrar_logo("Verificación de nacionalidad")
    st.write("¿Eres de Chile?")
    col_ch1, col_ch2 = st.columns(2)
    with col_ch1:
        if st.button("Sí, soy de Chile", use_container_width=True):
            st.session_state.es_chileno = True
            st.rerun()
    with col_ch2:
        if st.button("No", use_container_width=True):
            st.session_state.es_chileno = False
            st.session_state.modo_presupuesto = False
            st.rerun()
    st.stop()

idioma = st.session_state.idioma

# --- PASO 3: WIZARD DE CONFIGURACIÓN INICIAL (Para evitar sobrecargar la interfaz) ---
if not st.session_state.onboarding_completado:
    mostrar_logo("⚙️ Configuración Inicial de tu Perfil & Objetivos")
    st.write("Completa tus datos una sola vez para calcular tus metas personalizadas antes de entrar a la calculadora.")

    with st.form("form_onboarding"):
        st.subheader("1. Tus Datos Físicos")
        col_onb1, col_onb2 = st.columns(2)
        with col_onb1:
            p_actual = st.number_input("Peso actual (kg):", min_value=30.0, value=float(st.session_state.setup_peso), step=0.5)
            alt_cm = st.number_input("Altura (cm):", min_value=100.0, value=float(st.session_state.setup_altura), step=1.0)
        with col_onb2:
            sex = st.selectbox("Sexo:", ["Masculino", "Femenino"], index=0 if st.session_state.setup_sexo=="Masculino" else 1)
            ed = st.number_input("Edad (años):", min_value=10, max_value=120, value=int(st.session_state.setup_edad), step=1)

        st.markdown("---")
        st.subheader("2. Tu Meta y Plazo")
        col_onb3, col_onb4 = st.columns(2)
        with col_onb3:
            p_ideal = st.number_input("Peso objetivo (kg):", min_value=30.0, value=float(st.session_state.setup_peso_ideal), step=0.5)
        with col_onb4:
            plazos_opts = {"corto": "Corto plazo (3-4 semanas)", "3m": "3 meses", "6m": "6 meses", "1a": "1 año"}
            plazo_keys = list(plazos_opts.keys())
            plazo_lbls = list(plazos_opts.values())
            try:
                idx_plazo = plazo_keys.index(st.session_state.setup_plazo)
            except:
                idx_plazo = 0
            plazo_sel_lbl = st.selectbox("¿En cuánto tiempo quieres lograrlo?", plazo_lbls, index=idx_plazo)
            plazo_sel_key = plazo_keys[plazo_lbls.index(plazo_sel_lbl)]

        st.markdown("---")
        st.subheader("3. Herramientas Opcionales")
        usar_agua_p = st.checkbox("💧 Activar calculadora de Agua y Pasos recomendados", value=st.session_state.setup_usar_agua_pasos)
        nivel_act = st.selectbox("Nivel de actividad física:", ["No hago actividad física", "Hago un poco / Me ejercito 2 veces a la semana", "Mucho / 4 o más veces a la semana"], index=1)

        activar_cheat_onb = st.checkbox("🚨 Activar Detector de Excesos / Cheat Meals en el balance", value=st.session_state.setup_activar_cheat)
        cheat_val = st.session_state.setup_cheat_extra
        if activar_cheat_onb:
            cheat_val = st.number_input("Estimado de calorías extra por cheat meals (kcal):", min_value=500, max_value=20000, value=int(st.session_state.setup_cheat_extra), step=500)

        if st.session_state.get("es_chileno", False):
            modo_p = st.checkbox("💡 Activar Modo de Presupuesto Reducido (Chile)", value=st.session_state.modo_presupuesto)
            presup_d = st.session_state.setup_presupuesto_diario
            if modo_p:
                presup_d = st.number_input("Presupuesto diario en CLP:", min_value=1000, value=int(st.session_state.setup_presupuesto_diario), step=500)
        else:
            modo_p = False
            presup_d = 6000

        submitted_onb = st.form_submit_button("🚀 Entrar a mi Calculadora y Panel", use_container_width=True)
        if submitted_onb:
            st.session_state.setup_peso = p_actual
            st.session_state.setup_altura = alt_cm
            st.session_state.setup_sexo = sex
            st.session_state.setup_edad = ed
            st.session_state.setup_peso_ideal = p_ideal
            st.session_state.setup_plazo = plazo_sel_key
            st.session_state.setup_usar_agua_pasos = usar_agua_p
            st.session_state.setup_nivel_actividad = nivel_act
            st.session_state.setup_activar_cheat = activar_cheat_onb
            st.session_state.setup_cheat_extra = cheat_val
            st.session_state.modo_presupuesto = modo_p
            st.session_state.setup_presupuesto_diario = presup_d
            st.session_state.onboarding_completado = True
            guardar_datos_usuario_actual()
            st.rerun()

    st.stop()

# --- DICCIONARIOS DE TEXTOS ---
textos = {
    "es": {
        "titulo": "🥗 Mi Calculadora de Calorías y Proteínas",
        "sidebar_meta": "🎯 Tu Perfil y Meta de Peso",
        "peso_actual": "Peso actual (kg):",
        "altura": "Altura (cm):",
        "sexo": "Sexo",
        "opciones_sexo": ["Masculino", "Femenino"],
        "edad": "Edad (años)",
        "peso_ideal": "Peso objetivo (kg):",
        "armar_plato": "🍽️ Registrar Comida",
        "texto_plato": "Escribe tu plato (ej: empanadas juanito o arroz con pollo):",
        "btn_guardar": "📥 Guardar esta comida",
        "resumen_plato": "📊 Resumen del Plato Actual",
        "resumen_mes": "📅 Balance y Historial Mensual",
        "total_cal": "🔥 Total Calorías Acumuladas",
        "total_prot": "💪 Total Proteínas Acumuladas",
        "meta_mensual_txt": "🎯 Meta Calórica Mensual",
        "desglose_comidas": "Historial de comidas:",
        "borrar": "❌ Borrar",
        "borrar_todo": "🗑️ Borrar todo el registro",
        "no_registros": "Aún no has guardado ninguna comida.",
        "ingresa_plato": "Escribe tu plato arriba para calcular.",
        "alimento_encontrado": "¡'{item}' encontrado!",
        "alimento_no_encontrado": "No encontré ese alimento en tu base ni en internet.",
        "nombre_en_uso": "⚠️️ Ese nombre ya está en uso."
    },
    "en": {
        "titulo": "🥗 My Calorie & Protein Calculator",
        "sidebar_meta": "🎯 Your Profile & Weight Goal",
        "peso_actual": "Current weight (kg):",
        "altura": "Height (cm):",
        "sexo": "Gender",
        "opciones_sexo": ["Male", "Female"],
        "edad": "Age (years)",
        "peso_ideal": "Target weight (kg):",
        "armar_plato": "🍽️ Log Meal",
        "texto_plato": "Type your meal (e.g., chicken or rice):",
        "btn_guardar": "📥 Save this meal",
        "resumen_plato": "📊 Current Meal Summary",
        "resumen_mes": "📅 Monthly Balance & History",
        "total_cal": "🔥 Total Calories",
        "total_prot": "💪 Total Protein",
        "meta_mensual_txt": "🎯 Target Monthly Goal",
        "desglose_comidas": "Meal history:",
        "borrar": "❌ Delete",
        "borrar_todo": "🗑️ Clear all logs",
        "no_registros": "No meals saved yet.",
        "ingresa_plato": "Type your meal above to calculate.",
        "alimento_encontrado": "'{item}' found!",
        "alimento_no_encontrado": "I couldn't find that food.",
        "nombre_en_uso": "⚠️ That name is already in use."
    }
}

t = textos[idioma]
mostrar_logo(t["titulo"])

# --- BARRA LATERAL (Navegación y Opciones rápidas) ---
with st.sidebar:
    if usuario_email:
        st.success(f"👤 {usuario_nombre}")
        if st.button("🚪 Cerrar sesión"):
            st.logout()
    else:
        st.info("🔒 Invitado (datos temporales)")
        st.button("🔐 Iniciar con Google", on_click=st.login, use_container_width=True)

    st.markdown("---")
    if st.button("⚙️ Reconfigurar Perfil / Objetivos"):
        st.session_state.onboarding_completado = False
        st.rerun()

    if st.button("🌐 Cambiar Idioma"):
        st.session_state.idioma = None
        st.session_state.es_chileno = None
        st.session_state.onboarding_completado = False
        st.rerun()

    if st.session_state.get("modo_presupuesto", False):
        st.markdown("---")
        st.subheader("💡 Presupuesto (Chile)")
        presupuesto_diario = st.session_state.setup_presupuesto_diario
        tipo_comida_select = st.selectbox("Comida a planificar:", ["Desayuno / Once", "Almuerzo / Cena"], key="sel_tipo_comida")
        es_desayuno_once = "Desayuno" in tipo_comida_select
        if es_desayuno_once:
            opcion_sana = "Té/café con pan marraqueta tostada y huevo revuelto (~$600 CLP)"
            opcion_inter = "Yogurt batido con 2 cdas de avena y medio plátano (~$700 CLP)"
            opcion_relajada = "Pan con mantequilla mix y leche con cacao (~$500 CLP)"
        else:
            opcion_sana = "Arroz con dos huevos duros y ensalada de tomate (~$1.200 CLP)"
            opcion_inter = "Pechuga de pollo a la plancha con arroz y ensalada (~$4.500 CLP)"
            opcion_relajada = "Fideos Carozzi con salsa y vienesa (~$1.800 CLP)"
        st.success(f"🌱 Sana: {opcion_sana}")
        st.info(f"⚖️ Intermedia: {opcion_inter}")

# Fusión de base de datos
base_datos_calorias = base_datos_global.copy()
base_datos_calorias.update(alimentos_propios)

def buscar_alimento_internet(nombre_alimento):
    try:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={nombre_alimento}&search_simple=1&action=process&json=1"
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            productos = datos.get("products", [])
            for p in productos:
                nutriments = p.get("nutriments", {})
                calorias = nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal")
                proteinas = nutriments.get("proteins_100g") or nutriments.get("proteins")
                if calorias is not None and proteinas is not None:
                    return {"calorias": float(calorias), "proteinas": float(proteinas)}
    except Exception:
        pass
    return None

PLANES_TIEMPO = {
    "corto": {"semanas": 4, "max_kg": 3},
    "3m": {"semanas": 13, "max_kg": 8},
    "6m": {"semanas": 26, "max_kg": 15},
    "1a": {"semanas": 52, "max_kg": 26},
}

peso_actual = st.session_state.setup_peso
altura_cm = st.session_state.setup_altura
sexo = st.session_state.setup_sexo
edad = st.session_state.setup_edad
peso_ideal = st.session_state.setup_peso_ideal
plazo_key = st.session_state.setup_plazo
plan = PLANES_TIEMPO.get(plazo_key, PLANES_TIEMPO["corto"])
semanas_periodo = plan["semanas"]
max_kg_periodo = plan["max_kg"]

mantenimiento_estimado = peso_actual * 30
diferencia_deseada = peso_actual - peso_ideal
if diferencia_deseada > max_kg_periodo:
    kg_meta_periodo = max_kg_periodo
elif diferencia_deseada < -max_kg_periodo:
    kg_meta_periodo = -max_kg_periodo
else:
    kg_meta_periodo = diferencia_deseada

dias_periodo = semanas_periodo * 7
if kg_meta_periodo > 0:
    cambio_diario = (kg_meta_periodo * 7700) / dias_periodo
    meta_calorias_diarias = mantenimiento_estimado - cambio_diario
elif kg_meta_periodo < 0:
    cambio_diario = (abs(kg_meta_periodo) * 7700) / dias_periodo
    meta_calorias_diarias = mantenimiento_estimado + cambio_diario
else:
    meta_calorias_diarias = mantenimiento_estimado

meta_calorias_mensual = meta_calorias_diarias * 30
st.session_state.plan_activo = {
    "semanas": semanas_periodo,
    "kg_meta_periodo": kg_meta_periodo,
    "meta_calorias_diarias": meta_calorias_diarias,
    "peso_objetivo": peso_ideal
}

activar_cheat = st.session_state.setup_activar_cheat
calorias_cheat_extra = st.session_state.setup_cheat_extra if activar_cheat else 0

# --- SECCIÓN PRINCIPAL: REGISTRO DE COMIDA ACTUAL ---
st.subheader(t["armar_plato"])
texto_ingresado = st.text_input(t["texto_plato"]).lower().strip()

calorias_plato_actual = 0
proteinas_plato_actual = 0
detalle_plato = {}

if texto_ingresado:
    alimentos_encontrados = [a for a in base_datos_calorias.keys() if a in texto_ingresado]
    if not alimentos_encontrados:
        with st.spinner("Buscando en web..." if idioma == "es" else "Searching web..."):
            info_web = buscar_alimento_internet(texto_ingresado)
            if info_web:
                base_datos_calorias[texto_ingresado] = info_web
                alimentos_encontrados.append(texto_ingresado)
                st.success(t["alimento_encontrado"].format(item=texto_ingresado))

    if alimentos_encontrados:
        st.markdown("**Ajusta las cantidades (g o ml):**")
        for alimento in alimentos_encontrados:
            cantidad = st.number_input(f"Cantidad de {alimento} (g/ml):", min_value=0.0, value=100.0, step=10.0, key=f"qty_{alimento}")
            cal_100 = base_datos_calorias[alimento]["calorias"]
            prot_100 = base_datos_calorias[alimento]["proteinas"]
            calorias_plato_actual += (cal_100 * cantidad) / 100
            proteinas_plato_actual += (prot_100 * cantidad) / 100
            detalle_plato[alimento] = cantidad

        col_f1, col_f2 = st.columns(2)
        with col_f1:
            nombre_comida = st.text_input("Nombre de la comida:", value="Almuerzo")
        with col_f2:
            fecha_comida = st.date_input("Fecha:", value=datetime.date.today())

        if st.button(t["btn_guardar"], use_container_width=True):
            nombres_existentes = [c["nombre"].strip().lower() for c in lista_comidas]
            if nombre_comida.strip().lower() in nombres_existentes:
                st.error(t["nombre_en_uso"])
            else:
                lista_comidas.append({
                    "nombre": nombre_comida,
                    "calorias": calorias_plato_actual,
                    "proteinas": proteinas_plato_actual,
                    "detalle": detalle_plato,
                    "fecha": fecha_comida.isoformat()
                })
                guardar_datos_usuario_actual()
                st.success("¡Comida guardada con éxito!")
    else:
        st.warning(t["alimento_no_encontrado"])

if detalle_plato:
    st.markdown("---")
    st.subheader(t["resumen_plato"])
    for alim, cant in detalle_plato.items():
        cp = (base_datos_calorias[alim]["calorias"] * cant) / 100
        pp = (base_datos_calorias[alim]["proteinas"] * cant) / 100
        st.write(f"- **{cant}g** de {alim} -> {cp:.1f} kcal | {pp:.1f}g prot")
    col_m1, col_m2 = st.columns(2)
    with col_m1:
        st.metric("Calorías del Plato", f"{calorias_plato_actual:.1f} kcal")
    with col_m2:
        st.metric("Proteína del Plato", f"{proteinas_plato_actual:.1f} g")

st.markdown("---")

# --- ALIMENTOS PERSONALIZADOS ---
st.subheader("⭐ Mis Alimentos Personalizados" if idioma == "es" else "⭐ My Custom Foods")
if usuario_email:
    with st.expander("➕ Agregar nuevo plato o producto a mi cuenta"):
        with st.form("form_custom"):
            c_nom = st.text_input("Nombre (ej: empanadas de mamá):").lower().strip()
            c_cal = st.number_input("Calorías por 100g/ml:", min_value=0.0, value=250.0)
            c_prot = st.number_input("Proteínas (g) por 100g/ml:", min_value=0.0, value=10.0)
            if st.form_submit_button("Guardar alimento personal"):
                if c_nom in alimentos_propios:
                    st.error("Ese nombre ya existe.")
                else:
                    alimentos_propios[c_nom] = {"calorias": c_cal, "proteinas": c_prot}
                    guardar_datos_usuario_actual()
                    st.success(f"¡'{c_nom}' guardado!")
                    st.rerun()
    if alimentos_propios:
        for al, inf in alimentos_propios.items():
            st.text(f"• {al} -> {inf['calorias']} kcal | {inf['proteinas']}g prot (100g)")
else:
    st.info("🔒 Inicia sesión con Google para crear y guardar tus alimentos personalizados permanentemente.")

st.markdown("---")

# --- SEGUIMIENTO DE PESO ---
st.subheader("📈 Seguimiento de Peso (Mes a Mes / Hasta 1 Año)")
if usuario_email:
    col_pw1, col_pw2, col_pw3 = st.columns([2, 2, 1])
    with col_pw1:
        f_peso = st.date_input("Fecha pesaje:", value=datetime.date.today(), key="f_peso_reg")
    with col_pw2:
        v_peso = st.number_input("Peso (kg):", min_value=30.0, value=float(peso_actual), step=0.5, key="v_peso_reg")
    with col_pw3:
        st.write("")
        st.write("")
        if st.button("💾 Guardar Peso"):
            f_iso = f_peso.isoformat()
            ex = next((r for r in registro_peso if r["fecha"] == f_iso), None)
            if ex:
                ex["peso"] = v_peso
            else:
                registro_peso.append({"fecha": f_iso, "peso": v_peso})
            registro_peso.sort(key=lambda r: r["fecha"])
            un_ano_atras = (datetime.date.today() - datetime.timedelta(days=365)).isoformat()
            registro_peso[:] = [r for r in registro_peso if r["fecha"] >= un_ano_atras]
            guardar_datos_usuario_actual()
            st.success("¡Peso guardado!")
            st.rerun()

    if registro_peso:
        df_p = pd.DataFrame(registro_peso)
        df_p["fecha"] = pd.to_datetime(df_p["fecha"])
        df_p = df_p.set_index("fecha").sort_index()
        st.line_chart(df_p["peso"])
else:
    st.info("🔒 Inicia sesión con Google para registrar y graficar tu peso durante todo un año.")

# --- CALCULADORA DE AGUA Y PASOS (Si está activada) ---
if st.session_state.setup_usar_agua_pasos:
    st.markdown("---")
    st.subheader("💧 Hidratación y Pasos Diarios Recomendados")
    ml_b = peso_actual * 35
    if sexo == "Masculino": ml_b += 200
    if "No hago" in st.session_state.setup_nivel_actividad:
        agua_ext, pasos_b = 0, 6500
    elif "2 veces" in st.session_state.setup_nivel_actividad:
        agua_ext, pasos_b = 400, 8500
    else:
        agua_ext, pasos_b = 800, 11000

    tot_agua_l = (ml_b + agua_ext) / 1000
    vasos = round((ml_b + agua_ext) / 250)
    if edad < 30: pasos_b += 500
    if sexo == "Masculino": pasos_b += 300

    col_ag1, col_ag2 = st.columns(2)
    with col_ag1:
        st.metric("Agua Recomendada", f"{tot_agua_l:.2f} L (~{vasos} vasos)")
    with col_ag2:
        st.metric("Meta de Pasos Diarios", f"{pasos_b:,} pasos".replace(",", "."))

st.markdown("---")

# ==================================================================
# REVISIÓN SEMANAL (Historial ordenado de semanas a lo largo de un año)
# ==================================================================
st.subheader("📅 Historial de Semanas Anteriores y Actual (Hasta 1 Año)")

if "semana_offset" not in st.session_state:
    st.session_state.semana_offset = 0

col_sbtn1, col_sbtn2, col_sbtn3 = st.columns([1, 2, 1])
with col_sbtn1:
    if st.button("⬅️ Semana Anterior"):
        st.session_state.semana_offset -= 1
        st.rerun()
with col_sbtn3:
    if st.session_state.semana_offset < 0:
        if st.button("Semana Siguiente ➡️"):
            st.session_state.semana_offset += 1
            st.rerun()

hoy = datetime.date.today()
lunes_actual = hoy - datetime.timedelta(days=hoy.weekday())
lunes_semana = lunes_actual + datetime.timedelta(weeks=st.session_state.semana_offset)
dias_semana_dates = [lunes_semana + datetime.timedelta(days=i) for i in range(7)]

nombres_dias = ["Lunes", "Martes", "Miércoles", "Jueves", "Viernes", "Sábado", "Domingo"]

with col_sbtn2:
    st.markdown(f"<p style='text-align:center; margin-top:8px;'><b>Semana: {dias_semana_dates[0].strftime('%d/%m/%Y')} — {dias_semana_dates[-1].strftime('%d/%m/%Y')}</b></p>", unsafe_allow_html=True)

calorias_por_dia = {d.isoformat(): 0.0 for d in dias_semana_dates}
proteinas_por_dia = {d.isoformat(): 0.0 for d in dias_semana_dates}

for comida in lista_comidas:
    fc = comida.get("fecha")
    if fc in calorias_por_dia:
        calorias_por_dia[fc] += comida["calorias"]
        proteinas_por_dia[fc] += comida["proteinas"]

# Construir DataFrame ordenado cronológicamente para evitar desorden visual en gráficos
df_semana = pd.DataFrame({
    "Día": nombres_dias,
    "Calorías": [calorias_por_dia[d.isoformat()] for d in dias_semana_dates],
    "Proteínas (g)": [proteinas_por_dia[d.isoformat()] for d in dias_semana_dates],
    "_fecha_obj": dias_semana_dates
})

# Mostrar tabla limpia
st.dataframe(df_semana[["Día", "Calorías", "Proteínas (g)"]], use_container_width=True, hide_index=True)

# Gráficos limpios con índice categórico ordenado correctamente
col_c1, col_c2 = st.columns(2)
with col_c1:
    st.write("**Calorías por Día**")
    st.bar_chart(df_semana.set_index("Día")["Calorías"])
with col_c2:
    st.write("**Proteínas por Día (g)**")
    st.bar_chart(df_semana.set_index("Día")["Proteínas (g)"])

dias_con_datos_sem = sum(1 for d in dias_semana_dates if calorias_por_dia[d.isoformat()] > 0)
if dias_con_datos_sem > 0:
    prom_sem = sum(calorias_por_dia.values()) / dias_con_datos_sem
    st.info(f"📊 Promedio diario real de esta semana: **{prom_sem:.0f} kcal/día** (Meta del plan: ~{meta_calorias_diarias:.0f} kcal)")

st.markdown("---")

# ==================================================================
# RESUMEN Y BALANCE MENSUAL
# ==================================================================
st.subheader("📅 Resúmenes Mensuales (Balance de 30 Días)")

# Selector de mes/año para ver resúmenes históricos mensuales
meses_nombres = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}

col_msel1, col_msel2 = st.columns(2)
with col_msel1:
    anio_sel = st.selectbox("Selecciona el año:", list(range(datetime.date.today().year - 1, datetime.date.today().year + 2)), index=1)
with col_msel2:
    mes_sel_nombre = st.selectbox("Selecciona el mes:", list(meses_nombres.values()), index=datetime.date.today().month - 1)
    mes_sel_num = [k for k, v in meses_nombres.items() if v == mes_sel_nombre][0]

# Filtrar comidas del mes seleccionado
comidas_mes_sel = []
for c in lista_comidas:
    f_c = c.get("fecha")
    if f_c:
        dt_c = datetime.date.fromisoformat(f_c)
        if dt_c.year == anio_sel and dt_c.month == mes_sel_num:
            comidas_mes_sel.append(c)

total_cal_mes_sel = sum(c["calorias"] for c in comidas_mes_sel) + (calorias_cheat_extra if (activar_cheat and datetime.date.today().month == mes_sel_num and datetime.date.today().year == anio_sel) else 0)
total_prot_mes_sel = sum(c["proteinas"] for c in comidas_mes_sel)

st.markdown(f"### Resumen para **{mes_sel_nombre} {anio_sel}**")
col_resm1, col_resm2, col_resm3 = st.columns(3)
with col_resm1:
    st.metric("Calorías del Mes", f"{total_cal_mes_sel:.1f} kcal")
with col_resm2:
    st.metric("Meta Mensual Objetivo", f"{meta_calorias_mensual:.0f} kcal")
with col_resm3:
    st.metric("Proteínas del Mes", f"{total_prot_mes_sel:.1f} g")

if comidas_mes_sel or (activar_cheat and datetime.date.today().month == mes_sel_num):
    dif_m = total_cal_mes_sel - meta_calorias_mensual
    if abs(dif_m) <= 2000:
        st.success("🎯 ¡Impecable! Tu balance de este mes está perfectamente alineado con tu objetivo.")
    elif dif_m < -2000:
        st.success("🔥 ¡Excelente balance! Déficit sostenible logrado en este mes.")
    else:
        st.warning("⚠️ Superávit o exceso registrado en este mes.")

    with st.expander(f"📋 Ver detalle de comidas en {mes_sel_nombre} {anio_sel}"):
        for i, comida in enumerate(comidas_mes_sel):
            col_e1, col_e2 = st.columns([4, 1])
            with col_e1:
                st.text(f"📌 {comida['nombre']} ({comida.get('fecha','')}) -> {comida['calorias']:.1f} kcal | {comida['proteinas']:.1f}g prot")
            with col_e2:
                if st.button("❌", key=f"del_mes_{i}_{comida.get('fecha','')}"):
                    # Encontrar y eliminar de lista_comidas original
                    lista_comidas.remove(comida)
                    guardar_datos_usuario_actual()
                    st.rerun()
else:
    st.info(f"No hay registros de comidas para {mes_sel_nombre} {anio_sel}.")

st.markdown("---")
if st.button("🗑️ Borrar todo el historial de comidas"):
    lista_comidas.clear()
    guardar_datos_usuario_actual()
    st.rerun()
 
