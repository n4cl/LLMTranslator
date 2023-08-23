import streamlit as st
from llm_translator import Translator
from const import JA, EN

def select_paramater():
    model = st.sidebar.radio("Choose a model:", ("GPT-3.5", "GPT-4"), horizontal=True)
    if model == "GPT-3.5":
        model_name = "gpt-3.5-turbo"
        max_chars = 3000
    else:
        model_name = "gpt-4"
        max_chars = 7000
    temperature = st.sidebar.slider("Temperature:", min_value=0.0, max_value=2.0, value=0.0, step=0.1)
    format_type = st.sidebar.radio("Output format:", ("text", "table"), horizontal=True, index=1)
    return model_name, max_chars, temperature, format_type


def main():
    st.title("LLM Translater")
    st.sidebar.title("Options")

    model, max_chars, temperature, format_type = select_paramater()
    llm = Translator(debug=True)
    if "cost" not in st.session_state:
        st.session_state.cost = 0.0

    col1, col2 = st.columns(2)

    # 左側のテキストエリアを配置
    with col1:
        source_language = st.selectbox("Source Language", (EN, JA))

    # 右側のテキストエリアを配置
    with col2:
        target_language = st.selectbox("Target Language", ((EN, JA)))

    text = st.text_area("Input", height=300, max_chars=max_chars)

    translation = None
    if st.button("Translate"):
        if source_language == target_language:
            st.markdown("## WARNING:\nSource language and target language must be different.")
        elif text == "":
            st.markdown("## WARNING:\nPlease input text.")
        else:
            with st.spinner("Translating ..."):
                if format_type == "text":
                    translation = llm.translate(source_language, target_language, text, model, temperature, format_type)
                    if translation.error == "":
                        st.write(translation.translated_texts)
                    else:
                        st.markdown(f"## WARNING:\n{translation.error}")
                elif format_type == "table":
                    translation = llm.translate_by_sentence(source_language, target_language, text, model, temperature)
                    if translation.error == "":
                        pair = [[s, t] for s, t in zip(translation.source_texts, translation.translated_texts)]
                        st.table(pair)
                    elif translation.error_no == "e0200":
                        st.write("## WARNING:\nCould not output in table.")
                        st.write("\n".join(translation.translated_texts))
                    else:
                        st.markdown(f"## WARNING:\n{translation.error}")

    st.sidebar.markdown("## Costs")
    if translation and translation.is_success and translation.cost > 0:
        st.session_state.cost += translation.cost

    if st.session_state.cost > 0:
        st.sidebar.markdown(f"- ${st.session_state.cost:.5f}")
    else:
        st.sidebar.markdown("- $0")

if __name__ == "__main__":
    main()
