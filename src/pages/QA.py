import streamlit as st
import pandas as pd
from component_template import generate_default_paramater
from const import JA, EN
from llm_qa import QualityAssurance

def main():
    st.title("QA")
    st.sidebar.title("Options")

    model, max_chars, temperature = generate_default_paramater()

    col1, col2 = st.columns(2)
    # 左側のテキストエリアを配置
    with col1:
        source_language = st.selectbox("Source Language", (EN, JA))

    # 右側のテキストエリアを配置
    with col2:
        target_language = st.selectbox("Target Language", (EN, JA))

    # tsvファイルのアップロード
    uploaded_file = st.file_uploader("Choose a file", type="tsv")
    if uploaded_file:
        qa = QualityAssurance(source_language=source_language,
                              target_language=target_language,
                              model=model,
                              temperature=temperature,
                              debug=True)

        df = pd.read_csv(uploaded_file, header=None, delimiter="\t")
        df.columns = ["source", "target"]
        st.write(df)
        if st.button("Check"):
            with st.spinner("Checking..."):
                res = qa.check_translation(translation_data=df)
                print("QA")
                st.write(res)

if __name__ == "__main__":
    main()
