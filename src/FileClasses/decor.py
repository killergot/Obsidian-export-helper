import logging
from functools import wraps
from collections.abc import Callable

log = logging.getLogger(__name__)


def except_catch(method: Callable) -> Callable:
    """Простой декоратор для отлавливания ошибок, что-бы сама программа не падала"""

    @wraps(method)
    def wrapper(self, *args, **kwargs):
        try:
            result = method(self, *args, **kwargs)
            return result
        except Exception:
            log.exception(f"Что-то пошло не так при исполнении {method.__name__}")
            return None

    return wrapper
