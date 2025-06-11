from agent import intern_agent
from agents import Runner
from openai.types.responses import ResponseTextDeltaEvent

class a2aAgentWrapper:
    def __init__(self):
        self.agent = intern_agent

    async def invoke(self, query, sessionId):
        try:
            result = await Runner.run(
                self.agent, 
                [{"role": "user", "content": query}]
            )
            return {
                "task_state": "completed",
                "content": result.final_output
            }
        except Exception as e:
            return {
                "task_state": "failed",
                "content": f"An error occurred: {str(e)}"
            }

    async def stream(self, query, sessionId):
        try:
            result = Runner.run_streamed(
                self.agent,
                [{"role": "user", "content": query}]
            )
            async for event in result.stream_events():
                if event.type == "raw_response_event" and isinstance(event.data, ResponseTextDeltaEvent):
                    delta = event.data.delta
                    if delta:
                        yield {
                            "task_state": "working",
                            "content": delta
                        }

            yield {
                "task_state": "completed",
                "content": result.final_output
            }

        except Exception as e:
            yield {
                "task_state": "failed",
                "content": f"Streaming error: {str(e)}"
            }

    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]
