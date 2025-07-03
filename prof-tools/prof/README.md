# Prof Package - Core Python Package

Main Python package containing all prof-tools functionality for Maya instructor grading tools.

## Module Overview

- **core/**: Installation, setup, version management, and system utilities
- **ui/**: Maya menu creation, UI builders, and interface components  
- **tools/**: All grading-related functionality including rubric engine and configurations
- **tests/**: Automated testing framework for ensuring code quality
- **utils/**: Shared utility functions used across the package

## Usage

This package is designed to be imported and used within Maya's Python environment. The main entry point is through the UI menu system which provides access to all grading tools.

## Development Notes

- All modules should follow Python 3.x standards (Maya 2020+)
- UI components use Maya's cmds and mel modules
- Grading tools are designed to be non-destructive to student work
- Configuration-driven approach separates rubric data from grading logic

## Author

Alexander T. Santiago  - https://github.com/Atsantiago