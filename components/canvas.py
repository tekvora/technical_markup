import tkinter as tk
from tkinter import ttk
from utils.balloon_marker import BalloonMarker
from PIL import Image, ImageTk
from tkinter import messagebox # Added to handle duplicate number error

class AnnotationCanvas(tk.Canvas):
    def __init__(self, parent):
        super().__init__(
            parent,
            bg="white",
            highlightthickness=0
        )
        self.container = parent
        self.main_window = self.container.master

        # Initialize state variables
        self.scale = 1.0
        self.pan_x = 0
        self.pan_y = 0
        self.annotations = []
        self.undo_stack = []
        self.redo_stack = []
        self.current_page = None
        self.drawing_mode = "select"
        self.selected_balloon = None
        self.panning = False # Added for panning

        # Store original image dimensions
        self.image_width = 0
        self.image_height = 0

        # Bind mouse events
        self.bind("<ButtonPress-1>", self.on_press)
        self.bind("<B1-Motion>", self.on_drag)
        self.bind("<ButtonRelease-1>", self.on_release)
        self.bind("<ButtonPress-2>", self.on_pan_start)  # Middle button press
        self.bind("<B2-Motion>", self.on_pan)  # Middle button drag
        self.bind("<ButtonRelease-2>", self.on_pan_end)  # Middle button release
        self.bind("<MouseWheel>", self.on_mousewheel)

        # Bind keyboard shortcuts
        self.bind_all("<Control-z>", self.undo)
        self.bind_all("<Control-y>", self.redo)
        self.bind_all("<Delete>", self.remove_selected_balloon)

        # Create balloon counter
        self.balloon_counter = 1

    def add_balloon(self, event):
        """Add a balloon marker at the clicked position"""
        if not self.current_page:
            return

        if self.drawing_mode != "balloon": # Changed mode to drawing_mode
            return

        # Calculate position in image coordinates
        x = (event.x - self.pan_x) / self.scale
        y = (event.y - self.pan_y) / self.scale

        # Create balloon with current properties
        main_window = self.winfo_toplevel()
        shape = main_window.sidebar.shape_var.get()
        color = main_window.sidebar.color_var.get()
        size = main_window.sidebar.size_var.get()
        dimension = main_window.sidebar.dimension_var.get()
        tolerance = main_window.sidebar.tolerance_var.get()
        remarks = main_window.sidebar.remarks_var.get()

        # Check if in editable index mode
        if main_window.sidebar.editable_index_mode.get():
            # Get balloon number from input field
            custom_number = main_window.sidebar.index_var.get()

            # Validate that the number is unique
            if custom_number and any(b.number == custom_number for b in self.annotations):
                messagebox.showerror("Duplicate Number", "A balloon with this number already exists!")
                return

            # If custom number is provided, use it, otherwise use sequential
            balloon_number = custom_number if custom_number else str(self.balloon_counter)
        else:
            # In standard mode, use sequential numbering
            balloon_number = str(self.balloon_counter)

        # Add balloon marker
        new_balloon = BalloonMarker(x, y, balloon_number, color, size, shape, dimension, tolerance, remarks)
        self.annotations.append(new_balloon)

        # Save state for undo
        self.undo_stack.append(("add", new_balloon, self.balloon_counter))
        self.redo_stack.clear()

        # Increment counter for next balloon (only used in standard mode)
        self.balloon_counter += 1

        # Redraw annotations
        self.redraw_annotations()

        # Update sidebar annotation list
        main_window.sidebar.update_annotation_list(self.annotations)

    def remove_selected_balloon(self):
        """Remove the currently selected balloon"""
        if self.selected_balloon:
            # Store balloon and its index for undo
            index = self.annotations.index(self.selected_balloon)
            self.undo_stack.append(("remove", self.selected_balloon, index))
            self.redo_stack.clear()

            # Remove from annotations
            self.annotations.remove(self.selected_balloon)
            self.selected_balloon = None

            # Get main window
            main_window = self.winfo_toplevel()

            # Update numbering only in standard mode
            if not main_window.sidebar.editable_index_mode.get():
                self.renumber_balloons()

            # Redraw
            self.redraw_annotations()

            # Update sidebar annotation list
            main_window.sidebar.update_annotation_list(self.annotations)

    def renumber_balloons(self):
        """Update balloon numbers to be sequential"""
        for i, balloon in enumerate(self.annotations, 1):
            balloon.number = str(i)
        self.balloon_counter = len(self.annotations) + 1

    def undo(self, event=None):
        """Undo last action"""
        if self.undo_stack:
            action = self.undo_stack.pop()
            if action[0] == "add":
                # Remove added balloon
                self.annotations.remove(action[1])
                self.balloon_counter = action[2]
                self.redo_stack.append(("remove", action[1], len(self.annotations)))
            elif action[0] == "remove":
                # Restore removed balloon
                self.annotations.insert(action[2], action[1])
                self.balloon_counter = max(int(b.number) for b in self.annotations) + 1
                self.redo_stack.append(("add", action[1], self.balloon_counter))
            self.renumber_balloons()
            self.redraw_annotations()

    def redo(self, event=None):
        """Redo last undone action"""
        if self.redo_stack:
            action = self.redo_stack.pop()
            if action[0] == "add":
                # Re-add balloon
                self.annotations.append(action[1])
                self.balloon_counter = max(int(b.number) for b in self.annotations) + 1
                self.undo_stack.append(("add", action[1], self.balloon_counter))
            elif action[0] == "remove":
                # Re-remove balloon
                self.annotations.remove(action[1])
                self.undo_stack.append(("remove", action[1], action[2]))
            self.renumber_balloons()
            self.redraw_annotations()

    def display_pdf(self, page_image):
        """Display PDF page on canvas"""
        # Store original image size
        self.image_width = page_image.width
        self.image_height = page_image.height

        # Resize image based on scale
        scaled_width = int(self.image_width * self.scale)
        scaled_height = int(self.image_height * self.scale)
        scaled_image = page_image.resize((scaled_width, scaled_height), Image.LANCZOS)

        self.current_page = ImageTk.PhotoImage(scaled_image)
        self.delete("all")
        self.create_image(self.pan_x, self.pan_y, image=self.current_page, anchor="nw")
        self.redraw_annotations()

    def screen_to_canvas(self, x, y):
        """Convert screen coordinates to canvas coordinates"""
        return ((x - self.pan_x) / self.scale, 
                (y - self.pan_y) / self.scale)

    def canvas_to_screen(self, x, y):
        """Convert canvas coordinates to screen coordinates"""
        return (x * self.scale + self.pan_x, 
                y * self.scale + self.pan_y)

    def on_press(self, event):
        self.last_x = event.x
        self.last_y = event.y

        if self.drawing_mode == "balloon":
            cx, cy = self.screen_to_canvas(event.x, event.y)
            self.add_balloon(event) # Pass event to add_balloon
        elif self.drawing_mode == "select":
            self.select_annotation(event.x, event.y)

    def on_drag(self, event):
        dx = event.x - self.last_x
        dy = event.y - self.last_y

        if self.drawing_mode == "pan":
            self.pan_x += dx
            self.pan_y += dy
            self.move_all(dx, dy)
        elif self.drawing_mode == "select" and self.selected_balloon:
            cx, cy = self.screen_to_canvas(event.x, event.y)
            px, py = self.screen_to_canvas(self.last_x, self.last_y)
            self.selected_balloon.move(cx - px, cy - py)
            self.redraw_annotations()

        self.last_x = event.x
        self.last_y = event.y

    def on_release(self, event):
        self.selected_balloon = None

    def on_mousewheel(self, event):
        """Handle zoom with mousewheel"""
        # Get mouse position relative to canvas
        x = self.canvasx(event.x)
        y = self.canvasy(event.y)

        # Calculate old scale
        old_scale = self.scale

        # Update scale
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1

        # Calculate scale difference
        scale_diff = self.scale / old_scale

        # Adjust pan to zoom towards mouse position
        self.pan_x = x - (x - self.pan_x) * scale_diff
        self.pan_y = y - (y - self.pan_y) * scale_diff

        # Apply zoom transformation
        self.scale_all()

    def select_annotation(self, x, y):
        """Select balloon at given position"""
        cx, cy = self.screen_to_canvas(x, y)
        for balloon in reversed(self.annotations):
            if balloon.contains_point(cx, cy):
                self.selected_balloon = balloon
                return
        self.selected_balloon = None

    def draw_balloon(self, balloon):
        """Draw single balloon marker"""
        # Convert canvas coordinates to screen coordinates
        x, y = self.canvas_to_screen(balloon.x, balloon.y)
        r = 20 * self.scale * balloon.size  # Radius

        if balloon.shape == "circle":
            self.create_oval(
                x-r, y-r, x+r, y+r,
                fill=balloon.color,
                outline="#212121",
                tags=("balloon", str(balloon.number))
            )
        elif balloon.shape == "square":
            self.create_rectangle(
                x-r, y-r, x+r, y+r,
                fill=balloon.color,
                outline="#212121",
                tags=("balloon", str(balloon.number))
            )
        elif balloon.shape == "triangle":
            points = [
                x, y-r,  # Top
                x-r, y+r,  # Bottom left
                x+r, y+r   # Bottom right
            ]
            self.create_polygon(
                points,
                fill=balloon.color,
                outline="#212121",
                tags=("balloon", str(balloon.number))
            )

        # Add text
        self.create_text(
            x, y,
            text=balloon.number,
            fill="#FFFFFF",
            font=("Roboto", int(12 * self.scale * balloon.size)),
            tags=("balloon", str(balloon.number))
        )

    def redraw_annotations(self):
        """Redraw all annotations"""
        self.delete("balloon")
        for balloon in self.annotations:
            self.draw_balloon(balloon)

    def move_all(self, dx, dy):
        """Move all elements on canvas"""
        self.move("all", dx, dy)

    def scale_all(self):
        """Apply scaling to all elements"""
        if self.current_page and hasattr(self, 'image_width'):
            # Resize image
            scaled_width = int(self.image_width * self.scale)
            scaled_height = int(self.image_height * self.scale)

            # Create new scaled image
            main_window = self.winfo_toplevel()
            original_image = main_window.pdf_handler.current_page
            if original_image:
                scaled_image = original_image.resize(
                    (scaled_width, scaled_height), 
                    Image.LANCZOS
                )
                self.current_page = ImageTk.PhotoImage(scaled_image)

                # Redraw everything
                self.delete("all")
                self.create_image(
                    self.pan_x, self.pan_y,
                    image=self.current_page,
                    anchor="nw"
                )
                self.redraw_annotations()

    def on_pan_start(self, event):
        """Start panning with middle mouse button"""
        self.last_x = event.x
        self.last_y = event.y
        self.panning = True

    def on_pan(self, event):
        """Pan view with middle mouse button"""
        if self.panning:
            dx = event.x - self.last_x
            dy = event.y - self.last_y
            self.pan_x += dx
            self.pan_y += dy
            self.move_all(dx, dy)
            self.last_x = event.x
            self.last_y = event.y

    def on_pan_end(self, event):
        """End panning"""
        self.panning = False

    def get_annotations(self):
        """Return list of annotations"""
        return [(balloon.x, balloon.y, balloon.number, 
                balloon.color, balloon.size, balloon.shape) 
                for balloon in self.annotations]