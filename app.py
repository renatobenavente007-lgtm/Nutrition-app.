# -*- coding: utf-8 -*-
import streamlit as st
import requests
import json
import os

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

# --- ARCHIVO DE PERSISTENCIA (guarda los datos de cada usuario en disco) ---
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

# --- ESTADO REAL DE SESIÓN (Google se encarga de validar la identidad) ---
usuario_email = None
usuario_nombre = None
if hasattr(st, "user") and st.user.is_logged_in:
    usuario_email = st.user.email
    usuario_nombre = st.user.get("name", usuario_email)

# Base de datos global predeterminada (valores por cada 100 gramos o ml)
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

# --- CARGA DE DATOS PERSONALES DEL USUARIO (una sola vez por sesión) ---
if "alimentos_personalizados" not in st.session_state:
    st.session_state.alimentos_personalizados = {}
if "comidas_registradas_por_usuario" not in st.session_state:
    st.session_state.comidas_registradas_por_usuario = {}
if "comidas_registradas_invitado" not in st.session_state:
    st.session_state.comidas_registradas_invitado = []

if usuario_email and st.session_state.get("datos_cargados_para") != usuario_email:
    todos_los_datos = cargar_todos_los_datos()
    datos_usuario = todos_los_datos.get(usuario_email, {})
    st.session_state.alimentos_personalizados[usuario_email] = datos_usuario.get("alimentos_personalizados", {})
    st.session_state.comidas_registradas_por_usuario[usuario_email] = datos_usuario.get("comidas_registradas", [])
    st.session_state.datos_cargados_para = usuario_email

def guardar_datos_usuario_actual():
    """Guarda en disco los datos del usuario logueado (invitados no se guardan)."""
    if not usuario_email:
        return
    todos_los_datos = cargar_todos_los_datos()
    todos_los_datos[usuario_email] = {
        "alimentos_personalizados": st.session_state.alimentos_personalizados.get(usuario_email, {}),
        "comidas_registradas": st.session_state.comidas_registradas_por_usuario.get(usuario_email, [])
    }
    guardar_todos_los_datos(todos_los_datos)

# Referencias activas según si hay sesión o es invitado
if usuario_email:
    if usuario_email not in st.session_state.alimentos_personalizados:
        st.session_state.alimentos_personalizados[usuario_email] = {}
    if usuario_email not in st.session_state.comidas_registradas_por_usuario:
        st.session_state.comidas_registradas_por_usuario[usuario_email] = []
    alimentos_propios = st.session_state.alimentos_personalizados[usuario_email]
    lista_comidas = st.session_state.comidas_registradas_por_usuario[usuario_email]
else:
    alimentos_propios = {}
    lista_comidas = st.session_state.comidas_registradas_invitado

# --- PASO 1: SELECCIÓN DE IDIOMA Y LOGIN REAL CON GOOGLE ---
if "idioma" not in st.session_state:
    st.session_state.idioma = None

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
    st.write("¿Tienes una cuenta de Google y quieres desbloquear tu menú personalizado guardado para siempre?")

    if usuario_email:
        st.success(f"✅ Ya iniciaste sesión como **{usuario_nombre}** ({usuario_email})")
        if st.button("Cerrar sesión"):
            st.logout()
    else:
        st.button("🔐 Iniciar sesión con Google", use_container_width=True, on_click=st.login)
        st.caption("Google se encarga de validar tu identidad y tu contraseña. Esta app nunca las ve ni las guarda; solo recibimos tu nombre y correo una vez que inicias sesión.")

    st.stop()

# --- PASO 2: PREGUNTA DE NACIONALIDAD Y MODO PRESUPUESTO (SOLO SI ES ESPAÑOL/CHILE) ---
if "es_chileno" not in st.session_state:
    st.session_state.es_chileno = None

if "modo_presupuesto" not in st.session_state:
    st.session_state.modo_presupuesto = None

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

if st.session_state.es_chileno and st.session_state.modo_presupuesto is None and st.session_state.idioma == "es":
    st.title("🛒 Modo de Presupuesto Reducido")
    st.write("¿Quieres usar el **modo de presupuesto reducido**? Este modo intentará buscar opciones más baratas, saludables y acorde a tus gustos posibles para alcanzar tu objetivo.")

    col_p1, col_p2 = st.columns(2)
    with col_p1:
        if st.button("Sí, activar modo presupuesto", use_container_width=True):
            st.session_state.modo_presupuesto = True
            st.rerun()
    with col_p2:
        if st.button("No, ir a la calculadora normal", use_container_width=True):
            st.session_state.modo_presupuesto = False
            st.rerun()
    st.stop()

