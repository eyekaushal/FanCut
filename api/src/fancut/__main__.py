"""Run the API locally: ``uv run fancut``."""

import uvicorn

from fancut.api.app import create_app
from fancut.config import get_settings


def main() -> None:
    settings = get_settings()
    uvicorn.run(create_app(settings), host=settings.host, port=settings.port)


if __name__ == "__main__":
    main()
