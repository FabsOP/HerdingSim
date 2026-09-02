"""
Shared path utilities for handling file paths in both development and PyInstaller builds.
"""
import sys
import os


def project_root():
    """The directory holding src/ and assets/, or the exe's folder when frozen."""
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.executable)

    here = os.path.dirname(os.path.abspath(__file__))
    while True:
        if os.path.isdir(os.path.join(here, 'src')) and os.path.isdir(os.path.join(here, 'assets')):
            return here
        parent = os.path.dirname(here)
        if parent == here:
            return os.path.dirname(os.path.abspath(__file__))
        here = parent


def resource_path(relative_path):
    """
    Get path for READ-ONLY bundled resources (icons, audio, etc.)
    Works in both development and PyInstaller builds.
    """
    if getattr(sys, 'frozen', False):
        return os.path.join(sys._MEIPASS, 'assets', relative_path)

    return os.path.join(project_root(), 'assets', relative_path)


def user_data_path(relative_path):
    """
    Get path for USER-CREATED files (terrains, uploads, etc.)
    Always resolves inside the app root, whether frozen or run from source.
    """
    return os.path.join(project_root(), relative_path)
