import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import json
from pathlib import Path

# Archivo para guardar datos
DATA_FILE = Path("datos.json")

def cargar_datos():
    if DATA_FILE.exists():
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def guardar_datos(datos):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)

# Cargar datos existentes
datos_por_fecha = cargar_datos()

# Configuración de la página
st.set_page_config(page_title="FamiWallet", layout="centered")
st.title("FamiWallet")

# Formulario de apellido de familia
if "apellido_familia" not in st.session_state:
    st.session_state.apellido_familia = ""

with st.form("familia_form"):
    apellido = st.text_input("Somos la familia:", value=st.session_state.apellido_familia)
    submitted = st.form_submit_button("Continuar")
    if submitted:
        if apellido.strip() == "":
            st.error("Por favor ingresa un apellido.")
        else:
            st.session_state.apellido_familia = apellido.strip().upper()
            st.success(f"Bienvenida, familia {st.session_state.apellido_familia}")

# Menú lateral
st.sidebar.title("Menú")
pagina = st.sidebar.radio("Ir a:", ["Agregar Gastos", "Visualizar Gastos", "Resumen General"])

# Página: Agregar Gastos
if pagina == "Agregar Gastos":
    st.header("➕ Agregar Gastos")
    with st.form("gastos_form"):
        fecha = st.date_input("Fecha").strftime("%d/%m/%Y")
        ingreso = st.number_input("Ingreso mensual ($):", min_value=0.0)
        luz = st.number_input("Gasto - Luz ($):", min_value=0.0)
        agua = st.number_input("Gasto - Agua ($):", min_value=0.0)
        internet = st.number_input("Gasto - Internet ($):", min_value=0.0)
        alimentos = st.number_input("Gasto - Alimentos ($):", min_value=0.0)
        otros = st.number_input("Otros gastos ($):", min_value=0.0)
        guardar = st.form_submit_button("Guardar")
        if guardar:
            datos_por_fecha[fecha] = {
                "Ingreso": float(ingreso),
                "Luz": float(luz),
                "Agua": float(agua),
                "Internet": float(internet),
                "Alimentos": float(alimentos),
                "Otros": float(otros),
            }
            guardar_datos(datos_por_fecha)
            st.success(f"Gastos del {fecha} guardados correctamente.")

# Página: Visualizar Gastos
elif pagina == "Visualizar Gastos":
    st.header("📊 Visualizar Gastos por Fecha")
    if not datos_por_fecha:
        st.info("No hay registros aún.")
    else:
        fechas = sorted(datos_por_fecha.keys(), key=lambda d: datetime.strptime(d, "%d/%m/%Y"), reverse=True)
        fecha_sel = st.selectbox("Selecciona fecha:", fechas)
        if fecha_sel:
            registro = datos_por_fecha[fecha_sel]
            ingreso = registro["Ingreso"]
            gastos = {k: v for k, v in registro.items() if k != "Ingreso"}
            total_gastos = sum(gastos.values())
            restante = ingreso - total_gastos

            st.subheader(f"Gastos del {fecha_sel}")
            st.write(f"Ingreso: ${ingreso:,.2f}")
            st.write(f"Total gastos: ${total_gastos:,.2f}")
            st.write(f"Dinero restante: ${restante:,.2f}")

            df = pd.DataFrame(list(gastos.items()), columns=["Categoría", "Monto"])
            st.table(df.style.format({"Monto": "${:,.2f}"}))

            fig, ax = plt.subplots()
            ax.pie(gastos.values(), labels=gastos.keys(), autopct="%1.1f%%", startangle=90)
            ax.axis("equal")
            st.pyplot(fig)

# Página: Resumen General
elif pagina == "Resumen General":
    st.header("📋 Resumen General")
    if not datos_por_fecha:
        st.info("No hay información registrada.")
    else:
        categorias = ["Luz", "Agua", "Internet", "Alimentos", "Otros"]
        suma = {c: 0.0 for c in categorias}
        total_ingresos = 0.0
        for registro in datos_por_fecha.values():
            total_ingresos += registro["Ingreso"]
            for c in categorias:
                suma[c] += registro[c]
        total_gastos = sum(suma.values())
        restante = total_ingresos - total_gastos
        st.write(f"Total ingresos: ${total_ingresos:,.2f}")
        st.write(f"Total gastos: ${total_gastos:,.2f}")
        st.write(f"Dinero restante: ${restante:,.2f}")

        df_suma = pd.DataFrame(list(suma.items()), columns=["Categoría", "Total"])
        st.bar_chart(df_suma.set_index("Categoría"))
