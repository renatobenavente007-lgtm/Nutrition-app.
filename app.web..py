# -*- coding: utf-8 -*-
import streamlit as st
import requests
import random

st.set_page_config(page_title="Calculadora Nutricional / Nutrition Calculator", page_icon="🥗")

# --- PASO 1: SELECCIÓN DE IDIOMA SI NO EXISTE EN LA SESIÓN ---
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
        if st.button("🇺🇸 English", use_container_width=True):
            st.session_state.idioma = "en"
            st.rerun()
            
    # Detenemos la ejecución aquí hasta que elijan un idioma
    st.stop()

# --- PASO 2: DICCIONARIOS DE TEXTOS SEGÚN EL IDIOMA ---
textos = {
    "es": {
        "titulo": "🥗 Mi Calculadora de Calorías y Proteínas",
        "sidebar_meta": "🎯 Tu Perfil y Meta de Peso",
        "peso_actual": "¿Cuál es tu peso actual (kg)?",
        "altura": "¿Cuál es tu altura (cm)?",
        "sexo": "Sexo",
        "opciones_sexo": ["Masculino", "Femenino"],
        "edad": "Edad (años)",
        "peso_ideal": "¿Cuál sería tu peso ideal (kg)?",
        "semanas_meta": "¿En cuántas semanas esperas obtenerlo?",
        "armar_plato": "🍽️ Armar Plato Actual",
        "cant_comidas": "¿Cuántas comidas comiste hoy?",
        "texto_plato": "Escribe tu plato (ej: arroz con carne en tiras y coca cola):",
        "btn_guardar": "📥 Guardar esta comida en el día",
        "resumen_plato": "📊 Resumen del Plato Actual",
        "resumen_dia": "📅 Registro Total de Hoy",
        "total_cal": "🔥 Total Calorías del Día",
        "total_prot": "💪 Total Proteínas del Día",
        "desglose_comidas": "Desglose de tus {n} comidas planificadas para hoy:",
        "borrar": "❌ Borrar",
        "borrar_todo": "🗑️ Borrar todo el registro del día",
        "no_registros": "Tienes presupuestado hacer {n} comidas hoy. Aún no has guardado ninguna.",
        "ingresa_plato": "Escribe tu plato en la barra lateral para comenzar a calcular.",
        "alimento_encontrado": "¡'{item}' encontrado en la web!",
        "alimento_no_encontrado": "No encontré ese alimento ni en tu base de datos ni en internet.",
        "cambio_deficit": "Debes comer unos **{val:.0f} kcal menos** al día.",
        "meta_deficit": "Meta diaria sugerida (Déficit):",
        "cambio_superavit": "Debes comer unos **{val:.0f} kcal más** al día.",
        "meta_superavit": "Meta diaria sugerida (Volumen):",
        "mantenimiento": "Mantenimiento: Tu peso ideal es igual al actual.",
        "meta_mant": "Meta diaria sugerida:"
    },
    "en": {
        "titulo": "🥗 My Calorie & Protein Calculator",
        "sidebar_meta": "🎯 Your Profile & Weight Goal",
        "peso_actual": "What is your current weight (kg)?",
        "altura": "What is your height (cm)?",
        "sexo": "Gender",
        "opciones_sexo": ["Male", "Female"],
        "edad": "Age (years)",
        "peso_ideal": "What would be your ideal weight (kg)?",
        "semanas_meta": "In how many weeks do you expect to reach it?",
        "armar_plato": "🍽️ Build Current Meal",
        "cant_comidas": "How many meals did you eat today?",
        "texto_plato": "Type your meal (e.g., rice with stripped meat and coke):",
        "btn_guardar": "📥 Save this meal for today",
        "resumen_plato": "📊 Current Meal Summary",
        "resumen_dia": "📅 Today's Total Log",
        "total_cal": "🔥 Total Daily Calories",
        "total_prot": "💪 Total Daily Protein",
        "desglose_comidas": "Breakdown of your {n} planned meals for today:",
        "borrar": "❌ Delete",
        "borrar_todo": "🗑️ Clear all today's logs",
        "no_registros": "You have budgeted {n} meals today. You haven't saved any yet.",
        "ingresa_plato": "Type your meal in the sidebar to start calculating.",
        "alimento_encontrado": "'{item}' found on the web!",
        "alimento_no_encontrado": "I couldn't find that food in your database or on the web.",
        "cambio_deficit": "You should eat about **{val:.0f} fewer kcal** per day.",
        "meta_deficit": "Suggested daily target (Deficit):",
        "cambio_superavit": "You should eat about **{val:.0f} more kcal** per day.",
        "meta_superavit": "Suggested daily target (Surplus):",
        "mantenimiento": "Maintenance: Your ideal weight matches your current one.",
        "meta_mant": "Suggested daily target:"
    }
}

