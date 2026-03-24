import streamlit as st
import json

st.set_page_config(page_title="Capítulo a Capítulo", layout="wide")

st.title("📖 Capítulo a Capítulo")

# -------- CONFIGURACIÓN DEL LIBRO --------
st.sidebar.header("📚 Configuración del libro")

titulo = st.sidebar.text_input("Título del libro", "Mi libro")

num_partes = st.sidebar.number_input("Número de partes", 1, 10, 2)

partes = []
total_capitulos = 0

for i in range(num_partes):
    caps = st.sidebar.number_input(f"Capítulos Parte {i+1}", 1, 200, 10)
    partes.append({"nombre": f"Parte {i+1}", "capitulos": caps})
    total_capitulos += caps

# -------- CARGAR PROGRESO --------
uploaded = st.sidebar.file_uploader("Cargar progreso (JSON)", type="json")

if uploaded:
    data = json.load(uploaded)
    st.session_state.leidos = data["leidos"]
else:
    if "leidos" not in st.session_state or len(st.session_state.leidos) != total_capitulos:
        st.session_state.leidos = [False] * total_capitulos

# -------- DASHBOARD --------
leidos = sum(st.session_state.leidos)
progreso = leidos / total_capitulos if total_capitulos else 0

st.subheader(titulo)

col1, col2, col3 = st.columns(3)
col1.metric("Capítulos leídos", f"{leidos}/{total_capitulos}")
col2.metric("Progreso", f"{int(progreso*100)}%")
col3.progress(progreso)

st.divider()

# -------- CUADRÍCULA --------
indice_global = 0

for parte in partes:
    st.markdown(f"### {parte['nombre']}")
    
    caps = parte["capitulos"]
    cols = 10
    
    for i in range(0, caps, cols):
        columnas = st.columns(cols)
        
        for j in range(cols):
            idx = indice_global + i + j
            
            if idx < indice_global + caps:
                if columnas[j].button(f"{(i+j)+1}", key=f"cap_{idx}"):
                    st.session_state.leidos[idx] = not st.session_state.leidos[idx]
                    st.rerun()
                
                if st.session_state.leidos[idx]:
                    columnas[j].markdown("🟩")
                else:
                    columnas[j].markdown("⬜")
    
    indice_global += caps

# -------- DESCARGAR PROGRESO --------
st.sidebar.download_button(
    label="💾 Descargar progreso",
    data=json.dumps({"leidos": st.session_state.leidos}),
    file_name="progreso_lectura.json",
    mime="application/json"
)
