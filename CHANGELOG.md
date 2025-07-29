# Changelog

All notable changes to YT Sprint Tool will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-07-29

### 🚀 Initial Release

#### ✨ Features

- **Sprint Creation**: Automated YouTrack sprint creation with `make_sprint.py`
- **Default Sync**: Sprint configuration synchronization with `default_sprint.py`
- **Multi-Platform Builds**: Cross-platform binary compilation (Windows .exe + Linux static)
- **Professional Metadata**: Windows .exe files with embedded version information
- **Environment Integration**: Support for environment variables (YOUTRACK_URL, YOUTRACK_TOKEN)
- **ISO Week Support**: Automatic current week detection and custom week specification (YYYY.WW format)
- **GNU GPL v3.0 License**: Full free software licensing with comprehensive legal framework

#### 🛠️ Technical Implementation

- **Static Linking**: Linux binaries with staticx for maximum portability
- **Docker Builds**: Automated cross-platform compilation via Docker
- **Wine Integration**: Windows .exe generation on Linux using Wine + PyInstaller
- **Version Management**: Centralized version system with argparse integration
- **Comprehensive Testing**: Full test suite with pytest and coverage
- **Code Quality**: Linting with flake8 and pylint (10/10 rating)
- **License Headers**: All source files include GPL-3.0 copyright notices
- **License Testing**: Automated verification of GPL-3.0 license configuration

#### 🏗️ Architecture

- **Modular Design**: Separate utility libraries (`lib_yt_api`, `lib_date_utils`)
- **Clean CLI**: Professional command-line interface with proper help and version info
- **Error Handling**: Robust error handling with meaningful user feedback
- **Documentation**: Comprehensive docstrings and type hints throughout
- **Legal Compliance**: Full GPL-3.0 licensing information in CLI version output

### 🤖 Development Credits

- **Primary Author**: Sergei Sveshnikov ([svesh87@gmail.com](mailto:svesh87@gmail.com))
- **AI Assistant**: GitHub Copilot (Claude 4 Sonnet) - Extensive code generation, architecture design, testing, and documentation
- **Build System**: Docker + Wine + PyInstaller + staticx integration
- **Quality Assurance**: Automated testing and linting pipeline
- **Project Repository**: [https://github.com/svesh/yt-sprint-tool/](https://github.com/svesh/yt-sprint-tool/)

### 📦 Build Artifacts

- `make-sprint.exe` - Windows executable for sprint creation
- `default-sprint.exe` - Windows executable for sprint synchronization  
- `make-sprint-linux` - Linux static binary for sprint creation
- `default-sprint-linux` - Linux static binary for sprint synchronization

### 🎯 Platform Support

- **Windows**: Native .exe files with embedded version metadata
- **Linux**: Statically linked binaries (no dependencies required)
- **Development**: Cross-platform Python 3.12+ support

### 📄 License & Legal

- **License**: GNU General Public License v3.0 (GPL-3.0)
- **Copyright**: © 2025 Sergei Sveshnikov ([svesh87@gmail.com](mailto:svesh87@gmail.com))
- **Project URL**: [https://github.com/svesh/yt-sprint-tool/](https://github.com/svesh/yt-sprint-tool/)
- **Freedom**: Free software - can be redistributed and/or modified under GPL terms
- **Full License**: Available in [`LICENSE`](LICENSE) file

---

*This project was developed with significant assistance from AI tooling, demonstrating modern collaborative development between human expertise and artificial intelligence capabilities.*
