import logging
import os
import sys
from logging.handlers import RotatingFileHandler

# Ensure logs directory exists
LOG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'logs'))
os.makedirs(LOG_DIR, exist_ok=True)

LOG_FILE = os.path.join(LOG_DIR, 'app.log')

# Unified formatter
formatter = logging.Formatter('%(asctime)s | %(levelname)s | %(name)s | %(message)s')

# File handler with rotation
file_handler = RotatingFileHandler(
    LOG_FILE,
    maxBytes=10 * 1024 * 1024,  # 10 MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(formatter)

# Stream handler for console visibility
console_handler = logging.StreamHandler(sys.stdout)
console_handler.setFormatter(formatter)

# Principal Logger Configuration
logger = logging.getLogger('apibinance2026')
logger.setLevel(logging.DEBUG)
logger.addHandler(file_handler)
logger.addHandler(console_handler)
logger.propagate = False

# Ensure root logs go to our file too (optional, but helps capture 3rd party issues)
# logging.getLogger().addHandler(file_handler)

# Export logger
__all__ = ['logger']
