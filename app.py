import streamlit as st
import pandas as pd

st.set_page_config(page_title="Depósito Bastías", page_icon="🦋", layout="centered")

# ==========================================
# BASE DE DATOS Y ESTADOS
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
        # CSS EXCLUSIVO PARA DANI: Todo gigante y botón titilante
        st.markdown("""
            <style>
            /* Aumentar letra general, inputs y etiquetas */
            html, body, p, div, input, label {
                font-size: 22px !important;
            }
            /* Títulos más grandes */
            h1 { font-size: 45px !important; }
            h2 { font-size: 35px !important; }
            h3 { font-size: 30px !important; }
            
            /* Botones más altos y anchos */
            .stButton > button {
                height: 70px !important;
                font-size: 22px !important;
                font-weight: bold !important;
                border-radius: 10px !important;
            }

            /* Animación del botón titilante (Apunta al botón primario del menú) */
            @keyframes parpadeo {
                0% { background-color: #ff4b4b; color: white; border-color: #ff4b4b; }
                50% { background-color: transparent; color: #ff4b4b; border-color: #ff4b4b; }
                100% { background-color: #ff4b4b; color: white; border-color: #ff4b4b; }
            }
            div[data-testid="stSidebar"] button[kind="primary"] {
                animation: parpadeo 1.5s infinite;
                height: 90px !important; /* Más gigante aún para que lo vea seguro */
                font-size: 24px !important;
            }
            </style>
        """, unsafe_allow_html=True)
    else:
        # CSS PARA LEANDRO Y EL INVITADO (Tamaño normal, pero mantenemos alerta sutil si querés)
        st.markdown("""
            <style>
            .stButton > button { font-weight: bold; }
            </style>
        """, unsafe_allow_html=True)

# ==========================================
# PANTALLA DE LOGIN
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

# ==========================================
# PANTALLA PRINCIPAL (El Sistema)
# ==========================================
def mostrar_sistema():
    aplicar_estilos_segun_usuario()
    
    rol = st.session_state["rol"]
    nombre = st.session_state["usuario_actual"]

    tareas_pendientes = [t for t in st.session_state["tareas"] if not t["hecha"]]
    hay_pendientes = len(tareas_pendientes) > 0

    # --- BARRA LATERAL (Menú) ---
    with st.sidebar:
        st.title(f"Hola, {nombre} 👋")
        st.write("---")
        
        if st.button("📦 Buscador de Stock", use_container_width=True):
            cambiar_pantalla("stock")
            st.rerun()

        if rol == "Empleado":
            # Si Dani tiene tareas, el botón es PRIMARIO (activa el CSS rojo titilante)
            if hay_pendientes:
                if st.button("⚠️ VER TAREAS", type="primary", use_container_width=True):
                    cambiar_pantalla("tareas")
                    st.rerun()
            else:
                # Si no tiene tareas, es un botón normal
                if st.button("📋 Ver Tareas", use_container_width=True):
                    cambiar_pantalla("tareas")
                    st.rerun()
        
        elif rol == "Admin":
            # A Leandro le mostramos el botón normal, sin titilar
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
        
        busqueda = st.text_input("🔍 Buscar por Nombre, Código Bejerman o Código de Producto...")
        
        if busqueda:
            st.write("---")
            st.subheader(f"Resultados para: {busqueda}")
            
            st.success("**TOTAL DISPONIBLE: 450 unidades**")
            
            st.write("Desglose por Lotes:")
            datos_lotes = pd.DataFrame({
                "Lote": ["L-2023-A", "L-2024-B", "L-2024-C"],
                "Vencimiento": ["12/2026", "05/2027", "11/2027"],
                "Cantidad": [100, 200, 150]
            })
            st.dataframe(datos_lotes, use_container_width=True, hide_index=True)

        if rol == "Admin":
            st.write("---")
            st.subheader("⚙️ Actualizar Base de Datos")
            archivo_db = st.file_uploader("Seleccioná la nueva BD (.db o Excel)", type=["db", "xlsx", "csv"])
            if archivo_db:
                st.success("✅ ¡Base de datos actualizada con éxito!")

    # --- PANTALLA 2: TAREAS ---
    elif st.session_state["pantalla"] == "tareas":
        st.header("📋 Panel de Tareas")
        
        if not hay_pendientes:
            st.info("No hay tareas pendientes. ¡Todo al día! 💪")
        else:
            for i, tarea in enumerate(st.session_state["tareas"]):
                if not tarea["hecha"]:
                    if rol == "Empleado":
                        # Diseño grande para Dani: Texto destacado y un botón gigante verde para completar
                        st.info(f"👉 **{tarea['texto']}**")
                        if st.button("✅ COMPLETADO", key=f"btn_{tarea['id']}", type="primary", use_container_width=True):
                            st.session_state["tareas"][i]["hecha"] = True
                            st.rerun()
                        st.write("---")
                    else:
                        # Vos ves la lista normal
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

# ==========================================
# ARRANQUE
# ==========================================
if st.session_state["usuario_actual"] is None:
    mostrar_login()
else:
    mostrar_sistema()
