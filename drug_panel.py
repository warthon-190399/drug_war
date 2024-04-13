import pandas as pd
import numpy as np
import plotly.express as px
import altair as alt 
import streamlit as st 
import json 
import warnings
warnings.filterwarnings("ignore")

# Config Page

st.title("Drugboard")

#Mapeo de variables y desarrollo del sidebar 

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
logo = "logoPulseNegro.png"
st.sidebar.image(logo, width=300)
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
#Hallamos medidas

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

#Choropleth
fig_map = px.choropleth_mapbox(df_filtered,
                           geojson=departamentos,
                           locations='departamento',
                           featureidkey="properties.NOMBDEP",
                           color=selected_var_code,
                           color_continuous_scale="Cividis",
                           mapbox_style="carto-darkmatter",
                           zoom=4,
                           center={"lat": -9.1900, "lon": -75.0152},
                           opacity=0.9,
                           labels={selected_var_code: selected_var},
                           hover_name='departamento',
                           hover_data={selected_var_code: True, 'departamento': False}
                           )
fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

#figdensity
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
                            scale=alt.Scale(scheme=input_color_theme)
                            ),
                    stroke=alt.value('black'),
                    strokeWidth=alt.value(0.25),
        ).properties(width=900
        ).configure_axis(
            labelFontSize=12,
            titleFontSize=12
        )
    return heatmap

    
heatmap = make_heatmap(df,"time", "departamento", selected_var_code, "cividis")

#Grafico de Barras
top_departments = df_filtered.nlargest(10, selected_var_code)[["departamento", selected_var_code]]
top_departments = top_departments.sort_values(by=selected_var_code,
                                                 ascending=True
                                                 )
fig_top = px.bar(top_departments,
                 x=selected_var_code,
                 y="departamento",
                 template="ggplot2",
                 orientation="h",
                 labels={
                     selected_var_code:"Valor",
                     "departamento":"Departamento"
                     },
                 height=250,
                 width=300,
                 )


fig_top.update_layout(xaxis=dict(title_text="Valor"),
                      yaxis=dict(title_text="Departamento"),
                      template="plotly_dark",
                      margin=dict(l=0, r=0, t=0, b=0)  # Aquí establecemos todos los márgenes a 0
                      )

# Mostrar el gráfico

#Columnas
col0 = st.columns((6,3), gap="medium")
with col0[0]:
    st.subheader("Métricas")

with col0[1]:
    st.subheader("Top 10 departamentos")

col1 = st.columns((3,3,3), gap="medium")

with col1[0]:
    if selected_var_code in ["dec_pbc","dec_cc","dec_mar","inc_sol","inc_usd","inc_act","int_tra","int_mic","int_con","det_tra","det_mic","det_con"]:
        st.metric(label=f"Total{selected_var}",
                  value=total_selecVar1,
                  delta=selected_year
                  )
        st.metric(label=f"{selected_var}",
                  value=f"{percent_chg:.2f}%" if percent_chg is not None else "No Data",
                  delta="Var.%"
                  )
    elif selected_var_code in ["dec_pbc100","dec_cc100","dec_mar100","t_iqf100","t_iqnf100","inc_sol100","inc_usd100","inc_act100","int_tra100","int_mic100","int_con100","det_tra100","det_mic100","det_con100"]:
        st.metric(label=f"Media de {selected_var}",
                  value=f"{mean_value:.2f}",
                  delta="Ajustado por población"
                  )
        st.metric(label=f"{selected_var}",
                  value=f"{percent_chg:.2f}%" if percent_chg is not None else "No Data",
                  delta="Var. %"
                  )
with col1[1]:
    if selected_var_code in ["dec_pbc","dec_cc","dec_mar","inc_sol","inc_usd","inc_act","int_tra","int_mic","int_con","det_tra","det_mic","det_con"]:
        st.metric(label=f"Media de {selected_var}",
                  value=f"{mean_value:.2f}",
                  delta=selected_year
                  )
        st.metric(label=f"{selected_var}",
                  value=f"{std_value:.2f}",
                  delta="Desv. Estándar"
                  )
    elif selected_var_code in ["dec_pbc100","dec_cc100","dec_mar100","t_iqf100","t_iqnf100","inc_sol100","inc_usd100","inc_act100","int_tra100","int_mic100","int_con100","det_tra100","det_mic100","det_con100"]:
        st.metric(label="Cant.Departamentos",
                  value=f"{prop_aboveMean*100:.1f}%",
                  delta="por encima de la media"
                  )
        
        st.metric(label="Cant. Departamentos",
                  value=f"{prop_belowMean*100:.1f}%",
                  delta="por debajo de la media"
                  )
with col1[2]:
    st.plotly_chart(fig_top, use_container_width=True)

st.subheader(f"{selected_var} en el año {selected_year}")
st.plotly_chart(fig_map, use_container_width=True)

col3 = st.columns((5.5, 2.5), gap = "medium")

with col3[0]:
    st.altair_chart(heatmap, use_container_width=True)
with col3[1]:
    with st.expander("Acerca de:",
                     expanded=False
                     ):
        st.write('''
            - :orange[**Realizado por:**] [Tato Warthon](https://github.com/warthon-190399).
            - :orange[**Entidad Gubernamental:**] [DIRANDRO - PNP](https://dirandro.policia.gob.pe/contenido.xhtml?id=10).
            - :orange[**Fuente**]: Datos extraídos a partir de los anuarios estadísticos de la PNP, sección Tráfico Ilícito de Drogas.
                 ''')













