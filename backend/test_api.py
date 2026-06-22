import os

# pyrefly: ignore [missing-import]
from dotenv import load_dotenv

load_dotenv()

print(
os.getenv(
"GOOGLE_API_KEY"
)
)
