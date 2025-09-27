from supabase_client import supabase
import streamlit as st
import json

def fetch_personas():
    response = supabase.table("personas").select("id, persona_name, description, kpi_template").order("created_at", desc=True).execute()
    if response.error:
        st.error("Error fetching personas: " + response.error.message)
        return []
    return response.data

def start_session(user_id, persona_id):
    data = {
        "user_id": user_id,
        "persona_id": persona_id
    }
    response = supabase.table("sessions").insert(data).execute()
    if response.error:
        st.error("Error starting session: " + response.error.message)
        return None
    return response.data[0]

def persona_selection_ui(user):
    st.header("Select Persona for Simulation")

    personas = fetch_personas()
    if not personas:
        st.warning("No personas available.")
        return

    persona_options = {p["persona_name"]: p for p in personas}

    selected_name = st.selectbox("Choose a persona", list(persona_options.keys()))
    selected_persona = persona_options[selected_name]

    st.markdown("**Persona Description:**")
    st.write(selected_persona["description"])

    st.markdown("**KPI Template:**")
    st.json(selected_persona["kpi_template"])

    if st.button("Start Simulation Session"):
        session = start_session(user.id, selected_persona["id"])
        if session:
            st.success(f"Session started with ID: {session['id']}")
            # Save session info if needed for further simulation steps
        else:
            st.error("Failed to start session. Please try again.")
