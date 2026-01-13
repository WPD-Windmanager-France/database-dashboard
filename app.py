import streamlit as st

from auth import require_authentication, show_user_info
from config import settings
from database import (
    get_all_farms,
    get_farm_by_code,
    get_farm_general_info,
    get_farm_technical_details,
    get_farm_contracts_admin,
    get_farm_performance_data,
    update_record,
    insert_record,
    delete_record,
    execute_query
)

# Configuration de la page
st.set_page_config(
    page_title="Windmanager France - Database",
    page_icon="https://upload.wikimedia.org/wikipedia/commons/thumb/c/c1/Wpd_Logo.svg/1200px-Wpd_Logo.svg.png",
    layout="wide"
)

# ==================== AUTHENTICATION GATE ====================
# This must be called BEFORE any app content
if not require_authentication():
    st.stop()  # Stop execution if not authenticated

# Show user info in sidebar (compact version)
show_user_info()

# Custom CSS for responsive sidebar layout with styled radio buttons
st.markdown("""
<style>
/* Sidebar can scroll if content is too tall */
section[data-testid="stSidebar"] {
    height: 100vh;
}

section[data-testid="stSidebar"] > div {
    max-height: 100vh;
    overflow-y: auto;
}

/* Radio button container - scrollable */
section[data-testid="stSidebar"] .stRadio {
    max-height: 40vh;
    overflow-y: auto;
    overflow-x: hidden;
    padding-right: 5px;
}

/* Hide the label block completely */
section[data-testid="stSidebar"] .stRadio > label[data-testid="stWidgetLabel"] {
    display: none !important;
    height: 0 !important;
    margin: 0 !important;
    padding: 0 !important;
}

/* Hide default radio button circles */
section[data-testid="stSidebar"] .stRadio input[type="radio"] {
    display: none;
}

/* Style radio button labels as cards */
section[data-testid="stSidebar"] .stRadio label {
    display: block;
    width: 100%;
    padding: 10px 12px;
    margin-bottom: 6px;
    border: 1px solid #e0e0e0;
    border-radius: 6px;
    background-color: #fafafa;
    cursor: pointer;
    transition: all 0.2s ease;
    font-size: 14px;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    box-sizing: border-box;
}

/* Hover effect */
section[data-testid="stSidebar"] .stRadio label:hover {
    background-color: #f0f0f0;
    border-color: #d0d0d0;
    transform: translateX(2px);
}

/* Text inside label should also be ellipsed */
section[data-testid="stSidebar"] .stRadio label > div {
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* Selected state */
section[data-testid="stSidebar"] .stRadio label[data-baseweb="radio"] > div:first-child {
    display: none;
}

/* Style du TEXTE sélectionné (Gras et Bleu, pas de bordure) */
section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div {
    color: #1565c0 !important;
    font-weight: 700 !important;
    border: none !important;
}
section[data-testid="stSidebar"] .stRadio input[type="radio"]:checked + div + div {
    color: #1565c0 !important;
    font-weight: 700 !important;
    border: none !important;
}

/* Style du BLOC (LABEL) sélectionné */
/* Utilise :has() pour changer la bordure de la carte entière */
section[data-testid="stSidebar"] .stRadio label:has(input:checked) {
    border: 2px solid #2196f3 !important;
    background-color: #f5faff !important; /* Fond très légèrement bleuté */
}

/* Style the scrollbar for radio list */
section[data-testid="stSidebar"] .stRadio::-webkit-scrollbar {
    width: 8px;
}
section[data-testid="stSidebar"] .stRadio::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}
section[data-testid="stSidebar"] .stRadio::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}
section[data-testid="stSidebar"] .stRadio::-webkit-scrollbar-thumb:hover {
    background: #555;
}

/* Style scrollbar for sidebar itself */
section[data-testid="stSidebar"] > div::-webkit-scrollbar {
    width: 8px;
}
section[data-testid="stSidebar"] > div::-webkit-scrollbar-track {
    background: #f1f1f1;
    border-radius: 4px;
}
section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb {
    background: #888;
    border-radius: 4px;
}
section[data-testid="stSidebar"] > div::-webkit-scrollbar-thumb:hover {
    background: #555;
}
</style>
""", unsafe_allow_html=True)