t = textos[st.session_state.idioma]

st.title(t["titulo"])

# Botón para cambiar de idioma arriba a la derecha o en un lugar visible
if st.sidebar.button("🌐 Cambiar Idioma / Change Language"):
    st.session_state.idioma = None
    st.rerun()

# Base de datos completa (valores por cada 100 gramos o ml)
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

# Función para buscar alimentos en internet (Open Food Facts API)
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

# Inicializar la memoria del día si no existe
if "comidas_registradas" not in st.session_state:
    st.session_state.comidas_registradas = []

# --- APARTADO DE METAS Y PERFIL EN LA BARRA LATERAL ---
st.sidebar.header(t["sidebar_meta"])
peso_actual = st.sidebar.number_input(t["peso_actual"], min_value=30.0, value=75.0, step=0.5)
altura_cm = st.sidebar.number_input(t["altura"], min_value=100.0, value=175.0, step=1.0)
sexo = st.sidebar.selectbox(t["sexo"], t["opciones_sexo"])
edad = st.sidebar.number_input(t["edad"], min_value=10, max_value=120, value=18, step=1)

# Cálculo del Índice de Masa Corporal (IMC)
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
semanas_meta = st.sidebar.number_input(t["semanas_meta"], min_value=1, value=10, step=1)

# Cálculo de calorías según la meta (1kg de cambio aprox. 7700 kcal)
mantenimiento_estimado = peso_actual * 30
diferencia_peso = peso_actual - peso_ideal  # Positivo = Bajar, Negativo = Subir

if diferencia_peso > 0:
    calorias_totales = diferencia_peso * 7700
    cambio_diario = calorias_totales / (semanas_meta * 7)
    meta_calorias_diarias = mantenimiento_estimado - cambio_diario
    
    st.sidebar.markdown(f"📉 {t['cambio_deficit'].format(val=cambio_diario)}")
    st.sidebar.markdown(f"🎯 **{t['meta_deficit']}** ~**{meta_calorias_diarias:.0f} kcal**")

elif diferencia_peso < 0:
    kilos_a_subir = abs(diferencia_peso)
    calorias_totales = kilos_a_subir * 7700
    cambio_diario = calorias_totales / (semanas_meta * 7)
    meta_calorias_diarias = mantenimiento_estimado + cambio_diario
    
    st.sidebar.markdown(f"📈 {t['cambio_superavit'].format(val=cambio_diario)}")
    st.sidebar.markdown(f"🎯 **{t['meta_superavit']}** ~**{meta_calorias_diarias:.0f} kcal**")

else:
    meta_calorias_diarias = mantenimiento_estimado
    st.sidebar.markdown(f"⚖️ {t['mantenimiento']}")
    st.sidebar.markdown(f"🎯 **{t['meta_mant']}** ~**{meta_calorias_diarias:.0f} kcal**")

st.sidebar.markdown("---")
st.sidebar.header(t["armar_plato"])

cantidad_comidas_hoy = st.sidebar.number_input(t["cant_comidas"], min_value=1, value=3, step=1)
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

        nombre_comida = st.sidebar.text_input("Nombre de esta comida (ej. Almuerzo):" if st.session_state.idioma == "es" else "Meal name (e.g. Lunch):", value="Comida")
        if st.sidebar.button(t["btn_guardar"]):
            st.session_state.comidas_registradas.append({
                "nombre": nombre_comida,
                "calorias": calorias_plato_actual,
                "proteinas": proteinas_plato_actual,
                "detalle": detalle_plato
            })
            st.sidebar.success("¡Guardado con éxito!" if st.session_state.idioma == "es" else "Saved successfully!")
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

