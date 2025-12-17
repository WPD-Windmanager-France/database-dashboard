import streamlit as st
import os
import pandas as pd
from database import get_database_engine, execute_query

# Configuration de la page
st.set_page_config(
    page_title="Wind Manager - Database Stats",
    page_icon="🌬️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Détecte l'environnement (local ou cloud)
# Priorité : st.secrets -> os.getenv -> Default (False/Cloud)
if hasattr(st, "secrets") and "USE_LOCAL_DB" in st.secrets:
    USE_LOCAL_DB = str(st.secrets["USE_LOCAL_DB"]).lower() == "true"
else:
    # Par défaut False (Cloud) pour la prod, sauf si .env local dit le contraire
    USE_LOCAL_DB = os.getenv("USE_LOCAL_DB", "false").lower() == "true"

# Titre principal
st.title("🌬️ Wind Manager - Database Statistics")
st.caption("Version 1.0 - Statistiques de la base de données")

# Sidebar pour la configuration
with st.sidebar:
    st.header("Configuration")

    # Affiche l'environnement actuel
    if USE_LOCAL_DB:
        st.info("🏠 **Mode:** Local (SQLite)")
        st.caption("Base: DATA/windmanager.db")
    else:
        st.success("☁️ **Mode:** Cloud (Supabase)")
        st.caption("PostgreSQL Connection")

    # Test de connexion
    st.divider()
    if st.button("🔌 Tester la connexion"):
        with st.spinner("Connexion en cours..."):
            try:
                engine = get_database_engine(use_local=USE_LOCAL_DB)
                with engine.connect() as conn:
                    st.success("✅ Connexion réussie !")
            except Exception as e:
                st.error(f"❌ Erreur de connexion")
                st.exception(e)

# Liste de toutes les tables de la base SQLite locale (20 tables)
TABLES = [
    # Reference Tables
    ("company_roles", "Rôles des entreprises", "📋"),
    ("farm_types", "Types de fermes", "📋"),
    ("person_roles", "Rôles des personnes", "📋"),

    # Entity Tables
    ("companies", "Entreprises", "🏢"),
    ("farms", "Fermes", "🏭"),
    ("ice_detection_systems", "Systèmes de détection de glace", "❄️"),
    ("persons", "Personnes", "👤"),
    ("substations", "Sous-stations", "🔌"),
    ("wind_turbine_generators", "Éoliennes", "⚡"),

    # Relationship Tables
    ("farm_company_roles", "Relations Ferme-Entreprise", "🔗"),
    ("farm_referents", "Référents de fermes", "📊"),

    # Look-up Tables
    ("farm_administrations", "Administrations", "📋"),
    ("farm_environmental_installations", "Installations environnementales", "🌱"),
    ("farm_ice_detection_systems", "Systèmes IDS par ferme", "❄️"),
    ("farm_locations", "Localisations", "📍"),
    ("farm_om_contracts", "Contrats O&M", "📄"),
    ("farm_statuses", "Statuts des fermes", "📊"),
    ("farm_substation_details", "Détails sous-stations", "🔌"),
    ("farm_tcma_contracts", "Contrats TCMA", "📄"),
    ("farm_turbine_details", "Détails turbines", "⚡"),
]

# Affichage des statistiques
st.header("📊 Statistiques par table")
st.markdown("Nombre de lignes dans chaque table de la base de données.")

# Conteneur pour les résultats
with st.spinner("Chargement des statistiques..."):
    try:
        # Prépare les données pour le DataFrame
        stats_data = []

        for table_name, description, icon in TABLES:
            try:
                # Compte les lignes
                query = f"SELECT COUNT(*) as count FROM {table_name}"
                result = execute_query(query, use_local=USE_LOCAL_DB)

                if result and isinstance(result, list) and len(result) > 0:
                    count = result[0]['count']
                    stats_data.append({
                        "Icône": icon,
                        "Table": table_name,
                        "Description": description,
                        "Nombre de lignes": count
                    })
                else:
                    stats_data.append({
                        "Icône": icon,
                        "Table": table_name,
                        "Description": description,
                        "Nombre de lignes": "Erreur"
                    })

            except Exception as e:
                stats_data.append({
                    "Icône": icon,
                    "Table": table_name,
                    "Description": description,
                    "Nombre de lignes": f"Erreur: {str(e)}"
                })

        # Affiche le DataFrame
        df = pd.DataFrame(stats_data)

        # Affichage avec style
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Icône": st.column_config.TextColumn("", width="small"),
                "Table": st.column_config.TextColumn("Table", width="medium"),
                "Description": st.column_config.TextColumn("Description", width="large"),
                "Nombre de lignes": st.column_config.NumberColumn(
                    "Nombre de lignes",
                    format="%d"
                )
            }
        )

        # Calcul du total
        try:
            total_rows = df[df["Nombre de lignes"].apply(lambda x: isinstance(x, int))]["Nombre de lignes"].sum()
            st.metric("📊 Total de lignes", f"{total_rows:,}")
        except:
            pass

        # Télécharger les stats en CSV
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Télécharger les statistiques (CSV)",
            data=csv,
            file_name="windmanager_stats.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error("❌ Impossible de charger les statistiques")
        st.exception(e)

# Informations complémentaires
st.divider()
st.subheader("ℹ️ Informations")

col1, col2 = st.columns(2)

with col1:
    st.markdown("""
    ### À propos
    Cette application affiche les statistiques de la base de données Wind Manager.

    **Fonctionnalités:**
    - Vue d'ensemble du nombre de lignes par table
    - Support SQLite (local) et Supabase (cloud)
    - Connexion sécurisée PostgreSQL
    """)

with col2:
    st.markdown("""
    ### Prochaines étapes
    1. ✅ Connexion Supabase configurée
    2. ✅ Statistiques de base affichées
    3. ⏳ CI/CD à mettre en place
    4. ⏳ Formulaires CRUD à développer

    **Version:** 1.0
    """)

# Footer
st.divider()
st.caption("Wind Manager Database Manager v1.0 - Développé avec Streamlit 🚀")
