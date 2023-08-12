import streamlit as st
import random
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

    # モデルの選択
    model_name, temperature = select_paramater()
    llm = Translator(model=model_name, temperature=temperature)

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
        with st.spinner("Translating ..."):
            translation = llm.translate_and_get_cost(source_language=source_lang, target_language=target_lang, text=source_text)
            if translation.is_success and translation.cost > 0:
                st.write(translation.translated_text)
            else:
                st.write("Failed to translate.")

    st.sidebar.markdown("## Costs")
    st.sidebar.markdown("**Total cost**")
    if translation and translation.is_success and translation.cost > 0:
        st.sidebar.markdown(f"- ${translation.cost}")
    else:
        st.sidebar.markdown("- $0")

if __name__ == "__main__":
    main()
