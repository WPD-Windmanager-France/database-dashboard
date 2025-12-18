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


# Liste complète des tables
TABLES = [
    "company_roles",
    "farm_types",
    "person_roles",
    "companies",
    "employees",
    "farms",
    "ice_detection_systems",
    "persons",
    "substations",
    "wind_turbine_generators",
    "farm_company_roles",
    "farm_referents",
    "farm_actual_performances",
    "farm_administrations",
    "farm_electrical_delegations",
    "farm_environmental_installations",
    "farm_financial_guarantees",
    "farm_ice_detection_systems",
    "farm_locations",
    "farm_om_contracts",
    "farm_statuses",
    "farm_substation_details",
    "farm_target_performances",
    "farm_tariffs",
    "farm_tcma_contracts",
    "farm_turbine_details",
    "ingestion_versions"
]

# Récupération des statistiques
stats_data = []

with st.spinner("Chargement des statistiques..."):
    for table_name in TABLES:
        try:
            data = execute_query(table=table_name, columns="*")
            count = len(data) if data else 0
            stats_data.append({
                "Table": table_name,
                "Entrées": count
            })
        except Exception as e:
            stats_data.append({
                "Table": table_name,
                "Entrées": "Erreur"
            })

# Affichage du DataFrame
df = pd.DataFrame(stats_data)

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Table": st.column_config.TextColumn("Table", width="large"),
        "Entrées": st.column_config.NumberColumn("Lignes", format="%d")
    }
)

# Statistiques globales
try:
    numeric_df = df[df["Entrées"].apply(lambda x: isinstance(x, int))]
    total_entries = numeric_df["Entrées"].sum()
    populated_tables = len(numeric_df[numeric_df["Entrées"] > 0])

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total entrées", f"{total_entries:,}")
    with col2:
        st.metric("Tables avec données", f"{populated_tables}/{len(TABLES)}")
    with col3:
        st.metric("Tables vides", f"{len(TABLES) - populated_tables}")
except:
    pass
