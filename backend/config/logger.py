from threading import Lock
from fastapi import HTTPException
from functools import wraps
from typing import Any
from datetime import timezone
import json
from loguru._logger import Logger, Core

def serialize(record):
    subset = {
        "timestamp": record["time"].astimezone(timezone.utc).isoformat('T').replace("+00:00", "") + 'Z',
        "message": record["message"],
        "data": record.get("extra", {}).get("data", {}),
    }
    return json.dumps(subset)

def formatter(record):
    record["extra"]["serialized"] = serialize(record)
    return "{extra[serialized]}\n"

class AppLogger(Logger):
    """
    Custom logger class that extends loguru's Logger.
    This class can be used to log messages with a specific format.
    """
    NAME = "app"

    _instance = None
    _lock = Lock()

    def __init__(self):
        super().__init__(
            core=Core(),
            exception=None,
            depth=0,
            record=False,
            lazy=False,
            colors=False,
            raw=False,
            capture=True,
            patchers=[],
            extra={}
        )
        self.add(
            f"logs/{self.NAME}/{{time:YYYY-MM-DD}}.log",
            rotation="1 day",
            retention="30 days",
            compression="zip",
            level="TRACE",
            format=formatter,
        )

    @classmethod
    def get_instance(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance

    @classmethod
    def log(cls, message, data: Any = None):
        """
        Log a message at the TRACE level.
        """
        cls.get_instance().trace(message, data=data)

def log_route_handler(Logger: type[AppLogger], action: str):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            data = {
                "args": [str(arg) for arg in args],
                "kwargs": {k: str(v) for k, v in kwargs.items()},
            }

            try:
                response = await func(*args, **kwargs)

                data["response"] = response.model_dump(mode="json") if hasattr(response, "model_dump") else response
                Logger.log(
                    action,
                    data = data,
                )
                return response
            except Exception as e:
                data["error"] = e.model_dump(mode="json") if hasattr(e, "model_dump") else str(e)

                Logger.log(
                    f"Error during {action}",
                    data = data,
                )

                raise e
        return wrapper
    return decorator

class MessageLogger(AppLogger):
    NAME = "message"

    def __init__(self):
        super().__init__()

class OperatorInputLogger(AppLogger):
    NAME = "operator_input"

    def __init__(self):
        super().__init__()

class OperatorNotificationLogger(AppLogger):
    NAME = "operator_notification"

    def __init__(self):
        super().__init__()

class PlanningAttemptLogger(AppLogger):
    NAME = "planning_attempt"

    def __init__(self):
        super().__init__()
