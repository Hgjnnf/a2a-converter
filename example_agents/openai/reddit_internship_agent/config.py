import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OpenAIClient = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY")
)

# 2) Reddit API credentials (PRAW)
REDDIT_CLIENT_ID     = os.getenv("REDDIT_CLIENT_ID")  # Set via environment :contentReference[oaicite:1]{index=1}
REDDIT_CLIENT_SECRET = os.getenv("REDDIT_CLIENT_SECRET")  # Set via environment :contentReference[oaicite:2]{index=2}
REDDIT_USER_AGENT    = "internDB_reddit_agent/1.0"

# 4) Default Subreddits to Search
DEFAULT_SUBREDDITS = ["internships", "cscareerquestions", "csMajors"]

# 5) Default lookback window (in days) for Pushshift queries
DEFAULT_DAYS_BACK = 180

# 6) Output File Path (where parsed records are written)
OUTPUT_FILE_PATH = "results.txt"
