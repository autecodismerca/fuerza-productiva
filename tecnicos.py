import streamlit as st
import pandas as pd
import plotly.express as px
import os
from fpdf import FPDF
from PIL import Image

st.set_page_config(page_title="Dashboard Postventa", layout="wide")

META = 6600000
archivo = "datos_taller.xlsx"

# -----------------------------
# CREAR BASE DE DATOS
# -----------------------------

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

# -----------------------------
# HEADER
# -----------------------------

logo = Image.open("logo_empresa.png")

col1, col2 = st.columns([2,4])

with col1:
    st.image(logo, width=250)

with col2:
        st.markdown("""
    <h2 style='margin-bottom:0px; font-size:30px;'>
    Productividad Postventa
    </h2>
    """, unsafe_allow_html=True)

st.markdown("---")

# -----------------------------
# MENU
# -----------------------------

menu = st.sidebar.selectbox(
    "Menú",
    [
        "Dashboard Ejecutivo",
        "Registrar Productividad",
        "Gestión de Técnicos",
        "Análisis por Técnico",
        "Informe Mensual",
        "Exportar PDF"
    ]
)

# -----------------------------
# GESTION TECNICOS
# -----------------------------

if menu == "Gestión de Técnicos":

    st.subheader("Administración de Técnicos")

    nuevo = st.text_input("Nuevo técnico")

    if st.button("Agregar técnico"):

        if nuevo != "":
            tecnicos.loc[len(tecnicos)] = [nuevo]

            with pd.ExcelWriter(archivo) as writer:
                tecnicos.to_excel(writer, sheet_name="tecnicos", index=False)
                datos.to_excel(writer, sheet_name="datos", index=False)

            st.success("Técnico agregado")

    st.dataframe(tecnicos)

# -----------------------------
# REGISTRO PRODUCTIVIDAD
# -----------------------------

elif menu == "Registrar Productividad":

    st.subheader("Registro mensual")

    meses = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]

    mes = st.selectbox("Mes", meses)

    tecnico = st.selectbox("Técnico", tecnicos["Tecnico"])

    mano = st.number_input("Mano de obra",0)

    rep = st.number_input("Repuestos",0)

    if st.button("Guardar"):

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

# -----------------------------
# DASHBOARD EJECUTIVO
# -----------------------------

elif menu == "Dashboard Ejecutivo":

    st.subheader("Indicadores generales")

    if len(datos)==0:
        st.warning("No hay datos")
        st.stop()

    total_mo = datos["Mano_Obra"].sum()
    total_rep = datos["Repuestos"].sum()

    col1,col2,col3,col4 = st.columns(4)

    col1.metric("Mano obra total",f"${total_mo:,.0f}")
    col2.metric("Repuestos totales",f"${total_rep:,.0f}")
    col3.metric("Técnicos activos",len(tecnicos))
    col4.metric("Meta mensual técnico",f"${META:,.0f}")

    st.divider()

    meses_trabajados = datos["Mes"].nunique()

    prod = datos.groupby("Tecnico")[["Mano_Obra","Repuestos"]].sum().reset_index()

    meta_acumulada = META * meses_trabajados

    prod["Cumplimiento %"] = (prod["Mano_Obra"] / meta_acumulada) * 100

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

    st.subheader("Evolución mensual")

    mes_data = datos.groupby("Mes")[["Mano_Obra","Repuestos"]].sum().reset_index()

    fig3 = px.line(
        mes_data,
        x="Mes",
        y=["Mano_Obra","Repuestos"],
        markers=True
    )

    st.plotly_chart(fig3,use_container_width=True)

    st.subheader("Tabla acumulada")

    st.dataframe(prod.sort_values("Mano_Obra",ascending=False))

# -----------------------------
# INFORME MES A MES
# -----------------------------

elif menu == "Informe Mensual":

    st.subheader("Seguimiento mes a mes")

    meses = [
        "Enero","Febrero","Marzo","Abril","Mayo","Junio",
        "Julio","Agosto","Septiembre","Octubre","Noviembre","Diciembre"
    ]

    for mes in meses:

        datos_mes = datos[datos["Mes"]==mes]

        if len(datos_mes)>0:

            st.markdown(f"## {mes}")

            tabla = datos_mes.groupby("Tecnico")[["Mano_Obra","Repuestos"]].sum().reset_index()

            tabla["Cumplimiento %"] = (tabla["Mano_Obra"]/META)*100

            st.dataframe(tabla)

            fig = px.bar(
                tabla,
                x="Tecnico",
                y="Mano_Obra",
                color="Cumplimiento %",
                text="Mano_Obra",
                color_continuous_scale="RdYlGn"
            )

            st.plotly_chart(fig,use_container_width=True)

# -----------------------------
# ANALISIS TECNICO
# -----------------------------

elif menu == "Análisis por Técnico":

    tecnico = st.selectbox("Seleccionar técnico", tecnicos["Tecnico"])

    datos_t = datos[datos["Tecnico"] == tecnico]

    if len(datos_t) == 0:
        st.warning("Sin datos")
        st.stop()

    fig = px.line(
        datos_t,
        x="Mes",
        y=["Mano_Obra", "Repuestos"],
        markers=True
    )

    st.plotly_chart(fig, use_container_width=True)

    total = datos_t["Mano_Obra"].sum()

    meses_trabajados = datos["Mes"].nunique()

    meta_acumulada = META * meses_trabajados

    cumplimiento = (total / meta_acumulada) * 100

    st.metric("Cumplimiento total", f"{cumplimiento:.1f}%")
# -----------------------------
# EXPORTAR PDF
# -----------------------------

elif menu == "Exportar PDF":

    if st.button("Generar informe"):

        pdf = FPDF()
        pdf.add_page()

        pdf.set_font("Arial",size=14)

        pdf.cell(200,10,"Informe Productividad Taller",ln=True)

        total_mo = datos["Mano_Obra"].sum()
        total_rep = datos["Repuestos"].sum()

        pdf.set_font("Arial",size=12)

        pdf.cell(200,10,f"Mano obra total: ${total_mo:,.0f}",ln=True)
        pdf.cell(200,10,f"Repuestos total: ${total_rep:,.0f}",ln=True)
        pdf.cell(200,10,f"Tecnicos: {len(tecnicos)}",ln=True)

        pdf.output("informe.pdf")

        with open("informe.pdf","rb") as f:

            st.download_button(
                "Descargar PDF",
                f,
                file_name="informe.pdf"
            )