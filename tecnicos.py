import streamlit as st
import pandas as pd
import plotly.express as px
import os
from fpdf import FPDF

st.set_page_config(page_title="Dashboard Postventa", layout="wide")

META = 6600000
archivo = "datos_taller.xlsx"

# Crear base si no existe
if not os.path.exists(archivo):

    tecnicos = pd.DataFrame(columns=["Tecnico"])

    datos = pd.DataFrame(columns=[
        "Mes",
        "Tecnico",
        "Mano_Obra",
        "Repuestos"
    ])

    with pd.ExcelWriter(archivo) as writer:
        tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
        datos.to_excel(writer, sheet_name="datos", index=False)

# cargar datos
tecnicos = pd.read_excel(archivo, sheet_name="tecnicos")
datos = pd.read_excel(archivo, sheet_name="datos")

import streamlit as st
from PIL import Image

# Configuración de página
st.set_page_config(
    page_title="Dashboard Postventa",
    layout="wide"
)

# Cargar logo
logo = Image.open("logo_empresa.png")

# Crear columnas para header
col1, col2 = st.columns([2,5])

with col1:
    st.image(logo, width=250)

with col2:
    st.markdown("""
    <h2 style='margin-bottom:0px; font-size:30px;'>
    Productividad Postventa
    </h2>
    """, unsafe_allow_html=True)

st.markdown("---")

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Dashboard Ejecutivo",
        "Registrar Productividad",
        "Gestión de Técnicos",
        "Análisis por Técnico",
        "Exportar Informe PDF"
    ]
)

# ------------------------------------------------
# GESTIÓN DE TECNICOS
# ------------------------------------------------

if menu == "Gestión de Técnicos":

    st.markdown(
    "<h3 style='font-size:24px; color:#2c3e50;'>Administración de Técnicos</h3>",
    unsafe_allow_html=True
)
    nuevo = st.text_input("Nuevo técnico")

    if st.button("Agregar técnico"):

        if nuevo != "":
            tecnicos.loc[len(tecnicos)] = [nuevo]

            with pd.ExcelWriter(archivo) as writer:
                tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
                datos.to_excel(writer, sheet_name="datos", index=False)

            st.success("Técnico agregado")

    st.subheader("Técnicos actuales")
    st.dataframe(tecnicos)

    if len(tecnicos) > 0:

        eliminar = st.selectbox(
            "Eliminar técnico",
            tecnicos["Tecnico"]
        )

        if st.button("Eliminar"):

            tecnicos = tecnicos[tecnicos["Tecnico"] != eliminar]

            with pd.ExcelWriter(archivo) as writer:
                tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
                datos.to_excel(writer, sheet_name="datos", index=False)

            st.warning("Técnico eliminado")

# ------------------------------------------------
# REGISTRO DE PRODUCTIVIDAD
# ------------------------------------------------

elif menu == "Registrar Productividad":

    st.markdown(
    "<h3 style='font-size:24px; color:#2c3e50;'>Registro mensual de productividad</h3>",
    unsafe_allow_html=True
)
   
    mes = st.selectbox(
        "Mes",
        [
            "Enero","Febrero","Marzo","Abril","Mayo","Junio",
            "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
        ]
    )

    tecnico = st.selectbox(
        "Técnico",
        tecnicos["Tecnico"]
    )

    mano = st.number_input("Mano de obra",0)
    rep = st.number_input("Repuestos",0)

    if st.button("Guardar registro"):

        nuevo = pd.DataFrame([{
            "Mes":mes,
            "Tecnico":tecnico,
            "Mano_Obra":mano,
            "Repuestos":rep
        }])

        datos = pd.concat([datos,nuevo],ignore_index=True)

        with pd.ExcelWriter(archivo) as writer:
            tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
            datos.to_excel(writer, sheet_name="datos", index=False)

        st.success("Registro guardado")

# ------------------------------------------------
# DASHBOARD EJECUTIVO
# ------------------------------------------------

