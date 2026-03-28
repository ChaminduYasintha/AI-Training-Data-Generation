class TaskTemplates:
    """
    Recipe cards specifying exactly how to generate data.
    """
    @staticmethod
    def qa_template(chunk: str) -> dict:
        return {
            "system": "You are an expert AI. Generate one Question & Answer pair from the provided text. Output in JSON format with 'q' and 'a' keys.",
            "user": f"Text:\n{chunk}"
        }

    @staticmethod
    def summary_template(chunk: str) -> dict:
        return {
            "system": "Summarize the key points of the provided text in 1-2 sentences. Output JSON with a 'summary' key.",
            "user": f"Text:\n{chunk}"
        }

    @staticmethod
    def classification_template(chunk: str) -> dict:
        return {
            "system": "Classify the provided text into one of the following categories: Technical, Business, Conversational. Output JSON with a 'label' key.",
            "user": f"Text:\n{chunk}"
        }
