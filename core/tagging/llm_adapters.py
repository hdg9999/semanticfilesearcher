from abc import ABC, abstractmethod
import os

class LLMAdapter(ABC):
    """
    다양한 LLM 서비스를 위한 추상화 레이어.
    """
    @abstractmethod
    def generate_keywords(self, content_description: str, existing_tags: list) -> list:
        """분석된 내용과 기존 태그 목록을 바탕으로 키워드(태그)를 생성합니다."""
        pass

class OpenAIAdapter(LLMAdapter):
    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        from openai import OpenAI
        self.client = OpenAI(api_key=api_key)
        self.model = model

    def generate_keywords(self, content_description, existing_tags):
        prompt = self._build_prompt(content_description, existing_tags)
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return self._parse_response(response.choices[0].message.content)

    def _build_prompt(self, desc, tags):
        return f"내용: {desc}\n기존 태그: {', '.join(tags)}\n위 내용을 바탕으로 적절한 태그 3개를 콤마로 구분해서 상위 3개만 답변해줘."

    def _parse_response(self, text):
        return [t.strip() for t in text.split(',') if t.strip()]

class GeminiAdapter(LLMAdapter):
    def __init__(self, api_key: str, model: str = "gemini-1.5-flash"):
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel(model)

    def generate_keywords(self, content_description, existing_tags):
        prompt = f"내용: {content_description}\n기존 태그: {', '.join(existing_tags)}\n적절한 태그 3개를 콤마로 구분해서 답변해줘."
        response = self.model.generate_content(prompt)
        return [t.strip() for t in response.text.split(',') if t.strip()]

class OllamaAdapter(LLMAdapter):
    def __init__(self, model: str = "llama3", base_url: str = "http://localhost:11434"):
        import requests
        self.model = model
        self.base_url = f"{base_url}/api/generate"

    def generate_keywords(self, content_description, existing_tags):
        import requests
        prompt = f"내용: {content_description}\n기존 태그: {', '.join(existing_tags)}\n적절한 태그 3개를 콤마로 구분해서 한국어로 답변해줘."
        payload = {"model": self.model, "prompt": prompt, "stream": False}
        try:
            r = requests.post(self.base_url, json=payload)
            r.raise_for_status()
            text = r.json().get('response', '')
            return [t.strip() for t in text.split(',') if t.strip()]
        except: return []

class HuggingFaceAdapter(LLMAdapter):
    def __init__(self, model_id: str = "polyglot-ko-1.3b"):
        from transformers import pipeline
        self.pipe = pipeline("text-generation", model=model_id, device_map="auto")

    def generate_keywords(self, content_description, existing_tags):
        prompt = f"내용: {content_description}\n태그:"
        # 경량 모델 특성상 프롬프트 엔지니어링 및 후처리가 더 필요할 수 있음
        res = self.pipe(prompt, max_new_tokens=20)
        return [res[0]['generated_text'].split('태그:')[-1].strip()]