# Panel de presupuesto reducido (Chile)
if st.session_state.get("modo_presupuesto", False):
    mostrar_logo("💡 Panel de Presupuesto Reducido (Chile)")
    st.write("Aquí tienes tus opciones inteligentes basadas en tu presupuesto diario para cumplir tus macros sin gastar de más.")

    presupuesto_diario = st.number_input("Ingresa tu presupuesto diario disponible (en pesos chilenos - CLP):", min_value=1000, value=6000, step=500)
    tipo_comida_select = st.text_input("¿Qué comida deseas planificar?", value="Desayuno / Once")

    st.markdown("---")
    st.subheader(f"🛒 Opciones para tu {tipo_comida_select} (Presupuesto: ${presupuesto_diario} CLP)")

    es_desayuno_once = any(term in tipo_comida_select.lower() for term in ["desayuno", "once", "once/desayuno"])

    if es_desayuno_once:
        if presupuesto_diario <= 5000:
            opcion_sana = "Té o café con 1 pan marraqueta o hallulla tostada con huevo revuelto o quesillo (~$600)"
            opcion_inter = "Yogurt batido con 2 cucharadas de avena y medio plátano (~$700)"
            opcion_relajada = "Pan con mantequilla mix o mermelada y un vaso de leche con cacao (~$500)"
        elif presupuesto_diario <= 10000:
            opcion_sana = "Té o café con pan marraqueta, palta molida y un huevo duro (~$1.200)"
            opcion_inter = "Yogurt griego con cereales o un pan con jamón de pavo y queso mantecoso (~$1.800)"
            opcion_relajada = "Tostadas con manjar/mermelada y leche con chocolate (~$1.500)"
        else:
            opcion_sana = "Tostadas en pan integral con palta, huevo pochado o revuelto y batido de fruta (~$2.500)"
            opcion_inter = "Queso fresco, jamón de pierna, pan de molde integral y café de grano (~$2.200)"
            opcion_relajada = "Medialunas de panadería con café con leche y jugo natural (~$3.000)"
    else:
        if presupuesto_diario <= 5000:
            opcion_sana = "Arroz o fideos con dos huevos duros y ensalada de tomate básica (~$1.200)"
            opcion_inter = "Lentejas guisadas con un trozo de zapallo y arroz (~$1.500)"
            opcion_relajada = "Fideos Carozzi con salsa de tomate básica y una vienesa (~$1.800)"
        elif presupuesto_diario <= 10000:
            opcion_sana = "Pechuga de pollo a la plancha con arroz y ensalada mixta de feria (~$4.500)"
            opcion_inter = "Carne molida salteada con puré de papas casero (~$5.000)"
            opcion_relajada = "Completos caseros con refresco (~$4.500)"
        else:
            opcion_sana = "Salmón o atún fresco con camote al horno y verduras salteadas (~$9.000)"
            opcion_inter = "Lomo vetado o posta rosada con papas doradas y ensalada a elección (~$8.500)"
            opcion_relajada = "Promoción de sushi para uno o porción de pizza local (~$10.000)"

    st.success(f"🌱 **Opción 1 (Bastante sana acorde al presupuesto):**\n- {opcion_sana}")
    st.info(f"⚖️ **Opción 2 (Punto intermedio equilibrado):**\n- {opcion_inter}")
    st.warning(f"🍕 **Opción 3 (No tan sana, pero encaja en calorías y presupuesto):**\n- {opcion_relajada}")

    st.markdown("---")
    if st.button("🔄 Volver / Ir a la Calculadora Normal de Calorías"):
        st.session_state.modo_presupuesto = False
        st.rerun()

    st.stop()

