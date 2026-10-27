import os
from pathlib import Path
from dotenv import load_dotenv

BACKEND_DIR = Path(__file__).resolve().parent.parent.parent
env_path = BACKEND_DIR / ".env"
load_dotenv(dotenv_path=env_path)

class Settings:
    @property
    def postgres_user(self) -> str:
        return os.getenv("POSTGRES_USER", "scraper_user")
    
    @property
    def postgres_password(self) -> str:
        return os.getenv("POSTGRES_PASSWORD", "change_this_to_a_strong_password")
    
    @property
    def postgres_db(self) -> str:
        return os.getenv("POSTGRES_DB", "scraper_db")
    
    @property
    def database_url(self) -> str:
        url = os.getenv("DATABASE_URL")
        if not url:
            ssl_mode = os.getenv("DATABASE_SSL_MODE", "prefer")
            url = f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@localhost:5432/{self.postgres_db}?ssl={ssl_mode}"
        return url
    
    @property
    def proxy_list(self) -> list:
        proxies_str = os.getenv("PROXY_LIST", "")
        if not proxies_str:
            return []
        return [p.strip() for p in proxies_str.split(",") if p.strip()]
    
    @property
    def gemini_api_key(self) -> str:
        return os.getenv("GEMINI_API_KEY", "")
    
    @property
    def curation_batch_size(self) -> int:
        try:
            return int(os.getenv("CURATION_BATCH_SIZE", "10"))
        except ValueError:
            return 10
            
    @property
    def curation_rate_limit_delay(self) -> float:
        try:
            return float(os.getenv("CURATION_RATE_LIMIT_DELAY", "1.0"))
        except ValueError:
            return 1.0
    
    @property
    def api_key(self) -> str:
        return os.getenv("API_KEY", "")
    
    @property
    def allowed_origins(self) -> list:
        origins_str = os.getenv("ALLOWED_ORIGINS", "")
        if not origins_str:
            return []
        return [origin.strip() for origin in origins_str.split(",") if origin.strip()]
    
    @property
    def environment(self) -> str:
        return os.getenv("ENVIRONMENT", "development")
    
    @property
    def enable_docs(self) -> bool:
        return self.environment.lower() == "development"

settings = Settings()
