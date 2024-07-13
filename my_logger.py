from __future__ import annotations

import os
# os.environ["LOGURU_AUTOINIT"] = "False"

import logging
import loguru
from loguru import logger

try:
    logger.add("riki.log")
except Exception as e:
    logger.error(f"Failed to set up log handler: {e}")

