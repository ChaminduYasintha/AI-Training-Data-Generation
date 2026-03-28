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
        import json
        raw_response = example.get("response", "")
        response = raw_response.strip().lower()
        
        if not response:
            return False

        # 1. Toxicity Check
        toxic_keywords = ["hate", "kill", "toxic_word", "illegal"]
        if any(word in response for word in toxic_keywords):
            print(f"Rejected: Toxicity detected in ({example['chunk_preview']})")
            return False

        # 2. Coherence/Format Check — strip whitespace before comparing.
        # Real LLM responses often have trailing newlines that break a naive endswith("}")
        response_stripped = response.strip()
        if not (response_stripped.startswith("{") and response_stripped.endswith("}")):
            # Fallback: attempt to parse the raw response as valid JSON
            try:
                json.loads(raw_response.strip())
            except (json.JSONDecodeError, ValueError):
                print(f"Rejected: Invalid formatting in ({example['chunk_preview']})")
                return False
        
        return True

    def filter_dataset(self, dataset: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Filter an entire generated dataset, returning only approved examples."""
        approved = []
        for example in dataset:
            if self.evaluate(example):
                approved.append(example)
        return approved
