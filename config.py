from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DATABASE_URL: str

    # អានពី .env ក្នុង Folder ជាមួយគ្នាផ្ទាល់
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()