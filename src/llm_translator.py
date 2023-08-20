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
from prompt import SYSTEM_TEMPLATE, TEXT_OUTPUT_FORMAT, TABLE_OUTPUT_FOTMAT, HUMAN_TEMPLATE, TEXT_EXAMPLE, \
                   EXAMPLE_EN_TO_JA, EXAMPLE_JA_TO_EN, EXAMPLE_JA_TO_CH, EXAMPLE_EN_TO_CH


def remove_line_feed_code(text: str) -> str:
    """
    Remove line feed code.
    """
    return "\n".join([line for line in text.split("\n") if line != ""])

class Translation:
    def __init__(self, translated_texts: list, is_success: bool=True, cost: float=0.0, tokens: int=0, error="", error_no=""):
        self.source_texts: list = []
        self.translated_texts: list = translated_texts
        self.is_success: bool = is_success
        self.cost: float = cost
        self.tokens: int = tokens
        self.error: str = error
        self.error_no: str = error_no

    def verify_text_pair(self) -> bool:
        """
        Verify that the number of cases in the source and target texts match.
        """
        if len(self.source_texts) == len(self.translated_texts):
            return True
        return False

    def set_source_texts(self, source_texts: list):
        self.source_texts = source_texts

    def __repr__(self):
        return f"<Translation translated_text={self.translated_texts} cost={self.cost} tokens={self.tokens} error={self.error}>"

    def __str__(self) -> str:
        return str(self.translated_texts)


class SplitedSentence:
    def __init__(self, split_sentences: list, is_success: bool=True, cost: float=0.0, tokens: int=0, error="", error_no=""):
        self.split_sentences: list = split_sentences
        self.is_success: bool = is_success
        self.cost: float = cost
        self.tokens: int = tokens
        self.error: str = error
        self.error_no: str = error_no

    def dump(self) -> str:
        return json.dumps(self.split_sentences)

    def __repr__(self):
        return f"<SplitedSentence split_sentences={self.split_sentences} cost={self.cost} tokens={self.tokens} error={self.error}>"

    def __str__(self) -> str:
        return str(self.split_sentences)


