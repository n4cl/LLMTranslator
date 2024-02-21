import streamlit as st
import pandas as pd
from component_template import generate_default_paramater
from const import JA, EN

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

    # csvファイルのアップロード
    uploaded_file = st.file_uploader("Choose a file", type="csv")
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file, header=None)
        df.columns = ["source", "target"]
        st.write(df)
        st.button("Quality Assurance")

if __name__ == "__main__":
    main()
