from supabase_client import supabase


def sign_up(email, password):
    result = supabase.auth.sign_up({"email": email, "password": password})
    if isinstance(result, dict):
        user = result.get('user')
        error = result.get('error')
    else:
        user = None
        error = None
    return user, error


def sign_in(email, password):
    result = supabase.auth.sign_in({"email": email, "password": password})
    if isinstance(result, dict):
        user = result.get('user')
        error = result.get('error')
    else:
        user = None
        error = None
    return user, error


def sign_out():
    supabase.auth.sign_out()
