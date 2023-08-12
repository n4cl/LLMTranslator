import os
import json
from langchain.chat_models import ChatOpenAI
from langchain import LLMChain
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.callbacks import get_openai_callback

class Translation:
    def __init__(self, translated_text="", is_success=True, error=""):
        self.translated_text: str = translated_text
        self.is_success: bool  = is_success
        self.cost: float = 0.0
        self.tokens: int = 0
        self.error: str = error

    def __repr__(self):
        return f"<Translation translated_text={self.translated_text} cost={self.cost} tokens={self.tokens} error={self.error}>"

    def __str__(self) -> str:
        return self.translated_text


class Translator:
    def __init__(self, model: str="gpt-3.5-turbo", temperature: float=0, max_tokens: int=500):
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set.")
        self.model = model
        self.temperature = temperature
        self.max_tokens = max_tokens

    def translate_and_get_cost(self, source_language: str, target_language: str, text: str) -> dict:
        with get_openai_callback() as _callback:
            _translation = self.translate(source_language=source_language, target_language=target_language, text=text)
            cost = _callback.total_cost
            tokens = _callback.total_tokens
        _translation.cost = cost
        _translation.tokens = tokens
        return _translation

    def translate(self, source_language: str, target_language: str, text: str) -> Translation:
        llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        template = ("You are a helpful assistant that translates {source_language} to {target_language}.\n"
                    "The result should be in json format with the key \"translated_text\" and the translated result as its value.\n")
        system_message_prompt = SystemMessagePromptTemplate.from_template(template)
        human_template = "{text}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        chain = LLMChain(llm=llm, prompt=chat_prompt)
        translated_text = chain.run(source_language=source_language, target_language=target_language, text=text)

        try:
            res = json.loads(translated_text)
        except json.decoder.JSONDecodeError:
            return Translation(is_success=False, error="Output format is not json")

        if "translated_text" not in res:
            return Translation(is_success=False, error="Output format is not translated_text key")

        return Translation(translated_text=res["translated_text"], is_success=True)


if __name__ == '__main__':
    llm_translator = Translator()
    print(llm_translator.translate(source_language="English", target_language="Japanese", text="Hello, world!"))
    print(llm_translator.translate_and_get_cost(source_language="English", target_language="Japanese", text="Hello, world!"))
