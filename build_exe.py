"""
Build Windows executable for PixelLang Compiler
Requires: pip install pyinstaller
"""
import PyInstaller.__main__
import os
import sys

# Build the GUI executable
sep = ';' if os.name == 'nt' else ':'
data_arg = f"examples{sep}examples"

PyInstaller.__main__.run([
    'main.py',
    '--name=PixelLangIDE',
    '--onefile',
    '--windowed',
    '--icon=NONE',
    f'--add-data={data_arg}',
    '--clean'
])

print("Build complete! Check dist/ folder for PixelLangIDE.exe")
