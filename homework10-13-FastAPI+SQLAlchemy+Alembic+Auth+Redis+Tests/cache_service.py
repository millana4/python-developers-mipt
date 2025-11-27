import redis
import json
import pickle
from typing import Any, Optional

class RedisCache:
    def __init__(self, host='localhost', port=6379, db=0, expire_time=300):
        self.redis_client = redis.Redis(host=host, port=port, db=db, decode_responses=True)
        self.expire_time = expire_time

    def get(self, key: str) -> Optional[Any]:
        """Получение данных из кеша"""
        try:
            data = self.redis_client.get(key)
            if data:
                return json.loads(data)
            return None
        except Exception:
            return None

    def set(self, key: str, value: Any) -> bool:
        """Сохранение данных в кеш"""
        try:
            self.redis_client.setex(key, self.expire_time, json.dumps(value))
            return True
        except Exception:
            return False

    def delete(self, key: str) -> bool:
        """Удаление данных из кеша"""
        try:
            self.redis_client.delete(key)
            return True
        except Exception:
            return False

    def delete_pattern(self, pattern: str) -> bool:
        """Удаление данных по паттерну"""
        try:
            keys = self.redis_client.keys(pattern)
            if keys:
                self.redis_client.delete(*keys)
            return True
        except Exception:
            return False

    def clear_all(self) -> bool:
        """Очистка всего кеша"""
        try:
            self.redis_client.flushdb()
            return True
        except Exception:
            return False

# Глобальный экземпляр кеша
cache = RedisCache()