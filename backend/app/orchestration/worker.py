import asyncio
from contextlib import suppress

from backend.app.config import Settings
from backend.app.orchestration.graph import process_utterance
from backend.app.orchestration.state import CallState
from backend.app.schemas.transcript import Utterance


class SessionWorker:
    def __init__(self, state: CallState, settings: Settings, broadcaster) -> None:
        self.state = state
        self.settings = settings
        self.broadcaster = broadcaster
        self.queue: asyncio.Queue[Utterance] = asyncio.Queue(maxsize=settings.max_queue_size)
        self._task: asyncio.Task | None = None

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = asyncio.create_task(self._run())

    async def stop(self) -> None:
        if self._task and not self._task.done():
            self._task.cancel()
            with suppress(asyncio.CancelledError):
                await self._task

    async def submit(self, utterance: Utterance) -> None:
        await self.queue.put(utterance)

    async def _run(self) -> None:
        while True:
            utterance = await self.queue.get()
            try:
                events = await process_utterance(self.state, utterance, self.settings)
                for event in events:
                    await self.broadcaster(event)
            finally:
                self.queue.task_done()
