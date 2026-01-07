"""Database Schema Documentation Page"""

import streamlit as st
from pathlib import Path

from auth import require_authentication, show_user_info

# Configuration de la page
st.set_page_config(
    page_title="Database Schema - Windmanager",
    page_icon="⚡",
    layout="wide"
)

# ==================== AUTHENTICATION GATE ====================
if not require_authentication():
    st.stop()

# Show user info in sidebar
show_user_info()

# ==================== MAIN CONTENT ====================
st.title("Database Schema Documentation")

# Back button
if st.button("← Back to Farm Management"):
    st.switch_page("app.py")

st.divider()

# Load and display the schema documentation
schema_file = Path(__file__).parent.parent / "RESOURCES" / "database_schema.md"

try:
    with open(schema_file, 'r', encoding='utf-8') as f:
        schema_content = f.read()

    st.markdown(schema_content)

except FileNotFoundError:
    st.error(f"Schema documentation file not found: {schema_file}")
except Exception as e:
    st.error(f"Error loading schema documentation: {e}")
