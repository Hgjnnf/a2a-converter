import logging
import click
import asyncio
import uvicorn

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events.event_queue import EventQueue
from a2a.utils import new_task
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import (
    AgentCard,
    AgentCapabilities,
    AgentSkill
)

from a2a_agent_wrapper import a2aAgentWrapper
import task_handler

logger = logging.getLogger(__name__)

class a2aAgentExecutor(AgentExecutor):
    """Generic A2A Executor using a2aAgentWrapper + task_handler."""

    def __init__(self):
        super().__init__()
        self.agent = a2aAgentWrapper()

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # 1) Extract user query and existing task (if any)
        query = context.get_user_input()
        task = context.current_task

        if not task:
            task = new_task(context.message)
            event_queue.enqueue_event(task)

        # 2) Decide between invoke vs. streaming
        can_stream = False
        accept_hdr = context.request.headers.get("accept", "")
        stream_qp  = context.request.query_params.get("stream", "").lower()
        want_stream = can_stream and (
            "text/event-stream" in accept_hdr or stream_qp == "true"
        )

        if not want_stream:
            # —— INVOKE PATH —— single-shot .invoke()
            try:
                result = await self.agent.invoke(query, task.contextId)
                task_handler.handle_event(
                    result,
                    context, event_queue, task
                )
            except Exception as e:
                task_handler.handle_event(
                    {"task_state": "failed", "content": str(e)},
                    context, event_queue, task
                )
            return

        # —— STREAM PATH —— loop over .stream()
        try:
            async for item in self.agent.stream(query, task.contextId):
                is_final = task_handler.handle_event(
                    item, context, event_queue, task
                )
                if is_final:
                    return
        except Exception as e:
            logger.error(f"Execution error: {e}")
            task_handler.handle_event(
                {"task_state": "failed", "content": "A server error occurred."},
                context, event_queue, task
            )

    async def cancel(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        # Cancellation requested → final canceled event + exception
        task = context.current_task
        if not task:
            task = new_task(context.message)
            event_queue.enqueue_event(task)

        cancel_event = {
            "task_state": "canceled",
            "content": "Task was canceled by client."
        }
        task_handler.handle_event(cancel_event, context, event_queue, task)
        raise Exception("Cancel not supported for this agent")


def get_agent_card(host: str, port: int) -> AgentCard:
    caps = AgentCapabilities(
        streaming=false,
        pushNotifications=true
    )
    skills = [        AgentSkill(
            id="reddit_search",
            name="Search Reddit and parse posts",
            description="Fetches Reddit posts, parses them, writes to file, returns summary",
            tags=['reddit', 'internship', 'parsing'],
            examples=['Topic: Google SRE internship…'],
        ),    ]
    return AgentCard(
        name="InternDB Reddit Agent",
        description="Searches Reddit for internship processes, parses posts, writes results, returns summary",
        url=f"http://localhost:10003/",
        version="1.0.0",
        defaultInputModes=['text/plain'],
        defaultOutputModes=['text/plain'],
        capabilities=caps,
        skills=skills,
    )


@click.command()
@click.option("--host", default="localhost", help="Bind host")
@click.option("--port", default=10000, type=int, help="Bind port")
def main(host: str, port: int):
    """Bootstraps the A2A server."""
    executor = a2aAgentExecutor()
    handler = DefaultRequestHandler(
        agent_executor=executor,
        task_store=InMemoryTaskStore(),
    )
    app = A2AStarletteApplication(
        agent_card=get_agent_card(host, port),
        http_handler=handler,
    ).build()

    config = uvicorn.Config(app=app, host=host, port=port, lifespan="auto")
    server = uvicorn.Server(config)

    click.echo(f"🚀 Starting A2A server on http://localhost:10003/")
    asyncio.run(server.serve())


if __name__ == "__main__":
    main()