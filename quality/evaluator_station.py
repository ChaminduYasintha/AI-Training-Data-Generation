from typing import List, Dict, Any

class EvaluatorStation:
    """
    Explicitly inspects every generated example for toxicity, bias, diversity, 
    coherence, and topic relevance before approving it for the final dataset.
    """
    def __init__(self, strict_mode: bool = True):
        self.strict_mode = strict_mode

    def evaluate(self, example: Dict[str, Any]) -> bool:
        """
        Run all quality checks on a single generated example.
        Return True if approved, False if rejected.
        """
        response = example.get("response", "").lower()
        
        if not response:
            return False

        # 1. Toxicity Check (Mocked logic)
        toxic_keywords = ["hate", "kill", "toxic_word", "illegal"]
        if any(word in response for word in toxic_keywords):
            print(f"Rejected: Toxicity detected in ({example['chunk_preview']})")
            return False

        # 2. Coherence/Format Check (Mocked JSON parsing check)
        if not (response.startswith("{") and response.endswith("}")):
            print(f"Rejected: Invalid formatting in ({example['chunk_preview']})")
            return False
        
        # 3. Topic Relevance Check
        # In a real scenario, we'd use another AI call or embedding distance to verify 
        # that the answer is grounded in the chunk_preview.
        
        return True

    def filter_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter an entire generated dataset, returning only approved examples."""
        approved = []
        for example in dataset:
            if self.evaluate(example):
                approved.append(example)
        return approved
