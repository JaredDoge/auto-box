import asyncio
import threading
import traceback
from typing import Callable


class TaskManager:
    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._start_loop, daemon=True)
        self.tasks = {}
        self.thread.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()

    def run_in_loop(self, coro):
        return asyncio.run_coroutine_threadsafe(coro, self.loop)

    def stop(self):
        self.loop.call_soon_threadsafe(self.loop.stop)
        self.thread.join()


class Macro:
    def __init__(self, manager: TaskManager) -> None:
        self.manager = manager
        self.rune = False
        self.main_task: asyncio.Task | None = None
        self.current_task: asyncio.Task | None = None
        self.switch_task: asyncio.Task | None = None
        self.stop_callback: Callable = None

    async def _cancel(self, task):
        if task is None:
            return
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    def set_stop_callback(self, call):
        self.stop_callback = call

    def _notify_stop_callback(self):
        if self.stop_callback:
            self.stop_callback()

    def stop(self):
        async def _stop():
            await self._cancel(self.current_task)
            self.current_task = None

            await self._cancel(self.main_task)
            self.main_task = None

            await self._cancel(self.switch_task)
            self.switch_task = None

            self._notify_stop_callback()

        self.manager.run_in_loop(_stop())

    async def _check_stop(self, timeout: float):
        # wait_for(self.stop_event.wait(), timeout=timeout)
        await asyncio.sleep(timeout)

    async def _macro_done(self):
        self.stop()

    async def _run(self):
        try:
            while True:
                if self.rune:
                    if self.current_task and self.current_task.get_name() == 'rune':
                        await self._check_stop(timeout=1)
                        continue

                    await self._cancel(self.current_task)

                    task = self.manager.loop.create_task(sample_task(1, '解輪'))
                    task.set_name('rune')
                    self.current_task = task

                    await self._check_stop(timeout=1)
                    continue

                if self.current_task and self.current_task.get_name() == 'macro':
                    await self._check_stop(timeout=1)
                    continue

                await self._cancel(self.current_task)

                task = self.manager.loop.create_task(gather(self._macro_done))
                task.set_name('macro')
                self.current_task = task

                await self._check_stop(timeout=1)
                continue
        except asyncio.CancelledError:
            print("取消主腳本了")
        except Exception as e:
            print(f'{e}')

    def start(self):
        async def _start():
            self.main_task = self.manager.loop.create_task(self._run())
            self.switch_task = self.manager.loop.create_task(self.switch())

        self.manager.run_in_loop(_start())

    async def switch(self):
        while True:
            await self._check_stop(timeout=10)
            self.rune = not self.rune

        # 示例任务


async def sample_task(duration, name):
    while True:
        await asyncio.sleep(duration)
        print(f'{name}: {threading.currentThread().name}')


async def sample_task2(duration, name):
    await asyncio.sleep(duration)
    print(f'{name}: {threading.current_thread().name}')


async def gather(done: Callable):
    try:
        tasks = [
            sample_task(1, '腳本1'),
            sample_task2(3, '腳本2'),
        ]
        await asyncio.gather(*tasks)
        done()
    except asyncio.CancelledError:
        print('gather取消')
    except BaseException as e:
        print(f'----------gather-----------')
        traceback.print_exc()
        print(f'----------gather-----------')


# 示例用法
def main_callback():
    print("所有任务已停止")


def main():
    manager = TaskManager()

    macro = Macro(manager)

    macro.set_stop_callback(main_callback)

    # 启动宏
    macro.start()

    # 模拟一些操作
    # asyncio.run(asyncio.sleep(3.5))

    # 停止宏并执行回调
    # macro.stop()

    # 停止事件循环
    # manager.stop()


if __name__ == "__main__":
    main()

    while True:
        pass