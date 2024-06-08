import pandas as pd
from llm import LLM

class QualityAssurance(LLM):
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
        df = pd.DataFrame(columns=["source", "target", "accuracy", "grammar", "fluency", "cultural", "style", "error", "review"])
        for index, row in translation_data.iterrows():
            source = row["source"]
            target = row["target"]
            # 先頭のカラムを除外したカラム名のリストを取得
            if source and target:
                is_success, result = self._call(source=source, target=target)
                if is_success:
                    df.loc[len(df)] = [source, target, result["accuracy"], result["grammar"], result["fluency"], result["cultural"], result["style"], result["error"], result["review"]]
                else:
                    df.loc[len(df)] = [source, target, None, None, "Failed to quality assurance."]
        return df

    def _call(self, source: str, target: str):
        llm = self._get_llm(model=self.model, temperature=self.temperature)

        system_template = ("次の tsv のデータには、対訳結果が含まれているので、評価してください。\n"
                           "原文は{source_language}で、訳文は{target_language}です。\n"
                           "評価軸は、以下の点で評価してください。\n"
                           "### 評価軸の定義\n"
                           "accuracy: 0: 翻訳が不正確である, 1: 意味は伝わるが正確ではない, 2: 翻訳が正確である\n"
                           "grammar: 0: 文法的に誤りが多い, 1: 一部に文法的な誤りがあるが、理解は可能, 2: 文法的に正しい\n"
                           "fluency: 0: 不自然で読みづらい, 1: 一部に不自然な表現があるが、理解は可能, 2: 自然で読みやすいn"
                           "cultural: 0: 文化的に不適切, 1: 一部に文化的な違和感があるが、全体としては理解可能, 2: 文化的に適切\n"
                           "style: 0: スタイルやトーンが不適切, 1: 一部にスタイルやトーンの不一致があるが、全体としては理解可能, 2:  スタイルやトーンが適切\n"
                           "error: 0: 明らかな誤訳や脱字が多い, 1: 一部に誤訳や脱字があるが、全体としては理解可能, 2: 誤訳や脱字がない\n"
                           "### 出力形式\n"
                           "json で、次のフォーマットに従ってください。\n"
                           "```json\n"
                           "{{\"accuracy\": 0 or 1 or 2, \"grammar\": 0 or 1 or 2, \"fluency\": 0 or 1 or 2, \"cultural\": 0 or 1 or 2, \"style\": 0 or 1 or 2, \"error\": -1 or 0 or 1, \"review\": \"具体的なレビュー内容\"}}\n"
                           "```\n"
                           "review: レビューした内容は日本語で記載してください。")
        human_template = ("```tsv\n"
                          "原文\t対訳\n"
                          "{source}\t{target}\n")
        chain = self._make_llm_chain(llm=llm, system_template=system_template, human_template=human_template)
        result, cost, tokens = self._run_llm_chain(chain=chain,
                                                   source_language=self.source_language,
                                                   target_language=self.target_language,
                                                   source=source,
                                                   target=target)
        if "accuracy" not in result or "grammar" not in result or "review" not in result:
            return False, "Output format is not correct."
        return True, result

