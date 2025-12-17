import streamlit as st
import pandas as pd
from database import execute_query, get_database_engine

# Configuration de la page
st.set_page_config(
    page_title="Wind Manager - DEBUG V3",
    page_icon="🐛",
    layout="wide"
)

st.title("Windmanager - DEBUG V3 (Force IPv4)")
st.caption("Si vous ne voyez pas ce titre, Streamlit n'a pas mis à jour le code.")

# Sidebar Debug
with st.sidebar:
    st.header("État de la connexion")
    if st.button("Tester la connexion"):
        res = execute_query("SELECT version();")
        if res:
            st.success(f"Version DB: {res[0]['version']}")

# Liste des tables
TABLES = [("companies", "Entreprises")]

for table_name, label in TABLES:
    st.write(f"Testing table: {table_name}")
    data = execute_query(f"SELECT * FROM {table_name} LIMIT 1")
    if data:
        st.write(data)
