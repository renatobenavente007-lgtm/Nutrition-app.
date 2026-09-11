# -*- coding: utf-8 -*-
import streamlit as st
import requests

st.set_page_config(page_title="Calculadora Nutricional", page_icon="🥗")

st.title("🥗 Mi Calculadora de Calorías y Proteínas")

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
st.sidebar.header("🎯 Tu Perfil y Meta de Peso")
peso_actual = st.sidebar.number_input("¿Cuál es tu peso actual (kg)?", min_value=30.0, value=75.0, step=0.5)
altura_cm = st.sidebar.number_input("¿Cuál es tu altura (cm)?", min_value=100.0, value=175.0, step=1.0)
sexo = st.sidebar.selectbox("Sexo", ["Masculino", "Femenino"])
edad = st.sidebar.number_input("Edad (años)", min_value=10, max_value=120, value=18, step=1)

# Cálculo del Índice de Masa Corporal (IMC)
altura_m = altura_cm / 100.0
imc = peso_actual / (altura_m ** 2)

if imc < 18.5:
    clasificacion_imc = "Bajo peso"
elif 18.5 <= imc < 25:
    clasificacion_imc = "Peso normal (saludable)"
elif 25 <= imc < 30:
    clasificacion_imc = "Sobrepeso"
else:
    clasificacion_imc = "Obesidad"

st.sidebar.markdown(f"📊 **IMC:** {imc:.1f} ({clasificacion_imc})")
st.sidebar.markdown("---")

peso_ideal = st.sidebar.number_input("¿Cuál sería tu peso ideal (kg)?", min_value=30.0, value=70.0, step=0.5)
semanas_meta = st.sidebar.number_input("¿En cuántas semanas esperas obtenerlo?", min_value=1, value=10, step=1)

# Cálculo de calorías según la meta (1kg de cambio aprox. 7700 kcal)
mantenimiento_estimado = peso_actual * 30
diferencia_peso = peso_actual - peso_ideal  # Positivo = Bajar, Negativo = Subir

if diferencia_peso > 0:
    # Déficit (Bajar de peso)
    calorias_totales = diferencia_peso * 7700
    cambio_diario = calorias_totales / (semanas_meta * 7)
    meta_calorias_diarias = mantenimiento_estimado - cambio_diario
    
    st.sidebar.markdown(f"📉 **Cálculo:** Debes comer unos **{cambio_diario:.0f} kcal menos** al día.")
    st.sidebar.markdown(f"🎯 **Meta diaria sugerida (Déficit):** ~**{meta_calorias_diarias:.0f} kcal**")

elif diferencia_peso < 0:
    # Superávit (Subir de peso)
    kilos_a_subir = abs(diferencia_peso)
    calorias_totales = kilos_a_subir * 7700
    cambio_diario = calorias_totales / (semanas_meta * 7)
    meta_calorias_diarias = mantenimiento_estimado + cambio_diario
    
    st.sidebar.markdown(f"📈 **Cálculo:** Debes comer unos **{cambio_diario:.0f} kcal más** al día.")
    st.sidebar.markdown(f"🎯 **Meta diaria sugerida (Volumen):** ~**{meta_calorias_diarias:.0f} kcal**")

else:
    # Mantenimiento
    meta_calorias_diarias = mantenimiento_estimado
    st.sidebar.markdown(f"⚖️ **Mantenimiento:** Tu peso ideal es igual al actual.")
    st.sidebar.markdown(f"🎯 **Meta diaria sugerida:** ~**{meta_calorias_diarias:.0f} kcal**")

st.sidebar.markdown("---")
st.sidebar.header("🍽️ Armar Plato Actual")

# Pregunta de cuántas comidas comiste hoy
cantidad_comidas_hoy = st.sidebar.number_input("¿Cuántas comidas comiste hoy?", min_value=1, value=3, step=1)

# Campo de texto libre para escribir lo que quieras comer combinado
texto_ingresado = st.sidebar.text_input("Escribe tu plato (ej: arroz con carne en tiras y coca cola):").lower().strip()

calorias_plato_actual = 0
proteinas_plato_actual = 0
detalle_plato = {}

