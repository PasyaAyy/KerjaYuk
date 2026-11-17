"""Database migration helpers shared by the API startup and demo seed command."""

from pathlib import Path

from alembic import command
from alembic.config import Config
from sqlalchemy.engine import Engine


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def upgrade_database(engine: Engine) -> None:
    """Upgrade the connected database to the newest checked-in migration."""
    config = Config(str(PROJECT_ROOT / "alembic.ini"))
    config.set_main_option("script_location", str(PROJECT_ROOT / "migrations"))
    with engine.begin() as connection:
        config.attributes["connection"] = connection
        command.upgrade(config, "head")
