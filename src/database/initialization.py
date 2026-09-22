"""Database initialization utility."""

from src.database.session import init_db
from src.logging_config import logger

if __name__ == "__main__":
    logger.info("Running standalone database initialization...")
    init_db()
    logger.info("Standalone initialization completed.")
