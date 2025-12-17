import os
from typing import Optional
from dotenv import load_dotenv
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine, URL

load_dotenv()


class DatabaseConnection:
    """Gère la connexion à la base de données (Supabase PostgreSQL ou SQLite local)"""

    def __init__(self, use_local: bool = False):
        self.use_local = use_local
        self.engine: Optional[Engine] = None

    def get_engine(self) -> Engine:
        """Retourne le SQLAlchemy engine approprié selon l'environnement"""
        if self.use_local:
            return self._create_sqlite_engine()
        else:
            return self._create_supabase_engine()

    def _create_sqlite_engine(self) -> Engine:
        """Crée un engine SQLAlchemy pour SQLite local"""
        db_path = os.path.join(os.path.dirname(__file__), "DATA", "windmanager.db")

        if not os.path.exists(db_path):
            raise FileNotFoundError(f"Base de données locale non trouvée: {db_path}")

        connection_string = f"sqlite:///{db_path}"
        engine = create_engine(
            connection_string,
            connect_args={"check_same_thread": False}
        )
        return engine

    def _create_supabase_engine(self) -> Engine:
        """Crée un engine SQLAlchemy pour Supabase (PostgreSQL)"""
        
        # Helper pour récupérer une valeur depuis secrets ou env
        def get_config(key, default=None):
            if hasattr(st, 'secrets') and key in st.secrets:
                return st.secrets[key]
            return os.getenv(key, default)

        # Récupération des credentials
        # On cherche d'abord les clés spécifiques SUPABASE, puis génériques DB
        host = get_config('SUPABASE_HOST') or get_config('DB_HOST')
        database = get_config('SUPABASE_DATABASE') or get_config('DB_NAME')
        user = get_config('SUPABASE_USER') or get_config('DB_USER')
        password = get_config('SUPABASE_PASSWORD') or get_config('DB_PASSWORD')
        port = get_config('SUPABASE_PORT') or get_config('DB_PORT', 5432)

        if not all([host, database, user, password]):
            missing = []
            if not host: missing.append("HOST")
            if not database: missing.append("DATABASE")
            if not user: missing.append("USER")
            if not password: missing.append("PASSWORD")
            raise ValueError(f"Configuration Supabase manquante: {', '.join(missing)}")

        # Construction de l'URL de connexion
        # Format: postgresql+psycopg2://user:password@host:port/dbname
        connection_url = URL.create(
            "postgresql+psycopg2",
            username=str(user),
            password=str(password),
            host=str(host),
            port=int(port),
            database=str(database),
        )

        # Création de l'engine
        # pool_pre_ping=True est utile pour les connexions cloud qui peuvent se fermer
        engine = create_engine(
            connection_url,
            pool_pre_ping=True
        )
        return engine


@st.cache_resource
def get_database_engine(use_local: bool = False) -> Engine:
    """
    Retourne un SQLAlchemy engine avec cache Streamlit

    Args:
        use_local: True pour SQLite local, False pour Supabase (Postgres)

    Returns:
        SQLAlchemy Engine
    """
    db = DatabaseConnection(use_local=use_local)
    return db.get_engine()


def execute_query(query: str, params: Optional[dict] = None, use_local: bool = False):
    """
    Exécute une requête SQL et retourne les résultats

    Args:
        query: Requête SQL à exécuter (utilisez :param pour les paramètres nommés)
        params: Dictionnaire de paramètres pour la requête (optional)
        use_local: True pour SQLite local, False pour Supabase

    Returns:
        Liste de dictionnaires pour SELECT, nombre de lignes affectées sinon
    """
    try:
        engine = get_database_engine(use_local=use_local)

        with engine.connect() as conn:
            # Pour SQLAlchemy avec psycopg2, les paramètres nommés fonctionnent généralement
            # mais il est plus sûr d'utiliser text()
            result = conn.execute(text(query), params or {})

            # Pour les SELECT
            if query.strip().upper().startswith('SELECT'):
                # fetchall retourne des Row objects qui se comportent comme des tuples nommés
                # on peut les convertir en dict via _mapping
                rows = result.fetchall()
                return [dict(row._mapping) for row in rows]
            else:
                # Pour les INSERT, UPDATE, DELETE
                conn.commit()
                return result.rowcount

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        # En prod, on pourrait vouloir logger l'erreur complète
        print(f"Database Error: {e}")
        return None