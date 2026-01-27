"""Unified database interface - routes to SQLite or Supabase implementation"""

import logging
from typing import Any, List, Optional

from config import settings

# Import dynamique selon l'environnement
if settings.db_type == "sqlite":
    from src.data import sqlite_db as db
elif settings.db_type == "supabase":
    from src.data import supabase_db as db
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


def get_all_farms() -> List[dict]:
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


def update_record(table: str, filters: dict, data: dict) -> bool:
    """
    Met à jour un enregistrement dans une table

    Args:
        table: Nom de la table
        filters: Dictionnaire des filtres pour identifier l'enregistrement {column: value}
        data: Dictionnaire des données à mettre à jour {column: new_value}

    Returns:
        True si la mise à jour a réussi, False sinon
    """
    return db.update_record(table, filters, data)


def insert_record(table: str, data: dict) -> Optional[dict]:
    """
    Insère un nouvel enregistrement dans une table

    Args:
        table: Nom de la table
        data: Dictionnaire des données à insérer {column: value}

    Returns:
        L'enregistrement inséré ou None en cas d'erreur
    """
    return db.insert_record(table, data)


def delete_record(table: str, filters: dict) -> bool:
    """
    Supprime un enregistrement d'une table

    Args:
        table: Nom de la table
        filters: Dictionnaire des filtres pour identifier l'enregistrement {column: value}

    Returns:
        True si la suppression a réussi, False sinon
    """
    return db.delete_record(table, filters)


# ==================== Farm Data Retrieval Functions ====================

def get_farm_general_info(farm_uuid: str) -> dict:
    """
    Récupère toutes les informations générales d'un farm

    Returns:
        Dict with keys: farm, farm_type, status, location
    """
    data = {}

    # Get main farm data
    farm_results = execute_query("farms", filters={"uuid": farm_uuid})
    data['farm'] = farm_results[0] if farm_results else None

    if not data['farm']:
        return data

    # Get farm type
    if data['farm'].get('farm_type_id'):
        type_results = execute_query("farm_types", filters={"id": data['farm']['farm_type_id']})
        data['farm_type'] = type_results[0] if type_results else None

    # Get farm status
    status_results = execute_query("farm_statuses", filters={"farm_uuid": farm_uuid})
    data['status'] = status_results[0] if status_results else None

    # Get farm location
    location_results = execute_query("farm_locations", filters={"farm_uuid": farm_uuid})
    data['location'] = location_results[0] if location_results else None

    return data


def get_farm_technical_details(farm_uuid: str) -> dict:
    """
    Récupère tous les détails techniques d'un farm

    Returns:
        Dict with keys: turbine_details, substations, wtg_list, ice_systems
    """
    data = {}

    # Get turbine details (wind farms only)
    turbine_results = execute_query("farm_turbine_details", filters={"wind_farm_uuid": farm_uuid})
    data['turbine_details'] = turbine_results[0] if turbine_results else None

    # Get substations
    data['substations'] = execute_query("substations", filters={"farm_uuid": farm_uuid}) or []

    # Get wind turbine generators
    data['wtg_list'] = execute_query("wind_turbine_generators", filters={"farm_uuid": farm_uuid}) or []

    # Get ice detection systems
    ice_farm_links = execute_query("farm_ice_detection_systems", filters={"farm_uuid": farm_uuid}) or []
    data['ice_systems'] = []
    for link in ice_farm_links:
        ice_system = execute_query("ice_detection_systems", filters={"uuid": link['ice_detection_system_uuid']})
        if ice_system:
            data['ice_systems'].append(ice_system[0])

    return data


def get_farm_contracts_admin(farm_uuid: str) -> dict:
    """
    Récupère toutes les informations contractuelles et administratives d'un farm

    Returns:
        Dict with keys: administration, om_contract, tcma_contract, electrical_delegation,
                       environmental_installation, financial_guarantee, substation_details
    """
    data = {}

    # Get all 1:1 relationship tables
    tables = [
        "farm_administrations",
        "farm_om_contracts",
        "farm_tcma_contracts",
        "farm_electrical_delegations",
        "farm_environmental_installations",
        "farm_financial_guarantees",
        "farm_substation_details"
    ]

    for table in tables:
        results = execute_query(table, filters={"farm_uuid": farm_uuid})
        key = table.replace("farm_", "").replace("_", " ").title().replace(" ", "_").lower()
        data[key] = results[0] if results else None

    return data


def get_farm_performance_data(farm_uuid: str) -> dict:
    """
    Récupère toutes les données de performance d'un farm

    Returns:
        Dict with keys: actual_performances, target_performances, tariffs
    """
    data = {}

    # Get actual performances (by year)
    data['actual_performances'] = execute_query(
        "farm_actual_performances",
        filters={"farm_uuid": farm_uuid},
        order_by="year"
    ) or []

    # Get target performances (by year)
    data['target_performances'] = execute_query(
        "farm_target_performances",
        filters={"farm_uuid": farm_uuid},
        order_by="year"
    ) or []

    # Get tariffs (1:many)
    data['tariffs'] = execute_query(
        "farm_tariffs",
        filters={"farm_uuid": farm_uuid},
        order_by="tariff_start_date"
    ) or []

    return data


def get_all_farm_data(farm_uuid: str) -> dict:
    """
    Récupère TOUTES les données d'un farm en une seule fois

    Returns:
        Dict with all farm data organized by category
    """
    return {
        'general_info': get_farm_general_info(farm_uuid),
        'technical_details': get_farm_technical_details(farm_uuid),
        'contracts_admin': get_farm_contracts_admin(farm_uuid),
        'performance_data': get_farm_performance_data(farm_uuid)
    }