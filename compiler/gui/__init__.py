"""
PixelLang GUI Package
=====================
Tkinter-based GUI for the PixelLang compiler.
Provides a code editor with syntax highlighting and live preview.
"""
from .app import PixelLangApp, run_gui

__all__ = ['PixelLangApp', 'run_gui']
