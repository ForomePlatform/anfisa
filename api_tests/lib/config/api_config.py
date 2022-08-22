import os
from dataclasses import dataclass
from pathlib import Path
from dotenv import load_dotenv

config_dir = Path(__file__).parent.parent.parent
dotenv_file = config_dir / ".env"

load_dotenv(dotenv_file)

@dataclass
class ApiConfig:
    base_url: str = os.getenv("BASE_URL")