from threading import Lock
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

class MessageLogger(Logger):
    """
    Custom logger class that extends loguru's Logger.
    This class can be used to log messages with a specific format.
    """
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
        # self.remove(0)
        self.add(
            "logs/messages/{time:YYYY-MM-DD}.log",
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

