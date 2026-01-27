"""
WNDMNGR - Wind Farm Management Application
Taipy version (migrated from Streamlit)
"""

import uuid as uuid_lib
from taipy.gui import Gui, State, notify
from config import settings
from src.auth.manager import auth_manager
from src.database import (
    get_all_farms,
    get_farm_by_code,
    get_farm_general_info,
    get_farm_technical_details,
    get_farm_contracts_admin,
    get_farm_performance_data,
    execute_query,
    update_record,
    insert_record,
    delete_record
)

# ==================== STATE VARIABLES ====================
# Auth
email = ""
password = ""
authenticated = False
user_email = ""
user_role = ""
env_info = f"Environment: {settings.CURRENT_ENV} | Auth: {settings.AUTH_TYPE}"

# Farms
farms_list = []
selected_farm = None
selected_farm_name = ""
selected_farm_info = ""
selected_farm_uuid = ""
current_tab = "General"

# General Info Tab
farm_spv = ""
farm_project = ""
farm_code = ""
farm_type = ""
farm_status = ""
farm_country = ""
farm_region = ""
farm_department = ""
farm_municipality = ""

# Referents Tab
ref_technical_manager = "N/A"
ref_kam = "N/A"
ref_head_tech = "N/A"
ref_electrical = "N/A"
ref_field_crew = "N/A"
ref_asset_manager = "N/A"

# Contracts Tab
admin_data = {}
om_contract = {}
tcma_contract = {}

# Location Tab
location_data = {}

# Performance Tab
performance_data = {}

# ==================== EDIT MODE STATE ====================
# General Info editing
editing_general_field = ""  # "spv", "project", "farm_type" or ""
edit_spv = ""
edit_project = ""
farm_type_options = []  # List of farm type names for selector
selected_farm_type = ""
current_farm_type_id = None

# Referents editing
editing_referent_role = ""  # Role name being edited or ""
all_persons_list = []  # ["N/A", "John Doe", "Jane Smith", ...]
selected_person = "N/A"
new_person_first = ""
new_person_last = ""
show_new_person_form = False

# Location editing
editing_location = False
edit_country = ""
edit_region = ""
edit_department = ""
edit_municipality = ""
edit_map_reference = ""
edit_arras_distance = 0.0


# ==================== AUTH FUNCTIONS ====================
def on_login(state: State):
    try:
        user_info = auth_manager.login(state.email, state.password)
        state.authenticated = user_info['authenticated']
        state.user_email = user_info['email']
        state.user_role = user_info['role']
        state.password = ""
        load_farms(state)
        notify(state, "success", f"Bienvenue {state.user_email}!")
    except ValueError as e:
        notify(state, "error", str(e))
    except Exception as e:
        notify(state, "error", f"Erreur: {str(e)}")


def on_logout(state: State):
    auth_manager.logout()
    state.authenticated = False
    state.user_email = ""
    state.user_role = ""
    state.email = ""
    state.farms_list = []
    state.selected_farm = None
    notify(state, "info", "Deconnexion reussie")


# ==================== FARM FUNCTIONS ====================
def load_farms(state: State):
    try:
        farms = get_all_farms()
        if farms:
            state.farms_list = [f"{f['code']} - {f['project']}" for f in farms]
            on_farm_selected(state, "farms_list", state.farms_list[0])
    except Exception as e:
        notify(state, "error", f"Erreur chargement farms: {str(e)}")


def on_farm_selected(state: State, var_name: str, value):
    if value:
        farm_code = value.split(" - ")[0]
        farm = get_farm_by_code(farm_code)
        if farm:
            state.selected_farm = value
            state.selected_farm_name = farm.get('project', '')
            state.selected_farm_info = f"Code: {farm.get('code', '')} | SPV: {farm.get('spv', 'N/A')}"
            state.selected_farm_uuid = farm.get('uuid', '')

            # Load all farm data
            load_farm_data(state, farm['uuid'])