if texto_ingresado:
    alimentos_encontrados = []
    for alimento in base_datos_calorias.keys():
        if alimento in texto_ingresado:
            alimentos_encontrados.append(alimento)
    
    # Si no se encuentra localmente, buscar en internet
    if not alimentos_encontrados and texto_ingresado:
        with st.spinner(f"Buscando '{texto_ingresado}' en internet..."):
            info_web = buscar_alimento_internet(texto_ingresado)
            if info_web:
                base_datos_calorias[texto_ingresado] = info_web
                alimentos_encontrados.append(texto_ingresado)
                st.sidebar.success(f"¡'{texto_ingresado}' encontrado en la web!")
    
    if alimentos_encontrados:
        st.sidebar.markdown("---")
        st.sidebar.write("**Ajusta las cantidades (g o ml) para cada uno:**")
        
        for alimento in alimentos_encontrados:
            cantidad = st.sidebar.number_input(
                f"Cantidad de {alimento}:", 
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

        nombre_comida = st.sidebar.text_input("Nombre de esta comida (ej. Almuerzo, Once):", value="Comida")
        if st.sidebar.button("📥 Guardar esta comida en el día"):
            st.session_state.comidas_registradas.append({
                "nombre": nombre_comida,
                "calorias": calorias_plato_actual,
                "proteinas": proteinas_plato_actual,
                "detalle": detalle_plato
            })
            st.sidebar.success(f"¡'{nombre_comida}' guardada con éxito!")
    else:
        st.sidebar.warning("No encontré ese alimento ni en tu base de datos ni en internet.")

# --- PANTALLA PRINCIPAL ---
st.subheader("📊 Resumen del Plato Actual")

if detalle_plato:
    for alim, cant in detalle_plato.items():
        c_parcial = (base_datos_calorias[alim]["calorias"] * cant) / 100
        p_parcial = (base_datos_calorias[alim]["proteinas"] * cant) / 100
        st.write(f"- **{cant}g** de {alim} -> {c_parcial:.1f} kcal | {p_parcial:.1f}g prot")
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Calorías del Plato", f"{calorias_plato_actual:.1f} kcal")
    with col2:
        st.metric("Proteínas del Plato", f"{proteinas_plato_actual:.1f} g")
else:
    st.info("Escribe tu plato en la barra lateral para comenzar a calcular.")

st.markdown("---")

# --- APARTADO: TOTAL DEL DÍA ---
st.subheader("📅 Registro Total de Hoy")

if st.session_state.comidas_registradas:
    total_calorias_dia = sum(c["calorias"] for c in st.session_state.comidas_registradas)
    total_proteinas_dia = sum(c["proteinas"] for c in st.session_state.comidas_registradas)

    col_d1, col_d2 = st.columns(2)
    with col_d1:
        st.metric("🔥 Total Calorías del Día", f"{total_calorias_dia:.1f} kcal")
    with col_d2:
        st.metric("💪 Total Proteínas del Día", f"{total_proteinas_dia:.1f} g")

    # Evaluación respecto a la meta de calorías diarias (margen de +/- 20 kcal)
    diferencia_meta = total_calorias_dia - meta_calorias_diarias
    if abs(diferencia_meta) <= 20:
        st.success("🎉 ¡Muy bien hecho! Lo lograste o estás muy cerca.")
    else:
        st.warning("💪 Sigue así, mañana lo lograrás.")

    st.write(f"### Desglose de tus {cantidad_comidas_hoy} comidas planificadas para hoy:")
    
    for i, comida in enumerate(st.session_state.comidas_registradas):
        col_exp, col_btn = st.columns([4, 1])
        
        with col_exp:
            with st.expander(f"📌 {comida['nombre']} ({comida['calorias']:.1f} kcal | {comida['proteinas']:.1f}g prot)"):
                for ing, cant in comida["detalle"].items():
                    st.text(f"- {cant}g de {ing}")
                    
        with col_btn:
            st.write("") 
            if st.button("❌ Borrar", key=f"eliminar_{i}"):
                st.session_state.comidas_registradas.pop(i)
                st.rerun()

    st.markdown("---")
    if st.button("🗑️ Borrar todo el registro del día"):
        st.session_state.comidas_registradas = []
        st.rerun()
else:
    st.info(f"Tienes presupuestado hacer {cantidad_comidas_hoy} comidas hoy. Aún no has guardado ninguna.")