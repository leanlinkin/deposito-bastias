import streamlit as st
import pandas as pd
import os

# Configuración de página: Modo escritorio amplio
st.set_page_config(page_title="Sistema de Depósito", page_icon="📦", layout="wide")

# ==========================================
# CONFIGURACIÓN DE TU EXCEL
# ==========================================
COL_NOMBRE = "Artículo - Desc. Gen."
COL_CODIGO_BEJ = "Stock - Artículo - Cód. Gen."
COL_CODIGO_PROV = "Codigo Proveedor"
COL_LOTE = "Stock - Partida - Cód."
COL_VENC = "Stock - Partida - F. Vto. / Ingreso"
COL_CANT = "Stock - Partida - Cant. Real en UM 1"

@st.cache_data
def cargar_bd():
    if os.path.exists("base_datos_actual.xlsx"):
        try:
            return pd.read_excel("base_datos_actual.xlsx")
        except Exception:
            return pd.DataFrame()
    return pd.DataFrame()

# ==========================================
# BASE DE DATOS USUARIOS Y ESTADO
# ==========================================
USUARIOS = {
    "Leandro": {"clave": "admin123", "rol": "Admin"},
    "Dani": {"clave": "dani123", "rol": "Empleado"},
    "Invitado": {"clave": "invitado123", "rol": "Invitado"}
}

if "usuario_actual" not in st.session_state:
    st.session_state["usuario_actual"] = None
    st.session_state["rol"] = None
    st.session_state["articulo_seleccionado"] = None
    st.session_state["ultima_busqueda"] = "" # Memoria para el buscador
    st.session_state["tareas"] = [
        {"id": 1, "texto": "Armar pedido para Farmacia Centro", "hecha": False}
    ]

# ==========================================
# CSS LIMPIO (Solo para textos, sin romper botones)
# ==========================================
st.markdown("""
    <style>
    /* Ocultar barra superior de Streamlit */
    header {visibility: hidden;}
    
    /* Agrandar textos de la interfaz */
    p, div, span, label { font-size: 20px !important; }
    h1 { font-size: 50px !important; }
    h3, h4 { font-size: 28px !important; }
    
    /* Botones más altos y cómodos nativos */
    .stButton > button {
        height: 65px !important;
        font-size: 18px !important;
        font-weight: bold !important;
        border-radius: 8px !important;
    }
    
    /* Estilos del Stock Total Verde */
    .stock-verde {
        font-size: 65px !important;
        color: #00b050 !important;
        font-weight: 900 !important;
        margin-top: 20px;
    }
    </style>
""", unsafe_allow_html=True)

# ==========================================
# VENTANAS FLOTANTES (POP-UPS)
# ==========================================

# 1. Pop-up de Resultados
@st.dialog("🎯 Resultados de búsqueda", width="large")
def modal_resultados(df_filtrado):
    st.write("Seleccioná el artículo correcto de la lista:")
    
    opciones = df_filtrado[COL_CODIGO_BEJ].astype(str) + " - " + df_filtrado[COL_NOMBRE].astype(str)
    elegido = st.radio("Opciones:", opciones.unique(), label_visibility="collapsed")
    
    st.write("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ABRIR SELECCIONADO", type="primary", use_container_width=True):
            st.session_state["articulo_seleccionado"] = elegido
            st.rerun()
    with col2:
        if st.button("CERRAR", use_container_width=True):
            st.rerun()

# 2. Pop-up de Lotes
@st.dialog("📦 Lotes del artículo", width="large")
def modal_lotes(df_lotes):
    df_lotes_limpio = df_lotes.rename(columns={
        COL_LOTE: "Nro de Lote",
        COL_CANT: "Cantidad",
        COL_VENC: "Vencimiento"
    })
    st.dataframe(df_lotes_limpio, use_container_width=True, hide_index=True)
    
    st.write("---")
    if st.button("VOLVER", use_container_width=True):
        st.rerun()

