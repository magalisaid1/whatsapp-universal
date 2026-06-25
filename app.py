import streamlit as st
import pandas as pd
import urllib.parse
import io 

st.set_page_config(page_title="WhatsApp Masivo Universal", page_icon="🚀")
st.title("🚀 Envíos Masivos por WhatsApp")
st.write("Sube tu lista, escribe tu mensaje personalizado y envía.")

# 1. LA MEMORIA
if 'datos' not in st.session_state:
    st.session_state.datos = None

# 2. SUBIR ARCHIVO
if st.session_state.datos is None:
    archivo_subido = st.file_uploader("Paso 1: Sube tu archivo Excel", type=["xlsx"])
    if archivo_subido is not None:
        df = pd.read_excel(archivo_subido)
        # Nos aseguramos de que existan las columnas básicas
        if 'Estado' not in df.columns:
            df['Estado'] = ''
        if 'Enviar' not in df.columns:
            df['Enviar'] = 'Si'
        df['Estado'] = df['Estado'].astype(str)
        st.session_state.datos = df
        st.rerun()

# 3. PANEL DE CONTROL UNIVERSAL
if st.session_state.datos is not None:
    df = st.session_state.datos 
    
    st.write("### 📋 1. Tus Datos:")
    st.dataframe(df)
    
    # --- LA MAGIA UNIVERSAL: EL CREADOR DE MENSAJES ---
    st.write("### ✍️ 2. Escribe tu Mensaje:")
    
    # Le mostramos al usuario qué columnas tiene su Excel
    columnas = df.columns.tolist()
    etiquetas = ", ".join([f"**{{{col}}}**" for col in columnas])
    st.info(f"💡 **Truco:** Puedes usar estas etiquetas en tu mensaje para que se personalice automáticamente: {etiquetas}")
    
    # Caja de texto para que el usuario escriba lo que quiera
    mensaje_base = st.text_area(
        "Escribe tu mensaje aquí:", 
        "Hola {Nombre}, este es un mensaje de prueba."
    )
    
    st.write("### 🚀 3. Pendientes de envío:")
    
    pendientes = 0
    for index, row in df.iterrows():
        enviar = str(row.get('Enviar', '')).strip().lower()
        estado = str(row.get('Estado', '')).strip().lower()
        
        if enviar == 'si' and estado != 'enviado':
            pendientes += 1
            
            # Intentamos obtener el teléfono y el nombre (si existen)
            telefono = str(row.get('Telefono', ''))
            nombre_mostrar = str(row.get('Nombre', f'Fila {index+1}'))
            
            if not telefono.startswith('+'):
                telefono = '+' + telefono
                
            # REEMPLAZO DINÁMICO: Cambiamos las {Etiquetas} por los datos reales
            mensaje_final = mensaje_base
            for col in columnas:
                etiqueta_buscar = "{" + col + "}"
                if etiqueta_buscar in mensaje_final:
                    mensaje_final = mensaje_final.replace(etiqueta_buscar, str(row[col]))
            
            mensaje_url = urllib.parse.quote(mensaje_final)
            link = f"https://web.whatsapp.com/send?phone={telefono}&text={mensaje_url}"
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.link_button(f"💬 Abrir chat de {nombre_mostrar}", link)
            
            with col2:
                if st.button(f"✅ Marcar como Enviado", key=f"btn_{index}"):
                    st.session_state.datos.at[index, 'Estado'] = 'Enviado'
                    st.rerun()
                    
    if pendientes == 0:
        st.success("¡No hay mensajes pendientes!")

    # 4. DESCARGAR Y REINICIAR
    st.write("---")
    st.write("### 💾 4. Finalizar:")
    
    col_descarga, col_reiniciar = st.columns([1, 1])
    
    with col_descarga:
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
            st.session_state.datos.to_excel(writer, index=False)
        
        st.download_button(
            label="📥 Descargar Excel Actualizado",
            data=buffer.getvalue(),
            file_name="lista_actualizada.xlsx",
            mime="application/vnd.ms-excel"
        )
        
    with col_reiniciar:
        # Botón para borrar la memoria y subir un Excel diferente
        if st.button("🔄 Subir una lista nueva"):
            st.session_state.datos = None
            st.rerun()
