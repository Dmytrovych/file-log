import os.path
from time import sleep

import click
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

import pathspec


class FileChangeHandler(FileSystemEventHandler):
    def __init__(self, path: str, gitignore_path=".gitignore"):
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
        if event.is_directory or self.is_ignored(event.src_path):
            return
        if event.src_path == os.path.join(self.path, '.gitignore'):
            self.ignore_spec = self.read_ignore()
        subprocess.run(['git', 'add', event.src_path])
        subprocess.run(['git', 'commit', '-m', f"auto: changes in {event.src_path}"])
        print(f"File {event.src_path} has been modified.")


@click.group()
def cli():
    pass


@cli.command()
@click.argument('path', default='.')
def init(path):
    """
    Initialize a new git repository.
    """
    if path == '.':
        path = os.path.abspath(path)
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
    if path == '.':
        path = os.path.abspath(path)
    observer = Observer()
    event_handler = FileChangeHandler(path)
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    click.echo(f"Watching for changes in {path}...")
    try:
        while True:
            sleep(4)
            pass
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


if __name__ == "__main__":
    cli()
