import os
import asyncio
from typing import Dict, Any
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

class AIClient:
    """
    Directly interacts with OpenAI/Anthropic/Gemini APIs.
    Includes a Simulation Mode to avoid burning credits.
    """
    def __init__(self):
        self.simulation_mode = os.getenv("SIMULATION_MODE", "False").lower() == "true"
        self.openai_key = os.getenv("OPENAI_API_KEY")
        self.anthropic_key = os.getenv("ANTHROPIC_API_KEY")
        self.gemini_key = os.getenv("GEMINI_API_KEY")

        if not self.simulation_mode and not self.openai_key and not self.anthropic_key and not self.gemini_key:
            print("Warning: No API keys found. Forcing Simulation Mode.")
            self.simulation_mode = True

        if self.gemini_key:
            genai.configure(api_key=self.gemini_key)

    async def generate_completion(self, system_prompt: str, user_prompt: str, provider: str = "openai") -> tuple:
        if self.simulation_mode:
            text = self._simulate_response(system_prompt, user_prompt)
            # Simulated token counts based on length
            usage = {"prompt": (len(system_prompt) + len(user_prompt)) // 4, "completion": len(text) // 4}
            return text, usage
        
        if provider == "gemini":
            if not self.gemini_key: raise ValueError("Gemini key missing.")
            
            # Using asyncio.to_thread because the SDK is synchronous
            def _call_gemini():
                model = genai.GenerativeModel('gemini-3-flash-preview')
                combined_prompt = f"{system_prompt}\n\n{user_prompt}"
                response = model.generate_content(combined_prompt)
                text = response.text.strip()
                # Clean markdown JSON wraps
                if text.startswith("```json"):
                    text = text[7:-3].strip()
                elif text.startswith("```"):
                    text = text[3:-3].strip()
                    
                prompt_tokens = 0
                completion_tokens = 0
                if hasattr(response, 'usage_metadata'):
                    prompt_tokens = getattr(response.usage_metadata, 'prompt_token_count', len(combined_prompt) // 4)
                    completion_tokens = getattr(response.usage_metadata, 'candidates_token_count', len(text) // 4)
                
                return text, {"prompt": prompt_tokens, "completion": completion_tokens}
                
            return await asyncio.to_thread(_call_gemini)
            
        elif provider == "openai":
            if not self.openai_key: raise ValueError("OpenAI key missing.")
            # For demonstration unless user decides to fully implement OpenAI SDK
            text = f'{{"q": "Real Question", "a": "Real OpenAI Response. Prompt length: {len(user_prompt)}"}}'
            return text, {"prompt": len(user_prompt)//4, "completion": len(text)//4}
            
        elif provider == "anthropic":
            if not self.anthropic_key: raise ValueError("Anthropic key missing.")
            # For demonstration
            text = f'{{"q": "Real Question", "a": "Real Anthropic Response. Prompt length: {len(user_prompt)}"}}'
            return text, {"prompt": len(user_prompt)//4, "completion": len(text)//4}
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def _simulate_response(self, system_prompt: str, user_prompt: str) -> str:
        """Mock AI responses based on the task type in the prompt."""
        if "Question & Answer" in system_prompt:
            return '{"q": "What is simulated?", "a": "This is a simulated response."}'
        elif "Summarize" in system_prompt:
            return '{"summary": "This is a simulated summary of the text chunk."}'
        else:
            return '{"label": "simulated_classification"}'
