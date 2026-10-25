from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    catalogue_url: str = "http://catalogue:8000"
    upstream_timeout_seconds: float = 30.0
