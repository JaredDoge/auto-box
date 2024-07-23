import asyncio
import threading
from typing import Dict


class Async:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.futures: Dict[str, asyncio.Future] = {}
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def _handle_done(self, name, future):
        print(f'{name}已完成')
        self.futures.pop(name, None)

    def run(self, name, coro):
        future = asyncio.run_coroutine_threadsafe(coro, self.loop)
        if name in self.futures:
            future.set_exception(ValueError(f"future with name {name} already exists."))
            return future
        self.futures[name] = future
        future.add_done_callback(lambda f: self._handle_done(name, f))
        return future

    def cancel(self, name):
        if name not in self.futures:
            return
        future = self.futures.pop(name)
        future.cancel()
        return future

    def cancel_all(self):
        for future in self.futures.values():
            future.cancel()
        try:
            await asyncio.gather(*self.futures.values())
        except asyncio.CancelledError:
            pass
        self.futures.clear()

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()