"""Configuration management"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    # Database
    database_url: str = "sqlite:///./modelgate.db"

    # Security
    secret_key: str = "dev-secret-change-in-production"
    
    # CORS
    cors_origins: str = "http://localhost:3000"
    
    # Demo mode
    demo_mode: bool = True
    
    # Server
    host: str = "0.0.0.0"
    port: int = 8000
    reload: bool = True
    
    # Provider credentials
    openai_api_key: str = ""
    anthropic_api_key: str = ""

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


settings = Settings()
