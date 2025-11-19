import os
from dotenv import load_dotenv
load_dotenv()


class Config:
    IMMICH_API_KEY = os.getenv("IMMICH_API_KEY")
    IMMICH_BASE_URL = os.getenv("IMMICH_URL")
    JOURNIV_BASE_URL = os.getenv("JOURNIV_URL")
    JOURNIV_EMAIL = os.getenv("JOURNIV_EMAIL")
    JOURNIV_PASSWORD = os.getenv("JOURNIV_PASSWORD")
    JOURNIV_JOURNAL_NAME = os.getenv("JOURNIV_JOURNAL_NAME")