# --- PASO 3: DICCIONARIOS DE TEXTOS SEGÚN EL IDIOMA ---
textos = {
    "es": {
        "titulo": "🥗 Mi Calculadora de Calorías y Proteínas (Enfoque Mensual)",
        "sidebar_meta": "🎯 Tu Perfil y Meta de Peso",
        "peso_actual": "¿Cuál es tu peso actual (kg)?",
        "altura": "¿Cuál es tu altura (cm)?",
        "sexo": "Sexo",
        "opciones_sexo": ["Masculino", "Femenino"],
        "edad": "Edad (años)",
        "peso_ideal": "¿Cuál sería tu peso ideal (kg)?",
        "meses_meta": "¿En cuántos meses esperas obtenerlo?",
        "armar_plato": "🍽️ Armar Plato Actual",
        "texto_plato": "Escribe tu plato (ej: empanadas juanito o arroz con pollo):",
        "btn_guardar": "📥 Guardar esta comida en el registro mensual",
        "resumen_plato": "📊 Resumen del Plato Actual",
        "resumen_mes": "📅 Balance Total del Mes (30 Días)",
        "total_cal": "🔥 Total Calorías Acumuladas (Mes)",
        "total_prot": "💪 Total Proteínas Acumuladas (Mes)",
        "meta_mensual_txt": "🎯 Meta Calórica Mensual Objetivo",
        "desglose_comidas": "Historial de comidas acumuladas en el mes:",
        "borrar": "❌ Borrar",
        "borrar_todo": "🗑️ Borrar todo el registro del mes",
        "no_registros": "Aún no has guardado ninguna comida en el registro mensual.",
        "ingresa_plato": "Escribe tu plato en la barra lateral para comenzar a calcular.",
        "alimento_encontrado": "¡'{item}' encontrado!",
        "alimento_no_encontrado": "No encontré ese alimento en tu base ni en internet.",
        "cambio_deficit": "Debes comer unos **{val:.0f} kcal menos** al día.",
        "meta_deficit": "Meta diaria sugerida (Déficit):",
        "cambio_superavit": "Debes comer unos **{val:.0f} kcal más** al día.",
        "meta_superavit": "Meta diaria sugerida (Volumen):",
        "mantenimiento": "Mantenimiento: Tu peso ideal es igual al actual.",
        "meta_mant": "Meta diaria sugerida:",
        "cheat_header": "🚨 Detector de Excesos / Cheat Meals del Mes",
        "cheat_checkbox": "¡Hubo descontrol o Cheat Meals acumulados en el mes!",
        "cheat_slider": "Estímese el exceso total aproximado en el mes (kcal extra):",
        "nombre_en_uso": "⚠️ Ese nombre ya está en uso. Usa otro nombre para no confundirte."
    },
    "en": {
        "titulo": "🥗 My Calorie & Protein Calculator (Monthly Focus)",
        "sidebar_meta": "🎯 Your Profile & Weight Goal",
        "peso_actual": "What is your current weight (kg)?",
        "altura": "What is your height (cm)?",
        "sexo": "Gender",
        "opciones_sexo": ["Male", "Female"],
        "edad": "Age (years)",
        "peso_ideal": "What would be your ideal weight (kg)?",
        "meses_meta": "In how many months do you expect to reach it?",
        "armar_plato": "🍽️ Build Current Meal",
        "texto_plato": "Type your meal (e.g., empanadas juanito or rice):",
        "btn_guardar": "📥 Save this meal to the month",
        "resumen_plato": "📊 Current Meal Summary",
        "resumen_mes": "📅 Monthly Total Balance (30 Days)",
        "total_cal": "🔥 Total Accumulated Calories (Month)",
        "total_prot": "💪 Total Accumulated Protein (Month)",
        "meta_mensual_txt": "🎯 Target Monthly Calorie Goal",
        "desglose_comidas": "History of accumulated meals for the month:",
        "borrar": "❌ Delete",
        "borrar_todo": "🗑️ Clear all monthly logs",
        "no_registros": "You haven't saved any meals in the monthly log yet.",
        "ingresa_plato": "Type your meal in the sidebar to start calculating.",
        "alimento_encontrado": "'{item}' found!",
        "alimento_no_encontrado": "I couldn't find that food in your database or on the web.",
        "cambio_deficit": "You should eat about **{val:.0f} fewer kcal** per day.",
        "meta_deficit": "Suggested daily target (Deficit):",
        "cambio_superavit": "You should eat about **{val:.0f} more kcal** per day.",
        "meta_superavit": "Suggested daily target (Surplus):",
        "mantenimiento": "Maintenance: Your ideal weight matches your current one.",
        "meta_mant": "Suggested daily target:",
        "cheat_header": "🚨 Excess / Monthly Cheat Meals Detector",
        "cheat_checkbox": "Extreme loss of control / Monthly Cheat Meals!",
        "cheat_slider": "Estimate approximate total excess (extra kcal):",
        "nombre_en_uso": "⚠️ That name is already in use. Use a different name to avoid confusion."
    }
}

