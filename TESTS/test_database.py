"""Tests de connexion et fonctions database"""
import os

from config import settings


def test_config_loading():
    """Vérifie que dynaconf charge bien la config"""
    assert settings.environment in ['development', 'production']
    assert settings.db_type in ['sqlite', 'supabase']
    assert settings.app_name == "Windmanager"


def test_sqlite_connection():
    """Vérifie que SQLite se connecte et retourne des stats"""
    if settings.db_type == "sqlite":
        from database import execute_rpc

        db_path = os.path.join(os.path.dirname(__file__), "..", settings.db_path)
        if not os.path.exists(db_path):
            # Skip test si la base n'existe pas (CI environment)
            return

        result = execute_rpc('get_table_stats')
        assert isinstance(result, list)
        assert len(result) > 0

        # Vérifier la structure des données
        first_table = result[0]
        assert 'table_name' in first_table
        assert 'column_count' in first_table
        assert 'row_count' in first_table
        assert isinstance(first_table['column_count'], int)
        assert isinstance(first_table['row_count'], int)


def test_supabase_imports():
    """Vérifie que les imports Supabase fonctionnent"""
    if settings.db_type == "supabase":
        from database import init_supabase_connection

        # Si l'import passe, c'est bon
        assert callable(init_supabase_connection)


def test_unified_rpc_interface():
    """Vérifie que l'interface unifiée execute_rpc existe"""
    from database import execute_rpc

    # La fonction doit exister et être appelable
    assert callable(execute_rpc)
