import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import altair as alt 
import folium 
import streamlit as st 
from streamlit_folium import folium_static 
import json 
import warnings
warnings.filterwarnings("ignore")

# Config Page

alt.themes.enable("dark")

st.title("Drugboard")

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


years = [2012, 2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2022]

st.sidebar.header("Seleccione el Año de Estudio:")

selected_year = st.sidebar.slider("Años:",
                                  min_value=min(years),
                                  max_value=max(years),
                                  value=max(years)
                                  )
st.sidebar.write("Por favor, una vez realizada la selección asegúrese de cerrar el panel para poder visualizar mejor el dashboard.")

#Importamos df's

df = pd.read_csv("peru_drugs.csv")

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
    "id":id,
    "departamento":departamento
})

df["time"] = pd.to_numeric(df["time"], errors="coerce")

df_filtered = df[df["time"] == selected_year]



total_selecVar1 = df_filtered[selected_var_code].sum()

#Cambio porcentual
if selected_year > min(years):
    prev_year = df[df["time"] == (selected_year - 1)]
    total_selecVar0 = prev_year[selected_var_code].sum()
    percent_chg = ((total_selecVar1 - total_selecVar0)/total_selecVar0)*100
else:
    percent_chg = None

#Media y desv estandar
mean_value = np.mean(df_filtered[selected_var_code])
std_value = np.std(df_filtered[selected_var_code])

df_filtered["mean_pos"] = np.where(df_filtered[selected_var_code] > mean_value,
                                   "Above Mean",
                                   "Below Mean"
                                   )

prop_aboveMean = len(df_filtered[df_filtered["mean_pos"] == "Above Mean"])/len(df_filtered)

prop_belowMean = 1 - prop_aboveMean

#Columnas

col = st.columns((1.5, 4.7, 1.8), gap = "medium")

with col[0]:
    st.subheader("Métricas")
    if selected_var_code in ["dec_pbc","dec_cc","dec_mar","inc_sol","inc_usd","inc_act","int_tra","int_mic","int_con","det_tra","det_mic","det_con"]:
        st.metric(label=f"Total{selected_var}",
                  value=total_selecVar1,
                  delta=selected_year
                  )
        st.metric(label=f"{selected_var}",
                  value=f"{percent_chg:.2f}%" if percent_chg is not None else "No Data",
                  delta="Var.%"
                  )                          
        st.metric(label=f"Media de {selected_var}",
                  value=f"{mean_value:.2f}",
                  delta=selected_year
                  )
        st.metric(label=f"{selected_var}",
                  value=f"{std_value:.2f}",
                  delta="Desv. Estándar"
                  )
    elif selected_var_code in ["dec_pbc100","dec_cc100","dec_mar100","t_iqf100","t_iqnf100","inc_sol100","inc_usd100","inc_act100","int_tra100","int_mic100","int_con100","det_tra100","det_mic100","det_con100"]:
        st.metric(label=f"Media de {selected_var}",
                  value=f"{mean_value:.2f}",
                  delta="Ajustado por población"
                  )
        st.metric(label="Cant.Departamentos",
                  value=f"{prop_aboveMean*100:.1f}%",
                  delta="por encima de la media"
                  )
        st.metric(label="Cant. Departamentos",
                  value=f"{prop_belowMean*100:.1f}%",
                  delta="por debajo de la media"
                  )
        st.metric(label=f"{selected_var}",
                  value=f"{percent_chg:.2f}%" if percent_chg is not None else "No Data",
                  delta="Var. %"
                  )
        
    min_value = df_filtered[selected_var_code].min()
    max_value = df_filtered[selected_var_code].max()

    normalized_min_value = (mean_value - min_value) / (max_value - min_value)
    normalized_max_value = (mean_value - min_value) / (max_value - min_value)

    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=mean_value,
        domain={
            "x":[normalized_min_value, normalized_max_value],
            "y":[0,1] 
        },
        title={'text': "Media Normalizada",
               'font':{"size":25}
               }
    ))
    fig_gauge.update_layout(width=200,
                            height=400,
                            margin=dict(l=10, r=10, b=10, t=10)
                            )
    st.plotly_chart(fig_gauge)

with col[1]:
    st.subheader(f"{selected_var} en el año {selected_year}")
    m = folium.Map(location=[-9.1900, -75.0152],
                   zoom_start=5,
                   tiles="CartoDB dark_matter"
                   )
    folium.Choropleth(geo_data=departamentos,
                      name="choropleth",
                      data=df_filtered,
                      columns=["departamento", selected_var_code],
                      key_on="feature.properties.NOMBDEP",
                      fill_color="plasma",
                      fill_opacity=0.45,
                      line_opacity=0.7,
                      legend_name=selected_var,
                      highlight=True,
                      tooltip=folium.features.GeoJsonTooltip(fields=['departamento', selected_var_code], labels=True, sticky=False)
                      ).add_to(m)
    folium_static(m)

    def make_heatmap(input_df, input_y, input_x, input_color, input_color_theme):
        heatmap = alt.Chart(input_df).mark_rect().encode(
            y=alt.Y(f'{input_y}:O',
                    axis=alt.Axis(title="Year",
                                  titleFontSize=18,
                                  titlePadding=15,
                                  titleFontWeight=900,
                                  labelAngle=0
                                  )),
            x=alt.X(f'{input_x}:O',
                    axis=alt.Axis(title="",
                                  titleFontSize=18,
                                  titlePadding=15,
                                  titleFontWeight=900
                                  )),
            color=alt.Color(f'max({input_color}):Q',
                            legend=None,
                            scale=alt.Scale(scheme=input_color_theme)),
            stroke=alt.value('black'),
            strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=12
        )
        return heatmap

    
    heatmap = make_heatmap(df,"time", "departamento", selected_var_code, "cividis")

    st.altair_chart(heatmap, use_container_width=True)

with col[2]:

    st.subheader("Top 10 Departamentos")
    top_departments = df_filtered.nlargest(10, selected_var_code)[["departamento", selected_var_code]]
    top_departments = top_departments.sort_values(by=selected_var_code,
                                                 ascending=True
                                                 )
    
    fig = px.bar(top_departments,
                 x=selected_var_code,
                 y="departamento",
                 orientation="h",
                 labels={
                     selected_var_code:"Valor",
                     "departamento":"Departamento"
                     },
                 height=400,
                 width=300,
                 )

    fig.update_layout(xaxis=dict(title_text="Valor"),
                      yaxis=dict(title_text="Departamento"),
                      template="plotly_dark"
                      )
    
    st.plotly_chart(fig)

    with st.expander("Acerca de:",
                     expanded=False
                     ):
        st.write('''
            - :orange[**Realizado por:**] [Tato Warthon](https://github.com/warthon-190399).
            - :orange[**Entidad Gubernamental:**] [DIRANDRO - PNP](https://dirandro.policia.gob.pe/contenido.xhtml?id=10).
            - :orange[**Fuente**]: Datos extraídos a partir de los anuarios estadísticos de la PNP, sección Tráfico Ilícito de Drogas.
                 ''')














