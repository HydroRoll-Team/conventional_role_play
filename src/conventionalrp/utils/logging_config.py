import logging
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime


def setup_logging(
    level: str = "INFO",
    log_file: Optional[str] = None,
    format_string: Optional[str] = None,
    include_timestamp: bool = True,
    include_module: bool = True
) -> logging.Logger:
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    if format_string is None:
        parts = []
        if include_timestamp:
            parts.append("%(asctime)s")
        parts.append("[%(levelname)s]")
        if include_module:
            parts.append("%(name)s")
        parts.append("%(message)s")
        format_string = " - ".join(parts)
    
    logging.basicConfig(
        level=log_level,
        format=format_string,
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[]
    )
    
    logger = logging.getLogger("conventionalrp")
    logger.setLevel(log_level)
    
    logger.handlers.clear()
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    console_formatter = logging.Formatter(format_string, datefmt="%Y-%m-%d %H:%M:%S")
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(log_level)
        file_handler.setFormatter(console_formatter)
        logger.addHandler(file_handler)
        
        logger.info(f"Logging to file: {log_file}")
    
    logger.info(f"Logging configured at {level} level")
    return logger


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"conventionalrp.{name}")


class LogContext:
    def __init__(self, logger: logging.Logger, level: str):
        self.logger = logger
        self.level = getattr(logging, level.upper())
        self.original_level = None
    
    def __enter__(self):
        self.original_level = self.logger.level
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.logger.setLevel(self.original_level)
        return False