t = textos[st.session_state.idioma]

mostrar_logo(t["titulo"])

if st.sidebar.button("🌐 Cambiar Idioma"):
    st.session_state.idioma = None
    st.session_state.es_chileno = None
    st.session_state.modo_presupuesto = None
    st.rerun()

# --- Fusión de base de datos global con los alimentos personalizados del usuario activo ---
base_datos_calorias = base_datos_global.copy()
base_datos_calorias.update(alimentos_propios)

def buscar_alimento_internet(nombre_alimento):
    try:
        url = f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={nombre_alimento}&search_simple=1&action=process&json=1"
        respuesta = requests.get(url, timeout=5)
        if respuesta.status_code == 200:
            datos = respuesta.json()
            productos = datos.get("products", [])
            if productos:
                for p in productos:
                    nutriments = p.get("nutriments", {})
                    calorias = nutriments.get("energy-kcal_100g") or nutriments.get("energy-kcal")
                    proteinas = nutriments.get("proteins_100g") or nutriments.get("proteins")

                    if calorias is not None and proteinas is not None:
                        return {
                            "calorias": float(calorias),
                            "proteinas": float(proteinas)
                        }
    except Exception:
        pass
    return None

# --- APARTADO DE METAS Y PERFIL EN LA BARRA LATERAL ---
st.sidebar.header(t["sidebar_meta"])
if usuario_email:
    st.sidebar.success(f"👤 Sesión: {usuario_nombre} ({usuario_email})")
    if st.sidebar.button("🚪 Cerrar sesión"):
        st.logout()
else:
    st.sidebar.info("🔒 Estás como invitado. Tus datos se perderán al cerrar la app.")
    st.sidebar.button("🔐 Iniciar sesión con Google", on_click=st.login, use_container_width=True)

peso_actual = st.sidebar.number_input(t["peso_actual"], min_value=30.0, value=75.0, step=0.5)
altura_cm = st.sidebar.number_input(t["altura"], min_value=100.0, value=175.0, step=1.0)
sexo = st.sidebar.selectbox(t["sexo"], t["opciones_sexo"])
edad = st.sidebar.number_input(t["edad"], min_value=10, max_value=120, value=18, step=1)

altura_m = altura_cm / 100.0
imc = peso_actual / (altura_m ** 2)

if st.session_state.idioma == "es":
    if imc < 18.5: clasificacion_imc = "Bajo peso"
    elif 18.5 <= imc < 25: clasificacion_imc = "Peso normal (saludable)"
    elif 25 <= imc < 30: clasificacion_imc = "Sobrepeso"
    else: clasificacion_imc = "Obesidad"
    st.sidebar.markdown(f"📊 **IMC:** {imc:.1f} ({clasificacion_imc})")
else:
    if imc < 18.5: clasificacion_imc = "Underweight"
    elif 18.5 <= imc < 25: clasificacion_imc = "Normal weight (healthy)"
    elif 25 <= imc < 30: clasificacion_imc = "Overweight"
    else: clasificacion_imc = "Obesity"
    st.sidebar.markdown(f"📊 **BMI:** {imc:.1f} ({clasificacion_imc})")

st.sidebar.markdown("---")

peso_ideal = st.sidebar.number_input(t["peso_ideal"], min_value=30.0, value=70.0, step=0.5)
meses_meta = st.sidebar.number_input(t["meses_meta"], min_value=1, value=3, step=1)

mantenimiento_estimado = peso_actual * 30
diferencia_peso = peso_actual - peso_ideal
total_dias_meta = meses_meta * 30

if diferencia_peso > 0:
    calorias_totales_cambio = diferencia_peso * 7700
    cambio_diario = calorias_totales_cambio / total_dias_meta
    meta_calorias_diarias = mantenimiento_estimado - cambio_diario
    st.sidebar.markdown(f"📉 {t['cambio_deficit'].format(val=cambio_diario)}")
    st.sidebar.markdown(f"🎯 **{t['meta_deficit']}** ~**{meta_calorias_diarias:.0f} kcal/día**")
