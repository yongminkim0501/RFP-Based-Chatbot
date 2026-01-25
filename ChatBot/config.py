from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    TAVILY_API_KEY : str
    OPENAI_API_KEY : str
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()