elif menu == "Dashboard Ejecutivo":

    st.markdown(
    "<h3 style='font-size:24px; color:#2c3e50;'>Indicadores del Taller</h3>",
    unsafe_allow_html=True
)

    if len(datos) == 0:
        st.warning("Aún no hay datos registrados")
        st.stop()

    total_mo = datos["Mano_Obra"].sum()
    total_rep = datos["Repuestos"].sum()

    promedio = total_mo / len(tecnicos) if len(tecnicos)>0 else 0

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Mano de obra total",f"${total_mo:,.0f}")
    col2.metric("Repuestos totales",f"${total_rep:,.0f}")
    col3.metric("Técnicos activos",len(tecnicos))
    col4.metric("Promedio por técnico",f"${promedio:,.0f}")

    st.divider()

    prod = datos.groupby("Tecnico")[["Mano_Obra","Repuestos"]].sum().reset_index()

    prod["Cumplimiento %"] = (prod["Mano_Obra"]/META)*100

    st.subheader("Ranking de Técnicos - Mano de Obra")

    fig = px.bar(
        prod,
        x="Tecnico",
        y="Mano_Obra",
        color="Cumplimiento %",
        text="Mano_Obra",
        color_continuous_scale="RdYlGn"
    )

    st.plotly_chart(fig,use_container_width=True)

    st.subheader("Ranking Repuestos")

    fig2 = px.bar(
        prod,
        x="Tecnico",
        y="Repuestos",
        text="Repuestos",
        color="Repuestos"
    )

    st.plotly_chart(fig2,use_container_width=True)

    st.subheader("Participación de repuestos")

    fig3 = px.pie(
        prod,
        names="Tecnico",
        values="Repuestos"
    )

    st.plotly_chart(fig3,use_container_width=True)

    st.subheader("Evolución mensual del taller")

    mes_data = datos.groupby("Mes")[["Mano_Obra","Repuestos"]].sum().reset_index()

    fig4 = px.line(
        mes_data,
        x="Mes",
        y=["Mano_Obra","Repuestos"],
        markers=True
    )

    st.plotly_chart(fig4,use_container_width=True)

    st.subheader("Tabla de desempeño")

    st.dataframe(prod.sort_values("Mano_Obra",ascending=False))

# ------------------------------------------------
# ANALISIS POR TECNICO
# ------------------------------------------------

elif menu == "Análisis por Técnico":

    st.markdown(
    "<h3 style='font-size:24px; color:#2c3e50;'>Análisis Individual</h3>",
    unsafe_allow_html=True
)
    tecnico = st.selectbox(
        "Seleccione técnico",
        tecnicos["Tecnico"]
    )

    datos_t = datos[datos["Tecnico"] == tecnico]

    if len(datos_t)==0:
        st.warning("Este técnico aún no tiene registros")
        st.stop()

    fig = px.line(
        datos_t,
        x="Mes",
        y=["Mano_Obra","Repuestos"],
        markers=True,
        title="Evolución mensual"
    )

    st.plotly_chart(fig,use_container_width=True)

    total_mo = datos_t["Mano_Obra"].sum()

    cumplimiento = (total_mo/META)*100

    st.metric("Cumplimiento mano de obra",f"{cumplimiento:.1f}%")

# ------------------------------------------------
# EXPORTAR PDF
# ------------------------------------------------

elif menu == "Exportar Informe PDF":

    st.markdown(
    "<h3 style='font-size:24px; color:#2c3e50;'>Informe Gerencial</h3>",
    unsafe_allow_html=True
)
    if st.button("Generar informe"):

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial",size=14)

        pdf.cell(200,10,"Informe de Productividad del Taller",ln=True)

        total_mo = datos["Mano_Obra"].sum()
        total_rep = datos["Repuestos"].sum()

        pdf.set_font("Arial",size=12)

        pdf.cell(200,10,f"Mano de obra total: ${total_mo:,.0f}",ln=True)
        pdf.cell(200,10,f"Repuestos totales: ${total_rep:,.0f}",ln=True)
        pdf.cell(200,10,f"Tecnicos activos: {len(tecnicos)}",ln=True)

        pdf.output("informe_taller.pdf")

        with open("informe_taller.pdf","rb") as f:

            st.download_button(
                "Descargar PDF",
                f,
                file_name="informe_taller.pdf"
            )