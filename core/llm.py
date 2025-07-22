from openai import OpenAI
from typing import List, Dict, Any, Optional
from .config import llm_config

class LLM:
    def __init__(self, temperature=llm_config.get("temperature", 0.3), 
                 n=llm_config.get("n", 1), 
                 top_p=llm_config.get("top_p", 0.5)):
        self.client = OpenAI(
            api_key=llm_config.get("api_key"),
            base_url=llm_config.get("url")
        )
        self.model = llm_config.get("model")
        self.temperature = temperature
        self.n = n
        self.top_p = top_p
        self.history = []

    def nschat(self, query: str, role: str = 'user', history: Optional[List] = None) -> str:
        messages = history or []
        messages.append({"role": role, "content": query})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            stream=False
        )
        result = response.choices[0].message.content
        
        if history is None:
            self.history.append({"role": role, "content": query})
            self.history.append({"role": "assistant", "content": result})
            
        return result

    def schat(self, query: str, role: str = 'user', history: Optional[List] = None) -> str:
        messages = history or []
        messages.append({"role": role, "content": query})
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=self.temperature,
            stream=True
        )
        
        accumulated_content = ""
        for chunk in response:
            if chunk.choices[0].delta.content:
                accumulated_content += chunk.choices[0].delta.content
                
        if history is None:
            self.history.append({"role": role, "content": query})
            self.history.append({"role": "assistant", "content": accumulated_content})
            
        return accumulated_content