# 3. Pop-up de Tareas (Nuevo diseño integrado)
@st.dialog("📋 Panel de Tareas", width="large")
def modal_tareas():
    rol = st.session_state["rol"]
    tareas_pendientes = [t for t in st.session_state["tareas"] if not t["hecha"]]
    
    if not tareas_pendientes:
        st.info("No hay tareas pendientes. ¡Todo al día! 💪")
    else:
        for i, tarea in enumerate(st.session_state["tareas"]):
            if not tarea["hecha"]:
                if rol == "Empleado":
                    st.warning(f"👉 **{tarea['texto']}**")
                    if st.button("✅ MARCAR COMO COMPLETADA", key=f"btn_{tarea['id']}", type="primary", use_container_width=True):
                        st.session_state["tareas"][i]["hecha"] = True
                        st.rerun()
                    st.write("---")
                else:
                    st.write(f"🔹 {tarea['texto']}")
                    
    if rol == "Admin":
        st.write("---")
        st.subheader("Asignar nueva tarea a Dani")
        nueva = st.text_input("Descripción de la tarea:")
        if st.button("Enviar Tarea", type="primary"):
            if nueva:
                nuevo_id = len(st.session_state["tareas"]) + 1
                st.session_state["tareas"].append({"id": nuevo_id, "texto": nueva, "hecha": False})
                st.success("¡Tarea enviada!")
                st.rerun()

# ==========================================
# PANTALLAS PRINCIPALES
# ==========================================

