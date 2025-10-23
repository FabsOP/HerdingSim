"""
Shared path utilities for handling file paths in both development and PyInstaller builds.
"""
import sys
import os

def resource_path(relative_path):
    """
    Get path for READ-ONLY bundled resources (icons, audio, etc.)
    Works in both development and PyInstaller builds.
    """
    try:
        # PyInstaller stores bundled files here during runtime
        base_path = sys._MEIPASS
    except Exception:
        # Running as script - use current directory
        base_path = os.path.abspath(".")
    
    return os.path.join(base_path, relative_path)


def user_data_path(relative_path):
    """
    Get path for USER-CREATED files (saves, uploads, etc.)
    These files persist outside the executable.
    """
    if getattr(sys, 'frozen', False):
        # Running as exe - save next to the executable
        base_path = os.path.dirname(sys.executable)
    else:
        # Running as script - use current directory
        base_path = os.path.dirname(os.path.abspath(__file__))
    
    return os.path.join(base_path, relative_path)