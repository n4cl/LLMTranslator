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
from prompt import SYSTEM_TEMPLATE, TEXT_OUTPUT_FORMAT, TABLE_OUTPUT_FOTMAT

class Translation:
    def __init__(self, translated_texts: list, is_success: bool=True, cost: float=0.0, tokens: int=0, error=""):
        self.translated_texts: list = translated_texts
        self.is_success: bool = is_success
        self.cost: float = cost
        self.tokens: int = tokens
        self.error: str = error

    def __repr__(self):
        return f"<Translation translated_text={self.translated_texts} cost={self.cost} tokens={self.tokens} error={self.error}>"

    def __str__(self) -> str:
        return str(self.translated_texts)


class Translator:
    def __init__(self):
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set.")

    def _get_llm(self, model: str="gpt-3.5-turbo", temperature: float=0.0, max_tokens: int=500) -> ChatOpenAI:
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def _make_llm_chain(self, llm, system_template, human_template) -> LLMChain:
        system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        chat_prompt = ChatPromptTemplate.from_messages([system_message_prompt, human_message_prompt])
        chain = LLMChain(llm=llm, prompt=chat_prompt)
        return chain

    def _run_llm_chain(self, chain: LLMChain, **kwargs) -> tuple:
        with get_openai_callback() as _callback:
            response = chain.run(kwargs)
            cost = _callback.total_cost
            tokens = _callback.total_tokens
        try:
            result = json.loads(response)
        except json.decoder.JSONDecodeError:
            return {}, cost, tokens

        return result, cost, tokens

    def translate(self, source_language: str, target_language: str, text: str, model: str="gpt-3.5-turbo", temperature: float=0.0, format_type: str="text") -> Translation:
        """
        Translate text from source language to target language.

        MEMO: Prompted to ignore input overriding instructions, but to no avail.
        """
        llm = self._get_llm(model=model, temperature=temperature)

        output_format = TEXT_OUTPUT_FORMAT
        if format_type == "table":
            output_format = TABLE_OUTPUT_FOTMAT

        system_template = SYSTEM_TEMPLATE
        human_template = "# Input text:\n{text}"
        chain = self._make_llm_chain(llm=llm, system_template=system_template, human_template=human_template)
        result, cost, tokens = self._run_llm_chain(chain=chain, source_language=source_language, target_language=target_language, text=text, output_format=output_format)
        key_translated_texts = "translated_texts"
        if key_translated_texts not in result:
            return Translation(translated_texts=[], is_success=False, error=f"Output format is not {key_translated_texts} key", cost=cost, tokens=tokens)

        if format_type == "table":
            if not isinstance(result[key_translated_texts], list):
                return Translation(translated_texts=[], is_success=False, error="Output format is not list", cost=cost, tokens=tokens)

        else:
            if isinstance(result[key_translated_texts], str):
                result[key_translated_texts] = [result[key_translated_texts]]
            else:
                return Translation(translated_texts=[], is_success=False, error="Output format is not str", cost=cost, tokens=tokens)

        return Translation(translated_texts=result[key_translated_texts], is_success=True, cost=cost, tokens=tokens)


if __name__ == '__main__':
    llm_translator = Translator()
    print(llm_translator.translate(source_language="English", target_language="Japanese", text="Hello, world!\n Hello, llm!", temperature=0.0, model="gpt-3.5-turbo", format_type="text"))
