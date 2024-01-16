# Narcotráfico en Perú: La Lucha en Cifras

## Descripción del Proyecto

Drugboard es una aplicación interactiva desarrollada en Streamlit que ofrece análisis detallados sobre el tráfico ilícito de drogas en Perú. El proyecto utiliza datos estadísticos de la Policía Nacional del Perú (PNP) para proporcionar visualizaciones informativas y mapas temáticos. Puedes observar el proyecto dando clic en: https://drugwar-b2d6m6rf2qsrwizby7bkio.streamlit.app/

## Funcionalidades Clave
1. **Panel Interactivo de Análisis de Datos**
**Visualización Dinámica:** Explora gráficos interactivos y métricas en tiempo real sobre variables clave, como incautaciones, decomisos y detenciones.
**Comparaciones Temporales:** Analiza tendencias a lo largo del tiempo y realiza comparaciones entre años para comprender la evolución del narcotráfico.
2. **Análisis de Clusteres (K-Means)**
**Clasificación Departamental:** Descubre patrones geográficos mediante el análisis de clústeres que agrupa departamentos con características similares en términos de tráfico ilícito de drogas.
**Mapas Temáticos:** Visualiza la clasificación de departamentos en el mapa para una comprensión rápida de las regiones con tendencias similares.

## Contenido del Repositorio
- **main.py:** Código principal que integra las funcionalidades y configura la interfaz de usuario utilizando Streamlit.
- **drug_panel.py:** Módulo que crea un panel interactivo de análisis de datos y visualizaciones.
- **drug_cluster.py:** Módulo que implementa el análisis de clústeres (K-Means) para clasificar departamentos según las estadísticas de narcotráfico.
- **peru_drugs.csv:** Conjunto de datos que contiene información sobre incautaciones, intervenciones y detenciones relacionadas con drogas en Perú.
- **peru_departamental_simple.geojson:** Datos geoespaciales en formato GeoJSON que representan la división departamental de Perú.

## Uso

- Asegúrate de tener todos los requisitos instalados.
- Ejecuta el siguiente comando en la terminal de tu IDE para iniciar la aplicación: **streamlit run drug_main.py**
- Se abrirá una ventana del navegador con la interfaz de usuario de Drugboard.
- Explora las diferentes opciones, selecciona variables de interés y obtén análisis detallados sobre el narcotráfico en Perú.

## Acerca del Autor
El proyecto fue realizado por Tato Warthon en colaboración con la Dirección Antidrogas de la Policía Nacional del Perú (DIRANDRO - PNP).

## Fuentes de Datos
Los datos utilizados en este proyecto fueron extraídos de los anuarios estadísticos de la PNP, específicamente de la sección de Tráfico Ilícito de Drogas.

## Licencia
Este proyecto está bajo la licencia MIT.





