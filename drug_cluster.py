import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans 
import streamlit as st
import json

st.title("Análisis de Clusteres (K-Means)")

variable_mapping = {
    "dec_pbc": "Incautaciones PBC (kg)",
    "dec_pbc100": "Incautaciones PBC (100mil hab)",
    "dec_cc": "Incautaciones Clor. Cocaína (kg.)",
    "dec_cc100": "Incautaciones Clor. Cocaína (100mil hab)",
    "dec_mar": "Incautaciones Marihuana (kg.)",
    "dec_mar100": "Incautaciones Marihuana (100mil hab)",
    "inc_sol": "Soles Decomisados (PEN)",
    "inc_usd": "Dólares Decomisados (USD)",
    "inc_act": "Activos Incautados (Cantidad)",
    "int_tra": "Intervenciones Tráfico Ilícito",
    "int_tra100": "Intervenciones Tráfico Ilícito (100mil hab)",
    "int_mic": "Intervenciones Microtráfico",
    "int_mic100":"Intervenciones Microtráfico (100mil hab)",
    "int_con": "Intervenciones Consumo",
    "int_con100":"Interveciones Consumo (100mil hab)",
    "det_tra": "Detenidos por Tráfico",
    "det_tra100": "Detenidos por Tráfico (100mil hab)",
    "det_mic": "Detenidos por Microtráfico",
    "det_mic100": "Detenidos por Microtráfico (100mil hab)",
    "det_con": "Detenidos por Consumo",
    "det_con100": "Detenidos por Consumo (100mil hab)"
}

st.sidebar.title("Panel de Selección")
st.sidebar.header("Seleccione la Variable de Interés:")
selected_var = st.sidebar.selectbox("Lista de Variables:",
                                    options=list(variable_mapping.values())
                                    )
selected_var_code = next(key for key, value in variable_mapping.items() if value == selected_var)

st.sidebar.header("Seleccione el Número de Clusteres:")
num_clusters = st.sidebar.slider("Número de Clusteres:", min_value=2, max_value=10, value=5)

df = pd.read_csv("peru_drugs.csv")


# Cargar datos geoespaciales desde el GeoJSON
with open("peru_departamental_simple.geojson", encoding="utf8") as data:
    departamentos = json.load(data)

for feature in departamentos["features"]:
    feature["properties"]["NOMBDEP"] = feature["properties"]["NOMBDEP"].lower()

id = []
departamento = []

for idx in range(len(departamentos["features"])):
    id.append(departamentos["features"][idx]["properties"]["FIRST_IDDP"])
    departamento.append(departamentos["features"][idx]["properties"]["NOMBDEP"])

geojson_df = pd.DataFrame({
    "id": id,
    "departamento": departamento
})

# Perform K-means clustering

X = df.groupby(["time", "departamento"])[selected_var_code].sum().unstack().fillna(0).T
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
cluster_labels = kmeans.fit_predict(X)

# Add cluster labels to the dataframe
df_clustered = pd.DataFrame({"departamento": X.index, "cluster": cluster_labels})

# Fusionar datos geoespaciales con información de clusters
map_df = pd.merge(geojson_df, df_clustered, how="inner", left_on="departamento", right_on="departamento")

# Visualize Clusters using Plotly


fig_clustered = px.scatter(df_clustered,
                           x="departamento",
                           y="cluster",
                           color="cluster",
                           hover_data=["departamento", "cluster"],
                           title=f"Clustering por Departamentos de {selected_var}",
                           labels={"cluster": "Cluster"},
                           width=900,
                           height=500)

fig_map = px.choropleth_mapbox(map_df,
                               geojson=departamentos,
                               locations="id",
                               featureidkey="properties.FIRST_IDDP",
                               color="cluster",
                               hover_data=["departamento", "cluster"],
                               mapbox_style="carto-darkmatter",
                               center={
                                   "lat":-9,
                                   "lon":-75
                               },
                               zoom=4,
                              )
fig_map.update_layout(margin={'r':0,'t':0,'l':0,'b':0})

cluster_stats = df_clustered.groupby("cluster").size().reset_index(name="Número de Departamentos")

fig = px.bar(cluster_stats,
             x="Número de Departamentos",  # Use the correct column name
             y="cluster",
             orientation="h",
             labels={
                "Número de Departamentos": "Número de Departamentos",  # Adjust label if needed
                "cluster": "Cluster"
                    },
             title="Cantidad de Clusteres",
             height=400,
             width=300,
             )
fig.update_layout(
    xaxis=dict(title_text="Número de Departamentos"),
    yaxis=dict(title_text="Cluster"),
    template="plotly_dark"
    )

st.subheader(f"Mapa de Clusters Departamental de {selected_var}")
st.plotly_chart(fig_map, use_container_width=True)

col = st.columns((5.5,2.5), gap="medium")

with col[0]:
    st.plotly_chart(fig_clustered, use_container_width=True)

with col[1]:
    st.plotly_chart(fig)
    with st.expander("Acerca de:",
                     expanded=False
                     ):
        st.write('''
            - :orange[**Realizado por:**] [Tato Warthon](https://github.com/warthon-190399).
            - :orange[**Entidad Gubernamental:**] [DIRANDRO - PNP](https://dirandro.policia.gob.pe/contenido.xhtml?id=10).
            - :orange[**Fuente**]: Datos extraídos a partir de los anuarios estadísticos de la PNP, sección Tráfico Ilícito de Drogas.
                 ''')

