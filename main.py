import uvicorn
from alembic import command
from alembic.config import Config

from src.config.settings import settings


def main():
    alembic_cfg = Config("alembic.ini")
    command.upgrade(alembic_cfg, "head")

    uvicorn.run(
        app="src.app:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.debug
    )


if __name__ == "__main__":
    main()