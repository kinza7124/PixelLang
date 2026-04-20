"""
PixelLang GUI Application
==========================
Tkinter-based IDE for PixelLang with:
- Code editor with syntax highlighting
- Line numbers gutter
- Error panel with clickable error navigation
- Image preview panel with zoom controls
- Compile & Run, Save PNG, Load File functionality

Color Scheme:
- Keywords: #4fc3f7 (blue)
- Colors: #ff9800 (orange)
- Numbers: #66bb6a (green)
- Comments: #78909c (gray)
- Background: #1e1e30 (dark)
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from PIL import Image, ImageTk
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from compiler import compile_source


class LineNumberCanvas(tk.Canvas):
    """Canvas widget displaying line numbers for the text editor."""
    
    def __init__(self, master, text_widget, font_size=12, **kwargs):
        super().__init__(master, **kwargs)
        self.text_widget = text_widget
        self.font_size = font_size
        self.config(width=50, highlightthickness=0)
        self.bg_color = '#151520'
        self.fg_color = '#6c6c80'
        
    def set_theme(self, colors, font_size=None):
        """Update colors based on theme."""
        self.bg_color = colors.get('line_bg', '#151520')
        self.fg_color = colors.get('line_fg', '#6c6c80')
        self.config(bg=self.bg_color)
        if font_size:
            self.font_size = font_size
        
    def redraw(self):
        """Redraw line numbers based on text widget content."""
        self.delete('all')
        
        i = self.text_widget.index('@0,0')
        while True:
            dline = self.text_widget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split('.')[0]
            self.create_text(35, y, anchor='ne', text=linenum, fill=self.fg_color, font=('Consolas', self.font_size))
            i = self.text_widget.index(f'{i}+1line')


class PixelLangApp(tk.Tk):
    """Main application window for PixelLang IDE."""
    
    # Theme definitions - comprehensive color schemes
    THEMES = {
        'dark': {
            'name': 'Dark (Default)',
            'keyword': '#4fc3f7',      # Blue
            'color': '#ff9800',        # Orange
            'number': '#66bb6a',       # Green
            'comment': '#78909c',      # Gray
            'string': '#ce9178',       # Brown/Orange
            'background': '#1e1e30',   # Dark blue-gray
            'foreground': '#e8e8e8',   # Light text
            'error_bg': '#4a2020',     # Dark red
            'line_bg': '#151520',      # Line numbers
            'line_fg': '#6c6c80',      # Line number text
            'insert': '#ffffff',       # Cursor
            'select_bg': '#3d3d5c',    # Selection
            'button_bg': '#2d2d4a',    # Buttons
            'preview_bg': '#151520',   # Preview canvas
            'status_bg': '#1e1e30',    # Status bar
            'menu_bg': '#2d2d4a',      # Menu
            'border': '#3d3d5c',       # Borders
            'highlight': '#4fc3f7',    # Accent
        },
        'light': {
            'name': 'Light',
            'keyword': '#0066cc',      # Blue
            'color': '#cc6600',        # Orange
            'number': '#009900',       # Green
            'comment': '#808080',      # Gray
            'string': '#a31515',       # Dark red
            'background': '#ffffff',   # White
            'foreground': '#333333',   # Dark text
            'error_bg': '#ffcccc',     # Light red
            'line_bg': '#f0f0f0',      # Light gray
            'line_fg': '#808080',      # Gray text
            'insert': '#000000',       # Black cursor
            'select_bg': '#add6ff',    # Light blue selection
            'button_bg': '#e0e0e0',    # Light buttons
            'preview_bg': '#f5f5f5',   # Light gray
            'status_bg': '#f0f0f0',    # Status bar
            'menu_bg': '#f0f0f0',      # Menu
            'border': '#cccccc',       # Borders
            'highlight': '#0066cc',    # Accent
        },
        'high_contrast': {
            'name': 'High Contrast',
            'keyword': '#ffff00',      # Yellow
            'color': '#00ffff',        # Cyan
            'number': '#00ff00',       # Green
            'comment': '#808080',      # Gray
            'string': '#ff8080',       # Light red
            'background': '#000000',   # Black
            'foreground': '#ffffff',   # White
            'error_bg': '#ff0000',     # Red
            'line_bg': '#000000',      # Black
            'line_fg': '#ffff00',      # Yellow
            'insert': '#ffffff',       # White cursor
            'select_bg': '#0000ff',    # Blue selection
            'button_bg': '#000000',    # Black
            'preview_bg': '#000000',   # Black
            'status_bg': '#000000',    # Black
            'menu_bg': '#000000',      # Black
            'border': '#ffffff',       # White
            'highlight': '#ffff00',    # Yellow
        },
        'monokai': {
            'name': 'Monokai',
            'keyword': '#f92672',      # Pink
            'color': '#ae81ff',        # Purple
            'number': '#ae81ff',       # Purple
            'comment': '#75715e',      # Olive
            'string': '#e6db74',       # Yellow
            'background': '#272822',   # Dark gray-green
            'foreground': '#f8f8f2',   # Off-white
            'error_bg': '#f92672',     # Pink
            'line_bg': '#1e1f1c',      # Darker
            'line_fg': '#75715e',      # Olive
            'insert': '#f8f8f2',       # White
            'select_bg': '#49483e',    # Gray
            'button_bg': '#3e3d32',    # Dark gray
            'preview_bg': '#1e1f1c',   # Dark
            'status_bg': '#272822',    # Match bg
            'menu_bg': '#3e3d32',      # Dark
            'border': '#49483e',       # Gray
            'highlight': '#f92672',    # Pink
        },
        'dracula': {
            'name': 'Dracula',
            'keyword': '#ff79c6',      # Pink
            'color': '#bd93f9',        # Purple
            'number': '#bd93f9',       # Purple
            'comment': '#6272a4',      # Blue-gray
            'string': '#f1fa8c',       # Yellow
            'background': '#282a36',   # Dark blue-gray
            'foreground': '#f8f8f2',   # White
            'error_bg': '#ff5555',     # Red
            'line_bg': '#21222c',      # Darker
            'line_fg': '#6272a4',      # Blue-gray
            'insert': '#f8f8f2',       # White
            'select_bg': '#44475a',    # Gray
            'button_bg': '#44475a',    # Gray
            'preview_bg': '#21222c',   # Dark
            'status_bg': '#282a36',    # Match bg
            'menu_bg': '#44475a',      # Gray
            'border': '#6272a4',       # Blue-gray
            'highlight': '#ff79c6',    # Pink
        },
        'solarized': {
            'name': 'Solarized Dark',
            'keyword': '#268bd2',      # Blue
            'color': '#cb4b16',        # Orange
            'number': '#2aa198',       # Teal
            'comment': '#586e75',      # Gray
            'string': '#b58900',       # Yellow
            'background': '#002b36',   # Dark blue
            'foreground': '#839496',   # Gray
            'error_bg': '#dc322f',     # Red
            'line_bg': '#073642',      # Darker blue
            'line_fg': '#586e75',      # Gray
            'insert': '#839496',       # Gray
            'select_bg': '#073642',    # Darker
            'button_bg': '#073642',    # Darker
            'preview_bg': '#073642',   # Darker
            'status_bg': '#002b36',    # Match bg
            'menu_bg': '#073642',      # Darker
            'border': '#586e75',       # Gray
            'highlight': '#268bd2',    # Blue
        },
    }
    
    # Current theme reference
    COLORS = None  # Will be set to current theme dict
    
    # Keywords for highlighting (30+ reserved words including v2.0)
    KEYWORDS = [
        'CANVAS', 'PIXEL', 'RECT', 'LINE', 'CIRCLE', 'FILL', 'ELLIPSE', 'CLEAR', 
        'BORDER', 'TRIANGLE', 'ARC', 'POLYGON', 'TEXT', 'MIRROR', 'SCALE', 'LOOP', 
        'TRANSLATE', 'ROTATE',
        # v2.0 Advanced Commands
        'BEZIER', 'STAR', 'ROUNDRECT', 'HEART', 'ARROW', 'PALETTE', 'SETPALETTE',
        'SPRITE', 'RANDOM', 'VAR', 'SET'
    ]
    
    # Editor settings
    FONT_FAMILY = 'Consolas'
    FONT_SIZE = 12
    
    def __init__(self):
        super().__init__()
        
        # Set default theme
        self.current_theme = 'dark'
        self.COLORS = self.THEMES[self.current_theme]
        
        self.title('PixelLang IDE - Compiler Construction Project')
        self.geometry('1200x800')
        self.configure(bg=self.COLORS['background'])
        
        # Current image
        self.current_image = None
        self.current_image_path = None
        self.zoom_level = 1.0
        
        # Error tracking
        self.error_lines = []
        
        # Undo/Redo stack
        self.undo_stack = []
        self.redo_stack = []
        self.max_undo = 50
        self._ignore_change = False
        
        self.setup_styles()
        self.setup_layout()
        self.setup_editor()
        self.setup_preview()
        self.setup_toolbar()
        self.setup_error_panel()
        self.setup_menu()
        self.bind_shortcuts()
        
        # Insert sample code
        self.insert_sample_code()
    
    def setup_styles(self):
        """Configure ttk styles."""
        c = self.COLORS
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Configure styles for current theme
        self.style.configure('TFrame', background=c['background'])
        self.style.configure('TButton', 
                           background=c['button_bg'],
                           foreground=c['foreground'],
                           font=('Segoe UI', 10))
        self.style.configure('TLabel', 
                           background=c['background'],
                           foreground=c['foreground'],
                           font=('Segoe UI', 10))
        self.style.configure('TCheckbutton',
                           background=c['background'],
                           foreground=c['foreground'])
    
    def setup_layout(self):
        """Create main layout with paned windows."""
        # Main container
        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Top toolbar frame
        self.toolbar_frame = ttk.Frame(self.main_frame)
        self.toolbar_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Horizontal paned window (editor | preview)
        self.h_paned = ttk.PanedWindow(self.main_frame, orient=tk.HORIZONTAL)
        self.h_paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel (editor)
        self.editor_frame = ttk.Frame(self.h_paned)
        self.h_paned.add(self.editor_frame, weight=1)
        
        # Right panel (preview)
        self.preview_frame = ttk.Frame(self.h_paned)
        self.h_paned.add(self.preview_frame, weight=1)
        
        # Bottom error panel
        self.error_frame = ttk.LabelFrame(self.main_frame, text='Errors', padding=5)
        self.error_frame.pack(fill=tk.X, pady=(5, 0))
        self.error_frame.pack_forget()  # Hidden by default
        
        # Status bar
        self.status_bar = tk.Label(
            self.main_frame, 
            text='Ready', 
            anchor=tk.W,
            bg=self.COLORS['status_bg'],
            fg=self.COLORS['foreground'],
            font=('Segoe UI', 10)
        )
        self.status_bar.pack(fill=tk.X, pady=(5, 0))
    
    def setup_toolbar(self):
        """Create toolbar with action buttons."""
        # Compile button
        self.compile_btn = ttk.Button(
            self.toolbar_frame, 
            text='Compile & Run (Ctrl+Return)',
            command=self.compile_and_run
        )
        self.compile_btn.pack(side=tk.LEFT, padx=5)
        
        # Save PNG button
        self.save_btn = ttk.Button(
            self.toolbar_frame,
            text='Save PNG',
            command=self.save_png,
            state=tk.DISABLED
        )
        self.save_btn.pack(side=tk.LEFT, padx=5)
        
        # Load File button
        self.load_btn = ttk.Button(
            self.toolbar_frame,
            text='Load File',
            command=self.load_file
        )
        self.load_btn.pack(side=tk.LEFT, padx=5)
        
        # New File button
        self.new_btn = ttk.Button(
            self.toolbar_frame,
            text='New',
            command=self.new_file
        )
        self.new_btn.pack(side=tk.LEFT, padx=5)
        
        # Zoom controls
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        ttk.Label(self.toolbar_frame, text='Zoom:').pack(side=tk.LEFT)
        self.zoom_in_btn = ttk.Button(self.toolbar_frame, text='+', command=self.zoom_in, width=3)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_out_btn = ttk.Button(self.toolbar_frame, text='-', command=self.zoom_out, width=3)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        
        self.zoom_reset_btn = ttk.Button(self.toolbar_frame, text='Reset', command=self.zoom_reset)
        self.zoom_reset_btn.pack(side=tk.LEFT, padx=2)
        
        # Grid overlay toggle
        ttk.Separator(self.toolbar_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        self.grid_var = tk.BooleanVar(value=False)
        self.grid_check = ttk.Checkbutton(
            self.toolbar_frame,
            text='Grid',
            variable=self.grid_var,
            command=self.toggle_grid
        )
        self.grid_check.pack(side=tk.LEFT, padx=5)
    
    def setup_editor(self):
        """Create code editor with line numbers and syntax highlighting."""
        c = self.COLORS
        
        # Editor container
        editor_container = ttk.Frame(self.editor_frame)
        editor_container.pack(fill=tk.BOTH, expand=True)
        
        # Line numbers
        self.line_numbers = LineNumberCanvas(editor_container, None, font_size=self.FONT_SIZE, width=50)
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        self.line_numbers.set_theme(c, self.FONT_SIZE)
        
        # Text widget
        self.editor = tk.Text(
            editor_container,
            wrap=tk.NONE,
            font=(self.FONT_FAMILY, self.FONT_SIZE),
            bg=c['background'],
            fg=c['foreground'],
            insertbackground=c['insert'],
            selectbackground=c['select_bg'],
            selectforeground=c['foreground'],
            undo=True,
            tabs='40',
            padx=10,
            pady=10,
            borderwidth=0,
            highlightthickness=1,
            highlightcolor=c['border']
        )
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Connect line numbers to text widget
        self.line_numbers.text_widget = self.editor
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(editor_container, command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=scrollbar.set)
        
        # Horizontal scrollbar
        h_scrollbar = ttk.Scrollbar(self.editor_frame, command=self.editor.xview, orient=tk.HORIZONTAL)
        h_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.config(xscrollcommand=h_scrollbar.set)
        
        # Bind events for line number updates and syntax highlighting
        self.editor.bind('<KeyRelease>', self.on_editor_change)
        self.editor.bind('<ButtonRelease>', self.on_editor_change)
        self.editor.bind('<MouseWheel>', self.on_editor_change)
        self.editor.bind('<Configure>', self.on_editor_change)
        
        # Bind font shortcuts
        self.bind('<Control-plus>', self.increase_font)
        self.bind('<Control-minus>', self.decrease_font)
    
    def setup_preview(self):
        """Create image preview panel."""
        c = self.COLORS
        # Preview canvas with scrollbars
        self.preview_canvas = tk.Canvas(
            self.preview_frame,
            bg=c['preview_bg'],
            highlightthickness=1,
            highlightcolor=c['border']
        )
        self.preview_canvas.pack(fill=tk.BOTH, expand=True)
        
        # Placeholder text
        self.preview_canvas.create_text(
            self.preview_canvas.winfo_width() // 2 or 200,
            self.preview_canvas.winfo_height() // 2 or 200,
            text='Compile to see preview',
            fill=c['line_fg'],
            font=('Segoe UI', 14),
            tags='placeholder'
        )
        
        # Bind resize
        self.preview_canvas.bind('<Configure>', self.on_preview_resize)
    
    def setup_error_panel(self):
        """Create error list panel."""
        c = self.COLORS
        self.error_listbox = tk.Listbox(
            self.error_frame,
            height=5,
            font=(self.FONT_FAMILY, self.FONT_SIZE - 2),
            bg=c['background'],
            fg=c['foreground'],
            selectbackground=c['select_bg'],
            selectforeground=c['foreground']
        )
        self.error_listbox.pack(fill=tk.BOTH, expand=True)
        
        # Click to jump to error
        self.error_listbox.bind('<Double-Button-1>', self.on_error_click)
    
    def setup_menu(self):
        """Create menu bar."""
        menubar = tk.Menu(self, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        self.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        menubar.add_cascade(label='File', menu=file_menu)
        file_menu.add_command(label='New', command=self.new_file, accelerator='Ctrl+N')
        file_menu.add_command(label='Open...', command=self.load_file, accelerator='Ctrl+O')
        file_menu.add_command(label='Save', command=self.save_file, accelerator='Ctrl+S')
        file_menu.add_separator()
        file_menu.add_command(label='Exit', command=self.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        menubar.add_cascade(label='Edit', menu=edit_menu)
        edit_menu.add_command(label='Undo', command=self.undo, accelerator='Ctrl+Z')
        edit_menu.add_command(label='Redo', command=self.redo, accelerator='Ctrl+Y')
        edit_menu.add_separator()
        edit_menu.add_command(label='Increase Font', command=self.increase_font, accelerator='Ctrl+Plus')
        edit_menu.add_command(label='Decrease Font', command=self.decrease_font, accelerator='Ctrl+Minus')
        edit_menu.add_command(label='Reset Font', command=self.reset_font)
        
        # View menu
        view_menu = tk.Menu(menubar, tearoff=0, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        menubar.add_cascade(label='View', menu=view_menu)
        
        # Theme submenu
        theme_menu = tk.Menu(view_menu, tearoff=0, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        view_menu.add_cascade(label='Theme', menu=theme_menu)
        
        # Add theme options
        for theme_key, theme_data in self.THEMES.items():
            theme_menu.add_command(
                label=theme_data['name'],
                command=lambda t=theme_key: self.apply_theme(t)
            )
        
        view_menu.add_separator()
        view_menu.add_checkbutton(label='Line Numbers', variable=tk.BooleanVar(value=True))
        view_menu.add_checkbutton(label='Word Wrap', command=self.toggle_wrap)
        
        # Run menu
        run_menu = tk.Menu(menubar, tearoff=0, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        menubar.add_cascade(label='Run', menu=run_menu)
        run_menu.add_command(label='Compile & Run', command=self.compile_and_run, accelerator='Ctrl+Return')
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, bg=self.COLORS['menu_bg'], fg=self.COLORS['foreground'])
        menubar.add_cascade(label='Help', menu=help_menu)
        help_menu.add_command(label='PixelLang Reference', command=self.show_help)
    
    def bind_shortcuts(self):
        """Bind keyboard shortcuts."""
        self.bind('<Control-Return>', lambda e: self.compile_and_run())
        self.bind('<Control-r>', lambda e: self.compile_and_run())
        self.bind('<Control-n>', lambda e: self.new_file())
        self.bind('<Control-o>', lambda e: self.load_file())
        self.bind('<Control-s>', lambda e: self.save_file())
        self.bind('<Control-z>', self.undo)
        self.bind('<Control-y>', self.redo)
    
    def on_editor_change(self, event=None):
        """Handle editor changes - update line numbers and highlight."""
        self.line_numbers.redraw()
        self.highlight_syntax()
    
    def highlight_syntax(self):
        """Apply syntax highlighting to editor content."""
        # Remove existing tags
        for tag in ['keyword', 'color', 'number', 'comment', 'string']:
            self.editor.tag_remove(tag, '1.0', tk.END)
        
        content = self.editor.get('1.0', tk.END)
        lines = content.split('\n')
        
        for line_num, line in enumerate(lines, start=1):
            # Highlight keywords
            for keyword in self.KEYWORDS:
                start_idx = 0
                while True:
                    idx = line.find(keyword, start_idx)
                    if idx == -1:
                        break
                    # Check it's a whole word
                    end_idx = idx + len(keyword)
                    if (idx == 0 or not line[idx-1].isalnum()) and \
                       (end_idx >= len(line) or not line[end_idx].isalnum()):
                        start_pos = f'{line_num}.{idx}'
                        end_pos = f'{line_num}.{end_idx}'
                        self.editor.tag_add('keyword', start_pos, end_pos)
                    start_idx = end_idx
            
            # Highlight colors (#RRGGBB)
            start_idx = 0
            while True:
                idx = line.find('#', start_idx)
                if idx == -1:
                    break
                # Check for 6 hex digits after #
                hex_part = line[idx+1:idx+7]
                if len(hex_part) == 6 and all(c in '0123456789ABCDEFabcdef' for c in hex_part):
                    start_pos = f'{line_num}.{idx}'
                    end_pos = f'{line_num}.{idx+7}'
                    self.editor.tag_add('color', start_pos, end_pos)
                start_idx = idx + 1
            
            # Highlight numbers
            import re
            for match in re.finditer(r'\b\d+\b', line):
                start_pos = f'{line_num}.{match.start()}'
                end_pos = f'{line_num}.{match.end()}'
                self.editor.tag_add('number', start_pos, end_pos)
            
            # Highlight comments
            idx = line.find('//')
            if idx != -1:
                start_pos = f'{line_num}.{idx}'
                end_pos = f'{line_num}.end'
                self.editor.tag_add('comment', start_pos, end_pos)
            
            # Highlight strings (quoted text)
            for quote in ['"', "'"]:
                start_idx = 0
                while True:
                    start = line.find(quote, start_idx)
                    if start == -1:
                        break
                    end = line.find(quote, start + 1)
                    if end == -1:
                        break  # Unterminated string, skip
                    start_pos = f'{line_num}.{start}'
                    end_pos = f'{line_num}.{end + 1}'
                    self.editor.tag_add('string', start_pos, end_pos)
                    start_idx = end + 1
        
        # Configure tag colors from current theme
        c = self.COLORS
        self.editor.tag_config('keyword', foreground=c['keyword'], font=(self.FONT_FAMILY, self.FONT_SIZE, 'bold'))
        self.editor.tag_config('color', foreground=c['color'])
        self.editor.tag_config('number', foreground=c['number'])
        self.editor.tag_config('comment', foreground=c['comment'], font=(self.FONT_FAMILY, self.FONT_SIZE, 'italic'))
        self.editor.tag_config('string', foreground=c['string'])
    
    def clear_error_highlights(self):
        """Remove error highlighting from all lines."""
        for line_num in self.error_lines:
            self.editor.tag_remove(f'error_{line_num}', f'{line_num}.0', f'{line_num}.end')
        self.error_lines = []
    
    def highlight_error_line(self, line_num: int):
        """Highlight a line with an error."""
        self.editor.tag_add(f'error_{line_num}', f'{line_num}.0', f'{line_num}.end')
        self.editor.tag_config(f'error_{line_num}', background=self.COLORS['error_bg'])
        self.error_lines.append(line_num)
    
    def compile_and_run(self):
        """Compile the source and display result."""
        source = self.editor.get('1.0', tk.END)
        
        # Clear previous error highlights
        self.clear_error_highlights()
        
        # Compile
        image, errors = compile_source(source)
        
        if errors:
            # Show errors
            self.error_frame.pack(fill=tk.X, pady=(5, 0))
            self.error_listbox.delete(0, tk.END)
            
            for error in errors:
                self.error_listbox.insert(tk.END, error)
                # Try to extract line number and highlight
                import re
                match = re.search(r'line (\d+)', error)
                if match:
                    line_num = int(match.group(1))
                    self.highlight_error_line(line_num)
            
            # Update status
            self.status_bar.config(text=f'Compilation failed - {len(errors)} error(s)', foreground='#ff6b6b')
            self.save_btn.config(state=tk.DISABLED)
        else:
            # Hide error panel
            self.error_frame.pack_forget()
            
            # Display image
            self.current_image = image
            self.display_image()
            
            # Update status
            self.status_bar.config(text='Compilation successful!', foreground='#4ec9b0')
            self.save_btn.config(state=tk.NORMAL)
    
    def display_image(self):
        """Display the current image in the preview canvas."""
        if self.current_image is None:
            return
        
        # Clear canvas
        self.preview_canvas.delete('all')
        
        # Calculate scaled size
        canvas_width = self.preview_canvas.winfo_width()
        canvas_height = self.preview_canvas.winfo_height()
        
        if canvas_width < 50:
            canvas_width = 400
        if canvas_height < 50:
            canvas_height = 400
        
        img_width, img_height = self.current_image.size
        
        # Calculate scale to fit canvas while maintaining aspect ratio
        scale_x = canvas_width / img_width
        scale_y = canvas_height / img_height
        scale = min(scale_x, scale_y) * 0.9 * self.zoom_level  # 90% of available space
        
        new_width = int(img_width * scale)
        new_height = int(img_height * scale)
        
        # Resize image
        display_image = self.current_image.resize((new_width, new_height), Image.NEAREST)
        self.photo = ImageTk.PhotoImage(display_image)
        
        # Center in canvas
        x = canvas_width // 2
        y = canvas_height // 2
        
        self.preview_canvas.create_image(x, y, image=self.photo, anchor=tk.CENTER, tags='image')
        
        # Draw grid if enabled
        self.preview_canvas.delete('grid')
        if self.grid_var.get():
            self.draw_grid(canvas_width, canvas_height, img_width, img_height, x, y)
    
    def on_preview_resize(self, event=None):
        """Handle preview canvas resize."""
        if self.current_image:
            self.display_image()
        else:
            # Center placeholder
            self.preview_canvas.coords(
                'placeholder',
                self.preview_canvas.winfo_width() // 2,
                self.preview_canvas.winfo_height() // 2
            )
    
    def on_error_click(self, event=None):
        """Jump to error line when clicked."""
        selection = self.error_listbox.curselection()
        if selection:
            error_text = self.error_listbox.get(selection[0])
            import re
            match = re.search(r'line (\d+)', error_text)
            if match:
                line_num = int(match.group(1))
                # Jump to line
                self.editor.see(f'{line_num}.0')
                self.editor.mark_set(tk.INSERT, f'{line_num}.0')
                self.editor.focus_set()
    
    def save_png(self):
        """Save the generated image as PNG."""
        if self.current_image is None:
            return
        
        filepath = filedialog.asksaveasfilename(
            defaultextension='.png',
            filetypes=[('PNG files', '*.png'), ('All files', '*.*')]
        )
        
        if filepath:
            self.current_image.save(filepath)
            self.status_bar.config(text=f'Saved to {filepath}', foreground='#4ec9b0')
    
    def load_file(self):
        """Load a .px file into the editor."""
        filepath = filedialog.askopenfilename(
            filetypes=[('PixelLang files', '*.px'), ('Text files', '*.txt'), ('All files', '*.*')]
        )
        
        if filepath:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                self.editor.delete('1.0', tk.END)
                self.editor.insert('1.0', content)
                self.on_editor_change()
                self.current_image_path = filepath
                self.title(f'PixelLang IDE - {filepath}')
                self.status_bar.config(text=f'Loaded {filepath}', foreground='#4ec9b0')
                # Clear previous compilation results
                self.current_image = None
                self.preview_canvas.delete('all')
                self.preview_canvas.create_text(
                    200, 200,
                    text='Compile to see preview',
                    fill='#6c6c80',
                    font=('Segoe UI', 14),
                    tags='placeholder'
                )
                self.save_btn.config(state=tk.DISABLED)
            except Exception as e:
                messagebox.showerror('Error', f'Failed to load file: {e}')
    
    def new_file(self):
        """Clear editor for new file."""
        self.editor.delete('1.0', tk.END)
        self.current_image = None
        self.current_image_path = None
        self.title('PixelLang IDE - Compiler Construction Project')
        self.status_bar.config(text='New file', foreground=self.COLORS['foreground'])
        self.preview_canvas.delete('all')
        self.preview_canvas.create_text(
            200, 200,
            text='Compile to see preview',
            fill='#6c6c80',
            font=('Segoe UI', 14),
            tags='placeholder'
        )
        self.save_btn.config(state=tk.DISABLED)
        self.error_frame.pack_forget()
        self.clear_error_highlights()
        self.insert_sample_code()
    
    def save_file(self):
        """Save editor content to file."""
        if self.current_image_path:
            filepath = self.current_image_path
        else:
            filepath = filedialog.asksaveasfilename(
                defaultextension='.px',
                filetypes=[('PixelLang files', '*.px'), ('Text files', '*.txt'), ('All files', '*.*')]
            )
        
        if filepath:
            try:
                content = self.editor.get('1.0', tk.END)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(content)
                self.current_image_path = filepath
                self.title(f'PixelLang IDE - {filepath}')
                self.status_bar.config(text=f'Saved {filepath}', foreground='#4ec9b0')
            except Exception as e:
                messagebox.showerror('Error', f'Failed to save file: {e}')
    
    def zoom_in(self):
        """Increase zoom level."""
        self.zoom_level *= 1.25
        if self.current_image:
            self.display_image()
    
    def zoom_out(self):
        """Decrease zoom level."""
        self.zoom_level /= 1.25
        if self.zoom_level < 0.1:
            self.zoom_level = 0.1
        if self.current_image:
            self.display_image()
    
    def zoom_reset(self):
        """Reset zoom level."""
        self.zoom_level = 1.0
        if self.current_image:
            self.display_image()
    
    def toggle_grid(self):
        """Toggle grid overlay on preview."""
        self.display_image()
    
    def draw_grid(self, canvas_width, canvas_height, img_width, img_height, x, y):
        """Draw pixel grid overlay on the preview canvas."""
        if not self.grid_var.get() or not self.current_image:
            return
        
        # Calculate scaled pixel size
        scale = min(canvas_width / img_width, canvas_height / img_height) * self.zoom_level
        pixel_size = max(1, int(scale))
        
        # Calculate offset to center the image
        offset_x = x - (img_width * pixel_size) // 2
        offset_y = y - (img_height * pixel_size) // 2
        
        # Draw vertical grid lines
        for i in range(img_width + 1):
            line_x = offset_x + i * pixel_size
            self.preview_canvas.create_line(
                line_x, offset_y,
                line_x, offset_y + img_height * pixel_size,
                fill='#666666', width=1, tags='grid'
            )
        
        # Draw horizontal grid lines
        for i in range(img_height + 1):
            line_y = offset_y + i * pixel_size
            self.preview_canvas.create_line(
                offset_x, line_y,
                offset_x + img_width * pixel_size, line_y,
                fill='#666666', width=1, tags='grid'
            )
    
    def show_help(self):
        """Show help dialog with PixelLang reference."""
        help_text = """PixelLang Reference v2.0
