from pydantic import BaseSettings

class Settings(BaseSettings):
    APP_NAME: str = "EMR Platform"
    DEBUG: bool = False

    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    POSTGRES_URL: str
    MONGO_URL: str
    REDIS_URL: str
    MONGO_DB_NAME: str = "emr_control_plane"
    OPENAI_API_KEY: str


    ENV: str = "development"

    class Config:
        env_file = ".env"

settings = Settings()