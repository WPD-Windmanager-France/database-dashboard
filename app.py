import pandas as pd
import streamlit as st

from config import settings
from database import execute_rpc

# Configuration de la page
st.set_page_config(
    page_title="Windmanager France - Database",
    page_icon="",
    layout="wide"
)

st.title("Windmanager - Database")
st.caption(f"Environnement: {settings.environment} | Base de données: {settings.db_type}")

# Récupération des statistiques via RPC
with st.spinner("Chargement des statistiques..."):
    try:
        data = execute_rpc('get_table_stats')

        # Transformer les données pour le DataFrame
        stats_data = []
        for row in data:
            stats_data.append({
                "Table": row.get('table_name', 'N/A'),
                "Colonnes": row.get('column_count', 'N/A'),
                "Entrées": row.get('row_count', 'N/A')
            })

        df = pd.DataFrame(stats_data)

        # Trier par nombre d'entrées décroissant
        df = df.sort_values(by='Entrées', ascending=False).reset_index(drop=True)

    except Exception as e:
        st.error(f"Erreur lors du chargement des statistiques: {e}")
        df = pd.DataFrame(columns=["Table", "Colonnes", "Entrées"])

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Table": st.column_config.TextColumn("Table", width="large"),
        "Colonnes": st.column_config.NumberColumn("Colonnes", format="%d"),
        "Entrées": st.column_config.NumberColumn("Lignes", format="%d")
    }
)

# Statistiques globales
if not df.empty:
    try:
        total_entries = df["Entrées"].sum()
        populated_tables = len(df[df["Entrées"] > 0])
        total_tables = len(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total entrées", f"{total_entries:,}")
        with col2:
            st.metric("Tables avec données", f"{populated_tables}/{total_tables}")
        with col3:
            st.metric("Tables vides", f"{total_tables - populated_tables}")
    except Exception:
        pass
