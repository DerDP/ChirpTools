import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file if not production
if os.environ.get("ENV") != "production":
    load_dotenv()

class Config(BaseSettings):
    CHIRP_URL: str = os.getenv("CHIRP_URL")
    CHIRP_TENANT: str = os.getenv("CHIRP_TENANT")
    CHIRP_API_KEY: str = os.getenv("CHIRP_API_KEY")
    SNIPE_URL: str = os.getenv("SNIPE_URL")
    SNIPE_API_KEY: str = os.getenv("SNIPE_API_KEY")
    TITLE: str = os.getenv("TITLE", "ChirpTools")
config = Config()