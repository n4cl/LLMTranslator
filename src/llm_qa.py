
from llm import LLM
from qa_promp import SYSTEM_TEMPLATE, HUMAN_TEMPLATE, EXSAMPLE
from const import EN, JA


class QualityAssurance(LLM):
    def evaluate_quality(self, source_language: str, target_language: str, csv: str, model: str="gpt-3.5-turbo", temperature: float=0.0):
        llm = self._get_llm(model=model, temperature=temperature)

        chain = self._make_llm_chain(llm=llm, system_template=SYSTEM_TEMPLATE, human_template=HUMAN_TEMPLATE)
        result, cost, tokens = self._run_llm_chain(chain=chain,
                                                   source_language=source_language,
                                                   target_language=target_language,
                                                   exsample=EXSAMPLE,
                                                   csv=csv
                                                   )
        return result, cost, tokens

if __name__ == '__main__':
    qa = QualityAssurance()
    res = qa.evaluate_quality(source_language=EN, target_language=JA, csv="id,原文,訳文\n1,This is a test.,これはテスト\nid,原文,訳文\n1,This is a test.,これは", model="gpt-4", temperature=0.0)
    print(res)
