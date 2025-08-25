from pydantic_settings import BaseSettings, SettingsConfigDict
# from pydantic import SecretStr
# from pathlib import Path

class Settings(BaseSettings):
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASS: str
    DB_NAME: str
    # SECRET_KEY: SecretStr
    # DEBUG: bool = False

    @property
    def db_url(self):
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASS}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()