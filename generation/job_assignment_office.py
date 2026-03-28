import asyncio
from typing import List, Dict, Any
from .ai_client import AIClient
from .task_templates import TaskTemplates

class JobAssignmentOffice:
    """
    Manages generation using asyncio to orchestrate massive concurrent task execution.
    """
    def __init__(self):
        self.ai_client = AIClient()

    async def _process_chunk(self, chunk: str, task_type: str, provider: str) -> Dict[str, Any]:
        """Process a single chunk based on task type."""
        if task_type == "qa":
            template = TaskTemplates.qa_template(chunk)
        elif task_type == "summary":
            template = TaskTemplates.summary_template(chunk)
        elif task_type == "classification":
            template = TaskTemplates.classification_template(chunk)
        else:
            raise ValueError(f"Unknown task type: {task_type}")

        # Execute AI call asynchronously
        response_text, usage_metrics = await self.ai_client.generate_completion(
            system_prompt=template['system'],
            user_prompt=template['user'],
            provider=provider
        )
        
        return {
            "chunk_preview": chunk[:50] + "...",
            "task_type": task_type,
            "response": response_text,
            "usage": usage_metrics
        }

    async def generate_dataset(self, chunks: List[str], task_type: str, provider: str = "openai") -> List[Dict]:
        """Generate dataset points for a list of chunks concurrently, respecting rate limits."""
        sem = asyncio.Semaphore(3) # Limit to 3 concurrent parallel requests to avoid HTTP 429
        
        async def _bound_process(chunk):
            async with sem:
                await asyncio.sleep(1) # Add delay between requests
                return await self._process_chunk(chunk, task_type, provider)

        tasks = [_bound_process(chunk) for chunk in chunks]
        
        # Gather all concurrent AI calls
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter valid results, logging exceptions
        valid_results = []
        for res in results:
            if isinstance(res, Exception):
                print(f"Task failed: {res}")
            else:
                valid_results.append(res)
                
        return valid_results