========================

Core Keywords (18):
  CANVAS W H;                - Set canvas size (must be first)
  PIXEL x y #COLOR;          - Draw pixel at (x,y)
  RECT x y w h #C;           - Draw rectangle
  LINE x1 y1 x2 y2 #C;       - Draw line
  CIRCLE cx cy r #C;         - Draw circle
  FILL x y #C;               - Flood fill from (x,y)
  ELLIPSE cx cy rx ry #C;    - Draw ellipse
  CLEAR #COLOR;              - Fill entire canvas
  BORDER x y w h t #C;       - Draw hollow rectangle border
  TRIANGLE x1 y1 x2 y2 x3 y3 #C; - Draw filled triangle
  ARC cx cy r start end #C;  - Draw circular arc
  POLYGON x1 y1 x2 y2 x3 y3 x4 y4 #C; - Draw 4-point polygon
  TEXT x y text #C;          - Draw text (uppercase, e.g., HI)
  MIRROR axis;               - Flip: 0=horizontal, 1=vertical
  SCALE factor;              - Scale drawing (1-10)
  LOOP n { ... }             - Repeat body n times
  TRANSLATE dx dy;          - Shift origin
  ROTATE angle;              - Rotate context (0-360)

v2.0 Advanced Keywords (12):
  BEZIER x1 y1 cx1 cy1 cx2 cy2 x2 y2 #C; - Cubic bezier curve
  STAR cx cy outer_r inner_r points #C; - Star shape
  ROUNDRECT x y w h radius #C;           - Rounded rectangle
  HEART cx cy size #C;                   - Heart shape
  ARROW x1 y1 x2 y2 head_size #C;      - Arrow with arrowhead
  PALETTE idx #COLOR;                    - Define palette color (0-15)
  SETPALETTE idx;                        - Set active palette
  SPRITE x y pattern #C;                - Draw sprite (binary pattern)
  RANDOM min max;                        - Generate random number
  VAR name value;                        - Define variable
  SET name value;                        - Set variable value

