"""
PixelLang Compiler - Main Entry Point
======================================
CS4031 Compiler Construction Course Project

Usage:
    python main.py                    # Launch GUI
    python main.py --gui              # Launch GUI
    python main.py program.px         # Compile file to PNG
    python main.py --test             # Run test suite
"""
import sys
import os

# Ensure compiler package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_gui():
    """Launch the GUI IDE."""
    from compiler.gui import run_gui
    run_gui()

def compile_file(filepath: str):
    """Compile a .px file and save as PNG."""
    from compiler import compile_source
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            source = f.read()
    except FileNotFoundError:
        print(f"Error: File not found: {filepath}")
        sys.exit(1)
    except IOError as e:
        print(f"Error reading file: {e}")
        sys.exit(1)
    
    print(f"Compiling: {filepath}")
    print("-" * 50)
    
    image, errors = compile_source(source)
    
    if errors:
        print("Compilation failed!")
        for error in errors:
            print(f"  {error}")
        sys.exit(1)
    else:
        # Save PNG
        output_path = filepath.replace('.px', '.png')
        if output_path == filepath:  # No .px extension
            output_path += '.png'
        
        image.save(output_path)
        print(f"Compiled successfully!")
        print(f"Output saved to: {output_path}")
        print(f"Image size: {image.size[0]}x{image.size[1]} pixels")

def run_tests():
    """Run test suite."""
    from tests.test_compiler import run_tests
    run_tests()

def print_help():
    """Print help message."""
    print("""PixelLang Compiler - CS4031 Project

Usage:
    python main.py                    Launch GUI IDE
    python main.py --gui              Launch GUI IDE
    python main.py program.px         Compile .px file to PNG
    python main.py --test             Run test suite
    python main.py --help             Show this help

Phases:
    1. Lexical Analysis    (lexer.py)     - Tokenization with DFA
    2. Syntax Analysis     (parser.py)    - LL(1) recursive descent
    3. Semantic Analysis   (semantic.py)  - 13 semantic rules
    4. Code Generation     (codegen.py)   - PNG generation with Pillow

GUI Features:
    - Syntax highlighting
    - Line numbers
    - Error navigation
    - Image preview with zoom
    - Save/Load .px files
""")

def main():
    """Main entry point."""
    args = sys.argv[1:]
    
    if len(args) == 0 or args[0] == '--gui':
        run_gui()
    elif args[0] == '--help' or args[0] == '-h':
        print_help()
    elif args[0] == '--test':
        run_tests()
    elif args[0].endswith('.px') or args[0].endswith('.txt'):
        compile_file(args[0])
    else:
        print(f"Unknown option: {args[0]}")
        print("Use --help for usage information")
        sys.exit(1)

if __name__ == '__main__':
    main()
