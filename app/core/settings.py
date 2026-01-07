import os
from dotenv import load_dotenv
from pydantic import BaseModel

# Load environment variables for app runtime
load_dotenv()

class Settings(BaseModel):
    polygon_api_key: str = os.getenv("POLYGON_API_KEY", "")
    database_url: str = os.getenv("DATABASE_URL", "")
    tz: str = os.getenv("TZ", "America/New_York")

# Renamed to avoid Alembic/import issues
app_settings = Settings()

# Polygon key is OPTIONAL (stage 1)
if not app_settings.polygon_api_key or app_settings.polygon_api_key.startswith("DUMMY"):
    print("⚠️ Polygon API key not set yet — ingestion disabled")

# ❗ IMPORTANT:
# Do NOT raise RuntimeError here.
# DB validation must happen at application startup, not import time.
