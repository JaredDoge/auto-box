import asyncio
import threading
import time


class Looper:

    def __init__(self):
        self.loop = asyncio.new_event_loop()
        self.thread_name = None
        t = threading.Thread(target=self._start_loop, daemon=True)
        t.start()

    def _start_loop(self):
        asyncio.set_event_loop(self.loop)
        print(threading.current_thread().name)
        self.loop.run_forever()


# 测试代码
def main():
    looper = Looper()

    async def wr():
        print(f'{wr}----{threading.current_thread().name}')

    async def test_run(a):
        await asyncio.sleep(5)
        task = asyncio.create_task(wr())
        print(f'{a}----{threading.current_thread().name}')
        print(asyncio.all_tasks(loop=looper.loop))
        # 等待 run 方法执行完成

    asyncio.run_coroutine_threadsafe(test_run('1'), looper.loop)



if __name__ == "__main__":
    main()
    while True:
        print(f'5')
        time.sleep(1)
