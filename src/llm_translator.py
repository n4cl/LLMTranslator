import json

from llm import LLM
from bunkai import Bunkai
from translation_prompt import SYSTEM_TEMPLATE, TEXT_OUTPUT_FORMAT, TABLE_OUTPUT_FOTMAT, HUMAN_TEMPLATE, EXAMPLE_EN_TO_JA, EXAMPLE_JA_TO_EN, TEXT_EXAMPLE
from const import EN, JA


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
    def __init__(self, texts: list, is_success: bool=True, cost: float=0.0, tokens: int=0, error="", error_no=""):
        self.texts: list = texts
        self.is_success: bool = is_success
        self.cost: float = cost
        self.tokens: int = tokens
        self.error: str = error
        self.error_no: str = error_no

    def dump(self) -> str:
        return json.dumps(self.texts)

    def __repr__(self):
        return f"<SplitedSentence texts={self.texts} cost={self.cost} tokens={self.tokens} error={self.error}>"

    def __str__(self) -> str:
        return str(self.texts)


class Translator(LLM):
    def __init__(self, debug: bool=False):
        super().__init__(debug=debug)
        self.japaneses_splitter = Bunkai()

    def translate_by_sentence(self, source_language, target_language, text, model, temperature):
        """
        Translate sentence unit from source language to target language.
        """

        base_error_message = "Failed to translate."
        if source_language == JA:
            splited_sentences = self.split_sentences_by_rule(text=text)
        else:
            splited_sentences = self.split_sentences_by_llm(text=text)

        if splited_sentences.is_success:
            _source_text = splited_sentences.dump()
        else:
            return Translation(translated_texts=[], is_success=False, error=base_error_message)

        translation = self.translate(source_language, target_language, _source_text, model, temperature, format_type="table")

        if translation and translation.is_success:
            translation.set_source_texts(splited_sentences.texts)
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

    def split_sentences_by_rule(self, text: str) -> SplitedSentence:
        """
        Split text into sentences using rule base.
        """
        texts = []
        empty_text = ""
        for _t in self.japaneses_splitter(text):
            if _t.strip() != empty_text:
                texts.append(_t)
        return SplitedSentence(texts=texts, is_success=True, cost=0.0, tokens=0, error="")

    def split_sentences_by_llm(self, text: str) -> SplitedSentence:
        """
        Split text into sentences using LLM.
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
            return SplitedSentence(texts=[], is_success=False, error=f"Output format is not {key_split_sentences} key", error_no="e0100", cost=cost, tokens=tokens)

        if not isinstance(result[key_split_sentences], list):
            return SplitedSentence(texts=[], is_success=False, error="Output format is not list", error_no="e0101", cost=cost, tokens=tokens)

        return SplitedSentence(texts=result[key_split_sentences], is_success=True, cost=cost, tokens=tokens)

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
            if source_language == JA and target_language == EN:
                example = EXAMPLE_JA_TO_EN
            elif source_language == EN and target_language == JA:
                example = EXAMPLE_EN_TO_JA

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
    _text = "これはテキストです。テキスト1です。\nテストです。"
    llm_translator = Translator(debug=True)
    #print(llm_translator.translate_by_sentence(source_language=JA, target_language=EN, text=_text, temperature=0.0, model="gpt-3.5-turbo"))
    print(llm_translator.translate(source_language=JA, target_language=EN, text=_text, temperature=0.0, model="gpt-3.5-turbo"))
    #print(llm_translator.split_sentences(text="Hello, world! Hello, llm! How are you?"))
    #print(llm_translator.split_sentences(text="こんにちは\n テスト。元気ですか?"))
