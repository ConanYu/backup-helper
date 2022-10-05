import threading
from typing import Callable, Union


def _sync_wrapper(function: Callable, lock: threading.Lock = None) -> Callable:
    if lock is None:
        lock = threading.Lock()

    def call(*args, **kwargs):
        try:
            lock.acquire()
            return function(*args, **kwargs)
        finally:
            lock.release()

    call.__name__ = function.__name__
    return call


def sync(lock: Union[Callable, threading.Lock, None] = None) -> Callable:
    if callable(lock):
        return _sync_wrapper(lock)

    def wrapper(function: Callable) -> Callable:
        return _sync_wrapper(function, lock)

    return wrapper


__all__ = [
    'sync',
]
