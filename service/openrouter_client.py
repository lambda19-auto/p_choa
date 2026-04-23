import os

import httpx


class OpenRouterClient:
    def __init__(self, api_key: str | None = None):
        self.api_key = api_key or os.getenv('OPENROUTER_API_KEY')
        if not self.api_key:
            raise ValueError('OPENROUTER_API_KEY not found in environment')

        self.base_url = 'https://openrouter.ai/api/v1'
        self.headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json',
        }

    async def create_chat_completion(self, model: str, messages: list[dict], temperature: float = 0):
        normalized_model = self._normalize_model_slug(model)
        payload = {
            'model': normalized_model,
            'messages': messages,
            'temperature': temperature,
        }

        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                f'{self.base_url}/chat/completions',
                headers=self.headers,
                json=payload,
            )
            response.raise_for_status()
            data = response.json()

        return data['choices'][0]['message']['content']

    @staticmethod
    def _normalize_model_slug(model: str) -> str:
        model = model.strip()
        if '/' in model:
            return model
        return f'openai/{model}'
