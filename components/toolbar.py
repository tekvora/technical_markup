import tkinter as tk
from tkinter import ttk
from assets.toolbar_icons import get_icon_data


class Toolbar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Toolbar.TFrame")
        self.parent = parent
        
        # Configure custom style for buttons
        """ self.configure_styles() """

        # Create toolbar buttons
        self.create_buttons()
        
        
    def configure_styles(self):
        """ Configure custom styles for toolbar buttons """
        style = ttk.Style()

        # Configure the button style
        style.configure(
            "Toolbar.TButton",
            font=("Helvetica", 12, "bold"),  # Bold and classic font with increased size
            padding=(10, 8),  # Larger padding for better button size
            anchor="center",  # Center-align text in the button
            relief="flat",  # Flat style for a modern look
            background="#001f3f",  # Navy blue background for buttons
            foreground="white"
        )

        # Optional: Add hover and focus styles for a polished look
        style.map(
            "Toolbar.TButton",
            background=[("active", "#004080")],  # Lighter navy blue on hover
            foreground=[("active", "#FFD700")],  # Gold text on hover for contrast
            relief=[("pressed", "groove")]
        )

        

    def create_buttons(self):
        # File operations
        self.create_button("Open", "open", self.parent.open_file)
        self.create_button("Save", "save", self.parent.save_file)

        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Edit operations
        self.create_button("Undo", "undo", lambda: self.parent.annotation_canvas.undo())
        self.create_button("Redo", "redo", lambda: self.parent.annotation_canvas.redo())

        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Drawing tools
        self.create_button("Select", "select", lambda: self.set_mode("select"))
        self.create_button("Balloon", "balloon", lambda: self.set_mode("balloon"))
        self.create_button("Pan", "pan", lambda: self.set_mode("pan"))

        # Separator
        ttk.Separator(self, orient=tk.VERTICAL).pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Zoom controls
        self.create_button("Zoom In", "zoom_in", self.zoom_in)
        self.create_button("Zoom Out", "zoom_out", self.zoom_out)

    def create_button(self, text, icon_name, command):
        """ Create toolbar button with optional icon """
        btn_args = {"text": text, "command": command,
            }

        # Try to load icon
        icon = get_icon_data(icon_name)
        if icon:
            btn_args.update({
                "image": icon,
                "compound": tk.CENTER
            })
            

        # Create button
        btn = ttk.Button(self, **btn_args)
        btn.pack(side=tk.LEFT, padx=2, pady=2)

        # Store icon reference if loaded
        if icon:
            btn._icon = icon  # Keep reference to prevent garbage collection

    def set_mode(self, mode):
        self.parent.annotation_canvas.drawing_mode = mode

    def zoom_in(self):
        self.parent.annotation_canvas.scale *= 1.1
        self.parent.annotation_canvas.scale_all()

    def zoom_out(self):
        self.parent.annotation_canvas.scale /= 1.1
        self.parent.annotation_canvas.scale_all()