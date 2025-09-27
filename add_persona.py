import streamlit as st
from supabase_client import supabase  # Use your supabase client instance
import json

def add_persona_ui():
    st.header("Add New Persona")

    persona_name = st.text_input("Persona Name")
    description = st.text_area("Description")
    kpi_metrics = st.text_area("KPI Metrics (JSON format)", '{"metrics": []}')

    if st.button("Add Persona"):
        try:
            kpi_json = json.loads(kpi_metrics)
        except json.JSONDecodeError as e:
            st.error("Invalid JSON in KPI Metrics: " + str(e))
            return

        data = {
            "persona_name": persona_name,
            "description": description,
            "kpi_template": kpi_json,
        }

        response = supabase.table("personas").insert(data).execute()

        if response.error:
            st.error(f"Failed to add persona: {response.error.message}")
        else:
            st.success(f"Persona '{persona_name}' added successfully!")
