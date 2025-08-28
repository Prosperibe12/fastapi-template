"""Logging configuration for the FastAPI application."""
from loguru import logger
from rich.console import Console
from rich.theme import Theme

custom_theme = Theme({
    "info": "bold cyan",
    "warning": "bold yellow",
    "error": "bold red",
    "debug": "dim green",
    "success": "bold green"
})

console = Console(theme=custom_theme, record=True)

def setup_logging():
    """configure the logging settings for the application."""
    logger.remove()

    logger.add(
        sink=console.print,
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level} | {name}:{function}:{line} - {message}",
        colorize=True,
        backtrace=True,
        diagnose=True,
        enqueue=True
    )

    logger.add(
        "logs/app_logs.log",
        level="INFO",
        rotation="50MB",
        compression="zip",
        retention="7 days",
        enqueue=True,
        backtrace=True,
        diagnose=True
    )

    logger.add(
        "logs/error_logs.log",
        level="ERROR",
        rotation="50 MB",  # same logic
        retention="90 days",
        compression="zip",
        backtrace=True,
        diagnose=True,
        enqueue=True
    )