elif diferencia_peso < 0:
    kilos_a_subir = abs(diferencia_peso)
    calorias_totales_cambio = kilos_a_subir * 7700
    cambio_diario = calorias_totales_cambio / total_dias_meta
    meta_calorias_diarias = mantenimiento_estimado + cambio_diario
    st.sidebar.markdown(f"📈 {t['cambio_superavit'].format(val=cambio_diario)}")
    st.sidebar.markdown(f"🎯 **{t['meta_superavit']}** ~**{meta_calorias_diarias:.0f} kcal/día**")
else:
    meta_calorias_diarias = mantenimiento_estimado
    st.sidebar.markdown(f"⚖️ {t['mantenimiento']}")
    st.sidebar.markdown(f"🎯 **{t['meta_mant']}** ~**{meta_calorias_diarias:.0f} kcal/día**")

meta_calorias_mensual = meta_calorias_diarias * 30
st.sidebar.markdown(f"📅 **Meta Mensual Total (30 días):** ~**{meta_calorias_mensual:.0f} kcal**")

st.sidebar.markdown("---")

st.sidebar.header(t["cheat_header"])
activar_cheat = st.sidebar.checkbox(t["cheat_checkbox"])
calorias_cheat_extra = 0
if activar_cheat:
    calorias_cheat_extra = st.sidebar.number_input(t["cheat_slider"], min_value=1000, max_value=20000, value=5000, step=500)

st.sidebar.markdown("---")
st.sidebar.header(t["armar_plato"])

texto_ingresado = st.sidebar.text_input(t["texto_plato"]).lower().strip()

calorias_plato_actual = 0
proteinas_plato_actual = 0
detalle_plato = {}

if texto_ingresado:
    alimentos_encontrados = []
    for alimento in base_datos_calorias.keys():
        if alimento in texto_ingresado:
            alimentos_encontrados.append(alimento)

    if not alimentos_encontrados and texto_ingresado:
        with st.spinner("Buscando..." if st.session_state.idioma == "es" else "Searching..."):
            info_web = buscar_alimento_internet(texto_ingresado)
            if info_web:
                base_datos_calorias[texto_ingresado] = info_web
                alimentos_encontrados.append(texto_ingresado)
                st.sidebar.success(t["alimento_encontrado"].format(item=texto_ingresado))

    if alimentos_encontrados:
        st.sidebar.markdown("---")
        st.sidebar.write("**Ajusta las cantidades (g o ml):**" if st.session_state.idioma == "es" else "**Adjust quantities (g or ml):**")

        for alimento in alimentos_encontrados:
            cantidad = st.sidebar.number_input(
                f"Cantidad de {alimento}:" if st.session_state.idioma == "es" else f"Amount of {alimento}:", 
                min_value=0.0, 
                value=100.0, 
                step=10.0, 
                key=f"qty_{alimento}"
            )

            cal_100 = base_datos_calorias[alimento]["calorias"]
            prot_100 = base_datos_calorias[alimento]["proteinas"]

            cal_total = (cal_100 * cantidad) / 100
            prot_total = (prot_100 * cantidad) / 100

            calorias_plato_actual += cal_total
            proteinas_plato_actual += prot_total
            detalle_plato[alimento] = cantidad

        nombre_comida = st.sidebar.text_input("Nombre de esta comida (ej. Almuerzo del 12):" if st.session_state.idioma == "es" else "Meal name (e.g. Lunch on the 12th):", value="Comida")
        if st.sidebar.button(t["btn_guardar"]):
            nombres_existentes = [c["nombre"].strip().lower() for c in lista_comidas]
            if nombre_comida.strip().lower() in nombres_existentes:
                st.sidebar.error(t["nombre_en_uso"])
            else:
                lista_comidas.append({
                    "nombre": nombre_comida,
                    "calorias": calorias_plato_actual,
                    "proteinas": proteinas_plato_actual,
                    "detalle": detalle_plato
                })
                guardar_datos_usuario_actual()
                st.sidebar.success("¡Guardado en el mes!" if st.session_state.idioma == "es" else "Saved to the month!")
    else:
        st.sidebar.warning(t["alimento_no_encontrado"])

# --- PANTALLA PRINCIPAL ---
st.subheader(t["resumen_plato"])

