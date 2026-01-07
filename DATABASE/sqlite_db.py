"""SQLite database implementation"""

import os
from typing import Any, Optional

import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from config import settings


@st.cache_resource
def get_sqlite_engine() -> Engine:
    """Crée un engine SQLAlchemy pour SQLite local"""
    db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), settings.db_path)

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Local database not found: {db_path}")

    connection_string = f"sqlite:///{db_path}"
    engine = create_engine(
        connection_string,
        connect_args={"check_same_thread": False}
    )
    return engine


def execute_rpc(function_name: str) -> list[dict]:
    """Simule un appel RPC pour SQLite en exécutant des requêtes SQL natives"""
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


def execute_query(table: str, columns: str = "*", filters: Optional[dict] = None, order_by: Optional[str] = None) -> Any:
    """Exécute une requête SELECT sur une table SQLite"""
    try:
        engine = get_sqlite_engine()
        with engine.connect() as conn:
            # Build SQL query
            sql_query = f"SELECT {columns} FROM {table}"

            params = {}
            if filters:
                where_clauses = []
                for i, (key, value) in enumerate(filters.items()):
                    param_name = f"param_{i}"
                    where_clauses.append(f"{key} = :{param_name}")
                    params[param_name] = value
                sql_query += " WHERE " + " AND ".join(where_clauses)

            if order_by:
                sql_query += f" ORDER BY {order_by}"

            result = conn.execute(text(sql_query), params)
            return [dict(row._mapping) for row in result]
    except Exception as e:
        st.error(f"Error querying table {table}: {e}")
        return None
