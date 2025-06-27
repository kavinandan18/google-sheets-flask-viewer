import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # GOOGLE_SHEET_ID is optional since it will come from user input
    GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID", "")
    CREDENTIALS_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "credentials.json")
    LOG_FILE = os.path.join(os.path.dirname(__file__), "../logs/app.log")

    @staticmethod
    def validate(credentials_path=None):
        """Validate configuration settings."""
        if credentials_path and not os.path.exists(credentials_path):
            raise FileNotFoundError(f"Credentials file not found at: {credentials_path}")
        if credentials_path and os.path.getsize(credentials_path) == 0:
            raise ValueError(f"Credentials file at {credentials_path} is empty")