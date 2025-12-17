import os
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL

class DatabaseConnection:
    """Gère la connexion à la base de données Supabase PostgreSQL"""

    def __init__(self):
        self.engine = None

    def get_engine(self) -> Engine:
        return self._create_supabase_engine()

    def _create_supabase_engine(self) -> Engine:
        """Crée un engine SQLAlchemy pour Supabase (PostgreSQL)"""
        
        # 1. Récupération des secrets
        if hasattr(st, 'secrets'):
            supabase_url = st.secrets.get('SUPABASE_URL')
            db_password = st.secrets.get('SUPABASE_DB_PASSWORD')
        else:
            supabase_url = os.getenv('SUPABASE_URL')
            db_password = os.getenv('SUPABASE_DB_PASSWORD')

        if not supabase_url or not db_password:
            raise ValueError("Configuration manquante")

        # 2. Extraction Host
        from urllib.parse import urlparse
        parsed = urlparse(supabase_url)
        hostname = parsed.hostname
        
        # Hostname théorique Supabase
        # Pour le pooling, c'est souvent la même adresse mais port 6543
        host = f"db.{hostname}" if not hostname.startswith("db.") else hostname
        
        st.write(f"🔄 Tentative connexion via Pooler (Port 6543) sur: {host}")

        # 3. Paramètres de connexion POOLER (Transaction Mode)
        # Port 6543 est recommandé pour les environnements serverless (Streamlit)
        # On désactive prepared statements pour la compatibilité pgbouncer/supavisor
        
        connection_url = URL.create(
            "postgresql+psycopg2",
            username=f"postgres.{hostname.split('.')[0]}", # Format user often required for pooler: user.projectref
            password=str(db_password),
            host=str(host),
            port=6543, 
            database="postgres",
        )
        
        # NOTE IMPORTANTE:
        # Avec le pooler Supabase, l'utilisateur doit souvent être au format:
        # [db_user].[project_ref]
        # Mais essayons d'abord avec "postgres" simple, si ça fail, on changera.
        # Edit: Je vais utiliser le user simple d'abord car Supavisor le supporte maintenant.
        
        connection_url = URL.create(
            "postgresql+psycopg2",
            username="postgres", 
            password=str(db_password),
            host=str(host),
            port=6543, 
            database="postgres",
        )

        # 4. Création de l'engine
        engine = create_engine(
            connection_url,
            pool_pre_ping=True,
            connect_args={
                "connect_timeout": 15,
                # "sslmode": "require" # Default in psycopg2
            }
        )
        return engine


@st.cache_resource
def get_database_engine() -> Engine:
    db = DatabaseConnection()
    return db.get_engine()


def execute_query(query: str, params: dict = None):
    try:
        engine = get_database_engine()
        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})
            if query.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
            else:
                conn.commit()
                return result.rowcount
    except Exception as e:
        st.error(f"Erreur SQL: {e}")
        return None
