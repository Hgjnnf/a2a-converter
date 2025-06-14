
import asyncio
from agent import cooking_agent
from agents import Runner, trace, ItemHelpers
import logging
import json

logger = logging.getLogger(__name__)
if not logger.hasHandlers():
    logging.basicConfig(level=logging.INFO)


async def main():
    recipe = "Pad Thai"
    # Initial user prompt
    user_message = [{
        "role": "user",
        "content": f"Let's cook **{recipe}**. Walk me through each step."
    }]

    print(f"🧑‍🍳 Starting interactive cooking guide for {recipe}...\n")

    # Wrap in a trace for visibility (optional)
    with trace("Cooking Workflow"):
        try:
            response = {
                "status": "",
                "message": ""
            }

            while response["status"] != "completed":
                stream = Runner.run_streamed(
                    cooking_agent,
                    user_message,
                    max_turns=100
                )

                async for event in stream.stream_events():
                    if event.type == "raw_response_event":
                        continue
                    # When the agent updates, print that
                    elif event.type == "agent_updated_stream_event":
                        print(f"Agent updated: {event.new_agent.name}")
                        continue
                    # When items are generated, print them
                    elif event.type == "run_item_stream_event":
                        if event.item.type == "tool_call_item":
                            print("-- Tool was called")
                        elif event.item.type == "tool_call_output_item":
                            print(f"-- Tool output: {event.item.output}")
                        elif event.item.type == "message_output_item":
                            print(f"-- Message output:\n {ItemHelpers.text_message_output(event.item)}")
                            raw = ItemHelpers.text_message_output(event.item)
                            response = json.loads(raw)
                        else:
                            pass  # Ignore other event types
                
                if response["status"] == "error":
                    raise Exception(response["message"])
                elif response["status"] == "input_required":
                    user_input = input("> ").strip()
                    user_message = stream.to_input_list() + [{"role": "user", "content": user_input}]
        except Exception as e:
            logger.error(
                f"Exception caught in Cooking Agent Streaming: {type(e).__name__} - {e}",
                exc_info=True,
            )
            return

    print("\n✅ Cooking session complete!")

if __name__ == "__main__":
    asyncio.run(main())
