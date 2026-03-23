from __future__ import annotations

import asyncio
import json
from datetime import datetime, timezone
from pathlib import Path


class DailyRequestLimiter:
    def __init__(self, file_path: Path, daily_limit: int = 10):
        self.file_path = file_path
        self.daily_limit = daily_limit
        self._lock = asyncio.Lock()

    async def allow_request(self, user_id: int) -> bool:
        async with self._lock:
            payload = await self._load_payload()
            today = datetime.now(timezone.utc).date().isoformat()
            user_key = str(user_id)
            user_state = payload.get(user_key)

            if user_state is None or user_state.get('date') != today:
                payload[user_key] = {'date': today, 'count': 1}
                await self._save_payload(payload)
                return True

            count = int(user_state.get('count', 0))
            if count >= self.daily_limit:
                return False

            user_state['count'] = count + 1
            payload[user_key] = user_state
            await self._save_payload(payload)
            return True

    async def _load_payload(self) -> dict[str, dict[str, int | str]]:
        if not self.file_path.exists():
            return {}

        try:
            content = await asyncio.to_thread(self.file_path.read_text, encoding='utf-8')
            data = json.loads(content)
        except (OSError, json.JSONDecodeError):
            return {}

        if isinstance(data, dict):
            return data
        return {}

    async def _save_payload(self, payload: dict[str, dict[str, int | str]]) -> None:
        await asyncio.to_thread(self.file_path.parent.mkdir, parents=True, exist_ok=True)
        serialized = json.dumps(payload, ensure_ascii=False, indent=2)
        await asyncio.to_thread(self.file_path.write_text, serialized, encoding='utf-8')
