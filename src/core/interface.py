import aiohttp
import os
from typing import List, Dict, Any, Optional
from .config import load_config
from .utils import parse_number_list


class Interface:
    """
    Чистая обёртка над HTTP API LLM.
    Методы:
      - post_messages -> возвращает json ответа
      - extract_text -> получает content из ответов
      - get_composition -> список вероятностей каждой интенсии
    """

    def __init__(self, session: Optional[aiohttp.ClientSession] = None):
        cfg = load_config()
        llm = (cfg or {}).get('llm', {})

        api_key = llm.get('api_key') or os.getenv(llm.get('api_key_env', '')) or os.getenv('OPENAI_API_KEY')
        if not api_key:
            raise ValueError("LLM API key not found")

        provider = llm.get('provider', 'openai')

        base_defaults = {
            'openai': 'https://api.openai.com/v1',
            'openai_proxy': os.getenv('PROXY_OPENAI_URL')
        }

        api_base = llm.get('api_base') or base_defaults.get( provider) or 'https://api.openai.com/v1'
        self.api_base = api_base.rstrip('/')
        self.header = {'Authorization': f'Bearer {
            api_key}', 'Content-Type': 'application/json'}
        self.session = session
        self.model_chat = llm.get('model_chat', 'gpt-4o-mini')

    async def post_messages(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> Dict[str, Any]:
        body = {
            "model": model or self.model_chat,
            "messages": messages
        }
        sess = self.session or aiohttp.ClientSession()
        close_after = self.session is None
        try:
            async with sess.post(self.api_base + "/chat/completions", headers=self.header, json=body) as resp:
                resp.raise_for_status()
                return await resp.json()
        finally:
            if close_after:
                await sess.close()

    async def extract_text(self, messages: List[Dict[str, str]], model: Optional[str] = None) -> str:
        j = await self.post_messages(messages, model=model)
        try:
            return j["choices"][0]["message"]["content"]
        except Exception:
            return ""

    async def get_composition(self, intents: Dict[int, str], phrase: str, model: Optional[str] = None) -> Optional[List[float]]:
        """
        Небольшой helper, который формирует промпт для модели и парсит числа,
        но НЕ содержит логики переходов/интерпретации.
        """
        cat_str = ', '.join(intents.values())
        num = len(intents)
        system = f"""You are a mechanism for determining probabilities of each intention in the given sentence.
                    Output {num} numbers between 0 and 1 separated by commas, corresponding to: {cat_str}
                    Sentence: "{phrase}"
                    Only output numbers separated by commas."""
        messages = [{"role": "user", "content": system}]
        text = await self.extract_text(messages, model=model)
        nums = parse_number_list(text)
        if not nums:
            # fallback: zeros
            return [0.0]*num
        # ensure length
        if len(nums) < num:
            nums += [0.0]*(num-len(nums))
        return [float(x) for x in nums[:num]]
