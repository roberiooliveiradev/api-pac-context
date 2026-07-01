import os

from dotenv import load_dotenv

load_dotenv()


def _get_env(*names: str, default=None):
    for name in names:
        value = os.getenv(name)
        if value is not None and value != "":
            return value
    return default


class Settings:
    PORT: str = _get_env("API_PAC_CONTEXT_PORT", "PORT", default="8011")
    API_ENV: str = _get_env("API_PAC_CONTEXT_ENV", default="development")
    LOG_LEVEL: str = _get_env("LOG_LEVEL", default="INFO")
    ROOT_PATH: str = _get_env("API_PAC_ROOT_PATH", default="")
    PUBLIC_BASE_URL: str | None = _get_env("PUBLIC_BASE_URL")
    PAC_CONTEXT_API_KEY: str | None = _get_env("PAC_CONTEXT_API_KEY")

    API_DELPI_BASE_URL: str | None = _get_env("API_DELPI_BASE_URL")
    API_DELPI_INTERNAL_SERVICE_TOKEN: str | None = _get_env("API_DELPI_INTERNAL_SERVICE_TOKEN")
    API_DELPI_TIMEOUT_SECONDS: float = float(
        _get_env("API_DELPI_TIMEOUT_SECONDS", default="60") or "60"
    )


settings = Settings()
