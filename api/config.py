import os
from functools import lru_cache
from dotenv import load_dotenv

if os.getenv("ENVIRONMENT") != "production":
    load_dotenv()

class Settings:
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configurações do banco
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")  # localhost para dev, db para docker
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "simulator_db")

    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        case_sensitive = True

@lru_cache
def get_settings() -> Settings:
    return Settings()

if __name__ == "__main__":
    settings = get_settings()
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Database URL: {settings.DATABASE_URL}")