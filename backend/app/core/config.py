import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "TerraWatch API"
    VERSION = "1.0.0"

    DATABASE_URL = os.getenv("DATABASE_URL")

    UPLOAD_DIR = "data/raw"
    REPORT_DIR = "reports/generated"


settings = Settings()