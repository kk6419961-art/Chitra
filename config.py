from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Chitra API"
    database_url: str = "sqlite:///./chitra.db"
    jwt_secret: str = "development-only-change-me"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 30
    admin_email: str = "admin@chitra.local"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 500
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
