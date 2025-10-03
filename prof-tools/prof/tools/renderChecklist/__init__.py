"""
CMI Rendering Checklist Module for Prof-Tools

This module provides comprehensive checklist functionality for validating
3D models and renders in Maya for professors and advanced users.

Main Functions:
    - main(): Launch the rendering checklist GUI
    - run(): Alternative entry point (alias for main)
    - get_checklist_version_info(): Get version information

Usage:
    from prof.tools.renderChecklist import checklist
    checklist.main()  # Launch the checklist tool
"""

from .checklist import main, run, get_checklist_version_info

__all__ = ['main', 'run', 'get_checklist_version_info']