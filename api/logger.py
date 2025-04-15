import logging
from logging.handlers import RotatingFileHandler
import os

# Diretório e arquivo de log
LOG_DIR = "logs"
LOG_FILE = "app.log"
os.makedirs(LOG_DIR, exist_ok=True)
log_path = os.path.join(LOG_DIR, LOG_FILE)

# Formato dos logs
formatter = logging.Formatter(
    fmt="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)

# Handler com rotação de 1MB e até 5 arquivos antigos
file_handler = RotatingFileHandler(log_path, maxBytes=1_000_000, backupCount=5)
file_handler.setFormatter(formatter)

# Logger principal da aplicação
logger = logging.getLogger("simulator_api")
logger.setLevel(logging.INFO)
logger.addHandler(file_handler)

# Loggers do FastAPI e Uvicorn
uvicorn_loggers = ("uvicorn", "uvicorn.error", "uvicorn.access", "fastapi")

for name in uvicorn_loggers:
    uv_logger = logging.getLogger(name)
    uv_logger.setLevel(logging.INFO)
    uv_logger.addHandler(file_handler)

# Evita que logs sejam duplicados no terminal se uvicorn já estiver lidando com eles
logger.propagate = False
