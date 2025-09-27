import streamlit as st
import pandas as pd
from supabase_client import supabase

def fetch_user_kpi_aggregates(user_id):
    resp = supabase.table("session_kpi_scores")\
        .select("kpi_name, score, session_id, sessions(user_id)")\
        .eq("sessions.user_id", user_id)\
        .execute()
    if resp.error:
        st.error("Failed to load KPI data")
        return {}

    from collections import defaultdict
    score_map = defaultdict(list)
    rows = resp.data
    for r in rows:
        score_map[r['kpi_name']].append(r['score'])

    avg_scores = {k: sum(v) / len(v) for k, v in score_map.items()}
    return avg_scores

def kpi_dashboard(user_id):
    st.title("KPI Dashboard - Performance Overview")

    avg_scores = fetch_user_kpi_aggregates(user_id)
    if not avg_scores:
        st.info("No KPI data available yet.")
        return
    df = pd.DataFrame(list(avg_scores.items()), columns=['KPI', 'Average Score'])
    st.bar_chart(df.set_index('KPI')['Average Score'])

    st.markdown("### KPI Insights")
    for kpi, score in avg_scores.items():
        if score > 7:
            st.markdown(f"**{kpi}**: Strong performance with an average score of {score:.1f}")
        elif score > 4:
            st.markdown(f"**{kpi}**: Moderate performance, room for improvement. Average score: {score:.1f}")
        else:
            st.markdown(f"**{kpi}**: Needs improvement. Average score: {score:.1f}")
