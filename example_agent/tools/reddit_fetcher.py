import time
from typing import List, Dict, Any

import praw  # Python Reddit API Wrapper :contentReference[oaicite:4]{index=4}
from agents import function_tool  # Agents SDK decorator for registering tools :contentReference[oaicite:6]{index=6}

from config import (
    REDDIT_CLIENT_ID,
    REDDIT_CLIENT_SECRET,
    REDDIT_USER_AGENT,
    DEFAULT_SUBREDDITS,
    OpenAIClient
)
import json

# 2) Initialize PRAW client
reddit = praw.Reddit(
    client_id=REDDIT_CLIENT_ID,
    client_secret=REDDIT_CLIENT_SECRET,
    user_agent=REDDIT_USER_AGENT
)

@function_tool
def generate_search_phrases(topic: str, num_phrases: int = 8) -> List[str]:
    """
    Generate diverse search strings for a given 'topic' using OpenAI.
    Returns a list of strings representing possible Reddit search queries.
    """
    prompt = f"""
Given the topic: "{topic}", generate {num_phrases} distinct Reddit search queries
that a user might enter to find posts about this topic. Output as a JSON array of strings.
"""
    response = OpenAIClient.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "You generate diverse Reddit search queries."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=200
    )
    content = response.choices[0].message.content.strip()
    try:
        phrases = json.loads(content)
    except Exception:
        # Fallback: split lines if JSON parsing fails
        phrases = [line.strip().strip('"') for line in content.splitlines() if line.strip()]
    return phrases

@function_tool
def praw_search_tool(
    queries: List[str],
    subreddits: List[str] = DEFAULT_SUBREDDITS,
    limit_per_query: int = 10
) -> List[Dict[str, Any]]:
    """
    For each query string, search each subreddit via PRAW’s subreddit.search(), 
    retrieving up to 'limit_per_query' posts. Aggregate and dedupe by post_id.
    Returns a list of dicts with fields: post_id, title, body, author, created_utc, url, subreddit, score, num_comments.
    """
    all_posts: Dict[str, Dict[str, Any]] = {}

    for query in queries:
        for sub in subreddits:
            subreddit = reddit.subreddit(sub)
            try:
                # PRAW’s search() returns up to 100 items per call :contentReference[oaicite:7]{index=7}
                for submission in subreddit.search(query=query, sort="relevance", limit=limit_per_query):
                    pid = submission.id
                    if pid not in all_posts:
                        all_posts[pid] = {
                            "post_id": pid,
                            "title": submission.title,
                            "body": submission.selftext or "",
                            "author": submission.author.name if submission.author else None,
                            "created_utc": submission.created_utc,
                            "url": submission.url,
                            "subreddit": sub,
                            "score": submission.score,
                            "num_comments": submission.num_comments
                        }
                # Be polite to Reddit’s API: throttle ~1 request/sec to avoid HTTP 429 :contentReference[oaicite:8]{index=8}
                time.sleep(1)
            except Exception as e:
                # If Reddit API error (rate limit or otherwise), skip that subreddit/query
                print(f"PRAW search error for '{query}' in r/{sub}: {e}")
                continue

    output = list(all_posts.values())
    return output
