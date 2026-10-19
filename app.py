import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="Depósito Bastías", page_icon="🦋", layout="centered")

# ==========================================
# CONFIGURACIÓN DE TU EXCEL (Nombres Reales)
# ==========================================
COL_NOMBRE = "Artículo - Desc. Gen."
COL_CODIGO_BEJ = "Stock - Artículo - Cód. Gen."
COL_CODIGO_PROV = "Codigo Proveedor"
COL_LOTE = "Stock - Partida - Cód."
COL_VENC = "Stock - Partida - F. Vto. / Ingreso"
COL_CANT = "Stock - Partida - Cant. Real en UM 1"

# ==========================================
# FUNCIÓN PARA LEER LA BASE DE DATOS REAL
# ==========================================
@st.cache_data
def cargar_bd():
    if os.path.exists("base_datos_actual.xlsx"):
        try:
            df = pd.read_excel("base_datos_actual.xlsx")
            return df
        except Exception as e:
            st.error(f"Error al leer el archivo: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

# ==========================================
# BASE DE DATOS USUARIOS Y TAREAS
# ==========================================
USUARIOS = {
    "Leandro": {"clave": "admin123", "rol": "Admin"},
    "Dani": {"clave": "dani123", "rol": "Empleado"},
    "Invitado": {"clave": "invitado123", "rol": "Invitado"}
}

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None
    st.session_state["rol"] = None
    st.session_state["pantalla"] = "stock"
    st.session_state["tareas"] = [
        {"id": 1, "texto": "Armar pedido para Farmacia Centro", "hecha": False, "vista": False}
    ]

def cambiar_pantalla(nueva_pantalla):
    st.session_state["pantalla"] = nueva_pantalla

# ==========================================
# INYECCIÓN DE DISEÑO (CSS)
# ==========================================
def aplicar_estilos_segun_usuario():
    rol = st.session_state["rol"]
    if rol == "Empleado":
        st.markdown("""
            <style>
            html, body, p, div, input, label, select { font-size: 22px !important; }
            h1 { font-size: 45px !important; }
            h2 { font-size: 35px !important; }
            h3 { font-size: 30px !important; }
            .stButton > button { height: 70px !important; font-size: 22px !important; font-weight: bold !important; border-radius: 10px !important; }
            @keyframes parpadeo {
                0% { background-color: #ff4b4b; color: white; border-color: #ff4b4b; }
                50% { background-color: transparent; color: #ff4b4b; border-color: #ff4b4b; }
                100% { background-color: #ff4b4b; color: white; border-color: #ff4b4b; }
            }
            div[data-testid="stSidebar"] button[kind="primary"] {
                animation: parpadeo 1.5s infinite; height: 90px !important; font-size: 24px !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<style>.stButton > button { font-weight: bold; }</style>", unsafe_allow_html=True)

# ==========================================
# PANTALLAS
# ==========================================
def mostrar_login():
    st.title("🦋 Sistema de Depósito")
    st.write("Iniciá sesión para continuar.")
    
    usuario = st.text_input("Usuario")
    clave = st.text_input("Contraseña", type="password")
    
    if st.button("Ingresar", type="primary"):
        if usuario in USUARIOS and USUARIOS[usuario]["clave"] == clave:
            st.session_state["usuario_actual"] = usuario
            st.session_state["rol"] = USUARIOS[usuario]["rol"]
            st.session_state["pantalla"] = "stock"
            st.rerun()
        else:
            st.error("Usuario o contraseña incorrectos ❌")

def mostrar_sistema():
    aplicar_estilos_segun_usuario()
    rol = st.session_state["rol"]
    nombre = st.session_state["usuario_actual"]
    
    tareas_pendientes = [t for t in st.session_state["tareas"] if not t["hecha"]]
    hay_pendientes = len(tareas_pendientes) > 0

    with st.sidebar:
        st.title(f"Hola, {nombre} 👋")
        st.write("---")
        
        if st.button("📦 Buscador de Stock", use_container_width=True):
            cambiar_pantalla("stock")
            st.rerun()

        if rol == "Empleado":
            if hay_pendientes:
                if st.button("⚠️ VER TAREAS", type="primary", use_container_width=True):
                    cambiar_pantalla("tareas")
                    st.rerun()
            else:
                if st.button("📋 Ver Tareas", use_container_width=True):
                    cambiar_pantalla("tareas")
                    st.rerun()
        elif rol == "Admin":
            if st.button("📋 Ver Tareas", use_container_width=True):
                cambiar_pantalla("tareas")
                st.rerun()

        st.write("---")
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state["usuario_actual"] = None
            st.session_state["rol"] = None
            st.rerun()

    # --- PANTALLA 1: STOCK ---
    if st.session_state["pantalla"] == "stock":
        st.header("📦 Buscador de Stock")
        
        busqueda = st.text_input("🔍 Buscar por Nombre, Cód. Bejerman o Cód. Proveedor...")
        
        if busqueda:
            df = cargar_bd()
            
            if df.empty:
                st.warning("⚠️ No hay base de datos cargada. Subí el Excel desde el panel inferior.")
            else:
                mask = df[COL_NOMBRE].astype(str).str.contains(busqueda, case=False, na=False) | \
                       df[COL_CODIGO_BEJ].astype(str).str.contains(busqueda, case=False, na=False)
                
                if COL_CODIGO_PROV in df.columns:
                    mask = mask | df[COL_CODIGO_PROV].astype(str).str.contains(busqueda, case=False, na=False)
                
                resultados = df[mask]
                
                if resultados.empty:
                    st.error("No se encontró ningún artículo con ese dato.")
                else:
                    opciones = resultados[COL_CODIGO_BEJ].astype(str) + " - " + resultados[COL_NOMBRE].astype(str)
                    opciones_unicas = opciones.unique()
                    
                    st.write("---")
                    articulo_elegido = st.selectbox("🎯 Resultados encontrados (Seleccioná el correcto):", opciones_unicas)
                    
                    if articulo_elegido:
                        # Filtramos solo el articulo que elegiste
                        df_exacto = resultados[opciones == articulo_elegido].copy()
                        
                        # Nos aseguramos que las cantidades sean números
                        df_exacto[COL_CANT] = pd.to_numeric(df_exacto[COL_CANT], errors='coerce').fillna(0)
                        
                        # Sumamos la cantidad de todas las partidas
                        total = df_exacto[COL_CANT].sum()
                        
                        # Mostramos el cartel de total
                        if total > 0:
                            st.success(f"**TOTAL DISPONIBLE: {total:g} unidades**")
                        else:
                            st.error("**SIN STOCK DISPONIBLE (0 unidades)**")
                        
                        # --- ACÁ ESTÁ LA MAGIA NUEVA ---
                        # Filtramos para quedarnos SOLO con las partidas que tengan más de 0
                        df_con_stock = df_exacto[df_exacto[COL_CANT] > 0]
                        
                        st.write("Desglose por Partidas (solo partidas con stock):")
                        if df_con_stock.empty:
                            st.info("No hay partidas con stock positivo para mostrar.")
                        else:
                            # Preparamos la tabla limpia
                            df_lotes = df_con_stock[[COL_LOTE, COL_VENC, COL_CANT]].copy()
                            df_lotes = df_lotes.rename(columns={
                                COL_LOTE: "Partida",
                                COL_VENC: "Vencimiento",
                                COL_CANT: "Cantidad"
                            })
                            
                            st.dataframe(df_lotes, use_container_width=True, hide_index=True)

        if rol == "Admin":
            st.write("---")
            st.subheader("⚙️ Actualizar Base de Datos")
            archivo_db = st.file_uploader("Seleccioná tu archivo actualizado (.xlsx)", type=["xlsx"])
            if archivo_db:
                with open("base_datos_actual.xlsx", "wb") as f:
                    f.write(archivo_db.getbuffer())
                st.cache_data.clear()
                st.success("✅ ¡Base de datos subida y actualizada con éxito para todos los usuarios!")

    # --- PANTALLA 2: TAREAS ---
    elif st.session_state["pantalla"] == "tareas":
        st.header("📋 Panel de Tareas")
        
        if not hay_pendientes:
            st.info("No hay tareas pendientes. ¡Todo al día! 💪")
        else:
            for i, tarea in enumerate(st.session_state["tareas"]):
                if not tarea["hecha"]:
                    if rol == "Empleado":
                        st.info(f"👉 **{tarea['texto']}**")
                        if st.button("✅ COMPLETADO", key=f"btn_{tarea['id']}", type="primary", use_container_width=True):
                            st.session_state["tareas"][i]["hecha"] = True
                            st.rerun()
                        st.write("---")
                    else:
                        st.write(f"🔹 {tarea['texto']}")
        
        if rol == "Admin":
            st.write("---")
            st.subheader("Asignar nueva tarea a Dani")
            with st.form("form_nueva_tarea"):
                nueva = st.text_input("Descripción de la tarea:")
                if st.form_submit_button("Enviar Tarea"):
                    if nueva:
                        nuevo_id = len(st.session_state["tareas"]) + 1
                        st.session_state["tareas"].append({"id": nuevo_id, "texto": nueva, "hecha": False, "vista": False})
                        st.success("¡Tarea enviada!")
                        st.rerun()

if st.session_state["usuario_actual"] is None:
    mostrar_login()
else:
    mostrar_sistema()
