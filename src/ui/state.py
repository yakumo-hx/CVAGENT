from __future__ import annotations

from dotenv import find_dotenv, load_dotenv


def load_env_without_echo() -> None:
    env_path = find_dotenv(usecwd=True)
    if env_path:
        load_dotenv(env_path, override=False)
