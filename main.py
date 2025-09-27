import streamlit as st
from user_profile import profile_ui
from auth import sign_up, sign_in, sign_out
from personas import persona_selection_ui
from interactive_simulation import interactive_simulation
from dashboard import kpi_dashboard 
from gemini_integration import call_gemini_api
from supabase import Client, create_client
from add_persona import add_persona_ui  # Add Persona import
import json

# Rerun helper for Streamlit version compatibility
try:
    rerun_app = st.experimental_rerun
except AttributeError:
    from streamlit.runtime.scriptrunner import RerunException

    def rerun_app():
        raise RerunException(None)

# Initialize Supabase client
SUPABASE_URL = "https://xogzmhedjdsdgdondght.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InhvZ3ptaGVkamRzZGdkb25kZ2h0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTg3MzE5MzgsImV4cCI6MjA3NDMwNzkzOH0.WxgfORSL9fMVGa91QhgF0PbyLd_gIQCeVEyQRwQQfGE"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Authentication functions handling response correctly
def sign_up(email, password):
    result = supabase.auth.sign_up({"email": email, "password": password})
    if isinstance(result, dict):
        user = result.get('user')
        error = result.get('error')
    else:
        user = getattr(result, 'user', None)
        error = getattr(result, 'error', None)
    return user, error

def sign_in(email, password):
    result = supabase.auth.sign_in({"email": email, "password": password})
    try:
        user = result.user
        error = result.error
    except AttributeError:
        user = result.get('user') if hasattr(result, 'get') else None
        error = result.get('error') if hasattr(result, 'get') else None
    return user, error

def sign_out():
    supabase.auth.sign_out()

# Fetch user profile
def get_user_profile(user_id):
    resp = supabase.table("users").select("*").eq("id", user_id).single().execute()
    return resp.data if resp.data else None

# Upsert user profile
def upsert_user_profile(user_id, email, business_vertical, role):
    data = {
        "id": user_id,
        "email": email,
        "business_vertical": business_vertical,
        "role": role
    }
    return supabase.table("users").upsert(data).execute()

# Fetch personas
def fetch_personas():
    resp = supabase.table("personas").select("id,persona_name,description,kpi_template").order("created_at", desc=True).execute()
    return resp.data if resp.data else []

# Start session
def start_session(user_id, persona_id):
    data = {"user_id": user_id, "persona_id": persona_id}
    resp = supabase.table("sessions").insert(data).execute()
    return resp.data[0] if resp.data else None

# Streamlit UI Code for authentication
def auth_ui():
    st.title("KPI Training Platform - Login or Signup")

    mode = st.radio("", ["Login", "Signup", "Fake Login Bypass (Dev)"])

    email = st.text_input("Email")
    password = None
    role = None
    business_vertical = None

    if mode != "Fake Login Bypass (Dev)":
        password = st.text_input("Password", type="password")
    else:
        role = st.selectbox("Select Role (Dev)", ['admin', 'manager', 'employee'])
        business_vertical = st.selectbox("Select Business Vertical (Dev)", ['sales', 'marketing', 'customer_service', 'operations', 'finance', 'hr'])

    if st.button(mode):
        if mode == "Signup":
            user, error = sign_up(email, password)
            if user:
                st.success("Signup successful! Please verify your email if required.")
            else:
                st.error(str(error) if error else "Signup failed")
        elif mode == "Login":
            user, error = sign_in(email, password)
            if user:
                st.session_state.user = user
                rerun_app()
            else:
                st.error(str(error) if error else "Login failed")
        else:  # Fake Login Bypass
            if email:
                fake_user = type("User", (), {})()
                fake_user.id = "fake_" + email
                fake_user.email = email
                fake_user.role = role
                fake_user.business_vertical = business_vertical
                st.session_state.user = fake_user
                rerun_app()
            else:
                st.error("Please enter an email")

# Profile UI
def profile_ui(user):
    st.header("User Profile Setup")

    is_fake_user = getattr(user, "id", "").startswith("fake_")
    if is_fake_user:
        business_vertical = st.selectbox("Business Vertical", ['sales', 'marketing', 'customer_service', 'operations', 'finance', 'hr'],
                                         index=['sales', 'marketing', 'customer_service', 'operations', 'finance', 'hr'].index(getattr(user, 'business_vertical', 'sales')))
        role = st.selectbox("Role", ['admin', 'manager', 'employee'],
                            index=['admin', 'manager', 'employee'].index(getattr(user, 'role', 'employee')))
        if st.button("Save Profile (Dev Mode)"):
            user.business_vertical = business_vertical
            user.role = role
            st.success("Profile updated (locally simulated)!")
    else:
        profile = get_user_profile(user.id)
        bv = profile.get("business_vertical") if profile else None
        rl = profile.get("role") if profile else None

        business_vertical = st.selectbox("Business Vertical", ['sales', 'marketing', 'customer_service', 'operations', 'finance', 'hr'],
                                         index=['sales', 'marketing', 'customer_service', 'operations', 'finance', 'hr'].index(bv) if bv else 0)
        role = st.selectbox("Role", ['admin', 'manager', 'employee'], index=['admin', 'manager', 'employee'].index(rl) if rl else 2)

        if st.button("Save Profile"):
            response = upsert_user_profile(user.id, user.email, business_vertical, role)
            if response.error:
                st.error(response.error.message)
            else:
                st.success("Profile updated!")

# Persona selection UI
def persona_selection_ui(user):
    st.header("Select Persona for Simulation")
    personas = fetch_personas()
    options = {p["persona_name"]: p for p in personas}

    if not options:
        st.warning("No personas available. Please add personas first.")
        return

    selected_persona_name = st.selectbox("Choose a persona", list(options.keys()))
    selected_persona = options[selected_persona_name]

    st.markdown("**Description:**")
    st.write(selected_persona["description"])
    st.markdown("**KPI Metrics:**")
    st.write(json.dumps(selected_persona["kpi_template"], indent=2))

    if st.button("Start Simulation Session"):
        session = start_session(user.id, selected_persona["id"])
        if session:
            st.success(f"Session started with ID: {session['id']}")
            st.session_state['current_session_id'] = session['id']
        else:
            st.error("Failed to start session. Try again.")

# Main app function
def main():
    if "user" not in st.session_state:
        auth_ui()
    else:
        user = st.session_state.user
        st.sidebar.write(f"Logged in as: {user.email}")
        page = st.sidebar.radio("Navigate", [
            "Profile Setup", 
            "Persona Selection", 
            "Add Persona",     # New page added here
            "Simulation", 
            "Dashboard", 
            "Logout"
        ])

        if page == "Profile Setup":
            profile_ui(user)
        elif page == "Persona Selection":
            persona_selection_ui(user)
        elif page == "Add Persona":
            add_persona_ui()  # Call the new Add Persona UI page
        elif page == "Simulation":
            if 'current_session_id' in st.session_state:
                interactive_simulation(st.session_state['current_session_id'], user.persona_name)
            else:
                st.warning("Please start a simulation session first by selecting a persona.")
        elif page == "Dashboard":
            kpi_dashboard(user.id)
        elif page == "Logout":
            sign_out()
            st.session_state.pop("user")
            st.session_state.pop("current_session_id", None)
            rerun_app()

if __name__ == "__main__":
    main()
