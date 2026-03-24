import streamlit as st
import json
from supabase import create_client

SUPABASE_URL = "https://dtlynhkxnqbfnjvfecuu.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImR0bHluaGt4bnFiZm5qdmZlY3V1Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzQzNzE3MjYsImV4cCI6MjA4OTk0NzcyNn0.uKTWukZzO5IshkNxsFu8wOC-y8UTTbPRlRI7X6IzxE4"

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.title("📖 Capítulo a Capítulo")

if "user" not in st.session_state:
    st.session_state.user = None

if not st.session_state.user:
    st.subheader("Login / Registro")

    email = st.text_input("Email")
    password = st.text_input("Password", type="password")

    col1, col2 = st.columns(2)

    if col1.button("Login"):
        try:
            res = supabase.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            st.session_state.user = res.user
            st.rerun()
        except Exception as e:
            st.error("Error en login")

    if col2.button("Registrarse"):
        try:
            supabase.auth.sign_up({
                "email": email,
                "password": password
            })
            st.success("Usuario creado. Ahora puedes hacer login.")
        except:
            st.error("Error al registrar")

    st.stop()

user = st.session_state.user

st.sidebar.success(f"Conectado como {user.email}")

if st.sidebar.button("Cerrar sesión"):
    st.session_state.user = None
    st.rerun()

st.sidebar.header("📚 Nuevo libro")

titulo = st.sidebar.text_input("Título del libro")

num_partes = st.sidebar.number_input("Número de partes", 1, 10, 1)

partes = []
total_capitulos = 0

for i in range(num_partes):
    caps = st.sidebar.number_input(f"Capítulos Parte {i+1}", 1, 200, 10)
    partes.append({"nombre": f"Parte {i+1}", "capitulos": caps})
    total_capitulos += caps

if st.sidebar.button("Guardar libro"):
    supabase.table("books").insert({
        "user_id": user.id,
        "title": titulo,
        "structure": partes
    }).execute()
    st.sidebar.success("Libro guardado")

res = supabase.table("books").select("*").eq("user_id", user.id).execute()
books = res.data

if not books:
    st.info("Crea tu primer libro en el menú lateral")
    st.stop()

book_titles = [b["title"] for b in books]

selected_title = st.selectbox("Selecciona un libro", book_titles)

selected_book = next(b for b in books if b["title"] == selected_title)

partes = selected_book["structure"]
book_id = selected_book["id"]

total_capitulos = sum(p["capitulos"] for p in partes)

res = supabase.table("progress").select("*") \
    .eq("user_id", user.id) \
    .eq("book_id", book_id) \
    .execute()

if res.data:
    st.session_state.leidos = res.data[0]["data"]
else:
    st.session_state.leidos = [False] * total_capitulos



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

                supabase.table("progress").upsert({
                    "user_id": user.id,
                    "book_id": book_id,
                    "data": st.session_state.leidos
                }).execute()

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
