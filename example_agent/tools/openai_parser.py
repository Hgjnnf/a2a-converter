import json
from typing import List, Dict, Any
from config import OpenAIClient
from agents import function_tool
from pydantic import BaseModel
from concurrent.futures import ThreadPoolExecutor, as_completed

class RedditPost(BaseModel):
    post_id: str
    title: str
    body: str
    author: str | None
    created_utc: float
    url: str
    subreddit: str
    score: int
    num_comments: int

@function_tool
def openai_parse_tool(posts: List[RedditPost]) -> List[Dict[str, Any]]:
    """
    Given a list of Reddit post dicts, extract structured internship details for each post.

    For each post in `posts`, this function:
      1. Constructs a prompt including the post's title and body.
      2. Calls the OpenAI chat completion endpoint (model: gpt-4o-mini, temperature=0.0).
      3. Parses the LLM's response as JSON with these required fields:
         - post_id, author, created_utc, subreddit, url
         - company, role, steps (list of strings), timeline (dict of YYYY-MM-DD strings), additional_notes
         - original_title, original_body
      4. On JSON parse error, returns a fallback dict containing the original post metadata,
         plus `parsing_error` and `raw_response` for manual inspection.

    Args:
        posts: A list of RedditPost instances.

    Returns:
        A list of dictionaries, each representing the structured data for one post.
    """
    def parse_one(post: RedditPost) -> Dict[str, Any]:
        prompt = f"""
Extract structured internship process data from the following Reddit post.

Required fields (output exactly as valid JSON):
- post_id
- author
- created_utc
- subreddit
- url
- company         (e.g., "Google", "Amazon")
- role            (e.g., "Software Engineering Intern")
- steps           (array of interview stages in order)
- timeline        (object with keys like "applied", "heard_back" in YYYY-MM-DD format)
- additional_notes (string with any extra details: stipend, coding challenge info, tips)
- original_title
- original_body

Post Title:
\"\"\"{post.title}\"\"\"

Post Body:
\"\"\"{post.body}\"\"\"
"""
        resp = OpenAIClient.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You extract internship process details into JSON."},
                {"role": "user",   "content": prompt}
            ],
            temperature=0.0,
            max_tokens=1500
        )
        content = resp.choices[0].message.content.strip()
        try:
            return json.loads(content)
        except json.JSONDecodeError as e:
            return {
                "post_id":          post.post_id,
                "author":           post.author,
                "created_utc":      post.created_utc,
                "subreddit":        post.subreddit,
                "url":              post.url,
                "company":          None,
                "role":             None,
                "steps":            [],
                "timeline":         {},
                "additional_notes": None,
                "original_title":   post.title,
                "original_body":    post.body,
                "parsing_error":    str(e),
                "raw_response":     content
            }

    output: List[Dict[str, Any]] = []
    # Choose a reasonable number of threads (e.g., up to 8)
    max_workers = min(10, len(posts))

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit all parse tasks
        futures = {executor.submit(parse_one, post): post for post in posts}
        for future in as_completed(futures):
            try:
                result = future.result()
            except Exception as exc:
                # In case one thread crashes, capture the error per-post
                post = futures[future]
                output.append({
                    "post_id": post.post_id,
                    "parsing_error": f"thread error: {exc}"
                })
            else:
                output.append(result)

    return output
