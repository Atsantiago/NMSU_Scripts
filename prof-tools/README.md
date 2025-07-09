# Prof-Tools for Maya

A comprehensive suite of instructor tools for grading and managing Maya assignments across NMSU's FDMA courses for the Creative Media Institute (CMI).

## Overview

Prof-Tools provides a menu-based interface in Maya for instructors to efficiently grade student assignments and help automate or enhance repetitive tasks.This system is designed to work alongside class-specific student tools and will grow as new needs are discovered.

## Features

- **Menu-Based Interface**: Clean dropdown menu system integrated into Maya's main interface
- **Universal Grading Engine**: Consistent grading logic across all courses and assignments  
- **Configurable Rubrics**: Class and assignment-specific grading criteria without code changes
- **Automated Analysis**: File validation, geometry analysis, scene organization checks
- **Drag-and-Drop Installation**: Simple installer for easy setup

## Target Courses

- **FDMA 1510 - Intro 3D Animation**: Fundamental 3D modeling and animation projects
- **FDMA 2530 - Introduction to Modeling**: 3D Modeling Fundamentals

## Installation

1. Download the latest release ZIP file from GitHub
2. Extract to your desktop
3. Drag `setup_drag_drop_maya-prof-tools.py` onto Maya's viewport
4. Follow the installation prompts
5. Prof-Tools menu will appear in Maya's main menu bar

## Development Status

**Current Version**: 0.1.0 (Initial Shell)

- [x] Project structure and architecture
- [x] Basic menu system framework
- [ ] Core grading engine implementation
- [ ] Rubric configuration system
- [ ] Assignment-specific grading tools
- [ ] Report generation system

## Requirements

- Maya 2020+ (Python 3.x)
- Windows, macOS, or Linux

## Troubleshooting

If you encounter installation issues:

1. **"'str' object is not callable" error**: This has been fixed in the latest version. Make sure you're using the most recent files.

2. **Version loading warnings**: The system will automatically fall back to a working version if the dynamic version loading fails.

3. **Manual verification**: After dragging the installer, check Maya's script editor for any error messages.

## License

MIT License - See LICENSE file for details

## Author

Alexander T. Santiago  - https://github.com/Atsantiago