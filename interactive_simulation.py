import json
import streamlit as st
from gemini_integration import call_gemini_api
from gemini_prompts import create_gemini_prompt, create_gemini_evaluation_prompt
from supabase_client import supabase

def save_transcript(session_id, question, user_answer, ai_feedback):
    record = {
        "session_id": session_id,
        "question": question,
        "user_answer": user_answer,
        "ai_feedback": ai_feedback,
    }
    supabase.table("qa_transcripts").insert(record).execute()

def save_kpi_scores(session_id, scores):
    for kpi, score in scores.items():
        supabase.table("session_kpi_scores").insert({
            "session_id": session_id,
            "kpi_name": kpi,
            "score": score,
        }).execute()

def interactive_simulation(session_id, persona_name):
    # Initialize or get adaptive difficulty from session state
    if "current_difficulty" not in st.session_state:
        st.session_state.current_difficulty = "easy"
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    # Generate the first question if no history
    if not st.session_state.chat_history:
        prompt = create_gemini_prompt(persona_name, st.session_state.current_difficulty)
        messages = [
            {"role": "system", "content": "You are a helpful KPI training coach."},
            {"role": "user", "content": prompt}
        ]
        try:
            question_json = call_gemini_api(messages)
            question_data = json.loads(question_json)
            st.session_state.chat_history.append({
                "question": question_data["question"],
                "expected_focus": question_data["expected_focus"],
                "difficulty": question_data["difficulty"]
            })
        except Exception as e:
            st.error(f"Error getting question from Gemini: {e}")
            return

    last_q = st.session_state.chat_history[-1]
    st.markdown(f"### Question ({last_q['difficulty']}):")
    st.write(last_q['question'])

    user_answer = st.text_area("Your Answer:")

    if st.button("Submit Answer"):
        eval_prompt = create_gemini_evaluation_prompt(last_q["question"], user_answer)
        messages = [
            {"role": "system", "content": "You are an expert KPI evaluator."},
            {"role": "user", "content": eval_prompt}
        ]
        try:
            feedback_json = call_gemini_api(messages)
            feedback_data = json.loads(feedback_json)

            save_transcript(session_id, last_q["question"], user_answer, feedback_data["feedback"])
            save_kpi_scores(session_id, feedback_data["scores"])

            st.markdown("**AI Feedback:**")
            st.write(feedback_data["feedback"])

            # Adjust difficulty based on average score
            avg_score = sum(feedback_data["scores"].values()) / len(feedback_data["scores"])
            if avg_score >= 7:
                if st.session_state.current_difficulty == "easy":
                    st.session_state.current_difficulty = "medium"
                elif st.session_state.current_difficulty == "medium":
                    st.session_state.current_difficulty = "hard"
                elif st.session_state.current_difficulty == "hard":
                    st.session_state.current_difficulty = "expert"
            else:
                if st.session_state.current_difficulty in ["hard", "expert"]:
                    st.session_state.current_difficulty = "medium"
                else:
                    st.session_state.current_difficulty = "easy"

            # Fetch next question based on new difficulty and user answer
            next_prompt = create_gemini_prompt(persona_name, st.session_state.current_difficulty, previous_answer=user_answer)
            messages = [
                {"role": "system", "content": "You are a helpful KPI training coach."},
                {"role": "user", "content": next_prompt}
            ]
            question_json = call_gemini_api(messages)
            question_data = json.loads(question_json)
            st.session_state.chat_history.append({
                "question": question_data["question"],
                "expected_focus": question_data["expected_focus"],
                "difficulty": question_data["difficulty"]
            })

        except Exception as e:
            st.error(f"Error evaluating answer: {e}")
