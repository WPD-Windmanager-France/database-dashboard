"""Supabase database implementation"""

from typing import Any, Optional, cast

import streamlit as st
from supabase import Client, create_client

from config import settings


@st.cache_resource
def init_supabase_connection() -> Client:
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
        raise ValueError("Missing configuration: SUPABASE_URL and SUPABASE_API_KEY required")

    try:
        client = create_client(supabase_url, supabase_key)
        return client
    except Exception as e:
        st.error(f"Error initializing Supabase client: {e}")
        raise


def execute_rpc(function_name: str) -> Any:
    """Exécute une fonction RPC Supabase"""
    client = init_supabase_connection()
    response = client.rpc(function_name).execute()
    return response.data


def execute_query(table: str, columns: str = "*", filters: Optional[dict] = None, order_by: Optional[str] = None) -> Any:
    """Exécute une requête SELECT sur une table Supabase"""
    try:
        client = init_supabase_connection()
        query = client.table(table).select(columns)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if order_by:
            query = query.order(order_by)

        response = query.execute()
        return response.data
    except Exception as e:
        st.error(f"Error querying table {table}: {e}")
        return None


def update_record(table: str, filters: dict, data: dict) -> bool:
    """
    Met à jour un enregistrement dans une table Supabase

    Args:
        table: Nom de la table
        filters: Dictionnaire des filtres pour identifier l'enregistrement {column: value}
        data: Dictionnaire des données à mettre à jour {column: new_value}

    Returns:
        True si la mise à jour a réussi, False sinon
    """
    try:
        client = init_supabase_connection()
        query = client.table(table).update(data)

        for key, value in filters.items():
            query = query.eq(key, value)

        response = query.execute()
        return True
    except Exception as e:
        st.error(f"Error updating table {table}: {e}")
        return False


def insert_record(table: str, data: dict) -> Optional[dict]:
    """
    Insère un nouvel enregistrement dans une table Supabase

    Args:
        table: Nom de la table
        data: Dictionnaire des données à insérer {column: value}

    Returns:
        L'enregistrement inséré ou None en cas d'erreur
    """
    try:
        client = init_supabase_connection()
        response = client.table(table).insert(data).execute()
        return cast(dict, response.data[0]) if response.data else None
    except Exception as e:
        st.error(f"Error inserting into table {table}: {e}")
        return None


def delete_record(table: str, filters: dict) -> bool:
    """
    Supprime un enregistrement d'une table Supabase

    Args:
        table: Nom de la table
        filters: Dictionnaire des filtres pour identifier l'enregistrement {column: value}

    Returns:
        True si la suppression a réussi, False sinon
    """
    try:
        client = init_supabase_connection()
        query = client.table(table).delete()

        for key, value in filters.items():
            query = query.eq(key, value)

        response = query.execute()
        return True
    except Exception as e:
        st.error(f"Error deleting from table {table}: {e}")
        return False
