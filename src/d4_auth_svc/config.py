import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///:memory:")
SERVICE_PORT = os.getenv("SERVICE_PORT", 8000)

# Configuration for external email service integration
EMAIL_SERVICE_URL = os.getenv("EMAIL_SERVICE_URL")
EMAIL_API_KEY = os.getenv("EMAIL_API_KEY")
