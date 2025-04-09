
import tkinter as tk
from tkinter import ttk, colorchooser, messagebox, simpledialog

class Sidebar(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent, style="Sidebar.TFrame")

        # Mode toggle
        self.editable_index_mode = tk.BooleanVar(value=False)
        
        # Create UI components
        self.create_mode_switch()
        
        # Create sidebar sections
        self.create_annotation_properties()
        self.create_layer_list()
        
        # Add balloon number input field for editable mode
        self.create_balloon_number_input()

    def create_mode_switch(self):
        """Create a checkbox to switch between standard and editable index mode"""
        mode_frame = ttk.Frame(self)
        mode_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.mode_checkbox = ttk.Checkbutton(
            mode_frame,
            text="Enable Editable Index Mode",
            variable=self.editable_index_mode,
            command=self.toggle_editable_index_mode
        )
        self.mode_checkbox.pack(side=tk.LEFT, padx=5)

    def create_balloon_number_input(self):
        """Add an input field for the balloon number in Editable Index Mode"""
        self.index_frame = ttk.Frame(self)
        self.index_frame.pack(fill=tk.X, padx=5, pady=5)
        
        ttk.Label(self.index_frame, text="Balloon Number:").pack(side=tk.LEFT)
        
        self.index_var = tk.StringVar()
        self.index_entry = ttk.Entry(self.index_frame, textvariable=self.index_var)
        self.index_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Initially hidden until editable mode is enabled
        self.index_frame.pack_forget()
        
    def create_annotation_properties(self):
        # Properties frame
        props_frame = ttk.LabelFrame(self, text="Annotation Properties")
        props_frame.pack(fill=tk.X, padx=5, pady=5)

        # Shape selector
        shape_frame = ttk.Frame(props_frame)
        shape_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(shape_frame, text="Shape:").pack(side=tk.LEFT)
        self.shape_var = tk.StringVar(value="circle")
        shapes = ["circle", "square", "triangle"]

        for shape in shapes:
            ttk.Radiobutton(
                shape_frame,
                text=shape.capitalize(),
                value=shape,
                variable=self.shape_var,
                command=self.on_shape_change
            ).pack(side=tk.LEFT, padx=5)
            
        # Dimension, Tolerance, and Remarks fields
        # Dimension field
        dimension_frame = ttk.Frame(props_frame)
        dimension_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(dimension_frame, text="Dimension:").pack(side=tk.LEFT)
        self.dimension_var = tk.StringVar(value="")
        dimension_entry = ttk.Entry(dimension_frame, textvariable=self.dimension_var)
        dimension_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        dimension_entry.bind("<KeyRelease>", self.on_dimension_change)
        
        # Tolerance field
        tolerance_frame = ttk.Frame(props_frame)
        tolerance_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(tolerance_frame, text="Tolerance:").pack(side=tk.LEFT)
        self.tolerance_var = tk.StringVar(value="")
        tolerance_entry = ttk.Entry(tolerance_frame, textvariable=self.tolerance_var)
        tolerance_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        tolerance_entry.bind("<KeyRelease>", self.on_tolerance_change)
        
        # Remarks field
        remarks_frame = ttk.Frame(props_frame)
        remarks_frame.pack(fill=tk.X, padx=5, pady=5)
        ttk.Label(remarks_frame, text="Remarks:").pack(side=tk.LEFT)
        self.remarks_var = tk.StringVar(value="")
        remarks_entry = ttk.Entry(remarks_frame, textvariable=self.remarks_var)
        remarks_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        remarks_entry.bind("<KeyRelease>", self.on_remarks_change)

        # Color selector
        color_frame = ttk.Frame(props_frame)
        color_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(color_frame, text="Color:").pack(side=tk.LEFT)
        self.color_var = tk.StringVar(value="#2196F3")

        # Predefined colors
        colors = ["#2196F3", "#FF5722", "#4CAF50", "#9C27B0", "#FFC107", "#607D8B"]
        color_panel = ttk.Frame(props_frame)
        color_panel.pack(fill=tk.X, padx=5, pady=2)

        for color in colors:
            btn = tk.Button(
                color_panel,
                bg=color,
                width=2,
                command=lambda c=color: self.set_color(c)
            )
            btn.pack(side=tk.LEFT, padx=2)

        # Custom color button
        custom_color_btn = ttk.Button(
            color_panel,
            text="Custom",
            command=self.choose_custom_color
        )
        custom_color_btn.pack(side=tk.LEFT, padx=5)

        # Size controls
        size_frame = ttk.Frame(props_frame)
        size_frame.pack(fill=tk.X, padx=5, pady=5)

        ttk.Label(size_frame, text="Size:").pack(side=tk.LEFT)

        self.size_var = tk.DoubleVar(value=1.0)
        size_scale = ttk.Scale(
            size_frame,
            from_=0.1,
            to=10.0,
            variable=self.size_var,
            orient=tk.HORIZONTAL,
            command=self.on_size_change
        )
        size_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)

        # Size presets
        size_presets = ttk.Frame(props_frame)
        size_presets.pack(fill=tk.X, padx=5, pady=2)

        for size in [0.1, 1.0, 5.0, 10.0]:
            btn = ttk.Button(
                size_presets,
                text=f"{size}x",
                width=4,
                command=lambda s=size: self.size_var.set(s)
            )
            btn.pack(side=tk.LEFT, padx=2)

    def create_layer_list(self):
        # Layer list frame
        layer_frame = ttk.LabelFrame(self, text="Annotations")
        layer_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Toolbar for layer operations
        toolbar = ttk.Frame(layer_frame)
        toolbar.pack(fill=tk.X, padx=5, pady=2)

        ttk.Button(
            toolbar,
            text="Delete",
            command=self.delete_selected_annotation
        ).pack(side=tk.LEFT)

        # Create treeview
        self.tree = ttk.Treeview(
            layer_frame,
            columns=("b_no", "position", "size", "shape", "dimension", "tolerance", "remarks"),
            show="headings",
            selectmode="browse"
        )

        self.tree.heading("b_no", text="B_No#")
        self.tree.heading("position", text="Position")
        self.tree.heading("size", text="Size")
        self.tree.heading("shape", text="Shape")
        self.tree.heading("dimension", text="Dimension")
        self.tree.heading("tolerance", text="Tolerance")
        self.tree.heading("remarks", text="Remarks")

        self.tree.column("b_no", width=30)
        self.tree.column("position", width=40)
        self.tree.column("size", width=30)
        self.tree.column("shape", width=30)
        self.tree.column("dimension", width=40)
        self.tree.column("tolerance", width=40)
        self.tree.column("remarks", width=80)

        # Add scrollbar
        scrollbar = ttk.Scrollbar(layer_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Bind events
        self.tree.bind("<<TreeviewSelect>>", self.on_annotation_select)
        self.tree.bind("<Double-1>", self.edit_balloon_number)

    def toggle_editable_index_mode(self):
        """Handle switching between standard and editable index modes"""
        canvas = self.master.master.annotation_canvas
        
        # If trying to turn OFF editable mode
        if not self.editable_index_mode.get():
            # Check if any custom balloon numbers exist
            if any(not balloon.number.isdigit() for balloon in canvas.annotations):
                # Show error message
                messagebox.showerror(
                    "Cannot Disable Editable Mode",
                    "Editable Index Mode cannot be disabled while custom balloon numbers exist."
                )
                # Force the checkbox to remain checked
                self.editable_index_mode.set(True)
                return
            
            # Hide the balloon number input field
            self.index_frame.pack_forget()
            
            # Renumber balloons sequentially
            canvas.renumber_balloons()
            canvas.redraw_annotations()
            self.update_annotation_list(canvas.annotations)
        else:
            # Show the balloon number input field when enabling editable mode
            self.index_frame.pack(after=self.mode_checkbox.winfo_parent(), fill=tk.X, padx=5, pady=5)
    
    def edit_balloon_number(self, event=None):
        """Enable editing of the balloon number when in editable mode"""
        if not self.editable_index_mode.get():
            return
            
        selected_item = self.tree.selection()
        if not selected_item:
            return
            
        item_id = selected_item[0]
        current_values = self.tree.item(item_id, "values")
        current_number = current_values[0]
        
        new_number = simpledialog.askstring(
            "Edit Balloon Number", 
            f"Enter new balloon number (current: {current_number}):"
        )
        
        if not new_number:
            return
            
        # Validate that the new number is unique
        canvas = self.master.master.annotation_canvas
        if any(balloon.number == new_number for balloon in canvas.annotations):
            messagebox.showerror("Duplicate Entry", "This balloon number already exists!")
            return
            
        # Update the balloon number
        for balloon in canvas.annotations:
            if balloon.number == current_number:
                balloon.number = new_number
                break
                
        # Update the display without renumbering
        canvas.redraw_annotations()
        self.update_annotation_list(canvas.annotations)

    def set_color(self, color):
        self.color_var.set(color)
        # Update selected annotation color if any
        canvas = self.master.master.annotation_canvas
        if canvas.selected_balloon:
            canvas.selected_balloon.set_color(color)
            canvas.redraw_annotations()

    def choose_custom_color(self):
        color = colorchooser.askcolor(self.color_var.get())[1]
        if color:
            self.set_color(color)

    def on_size_change(self, value):
        # Update selected annotation size if any
        canvas = self.master.master.annotation_canvas
        if canvas.selected_balloon:
            canvas.selected_balloon.set_size(float(value))
            canvas.redraw_annotations()

    def on_shape_change(self):
        # Update selected annotation shape if any
        canvas = self.master.master.annotation_canvas
        if canvas.selected_balloon:
            canvas.selected_balloon.set_shape(self.shape_var.get())
            canvas.redraw_annotations()
    
    def on_dimension_change(self, event=None):
        # Update selected annotation dimension
        canvas = self.master.master.annotation_canvas
        if canvas.selected_balloon:
            canvas.selected_balloon.set_dimension(self.dimension_var.get())
            self.update_annotation_list(canvas.annotations)
            
    def on_tolerance_change(self, event=None):
        # Update selected annotation tolerance
        canvas = self.master.master.annotation_canvas
        if canvas.selected_balloon:
            canvas.selected_balloon.set_tolerance(self.tolerance_var.get())
            self.update_annotation_list(canvas.annotations)
            
    def on_remarks_change(self, event=None):
        # Update selected annotation remarks
        canvas = self.master.master.annotation_canvas
        if canvas.selected_balloon:
            canvas.selected_balloon.set_remarks(self.remarks_var.get())
            self.update_annotation_list(canvas.annotations)

    def delete_selected_annotation(self):
        # Get selected item
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            b_no = item['values'][0]
            # Find and delete corresponding balloon
            canvas = self.master.master.annotation_canvas
            for balloon in canvas.annotations:
                if balloon.number == str(b_no):
                    canvas.selected_balloon = balloon
                    canvas.remove_selected_balloon()
                    break

    def on_annotation_select(self, event):
        # Get selected item
        selection = self.tree.selection()
        if selection:
            item = self.tree.item(selection[0])
            b_no = item['values'][0]
            # Find and select corresponding balloon
            canvas = self.master.master.annotation_canvas
            for balloon in canvas.annotations:
                if balloon.number == str(b_no):
                    canvas.selected_balloon = balloon
                    # Update properties to match selection
                    self.color_var.set(balloon.color)
                    self.size_var.set(balloon.size)
                    self.shape_var.set(balloon.shape)
                    self.dimension_var.set(balloon.dimension)
                    self.tolerance_var.set(balloon.tolerance)
                    self.remarks_var.set(balloon.remarks)
                    
                    # Update the editable index field if in Editable Mode
                    if self.editable_index_mode.get():
                        self.index_var.set(balloon.number)
                    break

    def update_annotation_list(self, annotations):
        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add current annotations
        for balloon in annotations:
            self.tree.insert(
                "",
                "end",
                values=(
                    balloon.number,
                    f"({int(balloon.x)}, {int(balloon.y)})",
                    f"{balloon.size:.1f}x",
                    balloon.shape,
                    balloon.dimension,
                    balloon.tolerance,
                    balloon.remarks
                )
            )
