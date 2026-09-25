# -*- coding: utf-8 -*-
import streamlit as st
import requests
import random

st.set_page_config(page_title="Calculadora Nutricional / Nutrition Calculator", page_icon="🥗")

# --- CONTROL DE SESIÓN DE USUARIO (GOOGLE O GUEST) ---
if "usuario_logueado" not in st.session_state:
    st.session_state.usuario_logueado = None

# --- PASO 1: SELECCIÓN DE IDIOMA Y LOGIN OPCIONAL DE GOOGLE ---
if "idioma" not in st.session_state:
    st.session_state.idioma = None

if st.session_state.idioma is None:
    st.title("🌐 Select your language / Selecciona tu idioma")
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
    st.write("¿Tienes una cuenta guardada o quieres sincronizar tu progreso?")
    
    # Botón opcional de inicio de sesión con Google
    if st.button("🔐 Iniciar sesión con Google (Opcional)", use_container_width=True):
        # Aquí se conectaría el flujo de OAuth de Google en producción
        st.session_state.usuario_logueado = "usuario_google@gmail.com"
        st.success("¡Sesión iniciada con éxito! Redirigiendo...")
        st.session_state.idioma = "es"  # Por defecto si entra por Google
        st.rerun()

    if st.session_state.usuario_logueado:
        st.info(f"Conectado como: **{st.session_state.usuario_logueado}**")

    st.stop()

# --- PASO 2: PREGUNTA DE NACIONALIDAD Y MODO PRESUPUESTO (SOLO SI ES ESPAÑOL/CHILE) ---
if "es_chileno" not in st.session_state:
    st.session_state.es_chileno = None

if "modo_presupuesto" not in st.session_state:
    st.session_state.modo_presupuesto = None

if st.session_state.es_chileno is None and st.session_state.idioma == "es":
    st.title("🇨🇱 Verificación de Nacionalidad")
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
    st.write("¿Quieres usar el **modo de presupuesto reducido**? Este modo intentará buscar opciones más baratas, saludables y acorde a tus gustos posibles para alcanzar tu objetivo, sugiriéndote por cada comida opciones basadas en un presupuesto diario que le des.")

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
    st.title("💡 Panel de Presupuesto Reducido (Chile)")
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
        "texto_plato": "Escribe tu plato (ej: arroz con carne en tiras y coca cola):",
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
        "alimento_encontrado": "¡'{item}' encontrado en la web!",
        "alimento_no_encontrado": "No encontré ese alimento ni en tu base de datos ni en internet.",
        "cambio_deficit": "Debes comer unos **{val:.0f} kcal menos** al día.",
        "meta_deficit": "Meta diaria sugerida (Déficit):",
        "cambio_superavit": "Debes comer unos **{val:.0f} kcal más** al día.",
        "meta_superavit": "Meta diaria sugerida (Volumen):",
        "mantenimiento": "Mantenimiento: Tu peso ideal es igual al actual.",
        "meta_mant": "Meta diaria sugerida:",
        "cheat_header": "🚨 Detector de Excesos / Cheat Meals del Mes",
        "cheat_checkbox": "¡Hubo descontrol o Cheat Meals acumulados en el mes!",
        "cheat_slider": "Estímese el exceso total aproximado en el mes (kcal extra):"
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
        "texto_plato": "Type your meal (e.g., rice with stripped meat and coke):",
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
        "alimento_encontrado": "'{item}' found on the web!",
        "alimento_no_encontrado": "I couldn't find that food in your database or on the web.",
        "cambio_deficit": "You should eat about **{val:.0f} fewer kcal** per day.",
        "meta_deficit": "Suggested daily target (Deficit):",
        "cambio_superavit": "You should eat about **{val:.0f} more kcal** per day.",
        "meta_superavit": "Suggested daily target (Surplus):",
        "mantenimiento": "Maintenance: Your ideal weight matches your current one.",
        "meta_mant": "Suggested daily target:",
        "cheat_header": "🚨 Excess / Monthly Cheat Meals Detector",
        "cheat_checkbox": "Extreme loss of control / Monthly Cheat Meals!",
        "cheat_slider": "Estimate approximate total excess (extra kcal):"
    }
}

t = textos[st.session_state.idioma]

st.title(t["titulo"])

if st.sidebar.button("🌐 Cambiar Idioma / Salir"):
    st.session_state.idioma = None
    st.session_state.es_chileno = None
    st.session_state.modo_presupuesto = None
    st.session_state.usuario_logueado = None
    st.rerun()

# Base de datos completa (valores por cada 100 gramos o ml) - Con mantequilla mix
base_datos_calorias = {
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

if "comidas_registradas" not in st.session_state:
    st.session_state.comidas_registradas = []

# --- APARTADO DE METAS Y PERFIL EN LA BARRA LATERAL ---
st.sidebar.header(t["sidebar_meta"])
if st.session_state.usuario_logueado:
    st.sidebar.success(f"👤 Sesión: {st.session_state.usuario_logueado}")

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
            st.session_state.comidas_registradas.append({
                "nombre": nombre_comida,
                "calorias": calorias_plato_actual,
                "proteinas": proteinas_plato_actual,
                "detalle": detalle_plato
            })
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

total_calorias_registradas = sum(c["calorias"] for c in st.session_state.comidas_registradas)
total_proteinas_mes = sum(c["proteinas"] for c in st.session_state.comidas_registradas)

total_calorias_mes = total_calorias_registradas + (calorias_cheat_extra if activar_cheat else 0)

if st.session_state.comidas_registradas or activar_cheat:
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

    if st.session_state.comidas_registradas:
        st.write(f"### {t['desglose_comidas']}")

        for i, comida in enumerate(st.session_state.comidas_registradas):
            col_exp, col_btn = st.columns([4, 1])

            with col_exp:
                with st.expander(f"📌 {comida['nombre']} ({comida['calorias']:.1f} kcal | {comida['proteinas']:.1f}g prot)"):
                    for ing, cant in comida["detalle"].items():
                        st.text(f"- {cant}g de {ing}")

            with col_btn:
                st.write("") 
                if st.button(t["borrar"], key=f"eliminar_{i}"):
                    st.session_state.comidas_registradas.pop(i)
                    st.rerun()

    st.markdown("---")
    if st.button(t["borrar_todo"]):
        st.session_state.comidas_registradas = []
        st.rerun()
else:
    st.info(t["no_registros"])