class Translator:
    def __init__(self, debug: bool=False):
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set.")
        self.debug = debug

    def _get_llm(self, model: str="gpt-3.5-turbo", temperature: float=0.0, max_tokens: int=2000) -> ChatOpenAI:
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
            if self.debug:
                print(response)
            result = json.loads(response, strict=False)
        except json.decoder.JSONDecodeError:
            return {}, cost, tokens

        return result, cost, tokens

    def translate_by_sentence(self, source_language, target_language, text, model, temperature):
        """
        Translate sentence unit from source language to target language.
        """

        base_error_message = "Failed to translate."
        splited_sentences = self.split_sentences(text=text)
        if splited_sentences.is_success:
            _source_text = splited_sentences.dump()
        else:
            return Translation(translated_texts=[], is_success=False, error=base_error_message)

        translation = self.translate(source_language, target_language, _source_text, model, temperature, format_type="table")

        if translation and translation.is_success:
            translation.set_source_texts(splited_sentences.split_sentences)
            # Verify that the number of cases in the source and target texts match.
            if translation.verify_text_pair():
                return translation

            translation.error = base_error_message
            translation.error_no = "e0200"
            return translation

        # NG case
        if translation:
            return translation
        return Translation(translated_texts=[], is_success=False, error=base_error_message, error_no="e0201")

    def split_sentences(self, text: str) -> SplitedSentence:
        """
        Split text into sentences.
        """
        text = remove_line_feed_code(text)
        llm = self._get_llm(model="gpt-3.5-turbo", temperature=0.0)
        system_template = ("Split input text with delimiters and line feed codes.\n"
                           "Based on the given constraints and input text, output the text segmentation results.\n"
                           "# Constraints:\n {constraints}")
        constraints = ("- The result must be in json format with a unique key, where the key is \"split_sentences\" and the values must be separated by an array of sentences."
                       "- The key of \"not unique\" cannot be used.\n"
                       "- Please refer to the following output format.\n"
                       "``` input fomat (string)\n"
                       "Hi, how are you? Not bad.\nThis is a test."
                       "```\n"
                       "```json\n"
                       "{\n"
                       "  \"split_sentences\": [\"Hi, how are you?\", \"Not bad.\", \"This is a test.\"]"
                       "}\n"
                       "```")

        human_template = HUMAN_TEMPLATE
        chain = self._make_llm_chain(llm=llm, system_template=system_template, human_template=human_template)
        result, cost, tokens = self._run_llm_chain(chain=chain, text=text, constraints=constraints)

        key_split_sentences = "split_sentences"
        if key_split_sentences not in result:
            return SplitedSentence(split_sentences=[], is_success=False, error=f"Output format is not {key_split_sentences} key", error_no="e0100", cost=cost, tokens=tokens)

        if not isinstance(result[key_split_sentences], list):
            return SplitedSentence(split_sentences=[], is_success=False, error="Output format is not list", error_no="e0101", cost=cost, tokens=tokens)

        return SplitedSentence(split_sentences=result[key_split_sentences], is_success=True, cost=cost, tokens=tokens)

    def translate(self, source_language: str, target_language: str, text: str, model: str="gpt-3.5-turbo", temperature: float=0.0, format_type: str="text") -> Translation:
        """
        Translate text from source language to target language.

        MEMO: Prompted to ignore input overriding instructions, but to no avail.
        """
        llm = self._get_llm(model=model, temperature=temperature)

        output_format = TEXT_OUTPUT_FORMAT
        example = TEXT_EXAMPLE
        if format_type == "table":
            output_format = TABLE_OUTPUT_FOTMAT
            if source_language == "Japanese" and target_language == "English":
                example = EXAMPLE_JA_TO_EN
            elif source_language == "English" and target_language == "Japanese":
                example = EXAMPLE_EN_TO_JA
            elif source_language == "Japanese" and target_language == "Chinese":
                example = EXAMPLE_JA_TO_CH
            elif source_language == "English" and target_language == "Chinese":
                example = EXAMPLE_EN_TO_CH

        system_template = SYSTEM_TEMPLATE
        human_template = HUMAN_TEMPLATE
        chain = self._make_llm_chain(llm=llm, system_template=system_template, human_template=human_template)
        result, cost, tokens = self._run_llm_chain(chain=chain,
                                                   source_language=source_language,
                                                   target_language=target_language,
                                                   text=text,
                                                   output_format=output_format,
                                                   example=example)
        key_translated_texts = "translated_texts"
        if key_translated_texts not in result:
            return Translation(translated_texts=[], is_success=False, error=f"Output format is not {key_translated_texts} key", error_no="e0000", cost=cost, tokens=tokens)
        _translated_texts = result[key_translated_texts]
        if format_type == "table":
            if isinstance(_translated_texts, list):
                return Translation(translated_texts=_translated_texts, is_success=True, cost=cost, tokens=tokens)
            return Translation(translated_texts=[], is_success=False, error="Output format is not list", error_no="e0001", cost=cost, tokens=tokens)
        else:
            if isinstance(_translated_texts, str):
                return Translation(translated_texts=_translated_texts, is_success=True, cost=cost, tokens=tokens)

            return Translation(translated_texts=[], is_success=False, error="Output format is not str", error_no="e0002", cost=cost, tokens=tokens)

if __name__ == '__main__':
    llm_translator = Translator(debug=True)
    _text = "これはテキストです。テキスト1です。"
    #print(llm_translator.translate_by_sentence(source_language="Japanese", target_language="English", text=_text, temperature=0.0, model="gpt-3.5-turbo"))
    print(llm_translator.translate(source_language="Japanese", target_language="English", text=_text, temperature=0.0, model="gpt-3.5-turbo"))
    #print(llm_translator.split_sentences(text="Hello, world! Hello, llm! How are you?"))
    #print(llm_translator.split_sentences(text="こんにちは\n テスト。元気ですか?"))
