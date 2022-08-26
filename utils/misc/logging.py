from pathlib import Path
from loguru import logger

logger.add(f'{Path(__file__).absolute().parent.parent.parent}/data/logs/log.out', format='[{level}]-[{time}]-[{message}]', level='DEBUG', rotation='1 day')
