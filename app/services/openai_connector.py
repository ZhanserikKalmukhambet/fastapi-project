import httpx
from app.core.config import get_settings

settings = get_settings()


class OpenRouterConnector:
    def __init__(self):
        self.base_url = settings.OPENROUTER_BASE_URL

        self.api_key = settings.OPENROUTER_API_KEY

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def create_chat_completion(self, content: str, model: str = "openai/gpt-3.5-turbo", role: str = "user"):
        data = {
            "model": model,
            "messages": [
                {"role": role, "content": content}
            ]
        }

        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(self.base_url, json=data, headers=self.headers)
                response.raise_for_status()  

                response_data = response.json()  

                return response_data['choices'][0]['message']['content']
            
            except httpx.HTTPStatusError as e:
                return f"HTTP error occurred: {e}"
            
            except Exception as e:
                return f"An error occurred: {e}"