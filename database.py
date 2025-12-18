"""Database connection module supporting both SQLite (local) and Supabase (production)"""

import os
from typing import Any, Optional

import streamlit as st

from config import settings

# Import conditionnel selon l'environnement
if settings.db_type == "sqlite":
    from sqlalchemy import create_engine, text
    from sqlalchemy.engine import Engine
elif settings.db_type == "supabase":
    from supabase import Client, create_client


# ==================== SQLite Functions ====================

@st.cache_resource
def get_sqlite_engine() -> "Engine":
    """Crée un engine SQLAlchemy pour SQLite local"""
    db_path = os.path.join(os.path.dirname(__file__), settings.db_path)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Base de données locale non trouvée: {db_path}")

    connection_string = f"sqlite:///{db_path}"
    engine = create_engine(
        connection_string,
        connect_args={"check_same_thread": False}
    )
    return engine


def execute_sqlite_rpc(function_name: str) -> list[dict]:
    """
    Simule un appel RPC pour SQLite en exécutant des requêtes SQL natives
    """
    if function_name == "get_table_stats":
        engine = get_sqlite_engine()

        with engine.connect() as conn:
            # Requête pour obtenir les stats des tables
            query = text("""
                SELECT
                    m.name as table_name,
                    COUNT(p.name) as column_count,
                    0 as row_count
                FROM sqlite_master m
                LEFT JOIN pragma_table_info(m.name) p ON 1=1
                WHERE m.type = 'table'
                    AND m.name NOT LIKE 'sqlite_%'
                GROUP BY m.name
                ORDER BY m.name
            """)

            result = conn.execute(query)
            tables_info = [dict(row._mapping) for row in result]

            # Pour chaque table, compter les lignes
            for table_info in tables_info:
                table_name = table_info['table_name']
                count_query = text(f"SELECT COUNT(*) as cnt FROM {table_name}")
                count_result = conn.execute(count_query)
                table_info['row_count'] = count_result.scalar()

            return tables_info
    else:
        raise NotImplementedError(f"RPC function '{function_name}' not implemented for SQLite")


# ==================== Supabase Functions ====================

@st.cache_resource
def init_supabase_connection() -> "Client":
    """Initialise la connexion au client Supabase"""
    # Récupération des secrets
    try:
        supabase_url = st.secrets.get('SUPABASE_URL')
        supabase_key = st.secrets.get('SUPABASE_API_KEY')
    except (FileNotFoundError, KeyError):
        # Fallback sur .secrets.toml via dynaconf
        supabase_url = settings.get('supabase_url')
        supabase_key = settings.get('supabase_api_key')

    if not supabase_url or not supabase_key:
        raise ValueError("Configuration manquante: SUPABASE_URL et SUPABASE_API_KEY requis")

    try:
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        st.error(f"Erreur lors de l'initialisation du client Supabase: {e}")
        raise


def execute_supabase_rpc(function_name: str) -> Any:
    """Exécute une fonction RPC Supabase"""
    client = init_supabase_connection()
    response = client.rpc(function_name).execute()
    return response.data


# ==================== Unified Interface ====================

def execute_rpc(function_name: str) -> Any:
    """
    Interface unifiée pour exécuter des fonctions RPC
    Route automatiquement vers SQLite ou Supabase selon la configuration
    """
    if settings.db_type == "sqlite":
        return execute_sqlite_rpc(function_name)
    elif settings.db_type == "supabase":
        return execute_supabase_rpc(function_name)
    else:
        raise ValueError(f"Type de base de données non supporté: {settings.db_type}")


def execute_query(table: str, columns: str = "*", filters: Optional[dict] = None) -> Any:
    """
    Exécute une requête SELECT sur une table (Supabase uniquement pour l'instant)
    """
    if settings.db_type == "supabase":
        try:
            client = init_supabase_connection()
            query = client.table(table).select(columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            response = query.execute()
            return response.data
        except Exception as e:
            st.error(f"Erreur lors de la requête sur {table}: {e}")
            return None
    else:
        raise NotImplementedError("execute_query not implemented for SQLite")
