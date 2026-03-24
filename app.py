import streamlit as st
import json

st.set_page_config(page_title="Capítulo a Capítulo", layout="wide")

with open("books/quijote.json", "r", encoding="utf-8") as f:
    libro = json.load(f)

titulo = libro["titulo"]
partes = libro["partes"]

total_capitulos = sum(p["capitulos"] for p in partes)

if "leidos" not in st.session_state:
    st.session_state.leidos = [False] * total_capitulos

st.title("📖 Capítulo a Capítulo")
st.subheader(titulo)

leidos = sum(st.session_state.leidos)
progreso = leidos / total_capitulos

col1, col2, col3 = st.columns(3)

col1.metric("Capítulos leídos", f"{leidos}/{total_capitulos}")
col2.metric("Progreso", f"{int(progreso*100)}%")
col3.progress(progreso)

st.divider()

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
                
                if st.session_state.leidos[idx]:
                    columnas[j].markdown("🟩")
                else:
                    columnas[j].markdown("⬜")
    
    indice_global += caps
