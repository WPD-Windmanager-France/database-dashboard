import pandas as pd
import streamlit as st

from config import settings
from database import execute_rpc
from auth import require_authentication, show_user_info

# Configuration de la page
st.set_page_config(
    page_title="Windmanager France - Database",
    page_icon="",
    layout="wide"
)

# ==================== AUTHENTICATION GATE ====================
# This must be called BEFORE any app content
if not require_authentication():
    st.stop()  # Stop execution if not authenticated

# Show environment info
st.caption(f"Environment: {settings.environment} | Database: {settings.db_type}")

# Show user info in sidebar
show_user_info()

# Fetch statistics via RPC
with st.spinner("Loading statistics..."):
    try:
        data = execute_rpc('get_table_stats')

        # Transform data for DataFrame
        stats_data = []
        for row in data:
            stats_data.append({
                "Table": row.get('table_name', 'N/A'),
                "Columns": row.get('column_count', 'N/A'),
                "Rows": row.get('row_count', 'N/A')
            })

        df = pd.DataFrame(stats_data)

        # Sort by row count descending
        df = df.sort_values(by='Rows', ascending=False).reset_index(drop=True)

    except Exception as e:
        st.error(f"Error loading statistics: {e}")
        df = pd.DataFrame(columns=["Table", "Columns", "Rows"])

st.dataframe(
    df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Table": st.column_config.TextColumn("Table", width="large"),
        "Columns": st.column_config.NumberColumn("Columns", format="%d"),
        "Rows": st.column_config.NumberColumn("Rows", format="%d")
    }
)

# Global statistics
if not df.empty:
    try:
        total_entries = df["Rows"].sum()
        populated_tables = len(df[df["Rows"] > 0])
        total_tables = len(df)

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Rows", f"{total_entries:,}")
        with col2:
            st.metric("Tables with Data", f"{populated_tables}/{total_tables}")
        with col3:
            st.metric("Empty Tables", f"{total_tables - populated_tables}")
    except Exception:
        pass
