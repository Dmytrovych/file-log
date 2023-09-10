import asyncio
import os
import os.path
import subprocess
from pathlib import Path
from time import sleep

import click
import pathspec
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, path: str, gitignore_path=".gitignore"):
        self.loop = asyncio.get_event_loop()
        self.commit_scheduled = False
        self.path = path
        self.gitignore_path = gitignore_path
        self.ignore_spec = self.read_ignore(gitignore_path)

    def read_ignore(self, gitignore_path=None):
        if gitignore_path is None:
            gitignore_path = self.gitignore_path
        with open(gitignore_path, 'r') as f:
            return pathspec.PathSpec.from_lines('gitwildmatch', f)

    def is_ignored(self, path: str):
        local_path = path.lstrip(self.path)
        ignored = self.ignore_spec.match_file(local_path)
        if ignored:
            print(f"Ignoring changes in: {local_path}")
        else:
            print(f"Track changes in: {local_path}")
        return ignored

    def on_modified(self, event):
        self.loop.run_until_complete(self._on_modified(event))

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

    async def _on_modified(self, event):
        if event.src_path == os.path.join(self.path, '.gitignore'):
            self.ignore_spec = self.read_ignore()
        if event.is_directory or self.is_ignored(event.src_path):
            return
        await self.git_commit(event.src_path)
        print(f"File {event.src_path} has been modified.")


@click.group()
def cli():
    pass


def to_absolute_path(path_str):
    return Path(os.path.expanduser(path_str)).resolve()


@cli.command()
@click.argument('path', default='.')
def init(path):
    """
    Initialize a new git repository.
    """
    path = to_absolute_path(path).as_posix()
    result = subprocess.run(['git', 'init', path])
    if result.returncode == 0:
        click.echo("Successfully initialized git repository.")
    else:
        click.echo("Failed to initialize git repository.")


@cli.command()
@click.argument('path', default='.')
def watch(path):
    """
    Watch for file changes and commit them.
    """
    path = to_absolute_path(path).as_posix()
    observer = Observer()
    event_handler = FileChangeHandler(path)
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    click.echo(f"Watching for changes in {path}...")
    try:
        while True:
            sleep(10)
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    cli()
