from supabase_client import supabase
import streamlit as st

def get_user_profile(user_id):
    response = supabase.table("users").select("*").eq("id", user_id).single().execute()
    if response.error:
        st.error("Error fetching profile: " + response.error.message)
        return None
    return response.data

def upsert_user_profile(user_id, email, business_vertical, role):
    profile = {
        "id": user_id,
        "email": email,
        "business_vertical": business_vertical,
        "role": role
    }
    response = supabase.table("users").upsert(profile).execute()
    if response.error:
        st.error("Error updating profile: " + response.error.message)
        return False
    return True

def profile_ui(user):
    st.header("User Profile Setup")

    profile = get_user_profile(user.id)

    business_vertical_options = ['sales', 'marketing', 'customer_service', 'operations', 'finance', 'hr']
    role_options = ['admin', 'manager', 'employee']

    current_vertical = profile['business_vertical'] if profile else None
    current_role = profile['role'] if profile else None

    business_vertical = st.selectbox("Business Vertical", business_vertical_options, index=business_vertical_options.index(current_vertical) if current_vertical else 0)
    role = st.selectbox("Role", role_options, index=role_options.index(current_role) if current_role else 2)

    if st.button("Save Profile"):
        success = upsert_user_profile(user.id, user.email, business_vertical, role)
        if success:
            st.success("Profile updated successfully!")
