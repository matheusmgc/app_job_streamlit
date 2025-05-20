import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import os

st.set_page_config(page_title="Mapa Interativo", layout="wide")

#st.markdown("<h1 style='text-align: center; color: #2F4F4F;'>📍 Mapa com Coordenadas</h1>", unsafe_allow_html=True)
#st.markdown("---")

file_path = r"C:\Users\mathe\Documents\Jobs\Gustavo\app_job_streamlit\data\lat_long.xlsx"

if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path)

        if {'Lat_long', 'Hora'}.issubset(df.columns):
            # Separar latitude e longitude
            df[['latitude', 'longitude']] = df['Lat_long'].str.split(',', expand=True).astype(float)

            # Converter hora
            df['Hora'] = pd.to_datetime(df['Hora'], format='%H:%M:%S', errors='coerce')
            df['Hora_str'] = df['Hora'].dt.strftime('%H:%M')

            # Lista única de horas para filtro
            horas_unicas = sorted(df['Hora_str'].dropna().unique())

            # Layout: duas colunas - mapa e filtros
            mapa_col, filtro_col = st.columns([7, 3])

            # No filtro, checkbox para cada hora
            with filtro_col:
                st.markdown("### Filtrar Horas")
                # Checkbox geral para "Selecionar tudo"
                select_all = st.checkbox("Selecionar todas as horas", value=True)

                if select_all:
                    selected_horas = st.multiselect("Escolha as horas para mostrar:", horas_unicas, default=horas_unicas)
                else:
                    selected_horas = st.multiselect("Escolha as horas para mostrar:", horas_unicas, default=[])

            # Filtrar dados de acordo com seleção
            df_filtrado = df[df['Hora_str'].isin(selected_horas)]

            # Calcular centro e bounds do mapa (se não tiver pontos, colocar default)
            if not df_filtrado.empty:
                lat_center = df_filtrado['latitude'].mean()
                lon_center = df_filtrado['longitude'].mean()
                min_lat, max_lat = df_filtrado['latitude'].min(), df_filtrado['latitude'].max()
                min_lon, max_lon = df_filtrado['longitude'].min(), df_filtrado['longitude'].max()
                zoom_start = 12
            else:
                # Centro padrão (exemplo: Brasil)
                lat_center, lon_center = -15.788, -47.894
                min_lat, max_lat, min_lon, max_lon = lat_center, lat_center, lon_center, lon_center
                zoom_start = 4

            # Criar mapa
            m = folium.Map(location=[lat_center, lon_center], zoom_start=zoom_start)

            # Adicionar marcadores filtrados
            for _, row in df_filtrado.iterrows():
                popup_text = f"<b>{row.get('nome', 'Ponto')}</b><br>Hora: {row['Hora_str']}"
                folium.Marker(
                    location=[row['latitude'], row['longitude']],
                    popup=popup_text,
                    icon=folium.Icon(color='green', icon='info-sign')
                ).add_to(m)

            # Ajustar view para os pontos filtrados
            if not df_filtrado.empty:
                m.fit_bounds([[min_lat, min_lon], [max_lat, max_lon]])

            # Mostrar mapa (altura fixa para evitar scroll vertical)
            with mapa_col:
                st_folium(m, width=800, height=600)

        else:
            st.error("O arquivo deve conter as colunas 'Lat_long' e 'Hora'.")
    except Exception as e:
        st.error(f"Erro ao processar o arquivo: {e}")
else:
    st.error(f"Arquivo '{file_path}' não encontrado.")
