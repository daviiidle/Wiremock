"""Environment configuration helper."""

import os
from typing import Optional
from dotenv import load_dotenv


def load_env_config() -> None:
    """Load environment variables from .env file."""
    load_dotenv()


def get_base_url() -> str:
    """Get the base URL for the WireMock server."""
    return os.getenv('BASE_URL', 'http://localhost:8080')


def get_port() -> int:
    """Get the port for the WireMock server."""
    return int(os.getenv('PORT', '8080'))


def get_env_var(name: str, default: Optional[str] = None) -> str:
    """Get environment variable with optional default."""
    value = os.getenv(name, default)
    if value is None:
        raise ValueError(f"Environment variable '{name}' is required")
    return value