import streamlit as st

st.set_page_config(page_title="Lucha Contra el Narcotráfico - Perú",
                   layout="wide",
                   page_icon="🍂",
                   initial_sidebar_state="expanded"
                   )

st.title("Narcotráfico en Perú: La Lucha en Cifras")
st.subheader("Seleccione el análisis que desea explorar:")

apps = {
    "drug_panel": "Panel Interactivo de Análisis de Datos",
    "drug_cluster": "Análisis de Clusteres (K-Means)"
}

selected_app = st.selectbox("App:", list(apps.values()))

selected_script = [key for key, value in apps.items() if value == selected_app][0]

if selected_script == "drug_panel":
    with open('drug_panel.py', 'r', encoding='utf-8') as file:
        exec(file.read())
elif selected_script == "drug_cluster":
    with open('drug_cluster.py', 'r', encoding='utf-8') as file:
        exec(file.read())