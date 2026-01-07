"""Unified database interface - routes to SQLite or Supabase implementation"""

from typing import Any, Optional

import streamlit as st

from config import settings

# Import dynamique selon l'environnement
if settings.db_type == "sqlite":
    from DATABASE import sqlite_db as db
elif settings.db_type == "supabase":
    from DATABASE import supabase_db as db
else:
    raise ValueError(f"Unsupported database type: {settings.db_type}")


# ==================== Exported Functions ====================

def execute_rpc(function_name: str) -> Any:
    """
    Interface unifiée pour exécuter des fonctions RPC
    Route automatiquement vers SQLite ou Supabase selon la configuration
    """
    return db.execute_rpc(function_name)


def execute_query(table: str, columns: str = "*", filters: Optional[dict] = None, order_by: Optional[str] = None) -> Any:
    """
    Exécute une requête SELECT sur une table

    Args:
        table: Table name
        columns: Columns to select (default: "*")
        filters: Dictionary of filters {column: value}
        order_by: Column name to order by

    Returns:
        Query results or None on error
    """
    return db.execute_query(table, columns, filters, order_by)


@st.cache_data(ttl=300)
def get_all_farms() -> list[dict]:
    """
    Récupère la liste de tous les parcs éoliens

    Returns:
        List of farms with uuid, code, project, spv
    """
    return execute_query(
        table="farms",
        columns="uuid, code, project, spv",
        order_by="code"
    ) or []


def get_farm_by_code(farm_code: str) -> Optional[dict]:
    """
    Récupère les détails d'un parc par son code

    Args:
        farm_code: Farm code

    Returns:
        Farm details or None
    """
    results = execute_query(
        table="farms",
        columns="*",
        filters={"code": farm_code}
    )
    return results[0] if results else None


# Expose connection functions for backward compatibility
if settings.db_type == "supabase":
    from DATABASE.supabase_db import init_supabase_connection
elif settings.db_type == "sqlite":
    from DATABASE.sqlite_db import get_sqlite_engine