# ==================== SIDEBAR NAVIGATION ====================
with st.sidebar:
    st.subheader("Wind Farms")

    # Load farms
    with st.spinner("Loading farms..."):
        farms = get_all_farms()

    selected_farm_code = None
    if farms:
        # Create display options: "CODE - Project Name"
        farm_options = {f"{farm['code']} - {farm['project']}": farm['code'] for farm in farms}
        farm_display_names = list(farm_options.keys())

        # Farm selector with styled radio buttons
        selected_display = st.radio(
            "Select a wind farm",
            farm_display_names,
            index=0,
            key="farm_selector",
            label_visibility="collapsed"
        )

        selected_farm_code = farm_options[selected_display]

        # Add new farm link (subtle, below the list)
        st.markdown("")
        if st.button("+ Add new farm", key="add_farm_link", use_container_width=False, type="secondary"):
            st.session_state['show_add_farm'] = True
            st.rerun()

    else:
        st.warning("No farms found in database")
        st.markdown("")
        if st.button("+ Add new farm", key="add_farm_link_empty", use_container_width=False, type="secondary"):
            st.session_state['show_add_farm'] = True
            st.rerun()

# ==================== MAIN CONTENT ====================
# Show environment info
#st.caption(f"Environment: {settings.environment} | Database: {settings.db_type}")

# Check if we should show the add farm dialog
if st.session_state.get('show_add_farm', False):
    st.warning("Add New Farm feature coming soon...")
    if st.button("Cancel"):
        st.session_state['show_add_farm'] = False
        st.rerun()
    st.stop()

# ==================== HELPER FUNCTIONS ====================
def render_field_display(label: str, value, col_width=None):
    """Affiche un champ en mode lecture seule"""
    if col_width:
        with col_width:
            st.text(label)
            st.markdown(f"**{value if value is not None else 'N/A'}**")
    else:
        st.text(label)
        st.markdown(f"**{value if value is not None else 'N/A'}**")


def get_person_by_role(farm_uuid: str, role_name: str) -> dict:
    """Helper function to get a person by their role for a specific farm"""
    # First get the role ID
    role = execute_query("person_roles", filters={"role_name": role_name})
    if not role:
        return {}

    role_id = role[0]['id']

    # Get the farm_referent with this role
    referent = execute_query("farm_referents", filters={"farm_uuid": farm_uuid, "person_role_id": role_id})
    if not referent or not referent[0].get('person_uuid'):
        return {}

    # Get the person details
    person = execute_query("persons", filters={"uuid": referent[0]['person_uuid']})
    if not person:
        return {}

    return person[0]


def render_referents_tab(farm_uuid: str, farm_code: str):
    """Onglet Referents pour gérer les contacts du parc"""
    st.subheader("Referents")

    # Define key person roles to display
    key_roles = [
        "Technical Manager",
        "Substitute Technical Manager",
        "Key Account Manager",
        "Substitute Key Account Manager",
        "Head of Technical Management",
        "Electrical Manager",
        "Field Crew Manager",
        "Control Room Operator",
        "HSE Coordination",
        "Administrative responsible",
        "Administrative Deputy",
        "Legal Representative",
        "Asset Manager",
        "Overseer"
    ]

    st.markdown("### Key Contacts")

    # Display in a 2-column layout
    col1, col2 = st.columns(2)

    for idx, role_name in enumerate(key_roles):
        person = get_person_by_role(farm_uuid, role_name)

        target_col = col1 if idx % 2 == 0 else col2

        with target_col:
            st.markdown(f"**{role_name}**")
            if person:
                full_name = f"{person.get('first_name', '')} {person.get('last_name', '')}"
                st.text(f"👤 {full_name}")
                if person.get('email'):
                    st.text(f"📧 {person.get('email')}")
                if person.get('mobile'):
                    st.text(f"📱 {person.get('mobile')}")
            else:
                st.text("N/A")
            st.markdown("")  # Spacing

    st.markdown("---")
    st.info("Fonctionnalité d'ajout/modification de référents en cours de développement")


def get_company_by_role(farm_uuid: str, role_name: str) -> dict:
    """Helper function to get a company by their role for a specific farm"""
    # First get the role ID
    role = execute_query("company_roles", filters={"role_name": role_name})
    if not role:
        return {}

    role_id = role[0]['id']

    # Get the farm_company_role with this role
    farm_company = execute_query("farm_company_roles", filters={"farm_uuid": farm_uuid, "company_role_id": role_id})
    if not farm_company:
        return {}

    # Get the company details
    company = execute_query("companies", filters={"uuid": farm_company[0]['company_uuid']})
    if not company:
        return {}

    return company[0]