def load_farm_data(state: State, farm_uuid: str):
    """Load all data for the selected farm."""
    # General Info
    general = get_farm_general_info(farm_uuid)
    farm = general.get('farm', {}) or {}
    farm_type_data = general.get('farm_type', {}) or {}
    status = general.get('status', {}) or {}
    location = general.get('location', {}) or {}

    state.farm_spv = farm.get('spv', 'N/A') or 'N/A'
    state.farm_project = farm.get('project', 'N/A') or 'N/A'
    state.farm_code = farm.get('code', 'N/A') or 'N/A'
    state.farm_type = farm_type_data.get('type_title', 'N/A') or 'N/A'
    state.farm_status = status.get('farm_status', 'N/A') or 'N/A'

    # Location
    state.farm_country = location.get('country', 'N/A') or 'N/A'
    state.farm_region = location.get('region', 'N/A') or 'N/A'
    state.farm_department = location.get('department', 'N/A') or 'N/A'
    state.farm_municipality = location.get('municipality', 'N/A') or 'N/A'
    state.location_data = location

    # Referents
    load_referents(state, farm_uuid)

    # Contracts
    contracts = get_farm_contracts_admin(farm_uuid)
    state.admin_data = contracts.get('administrations', {}) or {}
    state.om_contract = contracts.get('om_contracts', {}) or {}
    state.tcma_contract = contracts.get('tcma_contracts', {}) or {}

    # Performance
    state.performance_data = get_farm_performance_data(farm_uuid)


def load_referents(state: State, farm_uuid: str):
    """Load referents for the farm."""
    def get_name(role):
        person = get_person_by_role(farm_uuid, role)
        if person:
            return f"{person.get('first_name', '')} {person.get('last_name', '')}"
        return "N/A"

    state.ref_technical_manager = get_name("Technical Manager")
    state.ref_kam = get_name("Key Account Manager")
    state.ref_head_tech = get_name("Head of Technical Management")
    state.ref_electrical = get_name("Electrical Manager")
    state.ref_field_crew = get_name("Field Crew Manager")
    state.ref_asset_manager = get_name("Asset Manager")


def get_person_by_role(farm_uuid: str, role_name: str) -> dict:
    """Get a person by their role for a specific farm."""
    role = execute_query("person_roles", filters={"role_name": role_name})
    if not role:
        return {}

    role_id = role[0]['id']
    referent = execute_query("farm_referents", filters={"farm_uuid": farm_uuid, "person_role_id": role_id})
    if not referent or not referent[0].get('person_uuid'):
        return {}

    person = execute_query("persons", filters={"uuid": referent[0]['person_uuid']})
    return person[0] if person else {}


# ==================== GENERAL INFO EDITING ====================
def on_edit_spv(state: State):
    """Start editing SPV field."""
    state.editing_general_field = "spv"
    state.edit_spv = state.farm_spv if state.farm_spv != "N/A" else ""


def on_edit_project(state: State):
    """Start editing Project field."""
    state.editing_general_field = "project"
    state.edit_project = state.farm_project if state.farm_project != "N/A" else ""


def on_edit_farm_type(state: State):
    """Start editing Farm Type field."""
    state.editing_general_field = "farm_type"
    # Load farm types
    farm_types = execute_query("farm_types") or []
    state.farm_type_options = [ft['type_title'] for ft in farm_types]
    state.selected_farm_type = state.farm_type if state.farm_type in state.farm_type_options else (state.farm_type_options[0] if state.farm_type_options else "")


def on_save_general(state: State):
    """Save the edited general info field."""
    if not state.selected_farm_uuid:
        notify(state, "error", "No farm selected")
        return

    try:
        if state.editing_general_field == "spv":
            update_record("farms", {"uuid": state.selected_farm_uuid}, {"spv": state.edit_spv})
            state.farm_spv = state.edit_spv
            notify(state, "success", "SPV updated")

        elif state.editing_general_field == "project":
            update_record("farms", {"uuid": state.selected_farm_uuid}, {"project": state.edit_project})
            state.farm_project = state.edit_project
            state.selected_farm_name = state.edit_project
            notify(state, "success", "Project name updated")

        elif state.editing_general_field == "farm_type":
            # Get farm type ID
            farm_types = execute_query("farm_types", filters={"type_title": state.selected_farm_type})
            if farm_types:
                update_record("farms", {"uuid": state.selected_farm_uuid}, {"farm_type_id": farm_types[0]['id']})
                state.farm_type = state.selected_farm_type
                notify(state, "success", "Farm type updated")

        state.editing_general_field = ""

    except Exception as e:
        notify(state, "error", f"Error saving: {str(e)}")