if detalle_plato:
    for alim, cant in detalle_plato.items():
        c_parcial = (base_datos_calorias[alim]["calorias"] * cant) / 100
        p_parcial = (base_datos_calorias[alim]["proteinas"] * cant) / 100
        st.write(f"- **{cant}g** de {alim} -> {c_parcial:.1f} kcal | {p_parcial:.1f}g prot")

    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Calorías del Plato" if st.session_state.idioma == "es" else "Meal Calories", f"{calorias_plato_actual:.1f} kcal")
    with col2:
        st.metric("Proteínas del Plato" if st.session_state.idioma == "es" else "Meal Protein", f"{proteinas_plato_actual:.1f} g")
else:
    st.info(t["ingresa_plato"])

st.markdown("---")

# --- SECCIÓN: CREAR ALIMENTOS PERSONALIZADOS (SOLO SI HAY SESIÓN INICIADA CON GOOGLE) ---
st.subheader("⭐ Mis Alimentos Personalizados (Exclusivo de tu Cuenta)")

if usuario_email is not None:
    st.success(f"🔓 Hola **{usuario_nombre}**: Aquí puedes registrar platos específicos (ej. *empanadas juanito*) para que solo aparezcan en tu buscador. Se guardan permanentemente en tu cuenta.")

    with st.form("form_alimento_personalizado"):
        nuevo_nombre = st.text_input("Nombre del plato o producto (ej: empanadas juanito):").lower().strip()
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            cal_por_100 = st.number_input("Calorías por cada 100g o 100ml:", min_value=0.0, value=250.0, step=5.0)
        with col_p2:
            prot_por_100 = st.number_input("Proteínas (g) por cada 100g o 100ml:", min_value=0.0, value=10.0, step=0.5)

        submit_personalizado = st.form_submit_button("➕ Guardar en mi cuenta")

        if submit_personalizado and nuevo_nombre:
            if nuevo_nombre in alimentos_propios:
                st.error(t["nombre_en_uso"])
            else:
                # Guardamos el alimento en el espacio privado y persistente del usuario
                alimentos_propios[nuevo_nombre] = {
                    "calorias": cal_por_100,
                    "proteinas": prot_por_100
                }
                guardar_datos_usuario_actual()
                st.success(f"¡'{nuevo_nombre}' ha sido agregado a tu lista personal! Ya puedes buscarlo en la barra lateral.")
                st.rerun()

    # Mostrar alimentos que ya haya registrado el usuario actual
    if alimentos_propios:
        st.write("📋 **Tus alimentos guardados actualmente:**")
        for ali, info in alimentos_propios.items():
            st.text(f"• {ali} -> {info['calorias']} kcal | {info['proteinas']}g prot (por 100g)")
else:
    st.info("🔒 **¿Quieres agregar tus propios platos (como las empanadas de tu local favorito)?** Inicia sesión con Google (botón en la barra lateral) para desbloquear tu espacio personal, guardado permanentemente en tu cuenta.")

st.markdown("---")

# --- MODO: CALCULADORA DE AGUA Y PASOS ---
st.subheader("💧 Activador de Calculadora de Hidratación y Pasos")

if "activar_calculadora_agua" not in st.session_state:
    st.session_state.activar_calculadora_agua = False

col_btn_agua1, col_btn_agua2 = st.columns(2)
with col_btn_agua1:
    if st.button("💧 Activar Calculadora de Agua y Pasos", use_container_width=True):
        st.session_state.activar_calculadora_agua = True
        st.rerun()
with col_btn_agua2:
    if st.button("❌ Desactivar Calculadora de Agua y Pasos", use_container_width=True):
        st.session_state.activar_calculadora_agua = False
        st.rerun()

