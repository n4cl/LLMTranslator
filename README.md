LLMTranslator
===

LLMTranslator is a translation system that utilizes OpenAI's API.

## Requirements
- Python 3.11
- OpenAI API Key

## Getting Started

### Web UI

``` shell
export OPENAI_API_KEY=${OPENAI_API_KEY}
pip install -r requirements_front.txt
streamlit run src/llm_translation.py
```

### Module

``` shell
export OPENAI_API_KEY=${OPENAI_API_KEY}
pip install -r requirements.txt
```

``` python
from src.llm_translator import Translator
llm = Translator()
llm.translate(source_language="English", target_language="Japanese", text="Hello, world!")
llm.translate_by_sentence(source_language="English", target_language="Japanese", text="Hello, world! How are you?")
```
