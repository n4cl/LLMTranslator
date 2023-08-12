import streamlit as st
import random

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

    # レイアウトを横に並べるためのコンテナを作成
    col1, col2 = st.columns(2)

    # 左側のテキストエリアを配置
    with col1:
        source_lang = st.selectbox("Source Language", ("English", "Japanese"))
        source_text = st.text_area("原文", height=300)

    # 右側のテキストエリアを配置
    with col2:
        target_lang = st.selectbox("Target Language", ("English", "Japanese"))

        if source_text:
                target_text = st.text_area("訳文", value=source_text, height=300)
        else:
            target_text = st.text_area("訳文", height=300)

    st.sidebar.markdown("## Costs")
    st.sidebar.markdown("**Total cost**")
    # TODO: 仮実装
    r = random.uniform(1, 100)
    st.sidebar.markdown(f"- ${r}")

if __name__ == "__main__":
    main()
