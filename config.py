from functools import lru_cache
from typing import Optional

from pydantic import BaseSettings, PostgresDsn, Field


class GlobalConfig(BaseSettings):
    DEBUG: bool = False
    API_V1_STR: str = "/api/v1"
    DATABASE_URL: PostgresDsn = Field(env="DATABASE_URL")
    ENVIRONMENT: str = Field(env="ENVIRONMENT", default="DEV")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevConfig(GlobalConfig):
    DEBUG = True


class TestingConfig(GlobalConfig):
    DEBUG = True
    TESTING = True


class FactoryConfig:
    """Returns a config instance depends on the ENV_STATE variable."""

    def __init__(self, environment: Optional[str] = "DEV"):
        self.environment = environment

    def __call__(self):
        if self.environment == "TEST":
            return TestConfig()
        return DevConfig()


@lru_cache()
def get_configuration():
    return FactoryConfig(GlobalConfig().ENVIRONMENT)()


settings = get_configuration()
