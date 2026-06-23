import logging.config
from dataclasses import dataclass
from typing import Optional, Dict, Any

DAILY_TRANSFER_LIMIT = 100_000.00  
P2P_TRANSFER_FEE_PERCENT = 0.005  
MIN_ACCOUNT_BALANCE = 0.0        

LOGGING_CONFIG: Dict[str, Any] = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s %(context)s : %(message)s"
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
            "level": "INFO",
        },
    },
}