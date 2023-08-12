import streamlit as st
from llm_translator import Translator


def select_paramater():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"))
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo"
    else:
        model_name = "gpt-4"
    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
    return model_name, temperature


def main():
    st.title("LLM Translater")
    st.sidebar.title("Options")

    model_name, temperature = select_paramater()
    llm = Translator(model=model_name, temperature=temperature)
    if "cost" not in st.session_state:
        st.session_state.cost = 0.0

    col1, col2 = st.columns(2)

    # 左側のテキストエリアを配置
    with col1:
        source_lang = st.selectbox("Source Language", ("English", "Japanese"))

    # 右側のテキストエリアを配置
    with col2:
        target_lang = st.selectbox("Target Language", ("English", "Japanese"))

    source_text = st.text_area("Input", height=300)

    translation = None
    if st.button("Translate"):
        if source_lang == target_lang:
            st.markdown("## WARNING:\nSource language and target language must be different.")
        elif source_text == "":
            st.markdown("## WARNING:\nPlease input text.")
        else:
            with st.spinner("Translating ..."):
                translation = llm.translate_and_get_cost(source_language=source_lang, target_language=target_lang, text=source_text)
                if translation.is_success and translation.cost > 0:
                    st.write(translation.translated_text)
                else:
                    st.write("Failed to translate.")

    st.sidebar.markdown("## Costs")
    if st.session_state.cost > 0:
        if translation and translation.is_success and translation.cost > 0:
            st.session_state.cost += translation.cost
        st.sidebar.markdown(f"- {st.session_state.cost:.2f}")
    else:
        st.sidebar.markdown("- $0")

if __name__ == "__main__":
    main()
