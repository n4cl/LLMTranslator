import pandas as pd
from llm import LLM

class TranslationCompare(LLM):
    def __init__(self, source_language: str, target_language: str, model: str, temperature: float, debug: bool=False):
        super().__init__(debug=debug)
        self.source_language = source_language
        self.target_language = target_language
        self.model = model
        self.temperature = temperature

    def check_translation(self, translation_data: pd.DataFrame):
        """
        Check the quality of the translation.
        """
        if self.source_language == self.target_language:
            return False, "Source language and target language must be different."
        if translation_data.empty:
            return False, "Please input text."
        # 空の pandas.DataFrame を生成
        df = pd.DataFrame(columns=["source", "target1", "target2", "accuracy", "grammar", "total", "review"])
        for index, row in translation_data.iterrows():
            source = row["source"]
            target1 = row["target1"]
            target2 = row["target2"]
            # 先頭のカラムを除外したカラム名のリストを取得
            if source and target1 and target2:
                is_success, result = self._call(source=source, target1=target1, target2=target2)
                if is_success:
                    df.loc[len(df)] = [source, target1, target2, result["accuracy"], result["grammar"], result["total"], result["review"]]
                else:
                    df.loc[len(df)] = [source, target1, target2, -1, -1, "Failed to quality assurance."]
        return df

    def _call(self, source: str, target1: str, target2: str):
        llm = self._get_llm(model=self.model, temperature=self.temperature)

        system_template = ("あなたはどちらの翻訳エンジンの訳質が高いか評価してください。\n"
                           "次の tsv のデータには、原文と翻訳エンジン1の訳文と翻訳エンジン2の訳文が含まれています。\n"
                           "原文は{source_language}で、訳文は{target_language}です。\n"
                           "評価軸は、翻訳の正確性(accuracy)、文法の構造 (grammar) 、総合評価 (total) の3点で評価してください。\n"
                           "出力形式は json で、次のフォーマットに従ってください。\n"
                           "```json\n"
                           "{{\"accuracy\": 0 or 1 or 2, \"grammar\": 0 or 1 or 2, \"total\": 0 or 1 or 2, \"review\": \"具体的なレビュー内容\"}}\n"
                           "```\n"
                           "accuracy: 0=同じ, 1=1の方が良い, 2=2の方が良い\n"
                           "grammar: 0=同じ, 1=1の方が良い, 2=2の方が良い\n"
                           "total: 0=同じ, 1=1の方が良い, 2=2の方が良い\n"
                           "review: レビューした内容は日本語で記載してください。\n")
        human_template = ("```tsv\n"
                          "原文\t翻訳エンジン1による訳文\t翻訳エンジン2による訳文\n"
                          "{source}\t{target1}\t{target2}\n")
        chain = self._make_llm_chain(llm=llm, system_template=system_template, human_template=human_template)
        result, cost, tokens = self._run_llm_chain(chain=chain,
                                                   source_language=self.source_language,
                                                   target_language=self.target_language,
                                                   source=source,
                                                   target1=target1,
                                                   target2=target2)
        if "accuracy" not in result or "grammar" not in result or "total" not in result or "review" not in result:
            return False, "Output format is not correct."
        return True, result
