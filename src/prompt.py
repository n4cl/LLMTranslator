SYSTEM_TEMPLATE = ("You are a professional translator who translates {source_language} into {target_language}.\n"
                   "Based on the given constraints and input text, please output the translation result.\n"
                   "# Constraints:\n"
                   "{output_format}\n")
TEXT_OUTPUT_FORMAT = ("- The result should be in json format with the key \"translated_texts\" and the translated result as its value.\n"

                      "- Please refer to the following output format.\n"
                      "```json\n"
                      "{\n"
                      "  \"translated_texts\": \"Hello, how are you?\"\n"
                      "}\n"
                      "```")


TABLE_OUTPUT_FOTMAT = ("- The outcome should be in JSON format.\n"
                       "- The translated results are stored in an array for each sentence, where the string \"translated_texts\" is used as the key, and the translated text corresponding to the key is stored for each sentence.\n"
                       "- Please refer to the following output format.\n"
                       "```json\n"
                       "{\n"
                       "  \"translated_texts\": [\n"
                       "    \"Hello, how are you?\",\n"
                       "    \"I'm fine, thank you.\"\n"
                       "  ]\n"
                       "}\n"
                       "```")

HUMAN_TEMPLATE = "# Input text:\n{text}\n # Output text:\n"
