import asyncio
import logging
import random
from collections import defaultdict
from typing import Any, Dict, List, Optional

import httpx

# Абсолютный импорт
from config import config

logger = logging.getLogger(__name__)


class RateLimiter:
    def __init__(self):
        self.user_requests = defaultdict(list)

    def can_make_request(
        self, user_id: int, limit: int = 10, period: int = 3600
    ) -> bool:
        import time

        current_time = time.time()

        # Удаляем старые запросы
        self.user_requests[user_id] = [
            req_time
            for req_time in self.user_requests[user_id]
            if current_time - req_time < period
        ]

        if len(self.user_requests[user_id]) >= limit:
            return False

        self.user_requests[user_id].append(current_time)
        return True


class TarotAPI:
    def __init__(
        self, base_url: str = config.API_BASE_URL, timeout: int = config.API_TIMEOUT
    ):
        self.base_url = base_url
        self.timeout = timeout
        self.cards_cache = None
        self.cache_timestamp = 0
        self.cache_ttl = 300
        self.session = None

    async def get_session(self) -> httpx.AsyncClient:
        if self.session is None or self.session.is_closed:
            self.session = httpx.AsyncClient(timeout=self.timeout)
        return self.session

    async def close(self):
        if self.session:
            await self.session.aclose()

    async def get_cards(self) -> Optional[list]:
        current_time = asyncio.get_event_loop().time()

        if self.cards_cache and current_time - self.cache_timestamp < self.cache_ttl:
            return self.cards_cache

        try:
            client = await self.get_session()
            response = await client.get(f"{self.base_url}/api/cards/")
            response.raise_for_status()
            cards = response.json()

            self.cards_cache = cards
            self.cache_timestamp = current_time

            logger.info(f"Загружено {len(cards)} карт из API")
            return cards

        except Exception as e:
            logger.error(f"Ошибка при получении карт: {e}", exc_info=True)
            return None

    async def get_random_card(self) -> Optional[Dict[Any, Any]]:
        cards = await self.get_cards()
        return random.choice(cards) if cards else None

    async def register_user(
        self,
        user_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
    ) -> bool:
        try:
            data = {
                "telegram_id": user_id,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
            }

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/users/register/", json=data
                )
                return response.status_code in [201, 400]

        except Exception as e:
            logger.error(f"Ошибка регистрации пользователя {user_id}: {e}")
            return False

    async def save_user_request(self, user_id: int, request_text: str) -> bool:
        try:
            data = {"telegram_id": user_id, "request_text": request_text}

            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    f"{self.base_url}/api/users/requests/", json=data
                )
                return response.status_code == 201

        except Exception as e:
            logger.error(f"Ошибка сохранения запроса {user_id}: {e}")
            return False


# Создаем экземпляры здесь
tarot_api_instance = TarotAPI()
rate_limiter_instance = RateLimiter()
