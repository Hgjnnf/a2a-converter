from agents import Agent, ModelSettings
from tools.reddit_fetcher import (
    generate_search_phrases,
    praw_search_tool
)
from tools.openai_parser import openai_parse_tool
from tools.write_tool import write_to_file_tool

# 1) Model settings: Use GPT-4 o-mini, deterministic parsing
model_settings = ModelSettings(
    temperature=0.0,
    max_tokens=10_000
)

# 2) System instructions: guide the agent to use PRAW
instructions = """
You are the InternDB Reddit Agent. When given a topic, you should:
1) Call generate_search_phrases(topic) to get varied search queries.
2) Call praw_search_tool(queries, subreddits, limit_per_query) to fetch matching posts from Reddit.
3) Once all the posts are returned from praw_search_tool, call openai_parse_tool(post) to extract structured information from post and put them in a list.
4) Pass the output from openai_parse_tool(post) to and call write_to_file_tool(parsed_posts) to append results to a local text file.
5) Finally, return a summary of how many records were written.
Do not include any explanation. The final output will be in JSON format.
"""

# 3) Instantiate the Agent with PRAW-based search
intern_agent = Agent(
    model="gpt-4o-mini",
    name="InternDB Reddit Agent",
    instructions=instructions,
    tools=[
        generate_search_phrases,
        praw_search_tool,
        openai_parse_tool,
        write_to_file_tool
    ],
    model_settings=model_settings
)
