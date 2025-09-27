def create_gemini_prompt(persona_name, current_difficulty="easy", previous_answer=None):
    prompt = f"""
You are a KPI training coach for a sales manager persona '{persona_name}'. Use these rules to generate one scenario question at difficulty {current_difficulty}:

- Cover KPIs: conversion, upselling, cross-selling, retention, customer experience.
- Adaptive difficulty: easier questions if previous answer was incorrect or unclear; harder if correct.
- Provide question in JSON format:
{{
  "difficulty": "easy | medium | hard | expert",
  "question": "string",
  "expected_focus": "string (skills or concepts tested)"
}}

Previous answer: {previous_answer if previous_answer else 'N/A'}
"""
    return prompt.strip()


def create_gemini_evaluation_prompt(question, user_answer):
    prompt = f"""
You asked this question: "{question}".

The user answered: "{user_answer}".

Rate their answer from 0 to 10 on the following KPIs:
- conversion
- upselling
- cross-selling
- retention
- customer experience

Provide clear constructive feedback to help improve.

Return your response in JSON format with this structure:

{{
  "scores": {{
    "conversion": int,
    "upselling": int,
    "cross_selling": int,
    "retention": int,
    "customer_experience": int
  }},
  "feedback": "string"
}}
"""
    return prompt.strip()
