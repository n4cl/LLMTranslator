import streamlit as st
import pandas as pd
from component_template import generate_default_paramater
from const import JA, EN
from llm_trans_compare import TranslationCompare

def main():
    st.title("TransCompare")
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
    uploaded_file = st.file_uploader("Choose a file", type=["tsv", "csv"])
    if uploaded_file:
        tc = TranslationCompare(source_language=source_language,
                              target_language=target_language,
                              model=model,
                              temperature=temperature,
                              debug=True)
        file_type = uploaded_file.name.split(".")[-1]
        if file_type == "csv":
            df = pd.read_csv(uploaded_file, header=None)
        else:
            df = pd.read_csv(uploaded_file, header=None, delimiter="\t")
        df.columns = ["source", "target1", "target2"]
        st.write(df)
        if st.button("Check"):
            with st.spinner("Checking..."):
                res = tc.check_translation(translation_data=df)
                print("TransCompare")
                st.write(res)

if __name__ == "__main__":
    main()
