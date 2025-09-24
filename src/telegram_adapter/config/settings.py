"""Settings for project Telegram Adapter"""

import os
from enum import Enum

from pydantic import Field
from pydantic_settings import BaseSettings

env_file: str = f".env.{os.getenv('APP_ENV', 'dev')}"


# Enum for allowed APP_ENV values
class AppEnvEnum(str, Enum):
    DEV = "dev"
    PROD = "prod"
    STAGING = "staging"


class Settings(BaseSettings):
    """Settings for the database service."""

    # Fixed fields
    FIXED_VAR: str = "fixed_value"
    # Fields loaded from environment variables
    TELEGRAM_BOT_TOKEN: str
    TELEGRAM_USER1_ID: int
    TELEGRAM_USER2_ID: int
    app_env: AppEnvEnum = Field(
        default=AppEnvEnum.DEV
    )  # Field is necessary for pytest in Docker
    root_dir: str = Field(
        default=os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
    )  # Root directory of the project

    # File upload settings
    upload_dir: str = Field(default="tmp_upload")
    max_file_size_mb: int = Field(default=20)
    allowed_file_extensions: str = Field(default=".csv,.xls,.xlsx,.pdf")

    model_config = {
        "env_file": env_file,
        "env_file_encoding": "utf-8",
    }

    @property
    def log_level(self) -> str:
        """Return the log level depending on the environment."""
        if self.app_env == AppEnvEnum.PROD:
            return "INFO"
        else:
            return "DEBUG"

    @property
    def allowed_ids(self) -> list[int]:
        """Return a list of allowed IDs."""
        return [self.TELEGRAM_USER1_ID, self.TELEGRAM_USER2_ID]

    @property
    def max_file_size_bytes(self) -> int:
        """Return the maximum file size in bytes."""
        return self.max_file_size_mb * 1024 * 1024

    @property
    def allowed_extensions_set(self) -> set[str]:
        """Return a set of allowed file extensions."""
        return {ext.strip().lower() for ext in self.allowed_file_extensions.split(",")}

    @property
    def upload_dir_path(self) -> str:
        """Return the full path to the upload directory based on root_dir."""
        return os.path.join(self.root_dir, self.upload_dir)


settings = Settings()  # type: ignore


if __name__ == "__main__":
    print("Configuration:")
    print(f"Environment: {settings.app_env.value}")
    print(f"Log Level: {settings.log_level}")
