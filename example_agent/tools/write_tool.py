# tools/file_tools.py

import json
from typing import List, Any
from agents import function_tool  # Agents SDK decorator :contentReference[oaicite:20]{index=20}
from config import OUTPUT_FILE_PATH  # Path for output file

@function_tool(strict_mode=False)
def write_to_file_tool(parsed_posts: List[Any]) -> Any:
    """
    Write each parsed post (as JSON) into a local text file (OUTPUT_FILE_PATH), one JSON object per line.
    Returns a summary dict: { 'written_count': X }.
    """
    written = 0
    try:
        with open(OUTPUT_FILE_PATH, "a", encoding="utf-8") as f:
            for post in parsed_posts:
                # Dump as a compact JSON string and append newline
                f.write(json.dumps(post, ensure_ascii=False))
                f.write("\n")
                written += 1
    except Exception as e:
        return {"error": str(e)}
    return {"written_count": written}
