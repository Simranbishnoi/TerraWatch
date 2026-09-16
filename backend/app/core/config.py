import os

from dotenv import load_dotenv

load_dotenv()


class Settings:
    PROJECT_NAME = "TerraWatch API"
    VERSION = "1.0.0"

    DATABASE_URL = os.getenv("DATABASE_URL")

    SECRET_KEY = os.getenv("SECRET_KEY")
    ALGORITHM = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES = int(
        os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
    )

    UPLOAD_DIR = "data/raw"
    REPORT_DIR = "reports/generated"


settings = Settings()