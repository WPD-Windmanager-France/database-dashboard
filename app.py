import streamlit as st
import pandas as pd
from database import execute_query, init_supabase_connection

# Configuration de la page
st.set_page_config(
    page_title="Windmanager France- Database",
    page_icon="",
    layout="wide"
)

st.title("Windmanager - Database")


# Récupération des statistiques via RPC
with st.spinner("Chargement des statistiques..."):
    try:
        client = init_supabase_connection()
        response = client.rpc('get_table_stats').execute()

        # Transformer les données pour le DataFrame
        stats_data = []
        for row in response.data:
            stats_data.append({
                "Table": row['table_name'],
                "Colonnes": row['column_count'],
                "Entrées": row['row_count']
            })

        df = pd.DataFrame(stats_data)

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
    except:
        pass
