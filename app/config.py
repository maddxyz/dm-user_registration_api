from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    email_service: str = "console"

    model_config = {"env_file": ".env"}


settings = Settings()