def on_cancel_general(state: State):
    """Cancel editing general info."""
    state.editing_general_field = ""


# ==================== REFERENTS EDITING ====================
def load_all_persons(state: State):
    """Load all persons for the dropdown."""
    persons = execute_query("persons", order_by="last_name") or []
    state.all_persons_list = ["N/A"] + [f"{p['first_name']} {p['last_name']}" for p in persons]


def on_edit_referent(state: State, role_name: str):
    """Start editing a referent."""
    state.editing_referent_role = role_name
    state.show_new_person_form = False
    state.new_person_first = ""
    state.new_person_last = ""
    load_all_persons(state)

    # Find current person for this role
    person = get_person_by_role(state.selected_farm_uuid, role_name)
    if person:
        state.selected_person = f"{person.get('first_name', '')} {person.get('last_name', '')}"
    else:
        state.selected_person = "N/A"


def on_edit_technical_manager(state: State):
    on_edit_referent(state, "Technical Manager")


def on_edit_kam(state: State):
    on_edit_referent(state, "Key Account Manager")


def on_edit_head_tech(state: State):
    on_edit_referent(state, "Head of Technical Management")


def on_edit_electrical(state: State):
    on_edit_referent(state, "Electrical Manager")


def on_edit_field_crew(state: State):
    on_edit_referent(state, "Field Crew Manager")


def on_edit_asset_manager(state: State):
    on_edit_referent(state, "Asset Manager")


def on_toggle_new_person(state: State):
    """Toggle the new person form."""
    state.show_new_person_form = not state.show_new_person_form


def on_save_referent(state: State):
    """Save the edited referent."""
    if not state.selected_farm_uuid or not state.editing_referent_role:
        return

    try:
        role_name = state.editing_referent_role

        # Get role ID
        role = execute_query("person_roles", filters={"role_name": role_name})
        if not role:
            notify(state, "error", f"Role '{role_name}' not found")
            return
        role_id = role[0]['id']

        # Handle new person creation
        if state.show_new_person_form and state.new_person_first and state.new_person_last:
            new_uuid = str(uuid_lib.uuid4())
            insert_record("persons", {
                "uuid": new_uuid,
                "first_name": state.new_person_first,
                "last_name": state.new_person_last
            })
            person_uuid = new_uuid
            notify(state, "info", f"Created new person: {state.new_person_first} {state.new_person_last}")
        elif state.selected_person == "N/A":
            person_uuid = None
        else:
            # Find person UUID by name
            parts = state.selected_person.split(" ", 1)
            if len(parts) == 2:
                persons = execute_query("persons", filters={"first_name": parts[0], "last_name": parts[1]})
                person_uuid = persons[0]['uuid'] if persons else None
            else:
                person_uuid = None

        # Check existing referent
        existing = execute_query("farm_referents", filters={
            "farm_uuid": state.selected_farm_uuid,
            "person_role_id": role_id
        })

        if person_uuid is None:
            # Delete if exists
            if existing:
                delete_record("farm_referents", {
                    "farm_uuid": state.selected_farm_uuid,
                    "person_role_id": role_id
                })
        elif existing:
            # Update existing
            update_record("farm_referents",
                {"farm_uuid": state.selected_farm_uuid, "person_role_id": role_id},
                {"person_uuid": person_uuid}
            )
        else:
            # Get farm code for insert
            farm = execute_query("farms", filters={"uuid": state.selected_farm_uuid})
            farm_code = farm[0]['code'] if farm else ""

            # Insert new
            insert_record("farm_referents", {
                "farm_uuid": state.selected_farm_uuid,
                "farm_code": farm_code,
                "person_role_id": role_id,
                "person_uuid": person_uuid
            })

        # Refresh referents display
        load_referents(state, state.selected_farm_uuid)
        state.editing_referent_role = ""
        state.show_new_person_form = False
        notify(state, "success", f"{role_name} updated")

    except Exception as e:
        notify(state, "error", f"Error saving referent: {str(e)}")


def on_cancel_referent(state: State):
    """Cancel editing referent."""
    state.editing_referent_role = ""
    state.show_new_person_form = False


