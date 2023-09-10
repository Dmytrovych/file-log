## Auto-Commit Watcher (file-log)

### Overview

Auto-Commit Watcher, also known as `file-log`, is a tool designed to automatically track changes in files within your repository and make commits for every individual change. This granular approach to versioning allows developers to capture a step-by-step snapshot of their coding progress.

### Features

- **Automatic Commits**: For every file change within your repository, a commit is made, providing a clear history of project evolution.
- **Ease of Use**: With a few commands, initialize your repository and start monitoring file changes.

### Installation

Begin by installing the required libraries:

```bash
pip install click watchdog
```

### Usage

1. To initialize a new git repository:

```bash
python auto_commit_watcher.py init [PATH]
```

Where `PATH` is the directory path. If not specified, it defaults to the current directory.

2. To start monitoring and committing file changes:

```bash
python auto_commit_watcher.py watch [PATH]
```

### Precautions

- Ensure that the directory doesn't contain large files or a multitude of files you don't intend to commit.
- This tool is designed to aid in tracing the development process. It might not be suitable for large or critical projects without additional configurations.

### Future Prospects

This approach provides insights into a developer's thought process at each stage of code development. In the future, it could prove beneficial for analyzing coding styles, identifying recurrent mistakes, or studying the development process in-depth.
```