if st.session_state.activar_calculadora_agua:
    st.info("✨ ¡Modo de salud y movimiento activado! Selecciona tu nivel de actividad física para calcular tu agua y pasos recomendados:")

    nivel_actividad_agua = st.selectbox(
        "¿Cuál es tu nivel de actividad física?",
        [
            "No hago actividad física",
            "Hago un poco / Me ejercito 2 veces a la semana",
            "Mucho / 4 o más veces a la semana"
        ],
        key="select_actividad_agua"
    )

    if st.button("🧮 Calcular mis metas diarias", use_container_width=True):
        ml_base = peso_actual * 35
        if sexo == "Masculino":
            ml_base += 200

        if "No hago" in nivel_actividad_agua:
            extra_actividad_agua = 0
        elif "2 veces" in nivel_actividad_agua:
            extra_actividad_agua = 400
        else:
            extra_actividad_agua = 800

        total_agua_ml = ml_base + extra_actividad_agua
        total_agua_litros = total_agua_ml / 1000
        vasos_estandar = round(total_agua_ml / 250)

        if "No hago" in nivel_actividad_agua:
            pasos_base = 6500
        elif "2 veces" in nivel_actividad_agua:
            pasos_base = 8500
        else:
            pasos_base = 11000

        if edad < 30:
            pasos_base += 500
        if sexo == "Masculino":
            pasos_base += 300

        st.success(f"🎯 **Resultados personalizados para ti ({peso_actual} kg | {edad} años | {sexo}):**")
        
        col_res1, col_res2 = st.columns(2)
        with col_res1:
            st.metric("Litros de Agua Recomendados", f"{total_agua_litros:.2f} L")
            st.write(f"💧 Aprox. **{vasos_estandar} vasos** diarios.")
        with col_res2:
            st.metric("Meta de Pasos Diarios", f"{pasos_base:,} pasos".replace(",", "."))
            st.write(f"🚶‍♂️ Ideal para mantener tu nivel de actividad.")

st.markdown("---")

# --- APARTADO: BALANCE TOTAL DEL MES ---
st.subheader(t["resumen_mes"])

total_calorias_registradas = sum(c["calorias"] for c in lista_comidas)
total_proteinas_mes = sum(c["proteinas"] for c in lista_comidas)

total_calorias_mes = total_calorias_registradas + (calorias_cheat_extra if activar_cheat else 0)

if lista_comidas or activar_cheat:
    col_d1, col_d2, col_d3 = st.columns(3)
    with col_d1:
        st.metric(t["total_cal"], f"{total_calorias_mes:.1f} kcal")
    with col_d2:
        st.metric(t["meta_mensual_txt"], f"{meta_calorias_mensual:.0f} kcal")
    with col_d3:
        st.metric(t["total_prot"], f"{total_proteinas_mes:.1f} g")

    diferencia_mensual = total_calorias_mes - meta_calorias_mensual

    if activar_cheat:
        st.error(f"🚨 **¡CHEAT MEALS ACUMULADOS EN EL MES!** Le sumaste +{calorias_cheat_extra} kcal extra al balance mensual. Todavía tienes semanas por delante para ajustar el ritmo y cumplir tu objetivo.")
    elif total_calorias_mes == 0:
        st.info("🍽️ Aún no tienes registros acumulados para este mes.")
    elif diferencia_mensual < -10000:
        st.warning("⚠️ Cuidado: el acumulado mensual está muy por debajo de la meta. Podrías arriesgar fatiga extrema o pérdida de masa muscular.")
    elif -10000 <= diferencia_mensual <= -2000:
        st.success("🔥 ¡Excelente balance mensual! Vas muy bien encaminado con tu déficit para quemar grasa de forma sostenible.")
    elif -2000 < diferencia_mensual < 2000:
        st.success("🎯 ¡Impecable! Tu balance de los 30 días está perfectamente alineado con tu objetivo.")
    elif 2000 <= diferencia_mensual <= 10000:
        st.warning("👀 Vas algo pasado en el acumulado del mes. Intenta moderar un poco las porciones en las próximas semanas.")
    else:
        st.error("🚨 ¡Superávit mensual desatado! Te pasaste harto del presupuesto de los 30 días. ¡A ajustar las comidas que quedan del mes!")

    if lista_comidas:
        st.write(f"### {t['desglose_comidas']}")

        for i, comida in enumerate(lista_comidas):
            col_exp, col_btn = st.columns([4, 1])

            with col_exp:
                with st.expander(f"📌 {comida['nombre']} ({comida['calorias']:.1f} kcal | {comida['proteinas']:.1f}g prot)"):
                    for ing, cant in comida["detalle"].items():
                        st.text(f"- {cant}g de {ing}")

            with col_btn:
                st.write("") 
                if st.button(t["borrar"], key=f"eliminar_{i}"):
                    lista_comidas.pop(i)
                    guardar_datos_usuario_actual()
                    st.rerun()

    st.markdown("---")
    if st.button(t["borrar_todo"]):
        lista_comidas.clear()
        guardar_datos_usuario_actual()
        st.rerun()
else:
    st.info(t["no_registros"])