def mostrar_login():
    st.write("<br><br><br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.title("🦋 Sistema de Depósito")
        st.write("Iniciá sesión para continuar.")
        
        usuario = st.text_input("Usuario")
        clave = st.text_input("Contraseña", type="password")
        
        if st.button("Ingresar", type="primary", use_container_width=True):
            if usuario in USUARIOS and USUARIOS[usuario]["clave"] == clave:
                st.session_state["usuario_actual"] = usuario
                st.session_state["rol"] = USUARIOS[usuario]["rol"]
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos ❌")

def mostrar_sistema():
    rol = st.session_state["rol"]
    df = cargar_bd()
    
    tareas_pendientes = [t for t in st.session_state["tareas"] if not t["hecha"]]
    hay_pendientes = len(tareas_pendientes) > 0

    # --- BARRA SUPERIOR CON BOTONES BIEN ORDENADOS ---
    col_busq, col_esp, col_plan, col_hoja, col_tar, col_salir = st.columns([3.5, 0.5, 1.5, 1.5, 1.5, 1.5])
    
    with col_busq:
        # Buscador sin bordes raros
        busqueda = st.text_input("Buscador", label_visibility="collapsed", placeholder="🔍 Buscar y presionar Enter...")
    
    with col_plan:
        st.button("Planilla de Control", use_container_width=True)
    with col_hoja:
        st.button("Hoja de Ruta 🚚", use_container_width=True)
    with col_tar:
        # Si Dani tiene tareas, el botón se pone Rojo/Primario para llamar la atención
        tipo_boton_tarea = "primary" if (hay_pendientes and rol == "Empleado") else "secondary"
        texto_tarea = "⚠️ TAREAS NUEVAS" if (hay_pendientes and rol == "Empleado") else "📋 TAREAS ✔"
        if st.button(texto_tarea, type=tipo_boton_tarea, use_container_width=True):
            modal_tareas()
    with col_salir:
        if st.button("Cerrar Sesión", use_container_width=True):
            st.session_state["usuario_actual"] = None
            st.session_state["rol"] = None
            st.rerun()

    st.write("---")

    # --- LÓGICA DE BÚSQUEDA ---
    # Solo busca si escribiste algo y es diferente a la última búsqueda (para que no se trabe el modal)
    if busqueda and busqueda != st.session_state["ultima_busqueda"]:
        st.session_state["ultima_busqueda"] = busqueda
        if not df.empty:
            mask = df[COL_NOMBRE].astype(str).str.contains(busqueda, case=False, na=False) | \
                   df[COL_CODIGO_BEJ].astype(str).str.contains(busqueda, case=False, na=False)
            if COL_CODIGO_PROV in df.columns:
                mask = mask | df[COL_CODIGO_PROV].astype(str).str.contains(busqueda, case=False, na=False)
            
            resultados = df[mask]
            
            if not resultados.empty:
                modal_resultados(resultados)
            else:
                st.error("No se encontró el artículo.")

    # --- PANTALLA CENTRAL ---
    if st.session_state["articulo_seleccionado"] is None:
        # Pantalla vacía (Centrada)
        st.write("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='text-align: center;'>ESPERANDO BÚSQUEDA...</h1>", unsafe_allow_html=True)
        st.write("<br><br><br><br><br>", unsafe_allow_html=True)
        st.markdown("<p style='font-size: 60px; font-weight: bold;'>STOCK TOTAL: --</p>", unsafe_allow_html=True)

    else:
        # Pantalla con Artículo cargado
        articulo_actual = st.session_state["articulo_seleccionado"]
        opciones_df = df[COL_CODIGO_BEJ].astype(str) + " - " + df[COL_NOMBRE].astype(str)
        df_exacto = df[opciones_df == articulo_actual].copy()
        
        df_exacto[COL_CANT] = pd.to_numeric(df_exacto[COL_CANT], errors='coerce').fillna(0)
        total_stock = df_exacto[COL_CANT].sum()
        
        nombre_limpio = df_exacto.iloc[0][COL_NOMBRE] if not df_exacto.empty else "DESCONOCIDO"
        cod_prov = df_exacto.iloc[0][COL_CODIGO_PROV] if COL_CODIGO_PROV in df_exacto.columns else "--"
        
        st.markdown(f"<h1 style='text-align: center;'>{nombre_limpio}</h1>", unsafe_allow_html=True)
        st.markdown("<h3 style='text-align: center; color: #95a5a6;'>📍 UBICACIÓN: SIN ASIGNAR</h3>", unsafe_allow_html=True)
        st.markdown(f"<h4 style='text-align: center;'>CÓD. PROVEEDOR: {cod_prov}</h4>", unsafe_allow_html=True)
        
        st.write("<br><br>", unsafe_allow_html=True)
        
        # Fila inferior: Stock y Botones de acciones
        col_stock, col_btn1, col_btn2 = st.columns([2, 1, 1])
        with col_stock:
            st.markdown(f'<p class="stock-verde">STOCK TOTAL: {total_stock:g}</p>', unsafe_allow_html=True)
            
        with col_btn1:
            st.write("<br>", unsafe_allow_html=True)
            # Usa el botón NATIVO principal (Rojo/Naranja) para destacar
            if st.button("VER LOTES 🔍", type="primary", use_container_width=True):
                # Filtra los que tienen stock mayor a 0
                df_lotes_positivos = df_exacto[df_exacto[COL_CANT] > 0][[COL_LOTE, COL_CANT, COL_VENC]]
                modal_lotes(df_lotes_positivos)
                
        with col_btn2:
            st.write("<br>", unsafe_allow_html=True)
            st.button("UBICACIÓN 📍", use_container_width=True)

    # --- ZONA DE ADMINISTRADOR (Oculta abajo para no molestar a Dani) ---
    if rol == "Admin":
        st.write("---")
        with st.expander("⚙️ Actualizar Base de Datos (Solo Admin)"):
            archivo_db = st.file_uploader("Subir Excel", type=["xlsx"])
            if archivo_db:
                with open("base_datos_actual.xlsx", "wb") as f:
                    f.write(archivo_db.getbuffer())
                st.cache_data.clear()
                st.success("✅ Base de datos actualizada.")
                st.rerun()

# ==========================================
# LÓGICA DE ARRANQUE
# ==========================================
if st.session_state["usuario_actual"] is None:
    mostrar_login()
else:
    mostrar_sistema()