# ==================== LOCATION EDITING ====================
def on_edit_location(state: State):
    """Start editing location."""
    state.editing_location = True
    loc = state.location_data or {}
    state.edit_country = loc.get('country', '') or ''
    state.edit_region = loc.get('region', '') or ''
    state.edit_department = loc.get('department', '') or ''
    state.edit_municipality = loc.get('municipality', '') or ''
    state.edit_map_reference = loc.get('map_reference', '') or ''
    state.edit_arras_distance = float(loc.get('arras_round_trip_distance_km', 0) or 0)


def on_save_location(state: State):
    """Save location changes."""
    if not state.selected_farm_uuid:
        return

    try:
        # Get farm code
        farm = execute_query("farms", filters={"uuid": state.selected_farm_uuid})
        farm_code = farm[0]['code'] if farm else ""

        location_data = {
            "farm_uuid": state.selected_farm_uuid,
            "farm_code": farm_code,
            "country": state.edit_country,
            "region": state.edit_region,
            "department": state.edit_department,
            "municipality": state.edit_municipality,
            "map_reference": state.edit_map_reference,
            "arras_round_trip_distance_km": state.edit_arras_distance
        }

        # Check if location exists
        existing = execute_query("farm_locations", filters={"farm_uuid": state.selected_farm_uuid})

        if existing:
            update_record("farm_locations", {"farm_uuid": state.selected_farm_uuid}, location_data)
        else:
            insert_record("farm_locations", location_data)

        # Update display
        state.farm_country = state.edit_country or "N/A"
        state.farm_region = state.edit_region or "N/A"
        state.farm_department = state.edit_department or "N/A"
        state.farm_municipality = state.edit_municipality or "N/A"
        state.location_data = location_data

        state.editing_location = False
        notify(state, "success", "Location updated")

    except Exception as e:
        notify(state, "error", f"Error saving location: {str(e)}")


def on_cancel_location(state: State):
    """Cancel location editing."""
    state.editing_location = False


