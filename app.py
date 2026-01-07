import streamlit as st

from auth import require_authentication, show_user_info
from config import settings
from database import get_all_farms, get_farm_by_code
from auth import require_authentication, show_user_info

# Configuration de la page
st.set_page_config(
    page_title="Windmanager France - Database",
    page_icon="⚡",
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

        st.divider()

        # Add new farm button
        if st.button("Add New Farm", use_container_width=True, type="primary"):
            st.session_state['show_add_farm'] = True
            st.rerun()

    else:
        st.warning("No farms found in database")
        if st.button("Add New Farm", use_container_width=True, type="primary"):
            st.session_state['show_add_farm'] = True
            st.rerun()

    # Database documentation button at the bottom
    st.divider()
    st.caption("Database Schema")
    if st.button("View Documentation", use_container_width=True):
        st.switch_page("pages/database_schema.py")

# ==================== MAIN CONTENT ====================
# Show environment info
st.caption(f"Environment: {settings.environment} | Database: {settings.db_type}")

# Check if we should show the add farm dialog
if st.session_state.get('show_add_farm', False):
    st.warning("Add New Farm feature coming soon...")
    if st.button("Cancel"):
        st.session_state['show_add_farm'] = False
        st.rerun()
    st.stop()

# ==================== FARM MANAGEMENT ====================
if selected_farm_code:
    farm = get_farm_by_code(selected_farm_code)

    if farm:
        st.title(f"{farm['project']}")
        st.caption(f"Farm Code: {farm['code']} | SPV: {farm.get('spv', 'N/A')}")

        # Tabs for different sections
        tab1, tab2, tab3, tab4 = st.tabs([
            "General Information",
            "Technical Details",
            "Contracts & Administration",
            "Performance Data"
        ])

        with tab1:
            st.subheader("General Information")
            st.info("Section under development")
            st.json(farm)

        with tab2:
            st.subheader("Technical Details")
            st.info("Section under development")

        with tab3:
            st.subheader("Contracts & Administration")
            st.info("Section under development")

        with tab4:
            st.subheader("Performance Data")
            st.info("Section under development")

    else:
        st.error(f"Farm with code '{selected_farm_code}' not found")

else:
    st.info("Select a wind farm from the sidebar to view and edit its data")
