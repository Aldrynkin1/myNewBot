from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

class Settings(BaseSettings):
    app_name: str = 'Anonimous Bot'
    debug: bool = True
    database_url: str = Field(default=...)
    bot_token: str = Field(default=...) 
    
    cors_origins: list = [
        'http://localhost:5173',
        'http://localhost:3000',
        'http://127.0.0.1:5173',
        'http://127.0.0.1:3000',
    ]
    
    static_dir: str = "static"
    images_dir: str = "static/images"

    model_config = SettingsConfigDict(
        env_file=".env",
        case_sensitive=False,
        extra="ignore"
    )

settings = Settings()