import streamlit as st
import pandas as pd
from llm_translator import Translator
from const import JA, EN
from component_template import generate_default_paramater


def main():
    st.title("Translaion")
    st.sidebar.title("Options")

    model, max_chars, temperature = generate_default_paramater()
    format_type = st.sidebar.radio("Output format:", ("text", "table"), horizontal=True, index=1)

    llm = Translator(debug=True)
    if "cost" not in st.session_state:
        st.session_state.cost = 0.0

    col1, col2 = st.columns(2)

    # 左側のテキストエリアを配置
    with col1:
        source_language = st.selectbox("Source Language", (EN, JA))

    # 右側のテキストエリアを配置
    with col2:
        target_language = st.selectbox("Target Language", (EN, JA))

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
                        pd_pair = pd.DataFrame(pair, columns=["Source", "Target"])
                        st.download_button("Download csv", data=pd_pair.to_csv(index=False), file_name="pair.csv", mime="text/csv")
                    elif translation.error_no == "e0200":
                        st.write("## WARNING:\nCould not output in table.")
                        st.write("\n".join(translation.translated_texts))
                    else:
                        st.markdown(f"## WARNING:\n{translation.error}")


if __name__ == "__main__":
    main()
