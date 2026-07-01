"""Logger de arquivo no mesmo padrão da api-delpi (app/utils/logger.py).

Escreve em `logs/ctx_YYYYMMDD.log` (relativo ao WORKDIR do container, `/app`)
e também no console (stdout) para o `docker logs` continuar funcionando.
"""

from __future__ import annotations

import logging
import os
import sys
from datetime import datetime

from app.config import settings

LOG_DIR = os.getenv("LOG_DIR", "logs")
os.makedirs(LOG_DIR, exist_ok=True)

_fmt = "%(asctime)s [%(levelname)s] %(name)s %(message)s"
_log_formatter = logging.Formatter(_fmt)

_level = getattr(logging, (settings.LOG_LEVEL or "INFO").upper(), logging.INFO)


def get_logger(name: str = "ctx") -> logging.Logger:
    logger = logging.getLogger(name)
    if logger.handlers:
        return logger

    logger.setLevel(_level)

    log_file = os.path.join(LOG_DIR, f"ctx_{datetime.now().strftime('%Y%m%d')}.log")
    try:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(_level)
        file_handler.setFormatter(_log_formatter)
        logger.addHandler(file_handler)
    except (OSError, PermissionError):
        pass

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.setLevel(_level)
    stream_handler.setFormatter(_log_formatter)
    logger.addHandler(stream_handler)

    logger.propagate = False
    return logger
