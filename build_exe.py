"""
Build Windows executable for PixelLang Compiler
Requires: pip install pyinstaller
"""
import PyInstaller.__main__
import os

# Build the GUI executable
PyInstaller.__main__.run([
    'main.py',
    '--name=PixelLangIDE',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    '--add-data=examples;examples',
    '--clean'
])

print("Build complete! Check dist/ folder for PixelLangIDE.exe")