Color format: #RRGGBB (e.g., #FF0000 for red)

Example:
  CANVAS 100 100;
  CLEAR #1A1A2E;
  ARC 50 50 30 0 180 #FF0000;
  TEXT 40 80 HI #FFFFFF;

Keyboard Shortcuts:
  Ctrl+Return - Compile & Run
  Ctrl+N - New file
  Ctrl+O - Open file
  Ctrl+S - Save file
  Ctrl+Z - Undo
  Ctrl+Y - Redo
  Ctrl++ / Ctrl+-  - Zoom in/out
  Ctrl+Plus / Ctrl+Minus - Font size

IDE Features:
  View > Theme - Switch color themes (6 themes available)
  View > Word Wrap - Toggle line wrapping
  Edit > Font Size - Adjust editor font size
"""
        messagebox.showinfo('PixelLang Reference', help_text)
    
    def insert_sample_code(self):
        """Insert sample code into editor."""
        sample = '''// PixelLang Sample Program
// Tests all 18 keywords including advanced features

CANVAS 100 100;

// Clear with dark background
CLEAR #1A1A2E;

// Draw an arc (semicircle)
ARC 50 30 20 0 180 #E94560;

// Draw a 4-point polygon (diamond)
POLYGON 50 10 60 30 50 50 40 30 #16C79A;

// Draw pixel text
TEXT 35 88 HI #FFFFFF;

// Draw ellipse with different radii
ELLIPSE 20 70 12 6 #F9A825;

// Draw circle
CIRCLE 80 70 8 #E91E63;

// Draw triangle
TRIANGLE 10 40 30 40 20 25 #00BCD4;

// Draw border frame
BORDER 2 2 96 96 2 #4A4A6A;

// Draw rectangle
RECT 75 10 15 12 #9C27B0;

// Draw line
LINE 50 50 85 70 #FF9800;

// Place pixel
PIXEL 50 60 #FFFFFF;

// Flood fill
FILL 5 5 #16213E;

// Loop with translate and rotate
LOOP 3 {
    PIXEL 15 15 #A8D8EA;
    TRANSLATE 5 0;
    ROTATE 15;
}

// Mirror context
MIRROR 0;

// Scale drawing
SCALE 1;
'''
        self.editor.insert('1.0', sample)
        self.on_editor_change()
    
    def undo(self, event=None):
        """Undo last change."""
        if self.undo_stack:
            # Save current state to redo stack
            current = self.editor.get('1.0', 'end-1c')
            self.redo_stack.append(current)
            
            # Restore previous state
            prev = self.undo_stack.pop()
            self._ignore_change = True
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', prev)
            self._ignore_change = False
            self.highlight_syntax()
        return 'break'
    
    def redo(self, event=None):
        """Redo last undone change."""
        if self.redo_stack:
            # Save current state to undo stack
            current = self.editor.get('1.0', 'end-1c')
            self.undo_stack.append(current)
            
            # Restore next state
            next_state = self.redo_stack.pop()
            self._ignore_change = True
            self.editor.delete('1.0', 'end')
            self.editor.insert('1.0', next_state)
            self._ignore_change = False
            self.highlight_syntax()
        return 'break'
    
    def save_undo_state(self):
        """Save current state to undo stack."""
        if not self._ignore_change:
            current = self.editor.get('1.0', 'end-1c')
            if not self.undo_stack or self.undo_stack[-1] != current:
                self.undo_stack.append(current)
                if len(self.undo_stack) > self.max_undo:
                    self.undo_stack.pop(0)
                self.redo_stack.clear()
    
    def apply_theme(self, theme_name):
        """Apply a color theme to the entire IDE."""
        if theme_name not in self.THEMES:
            return
        
        self.current_theme = theme_name
        self.COLORS = self.THEMES[theme_name]
        c = self.COLORS
        
        # Update main window
        self.configure(bg=c['background'])
        
        # Update styles
        self.style.configure('TFrame', background=c['background'])
        self.style.configure('TButton', 
                           background=c['button_bg'],
                           foreground=c['foreground'],
                           font=('Segoe UI', 10))
        self.style.configure('TLabel', 
                           background=c['background'],
                           foreground=c['foreground'],
                           font=('Segoe UI', 10))
        
        # Update editor
        self.editor.config(
            bg=c['background'],
            fg=c['foreground'],
            insertbackground=c['insert'],
            selectbackground=c['select_bg'],
            selectforeground=c['foreground'],
            highlightcolor=c['border']
        )
        
        # Update line numbers
        self.line_numbers.set_theme(c, self.FONT_SIZE)
        
        # Update preview canvas
        self.preview_canvas.config(
            bg=c['preview_bg'],
            highlightcolor=c['border']
        )
        
        # Update error panel
        self.error_listbox.config(
            bg=c['background'],
            fg=c['foreground'],
            selectbackground=c['select_bg'],
            selectforeground=c['foreground']
        )
        
        # Update status bar
        self.status_bar.config(
            background=c['status_bg'],
            foreground=c['foreground']
        )
        
        # Note: error_frame is ttk.LabelFrame - bg is set via style, skip direct config
        
        # Re-highlight syntax with new colors
        self.highlight_syntax()
        
        # Update status
        self.status_bar.config(text=f'Theme changed to {c["name"]}', foreground=c['highlight'])
    
    def increase_font(self, event=None):
        """Increase editor font size."""
        self.FONT_SIZE = min(self.FONT_SIZE + 1, 24)
        self.editor.config(font=(self.FONT_FAMILY, self.FONT_SIZE))
        self.line_numbers.font_size = self.FONT_SIZE
        self.line_numbers.redraw()
        self.status_bar.config(text=f'Font size: {self.FONT_SIZE}', foreground=self.COLORS['highlight'])
    
    def decrease_font(self, event=None):
        """Decrease editor font size."""
        self.FONT_SIZE = max(self.FONT_SIZE - 1, 8)
        self.editor.config(font=(self.FONT_FAMILY, self.FONT_SIZE))
        self.line_numbers.font_size = self.FONT_SIZE
        self.line_numbers.redraw()
        self.status_bar.config(text=f'Font size: {self.FONT_SIZE}', foreground=self.COLORS['highlight'])
    
    def reset_font(self, event=None):
        """Reset font size to default."""
        self.FONT_SIZE = 12
        self.editor.config(font=(self.FONT_FAMILY, self.FONT_SIZE))
        self.line_numbers.font_size = self.FONT_SIZE
        self.line_numbers.redraw()
        self.status_bar.config(text='Font size reset to 12', foreground=self.COLORS['highlight'])
    
    def toggle_wrap(self):
        """Toggle word wrap in editor."""
        current = self.editor.cget('wrap')
        new_wrap = 'word' if current == 'none' else 'none'
        self.editor.config(wrap=new_wrap)
        status = 'enabled' if new_wrap == 'word' else 'disabled'
        self.status_bar.config(text=f'Word wrap {status}', foreground=self.COLORS['highlight'])


def run_gui():
    """Start the GUI application."""
    app = PixelLangApp()
    app.mainloop()


if __name__ == '__main__':
    run_gui()
