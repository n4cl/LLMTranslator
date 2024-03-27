import streamlit as st

def generate_default_paramater():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"), horizontal=True)
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo-0125"
        max_chars = 3000
    else:
        model_name = "gpt-4-0125-preview"
        max_chars = 7000
    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.1)

    return model_name, max_chars, temperature
