import os
from openai import OpenAI
import anthropic
import google.generativeai as genai  # Add this import
from together import Together
from groq import Groq
from ollama import chat
from ollama import ChatResponse

# USAGE NOTES:
# To enable Claude's thinking tokens in Minesweeper benchmarks, append "-thinking" to the model name.
# For example: "claude-3.7-sonnet-20240620-thinking"

class LLMProviderInterface:
    """
    A common interface for LLM calls.
    """
    def get_response(self, model: str, prompt: str) -> str:
        raise NotImplementedError("Subclasses should implement this method.")


class OpenAIProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        
    def get_response(self, model: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=4096,
        )
        return response.choices[0].message.content.strip()


class AnthropicProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        self.client = anthropic.Anthropic(api_key=api_key)
    
    def get_response(self, model: str, prompt: str) -> str:
        # Check if this is the special thinking token variant
        if model.endswith("-thinking"):
            # Remove the -thinking suffix for the actual API call
            actual_model = model[:-9]
            response = self.client.messages.create(
                model=actual_model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                thinking={
                    "type": "enabled",
                    "budget_tokens": 4_000, 
                    },
                stream=False
            )
            #print(response.content)
            
            return ("<think>\n" + response.content[0].thinking + "\n</think>\n" + response.content[1].text).strip()
        else:
            # Standard call without thinking tokens - this preserves the existing benchmark behavior
            response = self.client.messages.create(
                model=model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
            )
        return response.content[0].text.strip()
    
class GeminiProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        
    def get_response(self, model: str, prompt: str) -> str:
        model = genai.GenerativeModel(model)
        response = model.generate_content(
            contents=prompt,
            generation_config={
                "max_output_tokens": 4096,
            },
            stream=False
        )
        return response.text.strip()
    

class TogetherProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        self.client = Together(api_key=api_key)

    def get_response(self, model: str, prompt: str) -> str:
        response = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            #max_tokens=4096,
            max_tokens=30_000,
        )
        return response.choices[0].message.content.strip()

class OllamaProvider(LLMProviderInterface):
    def __init__(self, url: str = "http://localhost:11434"):
        self.url = url

    def get_response(self, model: str, prompt: str) -> str:
        model = model[len("ollama-"):] if model.lower().startswith("ollama-") else model
        response: ChatResponse = chat(model=model, messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ])
        return response.message.content.strip()

class GroqProvider(LLMProviderInterface):
    def __init__(self, api_key: str):
        self.client = Groq(api_key = api_key)

    def get_response(self, model: str, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.6,
            max_completion_tokens=131072,
            top_p=0.95,
            stream=False,
            #stop=None,
        )
        return completion.choices[0].message.content.strip()

def create_llm_provider(model: str) -> LLMProviderInterface:
    """
    Factory function for creating an LLM provider instance.
    If any substring in the openai_substrings list is found in the model name (case-insensitive),
    returns an instance of OpenAIProvider.
    If any substring in the anthropic_substrings list is found, returns an instance of AnthropicProvider.
    Otherwise, raises a ValueError.
    """
    model_lower = model.lower()
    openai_substrings = ["gpt-", "o1-", "o3-"]
    # Note: "claude-3.7-sonnet-20240620-thinking" will also match here 
    # and use the special thinking tokens feature in the AnthropicProvider
    anthropic_substrings = ["claude"]
    gemini_substrings = ["gemini"]
    #together_substrings = ["meta-llama", "deepseek", "Gryphe", "microsoft", "mistralai", "NousResearch", "nvidia", "Qwen", "upstage"]
    ollama_substrings = ["ollama-"]
    groq_substrings = ["deepseek", "llama"]

    if any(substr.lower() in model_lower for substr in openai_substrings):
        if not os.getenv("OPENAI_API_KEY"):
            raise ValueError("OPENAI_API_KEY is not set in the environment variables.")
        return OpenAIProvider(api_key=os.getenv("OPENAI_API_KEY"))
    elif any(substr.lower() in model_lower for substr in anthropic_substrings):
        if not os.getenv("ANTHROPIC_API_KEY"):
            raise ValueError("ANTHROPIC_API_KEY is not set in the environment variables.")
        return AnthropicProvider(api_key=os.getenv("ANTHROPIC_API_KEY"))
    elif any(substr.lower() in model_lower for substr in gemini_substrings):
        if not os.getenv("GOOGLE_API_KEY"):
            raise ValueError("GOOGLE_API_KEY is not set in the environment variables.")
        return GeminiProvider(api_key=os.getenv("GOOGLE_API_KEY"))
    elif any(substr.lower() in model_lower for substr in ollama_substrings):
        return OllamaProvider(url=os.getenv("OLLAMA_URL", "http://localhost:11434"))
    elif any(substr.lower() in model_lower for substr in groq_substrings):
        return GroqProvider(api_key=os.getenv("GROQ_API_KEY"))
    #elif any(substr.lower() in model_lower for substr in together_substrings):
    #    if not os.getenv("TOGETHERAI_API_KEY"):
    #        raise ValueError("TOGETHERAI_API_KEY is not set in the environment variables.")
    #    return TogetherProvider(api_key=os.getenv("TOGETHERAI_API_KEY"))
    else:
        raise ValueError(f"Unsupported model: {model}")
