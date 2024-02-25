import os
import json

from langchain import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.callbacks import get_openai_callback
from langchain.prompts.chat import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)

class LLM:
    def __init__(self, debug=False) -> None:
        if not os.environ.get("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set.")
        self.debug = debug
        self.BEGIN_JSON_FORMAT = "```json\n"
        self.END_JSON_FORMAT = "\n```"

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
            if response.startswith(self.BEGIN_JSON_FORMAT) and response.endswith(self.END_JSON_FORMAT):
                response = response[len(self.BEGIN_JSON_FORMAT): -len(self.END_JSON_FORMAT)]
            result = json.loads(response, strict=False)
        except json.decoder.JSONDecodeError:
            return {}, cost, tokens

        return result, cost, tokens