def render_services_tab(farm_uuid: str, farm_code: str):
    """Onglet Services pour gérer les entreprises liées au parc"""
    st.subheader("Services")

    # Define key company roles to display
    key_roles = [
        "OM Main Service Company",
        "OM Service Provider",
        "WTG Service Provider",
        "Substation Service Provider",
        "Grid Operator",
        "Energy Trader",
        "Asset Manager",
        "Project Developer",
        "Legal Representative",
        "Chartered Accountant",
        "Legal Auditor",
        "Bank Domiciliation",
        "Customer",
        "Co-developer",
        "Portfolio"
    ]

    st.markdown("### Service Providers & Partners")

    # Display in a 2-column layout
    col1, col2 = st.columns(2)

    for idx, role_name in enumerate(key_roles):
        company = get_company_by_role(farm_uuid, role_name)

        target_col = col1 if idx % 2 == 0 else col2

        with target_col:
            st.markdown(f"**{role_name}**")
            if company:
                st.text(f"🏢 {company.get('name', 'N/A')}")
            else:
                st.text("N/A")
            st.markdown("")  # Spacing

    st.markdown("---")
    st.info("Fonctionnalité d'ajout/modification de services en cours de développement")


def render_contracts_admin_tab(farm_uuid: str, farm_code: str):
    """Onglet Contracts & Administration avec Status et toutes les données administratives"""
    st.subheader("Contracts & Administration")

    # Get data
    general_data = get_farm_general_info(farm_uuid)
    status = general_data.get('status', {})
    contracts_data = get_farm_contracts_admin(farm_uuid)

    administration = contracts_data.get('administration', {})
    om_contract = contracts_data.get('om_contract', {})
    tcma_contract = contracts_data.get('tcma_contract', {})
    electrical_delegation = contracts_data.get('electrical_delegation', {})
    environmental_installation = contracts_data.get('environmental_installation', {})
    financial_guarantee = contracts_data.get('financial_guarantee', {})
    substation_details = contracts_data.get('substation_details', {})

    # Display Status section
    st.markdown("### Status")
    col1, col2 = st.columns(2)
    with col1:
        render_field_display("Farm Status", status.get('farm_status') if status else 'N/A')
    with col2:
        render_field_display("TCMA Status", status.get('tcma_status') if status else 'N/A')

    st.markdown("---")

    # Administration section
    st.markdown("### Administration")
    col1, col2 = st.columns(2)
    with col1:
        render_field_display("Account Number", administration.get('account_number') if administration else 'N/A')
        render_field_display("SIRET Number", administration.get('siret_number') if administration else 'N/A')
        render_field_display("VAT Number", administration.get('vat_number') if administration else 'N/A')
        render_field_display("Legal Representative", administration.get('legal_representative') if administration else 'N/A')
    with col2:
        render_field_display("Head Office Address", administration.get('head_office_address') if administration else 'N/A')
        render_field_display("WindManager Subsidiary", administration.get('windmanager_subsidiary') if administration else 'N/A')
        render_field_display("REMIT Subscription", "Yes" if administration and administration.get('has_remit_subscription') else "No")

    st.markdown("---")

    # Contracts section
    st.markdown("### Contracts")

    # O&M Contract
    with st.expander("O&M Contract", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            render_field_display("Service Contract Type", om_contract.get('service_contract_type') if om_contract else 'N/A')
        with col2:
            render_field_display("Contract End Date", om_contract.get('contract_end_date') if om_contract else 'N/A')

    # TCMA Contract
    with st.expander("TCMA Contract", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            render_field_display("WF Status", tcma_contract.get('wf_status') if tcma_contract else 'N/A')
            render_field_display("TCMA Status", tcma_contract.get('tcma_status') if tcma_contract else 'N/A')
            render_field_display("Contract Type", tcma_contract.get('contract_type') if tcma_contract else 'N/A')
        with col2:
            render_field_display("Signature Date", tcma_contract.get('signature_date') if tcma_contract else 'N/A')
            render_field_display("Effective Date", tcma_contract.get('effective_date') if tcma_contract else 'N/A')
            render_field_display("End Date", tcma_contract.get('end_date') if tcma_contract else 'N/A')
            render_field_display("Compensation Rate", tcma_contract.get('compensation_rate') if tcma_contract else 'N/A')

    st.markdown("---")

    # Other sections
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### Financial Guarantee")
        render_field_display("Amount", financial_guarantee.get('amount') if financial_guarantee else 'N/A')
        render_field_display("Due Date", financial_guarantee.get('due_date') if financial_guarantee else 'N/A')

        st.markdown("### Electrical Delegation")
        render_field_display("In Place", "Yes" if electrical_delegation and electrical_delegation.get('in_place') else "No")
        render_field_display("DREI Date", electrical_delegation.get('drei_date') if electrical_delegation else 'N/A')

    with col2:
        st.markdown("### Environmental Installation")
        render_field_display("AIP Number", environmental_installation.get('aip_number') if environmental_installation else 'N/A')
        render_field_display("Duty DREAL Contact", environmental_installation.get('duty_dreal_contact') if environmental_installation else 'N/A')
        render_field_display("Prefecture Name", environmental_installation.get('prefecture_name') if environmental_installation else 'N/A')

        st.markdown("### Substation Details")
        render_field_display("Station Count", substation_details.get('station_count') if substation_details else 'N/A')

    st.markdown("---")
    st.info("Fonctionnalité d'édition en cours de développement")


def render_location_tab(farm_uuid: str, farm_code: str):
    """Onglet Location avec mode édition"""
    st.subheader("Location")

    # Get data
    data = get_farm_general_info(farm_uuid)
    location = data.get('location', {})

    # Initialize edit mode state
    if 'edit_location' not in st.session_state:
        st.session_state.edit_location = False

    # Edit button
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        if not st.session_state.edit_location:
            if st.button("✏️ Modifier", key="edit_location_btn"):
                st.session_state.edit_location = True
                st.rerun()

    if st.session_state.edit_location:
        st.info("Mode édition activé - Modifiez les champs ci-dessous")

        # Location details
        st.markdown("### Geographic Location")
        col1, col2 = st.columns(2)
        with col1:
            new_country = st.text_input("Country", value=location.get('country', '') if location else '', key="edit_loc_country")
            new_region = st.text_input("Region", value=location.get('region', '') if location else '', key="edit_loc_region")
            new_department = st.text_input("Department", value=location.get('department', '') if location else '', key="edit_loc_department")
        with col2:
            new_municipality = st.text_input("Municipality", value=location.get('municipality', '') if location else '', key="edit_loc_municipality")
            new_map_ref = st.text_input("Map Reference", value=location.get('map_reference', '') if location else '', key="edit_loc_map_ref")

        st.markdown("### Distances & Travel")
        col1, col2 = st.columns(2)
        with col1:
            new_arras_distance = st.number_input("Arras Round Trip Distance (km)", value=float(location.get('arras_round_trip_distance_km', 0)) if location and location.get('arras_round_trip_distance_km') else 0.0, key="edit_loc_arras_distance")
            new_vertou_duration = st.number_input("Vertou Round Trip Duration (h)", value=float(location.get('vertou_round_trip_duration_h', 0)) if location and location.get('vertou_round_trip_duration_h') else 0.0, key="edit_loc_vertou_duration")
        with col2:
            new_arras_toll = st.number_input("Arras Toll (EUR)", value=float(location.get('arras_toll_eur', 0)) if location and location.get('arras_toll_eur') else 0.0, key="edit_loc_arras_toll")
            new_nantes_toll = st.number_input("Nantes Toll (EUR)", value=float(location.get('nantes_toll_eur', 0)) if location and location.get('nantes_toll_eur') else 0.0, key="edit_loc_nantes_toll")

        # Save/Cancel buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 6])
        with col1:
            if st.button("✅ Valider", key="save_location_btn", type="primary"):
                # Update or insert farm_locations
                location_updates = {
                    'farm_uuid': farm_uuid,
                    'farm_code': farm_code,
                    'country': new_country,
                    'region': new_region,
                    'department': new_department,
                    'municipality': new_municipality,
                    'map_reference': new_map_ref,
                    'arras_round_trip_distance_km': new_arras_distance,
                    'vertou_round_trip_duration_h': new_vertou_duration,
                    'arras_toll_eur': new_arras_toll,
                    'nantes_toll_eur': new_nantes_toll
                }
                if location:
                    update_record("farm_locations", {"farm_uuid": farm_uuid}, location_updates)
                else:
                    insert_record("farm_locations", location_updates)

                st.success("Données de localisation mises à jour avec succès!")
                st.session_state.edit_location = False
                st.rerun()

        with col2:
            if st.button("❌ Annuler", key="cancel_location_btn"):
                st.session_state.edit_location = False
                st.rerun()

    else:
        # Display mode
        st.markdown("### Geographic Location")
        col1, col2 = st.columns(2)
        with col1:
            render_field_display("Country", location.get('country') if location else 'N/A')
            render_field_display("Region", location.get('region') if location else 'N/A')
            render_field_display("Department", location.get('department') if location else 'N/A')
        with col2:
            render_field_display("Municipality", location.get('municipality') if location else 'N/A')
            render_field_display("Map Reference", location.get('map_reference') if location else 'N/A')

        st.markdown("### Distances & Travel")
        col1, col2 = st.columns(2)
        with col1:
            render_field_display("Arras Round Trip Distance (km)", location.get('arras_round_trip_distance_km') if location else 'N/A')
            render_field_display("Vertou Round Trip Duration (h)", location.get('vertou_round_trip_duration_h') if location else 'N/A')
        with col2:
            render_field_display("Arras Toll (EUR)", location.get('arras_toll_eur') if location else 'N/A')
            render_field_display("Nantes Toll (EUR)", location.get('nantes_toll_eur') if location else 'N/A')


def render_general_info_tab(farm_uuid: str, farm_code: str):
    """Onglet General Information avec mode édition"""
    st.subheader("General Information")

    # Get data
    data = get_farm_general_info(farm_uuid)
    farm = data.get('farm', {})
    farm_type = data.get('farm_type', {})
    status = data.get('status', {})
    location = data.get('location', {})

    # Initialize edit mode state
    if 'edit_general_info' not in st.session_state:
        st.session_state.edit_general_info = False

    # Edit button
    col1, col2, col3 = st.columns([1, 1, 6])
    with col1:
        if not st.session_state.edit_general_info:
            if st.button("✏️ Modifier", key="edit_general_btn"):
                st.session_state.edit_general_info = True
                st.rerun()

    if st.session_state.edit_general_info:
        st.info("Mode édition activé - Modifiez les champs ci-dessous")

        # Get all farm types for selectbox
        all_farm_types = execute_query("farm_types") or []
        farm_type_options = {ft['type_title']: ft['id'] for ft in all_farm_types}

        # Farm basic info
        st.markdown("### Farm Information")
        col1, col2 = st.columns(2)
        with col1:
            new_spv = st.text_input("SPV", value=farm.get('spv', ''), key="edit_spv")
            new_project = st.text_input("Project Name", value=farm.get('project', ''), key="edit_project")
        with col2:
            new_code = st.text_input("Farm Code", value=farm.get('code', ''), key="edit_code", disabled=True)
            current_type = farm_type.get('type_title', 'Wind') if farm_type else 'Wind'
            new_farm_type = st.selectbox(
                "Farm Type",
                options=list(farm_type_options.keys()),
                index=list(farm_type_options.keys()).index(current_type) if current_type in farm_type_options else 0,
                key="edit_farm_type"
            )

        # Save/Cancel buttons
        st.markdown("---")
        col1, col2, col3 = st.columns([1, 1, 6])
        with col1:
            if st.button("✅ Valider", key="save_general_btn", type="primary"):
                # Update farms table
                farm_updates = {
                    'spv': new_spv,
                    'project': new_project,
                    'farm_type_id': farm_type_options[new_farm_type]
                }
                update_record("farms", {"uuid": farm_uuid}, farm_updates)

                st.success("Informations générales mises à jour avec succès!")
                st.session_state.edit_general_info = False
                st.rerun()

        with col2:
            if st.button("❌ Annuler", key="cancel_general_btn"):
                st.session_state.edit_general_info = False
                st.rerun()

    else:
        # Display mode
        st.markdown("### Farm Information")
        col1, col2 = st.columns(2)
        with col1:
            render_field_display("SPV", farm.get('spv'))
            render_field_display("Project Name", farm.get('project'))
        with col2:
            render_field_display("Farm Code", farm.get('code'))
            render_field_display("Farm Type", farm_type.get('type_title') if farm_type else 'N/A')


# ==================== FARM MANAGEMENT ====================
if selected_farm_code:
    farm = get_farm_by_code(selected_farm_code)

    if farm:
        st.title(f"{farm['project']}")
        st.caption(f"Farm Code: {farm['code']} | SPV: {farm.get('spv', 'N/A')}")

        # Tabs for different sections
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "General Information",
            "Referents",
            "Services",
            "Technical Details",
            "Contracts & Administration",
            "Location",
            "Performance Data"
        ])

        with tab1:
            render_general_info_tab(farm['uuid'], farm['code'])

        with tab2:
            render_referents_tab(farm['uuid'], farm['code'])

        with tab3:
            render_services_tab(farm['uuid'], farm['code'])

        with tab4:
            st.subheader("Technical Details")
            st.info("Section under development")

        with tab5:
            render_contracts_admin_tab(farm['uuid'], farm['code'])

        with tab6:
            render_location_tab(farm['uuid'], farm['code'])

        with tab7:
            st.subheader("Performance Data")
            st.info("Section under development")

    else:
        st.error(f"Farm with code '{selected_farm_code}' not found")

else:
    st.info("Select a wind farm from the sidebar to view and edit its data")