# ==================== PAGE ====================
page = """
<style>
.sidebar-box {
    background: linear-gradient(180deg, #f8f9fa 0%, #e9ecef 100%);
    padding: 20px;
    min-height: 100vh;
    border-right: 1px solid #dee2e6;
}
.user-box {
    background: white;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.farm-list-box {
    max-height: 400px;
    overflow-y: auto;
    background: white;
    border-radius: 8px;
    padding: 10px;
    box-shadow: inset 0 2px 4px rgba(0,0,0,0.05);
}
.main-box {
    padding: 30px;
}
.farm-title {
    color: #1565c0;
    border-bottom: 2px solid #1565c0;
    padding-bottom: 10px;
}
.info-card {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 15px;
}
.info-label {
    color: #6c757d;
    font-size: 0.85rem;
    margin-bottom: 2px;
}
.info-value {
    font-weight: 600;
    color: #212529;
}
.section-title {
    color: #495057;
    border-bottom: 1px solid #dee2e6;
    padding-bottom: 8px;
    margin-bottom: 15px;
}
.small-btn button {
    padding: 2px 8px !important;
    font-size: 12px !important;
    min-height: 24px !important;
}
.primary-btn button {
    background-color: #1565c0 !important;
    color: white !important;
}
</style>

<|part|render={not authenticated}|

<|container|

# Windmanager France

<|{env_info}|>

---

**Email**

<|{email}|input|>

**Mot de passe**

<|{password}|input|password=True|>

<|Se connecter|button|on_action=on_login|>

|>

|>

<|part|render={authenticated}|

<|layout|columns=300px 1fr|gap=0|

<|part|class_name=sidebar-box|

<|part|class_name=user-box|

**<|{user_email}|>**

Role: <|{user_role}|>

|>

**WIND FARMS**

<|part|class_name=farm-list-box|

<|{selected_farm}|selector|lov={farms_list}|on_change=on_farm_selected|mode=radio|>

|>

<|Se deconnecter|button|on_action=on_logout|>

|>

<|part|class_name=main-box|

<|part|class_name=farm-title|

## <|{selected_farm_name}|>

<|{selected_farm_info}|>

|>

<|{current_tab}|toggle|lov=General;Referents;Services;Contracts;Location;Performance|>

---

<|part|render={current_tab == 'General'}|

### General Informations

<|layout|columns=1 1|gap=20px|

<|part|

<|part|class_name=info-card|
**SPV**

<|part|render={editing_general_field != 'spv'}|
<|{farm_spv}|> <|Edit|button|on_action=on_edit_spv|class_name=small-btn|>
|>

<|part|render={editing_general_field == 'spv'}|
<|{edit_spv}|input|>

<|Save|button|on_action=on_save_general|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_general|>
|>
|>

<|part|class_name=info-card|
**Project Name**

<|part|render={editing_general_field != 'project'}|
<|{farm_project}|> <|Edit|button|on_action=on_edit_project|class_name=small-btn|>
|>

<|part|render={editing_general_field == 'project'}|
<|{edit_project}|input|>

<|Save|button|on_action=on_save_general|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_general|>
|>
|>

|>

<|part|

<|part|class_name=info-card|
**Farm Code**

<|{farm_code}|>
|>

<|part|class_name=info-card|
**Farm Type**

<|part|render={editing_general_field != 'farm_type'}|
<|{farm_type}|> <|Edit|button|on_action=on_edit_farm_type|class_name=small-btn|>
|>

<|part|render={editing_general_field == 'farm_type'}|
<|{selected_farm_type}|selector|lov={farm_type_options}|dropdown|>

<|Save|button|on_action=on_save_general|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_general|>
|>
|>

|>

|>

<|part|class_name=section-title|
**Status**
|>

<|part|class_name=info-card|
**Farm Status:** <|{farm_status}|>
|>

|>

<|part|render={current_tab == 'Referents'}|

### Referents

<|layout|columns=1 1|gap=20px|

<|part|

<|part|class_name=info-card|
**Technical Manager**

<|part|render={editing_referent_role != 'Technical Manager'}|
<|{ref_technical_manager}|> <|Edit|button|on_action=on_edit_technical_manager|class_name=small-btn|>
|>

<|part|render={editing_referent_role == 'Technical Manager'}|
<|{selected_person}|selector|lov={all_persons_list}|dropdown|>

<|+ New Person|button|on_action=on_toggle_new_person|>

<|part|render={show_new_person_form}|
First: <|{new_person_first}|input|> Last: <|{new_person_last}|input|>
|>

<|Save|button|on_action=on_save_referent|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_referent|>
|>
|>

<|part|class_name=info-card|
**Key Account Manager**

<|part|render={editing_referent_role != 'Key Account Manager'}|
<|{ref_kam}|> <|Edit|button|on_action=on_edit_kam|class_name=small-btn|>
|>

<|part|render={editing_referent_role == 'Key Account Manager'}|
<|{selected_person}|selector|lov={all_persons_list}|dropdown|>

<|+ New Person|button|on_action=on_toggle_new_person|>

<|part|render={show_new_person_form}|
First: <|{new_person_first}|input|> Last: <|{new_person_last}|input|>
|>

<|Save|button|on_action=on_save_referent|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_referent|>
|>
|>

<|part|class_name=info-card|
**Head of Technical Management**

<|part|render={editing_referent_role != 'Head of Technical Management'}|
<|{ref_head_tech}|> <|Edit|button|on_action=on_edit_head_tech|class_name=small-btn|>
|>

<|part|render={editing_referent_role == 'Head of Technical Management'}|
<|{selected_person}|selector|lov={all_persons_list}|dropdown|>

<|+ New Person|button|on_action=on_toggle_new_person|>

<|part|render={show_new_person_form}|
First: <|{new_person_first}|input|> Last: <|{new_person_last}|input|>
|>

<|Save|button|on_action=on_save_referent|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_referent|>
|>
|>

|>

<|part|

<|part|class_name=info-card|
**Electrical Manager**

<|part|render={editing_referent_role != 'Electrical Manager'}|
<|{ref_electrical}|> <|Edit|button|on_action=on_edit_electrical|class_name=small-btn|>
|>

<|part|render={editing_referent_role == 'Electrical Manager'}|
<|{selected_person}|selector|lov={all_persons_list}|dropdown|>

<|+ New Person|button|on_action=on_toggle_new_person|>

<|part|render={show_new_person_form}|
First: <|{new_person_first}|input|> Last: <|{new_person_last}|input|>
|>

<|Save|button|on_action=on_save_referent|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_referent|>
|>
|>

<|part|class_name=info-card|
**Field Crew Manager**

<|part|render={editing_referent_role != 'Field Crew Manager'}|
<|{ref_field_crew}|> <|Edit|button|on_action=on_edit_field_crew|class_name=small-btn|>
|>

<|part|render={editing_referent_role == 'Field Crew Manager'}|
<|{selected_person}|selector|lov={all_persons_list}|dropdown|>

<|+ New Person|button|on_action=on_toggle_new_person|>

<|part|render={show_new_person_form}|
First: <|{new_person_first}|input|> Last: <|{new_person_last}|input|>
|>

<|Save|button|on_action=on_save_referent|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_referent|>
|>
|>

<|part|class_name=info-card|
**Asset Manager**

<|part|render={editing_referent_role != 'Asset Manager'}|
<|{ref_asset_manager}|> <|Edit|button|on_action=on_edit_asset_manager|class_name=small-btn|>
|>

<|part|render={editing_referent_role == 'Asset Manager'}|
<|{selected_person}|selector|lov={all_persons_list}|dropdown|>

<|+ New Person|button|on_action=on_toggle_new_person|>

<|part|render={show_new_person_form}|
First: <|{new_person_first}|input|> Last: <|{new_person_last}|input|>
|>

<|Save|button|on_action=on_save_referent|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_referent|>
|>
|>

|>

|>

|>

<|part|render={current_tab == 'Services'}|

### Services

*Liste des prestataires en cours de developpement...*

|>

<|part|render={current_tab == 'Contracts'}|

### Contracts & Administration

<|layout|columns=1 1|gap=20px|

<|part|

<|part|class_name=section-title|
**Administration**
|>

<|part|class_name=info-card|
**Account Number:** <|{admin_data.get('account_number', 'N/A') if admin_data else 'N/A'}|>

**SIRET:** <|{admin_data.get('siret_number', 'N/A') if admin_data else 'N/A'}|>

**VAT Number:** <|{admin_data.get('vat_number', 'N/A') if admin_data else 'N/A'}|>
|>

|>

<|part|

<|part|class_name=section-title|
**O&M Contract**
|>

<|part|class_name=info-card|
**Contract Type:** <|{om_contract.get('service_contract_type', 'N/A') if om_contract else 'N/A'}|>

**End Date:** <|{om_contract.get('contract_end_date', 'N/A') if om_contract else 'N/A'}|>
|>

|>

|>

|>

<|part|render={current_tab == 'Location'}|

### Location

<|part|render={not editing_location}|

<|Edit Location|button|on_action=on_edit_location|class_name=primary-btn|>

<|layout|columns=1 1|gap=20px|

<|part|

<|part|class_name=section-title|
**Geographic Location**
|>

<|part|class_name=info-card|
**Country:** <|{farm_country}|>

**Region:** <|{farm_region}|>

**Department:** <|{farm_department}|>

**Municipality:** <|{farm_municipality}|>
|>

|>

<|part|

<|part|class_name=section-title|
**Distances & Travel**
|>

<|part|class_name=info-card|
**Arras Distance:** <|{location_data.get('arras_round_trip_distance_km', 'N/A') if location_data else 'N/A'}|> km

**Map Reference:** <|{location_data.get('map_reference', 'N/A') if location_data else 'N/A'}|>
|>

|>

|>

|>

<|part|render={editing_location}|

**Edit Location**

<|layout|columns=1 1|gap=20px|

<|part|

**Country**

<|{edit_country}|input|>

**Region**

<|{edit_region}|input|>

**Department**

<|{edit_department}|input|>

**Municipality**

<|{edit_municipality}|input|>

|>

<|part|

**Map Reference**

<|{edit_map_reference}|input|>

**Arras Round Trip Distance (km)**

<|{edit_arras_distance}|number|>

|>

|>

<|Save|button|on_action=on_save_location|class_name=primary-btn|> <|Cancel|button|on_action=on_cancel_location|>

|>

|>

<|part|render={current_tab == 'Performance'}|

### Performance Data

<|part|class_name=info-card|
**Actual Performances:** <|{len(performance_data.get('actual_performances', [])) if performance_data else 0}|> records

**Target Performances:** <|{len(performance_data.get('target_performances', [])) if performance_data else 0}|> records

**Tariffs:** <|{len(performance_data.get('tariffs', [])) if performance_data else 0}|> records
|>

*Graphiques de performance en cours de developpement...*

|>

|>

|>

|>
"""

if __name__ == "__main__":
    Gui(page=page).run(debug=True, port="auto", title="WNDMNGR", dark_mode=False)