# --- APARTADO: TOTAL DEL DÍA ---
st.subheader(t["resumen_dia"])

if st.session_state.comidas_registradas:
    total_calorias_dia = sum(c["calorias"] for c in st.session_state.comidas_registradas)
    total_proteinas_dia = sum(c["proteinas"] for c in st.session_state.comidas_registradas)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.metric(t["total_cal"], f"{total_calorias_dia:.1f} kcal")
    with col_d2:
        st.metric(t["total_prot"], f"{total_proteinas_dia:.1f} g")

    # --- EVALUACIÓN INTELIGENTE CON FRASES ALEATORIAS (ES/EN) ---
    diferencia = total_calorias_dia - meta_calorias_diarias

    if total_calorias_dia == 0:
        mensajes = [
            "🍽️ Aún no registras nada hoy. ¡Empieza a sumar combustible!" if st.session_state.idioma == "es" else "🍽️ No meals logged today yet. Start adding fuel!",
            "👻 Tu registro está vacío. ¡A anotar se ha dicho!" if st.session_state.idioma == "es" else "👻 Your log is empty. Time to log some food!"
        ]
        st.info(random.choice(mensajes))

    elif diferencia < -400:
        mensajes = [
            "⚠️ ¡Estás comiendo demasiado poco! Súbele un poco más." if st.session_state.idioma == "es" else "⚠️ You are eating way too much below your target! Eat a bit more.",
            "🛑 Ojo: déficit muy agresivo, puedes perder músculo." if st.session_state.idioma == "es" else "🛑 Careful: very aggressive deficit, you might lose muscle."
        ]
        st.warning(random.choice(mensajes))

    elif -400 <= diferencia <= -150:
        mensajes = [
            "🔥 Buen ritmo de déficit. Zona ideal para quemar grasa." if st.session_state.idioma == "es" else "🔥 Good deficit pace. Ideal zone to burn fat.",
            "⚡ Excelente control de calorías." if st.session_state.idioma == "es" else "⚡ Excellent calorie control."
        ]
        st.success(random.choice(mensajes))

    elif -150 < diferencia < 150:
        mensajes = [
            "🎯 ¡Impecable! Números exactos." if st.session_state.idioma == "es" else "🎯 Spot on! Exact numbers.",
            "⚖️ Equilibrio absoluto hoy." if st.session_state.idioma == "es" else "⚖️ Absolute balance today."
        ]
        st.success(random.choice(mensajes))

    elif 150 <= diferencia <= 400:
        mensajes = [
            "👀 Te pasaste un poquito, ojo con el picoteo." if st.session_state.idioma == "es" else "👀 Went slightly over, watch out for evening snacking.",
            "⚠️ Leve exceso de calorías, nada grave." if st.session_state.idioma == "es" else "⚠️ Slight calorie excess, nothing major."
        ]
        st.warning(random.choice(mensajes))

    else:
        mensajes = [
            "🚨 ¡Alerta roja! Te pasaste harto hoy. Mañana se compensa." if st.session_state.idioma == "es" else "🚨 Red alert! Went way over today. Balance it tomorrow.",
            "🍔 Hubo banquete hoy. ¡A entrenar fuerte mañana!" if st.session_state.idioma == "es" else "🍔 Feast day today. Hit the gym hard tomorrow!"
        ]
        st.error(random.choice(mensajes))
    # -------------------------------------------------------------

    st.write(f"### {t['desglose_comidas'].format(n=cantidad_comidas_hoy)}")
    
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
    st.info(t["no_registros"].format(n=cantidad_comidas_hoy))
    st.info(f"Tienes presupuestado hacer {cantidad_comidas_hoy} comidas hoy. Aún no has guardado ninguna.")
