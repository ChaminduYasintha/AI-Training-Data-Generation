import json
import csv
from typing import List, Dict, Any

class MasterPackager:
    """
    Packages final validated datasets into JSONL and CSV formats.
    """
    def export_to_jsonl(self, dataset: List[Dict[str, Any]], filepath: str):
        """Export dataset to JSON Lines format suitable for fine-tuning."""
        with open(filepath, 'w', encoding='utf-8') as f:
            for item in dataset:
                f.write(json.dumps(item) + '\n')
        print(f"Successfully exported {len(dataset)} items to {filepath}")

    def export_to_csv(self, dataset: List[Dict[str, Any]], filepath: str):
        """Export dataset to CSV format."""
        if not dataset:
            print("Dataset is empty. Nothing to export.")
            return

        # Infer headers from the first valid parsed JSON response if possible
        parsed_dataset = []
        for item in dataset:
            try:
                parsed_resp = json.loads(item["response"])
                parsed_item = {"chunk_preview": item["chunk_preview"], "task_type": item["task_type"]}
                parsed_item.update(parsed_resp)
                parsed_dataset.append(parsed_item)
            except json.JSONDecodeError:
                continue

        if not parsed_dataset:
            print("No valid JSON responses to export to CSV.")
            return

        headers = list(parsed_dataset[0].keys())
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writeheader()
            for row in parsed_dataset:
                # Ensure missing keys don't crash
                safe_row = {k: row.get(k, "") for k in headers}
                writer.writerow(safe_row)
                
        print(f"Successfully exported {len(parsed_dataset)} items to {filepath}")
