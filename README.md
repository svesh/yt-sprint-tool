# YT Sprint Tool

> **⚠️ AI-Generated Content Notice**  
> This project and all its content (code, documentation, tests, build scripts) were fully generated using artificial intelligence tools (Claude 4 Sonnet). The project demonstrates modern AI-assisted development capabilities and serves as an example of human-AI collaboration in software engineering.

[![GitHub Repository](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/svesh/yt-sprint-tool/)
[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
[![AI Assisted](https://img.shields.io/badge/AI-Assisted-purple?logo=openai)](https://github.com/svesh/yt-sprint-tool/)
[![Generated with Claude](https://img.shields.io/badge/Generated%20with-Claude%204%20Sonnet-orange?logo=anthropic)](https://github.com/svesh/yt-sprint-tool/)

Set of utilities for automating sprint management in YouTrack.

## Description

The project contains two main utilities:

- **`make_sprint.py`** - creating sprints on YouTrack Agile board
- **`default_sprint.py`** - synchronizing sprint values between board and project

## Installation and Setup

### Local Usage

```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export YOUTRACK_URL="https://youtrack.example.com"
export YOUTRACK_TOKEN="your-bearer-token"
```

### Docker Build

```bash
# Linux image (fast)
docker build -f Dockerfile.debian -t yt-sprint-tool:linux .

# Windows image (with Wine)
docker build -f Dockerfile.windows -t yt-sprint-tool:windows .
```

## Usage

### make_sprint.py Utility

Create sprint for specified week on Agile board.

```bash
# Create sprint for current week
python make_sprint.py "My Board"

# Create sprint for specific week
python make_sprint.py "My Board" "2025.32"
```

### default_sprint.py Utility

Synchronize sprint values between board and project.

```bash
# Sync with default "Sprints" field
python default_sprint.py "My Board" "My Project"

# Sync with custom field
python default_sprint.py "My Board" "My Project" --field "Custom Field"

# For specific week
python default_sprint.py "My Board" "My Project" --week "2025.32"
```

## Parameters

### Common Parameters

- `--url` - YouTrack server URL (or env `YOUTRACK_URL`)
- `--token` - Bearer token for API (or env `YOUTRACK_TOKEN`)

### make_sprint.py Parameters

- `board` - Agile board name (positional argument)
- `week` - Week in YYYY.WW format (optional positional argument)

### default_sprint.py Parameters

- `board` - Agile board name (positional argument)
- `project` - Project name (positional argument)
- `--field` - Project field name (default "Sprints")
- `--week` - Week in YYYY.WW format (default - current)

## Architecture

### Libraries

- **`lib_date_utils.py`** - utilities for working with dates and ISO weeks
- **`lib_yt_api.py`** - YouTrack API client

### Testing

```bash
# Run tests
python test_yt_api.py

# Linting
flake8 lib_date_utils.py lib_yt_api.py default_sprint.py make_sprint.py test_yt_api.py
pylint lib_date_utils.py lib_yt_api.py default_sprint.py make_sprint.py test_yt_api.py
```

## Building Standalone Binaries

### Docker Build (recommended)

```bash
# Build binaries for Linux and Windows via Docker
./build-separate.sh
```

**Build results in `./dist/` folder:**

- 🐧 **Linux**: `make-sprint-linux`, `default-sprint-linux` (~11MB each)
- 🪟 **Windows**: `make-sprint.exe`, `default-sprint.exe` (~10MB each)

### Using Binaries

```bash
# Linux
./dist/make-sprint-linux "My Board" "2025.32"
./dist/default-sprint-linux "My Board" "My Project" --field "Sprints"

# Windows
./dist/make-sprint.exe "My Board" "2025.32"
./dist/default-sprint.exe "My Board" "My Project" --field "Sprints"
```

## Features

- ISO week support (Monday-Friday)
- Automatic current week detection
- Positional arguments for ease of use
- Comprehensive error handling and logging
- Docker-ready architecture for easy deployment
- Standalone binaries for independent distribution

## Requirements

- Python 3.12+
- YouTrack REST API token
- Access to YouTrack server
- Docker (for containerized usage)

## Authors and Contributors

### 👨‍💻 Primary Author

**Sergei Sveshnikov** - concept development, architecture, testing

- Email: [svesh87@gmail.com](mailto:svesh87@gmail.com)
- GitHub: [@svesh](https://github.com/svesh)

### 🤖 AI Co-author

**GitHub Copilot (Claude 4 Sonnet)** - code generation, architecture creation, test writing, documentation, CI/CD setup, optimization and refactoring

### 🤝 Collaborative Development

This project demonstrates effective collaboration between human expertise and artificial intelligence capabilities. The AI assistant participated in:

- Designing modular architecture
- Writing core code and utilities
- Creating Docker + Wine + staticx build system
- Developing comprehensive testing (pytest)
- Setting up linting and code quality
- Creating documentation and changelog
- Performance optimization and cross-platform compatibility

*This development approach represents a modern model of collaborative programming, where AI acts as a full team member in the development process.*

## License

This project is distributed under the **GNU General Public License v3.0** (GPL-3.0).

Full license text is available in the [`LICENSE`](LICENSE) file.

For questions about licensing or commercial use, contact: [svesh87@gmail.com](mailto:svesh87@gmail.com)

---

© 2025 [Sergei Sveshnikov](mailto:svesh87@gmail.com) | [GitHub Project](https://github.com/svesh/yt-sprint-tool/)
