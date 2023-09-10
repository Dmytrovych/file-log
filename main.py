import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


class AsyncHandler(FileSystemEventHandler):

    def __init__(self):
        self.loop = asyncio.get_event_loop()
        self.commit_scheduled = False

    async def git_commit(self, path):
        if self.commit_scheduled:
            return

        self.commit_scheduled = True
        await asyncio.sleep(10)

        proc = await asyncio.create_subprocess_shell(
            f'git add . && git commit -m "auto: changes in {path}"',
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()
        if stdout:
            print(stdout.decode())
        if stderr:
            print(f"Git error: {stderr.decode()}")

        self.commit_scheduled = False

    def on_modified(self, event):
        self.loop.run_until_complete(self.git_commit(event.src_path))


class Watcher:
    DIRECTORY_TO_WATCH = __dir__

    def __init__(self):
        self.observer = Observer()

    def run(self):
        event_handler = AsyncHandler()
        self.observer.schedule(event_handler, self.DIRECTORY_TO_WATCH, recursive=True)
        self.observer.start()
        try:
            while True:
                asyncio.sleep(5)
        except:
            self.observer.stop()
            print("Observer Stopped")
        self.observer.join()


if __name__ == '__main__':
    w = Watcher()
    w.run()
