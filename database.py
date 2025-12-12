import os
import struct
from typing import Optional
from dotenv import load_dotenv
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine
from azure.identity import ClientSecretCredential
import pyodbc
from urllib.parse import quote_plus

load_dotenv()


class DatabaseConnection:
    """Gère la connexion à la base de données (Azure SQL avec Entra ID ou SQL auth, ou SQLite local)"""

    def __init__(self, use_local: bool = False):
        self.use_local = use_local
        self.engine: Optional[Engine] = None

    def get_engine(self) -> Engine:
        """Retourne le SQLAlchemy engine approprié selon l'environnement"""
        if self.use_local:
            return self._create_sqlite_engine()
        else:
            return self._create_azure_engine()

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

    def _create_azure_engine(self) -> Engine:
        """Crée un engine SQLAlchemy pour Azure SQL (Entra ID ou SQL authentication)"""
        # Récupère les informations depuis l'environnement ou Streamlit secrets
        if hasattr(st, 'secrets') and 'AZURE_SQL_SERVER' in st.secrets:
            server = st.secrets['AZURE_SQL_SERVER']
            database = st.secrets['AZURE_SQL_DATABASE']
            use_entra_id = st.secrets.get('USE_ENTRA_ID', 'false').lower() == 'true'

            if use_entra_id:
                tenant_id = st.secrets['AZURE_TENANT_ID']
                client_id = st.secrets['AZURE_CLIENT_ID']
                client_secret = st.secrets['AZURE_CLIENT_SECRET']
                username = None
                password = None
            else:
                username = st.secrets['AZURE_SQL_USER']
                password = st.secrets['AZURE_SQL_PASSWORD']
                tenant_id = client_id = client_secret = None
        else:
            server = os.getenv('AZURE_SQL_SERVER')
            database = os.getenv('AZURE_SQL_DATABASE')
            use_entra_id = os.getenv('USE_ENTRA_ID', 'false').lower() == 'true'

            if use_entra_id:
                tenant_id = os.getenv('AZURE_TENANT_ID')
                client_id = os.getenv('AZURE_CLIENT_ID')
                client_secret = os.getenv('AZURE_CLIENT_SECRET')
                username = None
                password = None
            else:
                username = os.getenv('AZURE_SQL_USER')
                password = os.getenv('AZURE_SQL_PASSWORD')
                tenant_id = client_id = client_secret = None

        if not all([server, database]):
            raise ValueError("Configuration Azure SQL manquante (server, database)")

        # Entra ID mode (preferred)
        if use_entra_id:
            if not all([tenant_id, client_id, client_secret]):
                raise ValueError("Configuration Entra ID manquante (tenant_id, client_id, client_secret)")

            # Type narrowing: at this point we know these values are not None
            assert tenant_id is not None and client_id is not None and client_secret is not None

            # Get Entra ID token with Service Principal
            credential = ClientSecretCredential(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret
            )
            token_bytes = credential.get_token("https://database.windows.net/.default").token.encode("UTF-16-LE")
            token_struct = struct.pack(f'<I{len(token_bytes)}s', len(token_bytes), token_bytes)

            # Connection string for Entra ID
            # Note: server and database are guaranteed non-None by earlier check
            connection_url = URL.create(
                "mssql+pyodbc",
                query={
                    "driver": "ODBC Driver 18 for SQL Server",
                    "server": str(server),
                    "database": str(database),
                    "encrypt": "yes",
                    "TrustServerCertificate": "no",
                    "Connection Timeout": "30",
                }
            )

            engine = create_engine(
                connection_url,
                connect_args={
                    "attrs_before": {
                        1256: token_struct  # SQL_COPT_SS_ACCESS_TOKEN
                    }
                }
            )
            return engine

        # SQL Authentication mode (temporary)
        else:
            if not all([username, password]):
                raise ValueError("Configuration SQL Authentication manquante (username, password)")

            # Type narrowing: at this point we know these values are not None
            assert username is not None and password is not None

            # Connection string for SQL auth
            connection_url = URL.create(
                "mssql+pyodbc",
                username=str(username),
                password=str(password),
                host=str(server),
                database=str(database),
                query={
                    "driver": "ODBC Driver 18 for SQL Server",
                    "encrypt": "yes",
                    "TrustServerCertificate": "no",
                    "Connection Timeout": "30",
                }
            )

            engine = create_engine(connection_url)
            return engine


@st.cache_resource
def get_database_engine(use_local: bool = False) -> Engine:
    """
    Retourne un SQLAlchemy engine avec cache Streamlit

    Args:
        use_local: True pour SQLite local, False pour Azure SQL avec Azure AD

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
        use_local: True pour SQLite local, False pour Azure SQL

    Returns:
        Liste de dictionnaires pour SELECT, nombre de lignes affectées sinon
    """
    try:
        engine = get_database_engine(use_local=use_local)

        with engine.connect() as conn:
            result = conn.execute(text(query), params or {})

            # Pour les SELECT
            if query.strip().upper().startswith('SELECT'):
                rows = result.fetchall()
                # Convertit en liste de dictionnaires
                return [dict(row._mapping) for row in rows]
            else:
                # Pour les INSERT, UPDATE, DELETE
                conn.commit()
                return result.rowcount

    except Exception as e:
        st.error(f"Erreur lors de l'exécution de la requête: {str(e)}")
        return None
