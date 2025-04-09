import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from components.canvas import AnnotationCanvas
from components.toolbar import Toolbar
from components.sidebar import Sidebar
from utils.pdf_handler import PDFHandler
from utils.balloon_marker import BalloonMarker
import os, sys
import pandas as pd
from pandas import ExcelWriter
import openpyxl


class TechnicalAnnotator(tk.Tk):
    def __init__(self):
        super().__init__()

        # Configure main window
        self.title("Technical Drawing Annotator")
           # Cross-platform way to maximize the window
           
        self.state('zoomed')  # For Windows, use 'zoomed' to maximize
        """ self.update_idletasks()  # Make sure window is created before setting geometry
        width = self.winfo_screenwidth()
        height = self.winfo_screenheight()
        self.geometry(f"{width}x{height}+0+0")
        self.configure(bg="#F5F5F5") """
        
        # Create toolbar
        self.toolbar = Toolbar(self)
        self.toolbar.pack(fill=tk.X, pady=2)
        
        # Track open files
        self.open_files = []
        self.current_file_index = -1

        # Configure styles
        self.style = ttk.Style()
        self.style.configure("Toolbar.TFrame", background="#2196F3")
        self.style.configure("Sidebar.TFrame", background="#F5F5F5")

        # Create main container
        self.main_container = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        

        # Create canvas frame and canvas
        self.canvas_frame = ttk.Frame(self.main_container)
        self.annotation_canvas = AnnotationCanvas(self.canvas_frame)
        self.annotation_canvas.pack(fill=tk.BOTH, expand=True)

        # Create sidebar
        self.sidebar = Sidebar(self.main_container)

        # Add panels to PanedWindow with sidebar being smaller
        self.main_container.add(self.canvas_frame, weight=4)  # 80% of space
        self.main_container.add(self.sidebar, weight=1)       # 20% of space

        # Create menu bar
        self.create_menu_bar()

        # Setup event bindings
        self.setup_bindings()

        # Initialize PDF handler
        self.pdf_handler = PDFHandler()

    def create_menu_bar(self):
        """Create menu bar with File and other menus"""
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)
        
        # File menu
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Open", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Save", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Save As PDF", command=self.save_file_as_pdf)
        file_menu.add_command(label="Export to Excel", command=self.export_to_excel)
        file_menu.add_separator()
        """ file_menu.add_command(label="Close Current File", command=self.close_current_file) """
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.quit)
        
        # Edit menu
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Undo", command=lambda: self.annotation_canvas.undo(), accelerator="Ctrl+Z")
        edit_menu.add_command(label="Redo", command=lambda: self.annotation_canvas.redo(), accelerator="Ctrl+Y")
        edit_menu.add_separator()
        edit_menu.add_command(label="Delete Selected", command=lambda: self.annotation_canvas.remove_selected_balloon(), accelerator="Delete")

        # View menu
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="View", menu=view_menu)
        view_menu.add_command(label="Zoom In", command=self.toolbar.zoom_in, accelerator="Ctrl++")
        view_menu.add_command(label="Zoom Out", command=self.toolbar.zoom_out, accelerator="Ctrl+-")
        view_menu.add_command(label="Fit to Screen", command=self.fit_to_screen, accelerator="Ctrl+F")
        
        # Tools menu
        tools_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="AI Assistant", command=self.show_ai_assistant)
        tools_menu.add_command(label="Analysis", command=self.analyze_annotations)
        
        # Help menu
        help_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="User Guide", command=self.show_user_guide)
        help_menu.add_command(label="About", command=self.show_about)

    def setup_bindings(self):
        self.bind("<Control-o>", lambda e: self.open_file())
        self.bind("<Control-s>", lambda e: self.save_file())
        self.bind("<Control-f>", lambda e: self.fit_to_screen())
        self.bind("<Control-plus>", lambda e: self.toolbar.zoom_in())
        self.bind("<Control-minus>", lambda e: self.toolbar.zoom_out())

    def open_file(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("All supported files", "*.pdf *.tiff *.tif *.jpg *.jpeg *.png *.bmp *.tma"),
                ("PDF files", "*.pdf"),
                ("Image files", "*.tiff *.tif *.jpg *.jpeg *.png *.bmp"),
                ("Technical Markup Annotations", "*.tma")
            ])
        if not file_path:
            return
    
              
 
        try:
            ext = os.path.splitext(file_path)[1].lower()
            if ext == '.tma':
                # Load annotations from .tma file
                annotations = self.pdf_handler.load_annotation_file(file_path)
                self.annotation_canvas.annotations = []
                self.annotation_canvas.balloon_counter = 1
                for x, y, b_no, color, size, shape, dimension, tolerance, remarks in annotations:
                    balloon = BalloonMarker(x, y, b_no, color, size, shape, dimension, tolerance, remarks)
                    self.annotation_canvas.annotations.append(balloon)
                    self.annotation_canvas.balloon_counter = max(
                        self.annotation_canvas.balloon_counter,
                        int(b_no) + 1
                    )
            else:
                # Load new drawing
                self.pdf_handler.load_file(file_path)
                self.annotation_canvas.annotations = []
                self.annotation_canvas.balloon_counter = 1
 
            # Update display
            self.annotation_canvas.display_pdf(self.pdf_handler.current_page)
            self.sidebar.update_annotation_list(self.annotation_canvas.annotations)
        
            # Automatically fit view to screen after opening file
            self.fit_to_screen()
        
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open file: {str(e)}")

    def display_current_file(self, index):
        if not self.open_files or index < 0 or index >= len(self.open_files):
            return False

        if self.current_file_index >= 0 < len(self.open_files):
            self.open_files[self.current_file_index]['annotations'] = self.annotation_canvas.annotations

        self.current_file_index = index
        current_file = self.open_files[index]

        if current_file['image'] is None and os.path.exists(current_file['path']):
            current_file['image'] = self.pdf_handler.load_file(current_file['path'])

        self.annotation_canvas.annotations = current_file['annotations']
        self.annotation_canvas.balloon_counter = current_file.get('balloon_counter', 1)

        if current_file['image']:
            self.annotation_canvas.display_pdf(current_file['image'])

        self.sidebar.update_annotation_list(self.annotation_canvas.annotations)
        self.title(f"Technical Drawing Annotator - {current_file['name']}")
        self.fit_to_screen()
        return True

    def close_current_file(self):
        if not self.open_files or self.current_file_index < 0:
            return

        if self.annotation_canvas.annotations and not messagebox.askyesno("Close File", "Do you want to close this file? Any unsaved changes will be lost."):
            return

        self.open_files.pop(self.current_file_index)

        if self.open_files:
            self.current_file_index = max(0, min(self.current_file_index, len(self.open_files) - 1))
            self.display_current_file(self.current_file_index)
        else:
            self.current_file_index = -1
            self.annotation_canvas.current_page = None
            self.annotation_canvas.annotations.clear()
            self.annotation_canvas.delete("all")
            self.annotation_canvas.balloon_counter = 1
            self.sidebar.update_annotation_list([])
            self.title("Technical Drawing Annotator")

        self.update_window_menu()

    def update_window_menu(self):
        window_menu = None
        for i in range(self.menu_bar.index("end") + 1):
            if self.menu_bar.entrycget(i, "label") == "Window":
                window_menu = self.menu_bar.nametowidget(self.menu_bar.entrycget(i, "menu"))
                break

        if window_menu is None:
            window_menu = tk.Menu(self.menu_bar, tearoff=0)
            self.menu_bar.add_cascade(label="Window", menu=window_menu)

        window_menu.delete(0, "end")

        for i, file_data in enumerate(self.open_files):
            window_menu.add_command(
                label=file_data['name'],
                command=lambda idx=i: self.display_current_file(idx),
               # background="#E0E0E0" if i == self.current_file_index else "SystemMenu"
            )
            if i == self.current_file_index:
                window_menu.entryconfig(i, background="#E0E0E0")


            
    def export_to_excel(self):
        """Export annotation data to Excel"""
        if not self.annotation_canvas.annotations:
            messagebox.showinfo("Export", "No annotations to export.")
            return
            
        # try:
            # Import the required module
            """ import pandas as pd
            from pandas import ExcelWriter
            import openpyxl """
            
        file_path = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")]
        )
            
        if not file_path:
            return
                
        # Create a dataframe from annotations
        data = []
        for balloon in self.annotation_canvas.annotations:
            data.append({
                'B_No#': balloon.number,
                'X Position': int(balloon.x),
                'Y Position': int(balloon.y),
                'Size': balloon.size,
                'Shape': balloon.shape,
                'Color': balloon.color,
                'Dimension': balloon.dimension,
                'Tolerance': balloon.tolerance,
                'Remarks': balloon.remarks
            })
                
        df = pd.DataFrame(data)
            
        # Create Excel file
        with ExcelWriter(file_path, engine='openpyxl') as writer:
            df.to_excel(writer, sheet_name='Annotations', index=False)
                
        messagebox.showinfo("Export Successful", f"Annotations exported to {file_path}")
            
        
            
    def save_file_as_pdf(self):
        """Save annotations to PDF"""
        try:
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[("PDF files", "*.pdf")]
            )
            
            if not file_path:
                return
                
            annotations = self.annotation_canvas.get_annotations()
            self.pdf_handler.save_annotations(file_path, annotations)
            
            messagebox.showinfo("Success", "File saved as PDF successfully!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save PDF: {str(e)}")
            
    def fit_to_screen(self, event=None):
        """Adjust canvas scale and position to fit within the window"""
        if not self.annotation_canvas.current_page:
            return

        canvas_width = self.annotation_canvas.winfo_width()
        canvas_height = self.annotation_canvas.winfo_height()

        if canvas_width <= 1 or canvas_height <= 1:  # Avoid division by zero
            self.after(100, self.fit_to_screen)  # Try again after GUI has sized
            return

        image_width = self.annotation_canvas.image_width
        image_height = self.annotation_canvas.image_height

        if image_width <= 0 or image_height <= 0:
            return

        scale_x = canvas_width / image_width
        scale_y = canvas_height / image_height
        new_scale = min(scale_x, scale_y) * 0.95  # 95% to add some margin

        # Update canvas scale
        self.annotation_canvas.scale = new_scale
        self.annotation_canvas.pan_x = (canvas_width - image_width * new_scale) / 2
        self.annotation_canvas.pan_y = (canvas_height - image_height * new_scale) / 2
        self.annotation_canvas.scale_all()

    def save_file(self):
        try:
            # If this is an existing file, save to it
            if self.current_file_index >= 0 and 'path' in self.open_files[self.current_file_index]:
                file_path = self.open_files[self.current_file_index]['path']
                ext = os.path.splitext(file_path)[1].lower()
                
                # Only save to original path if it's a .tma file
                if ext == '.tma':
                    self.pdf_handler.save_annotation_file(file_path, self.annotation_canvas.get_annotations())
                    messagebox.showinfo("Success", "File saved successfully!")
                    return
            
            # Otherwise do a save-as dialog
            file_path = filedialog.asksaveasfilename(
                defaultextension=".pdf",
                filetypes=[
                    ("PDF files", "*.pdf"),
                    ("Technical Markup Annotations", "*.tma")
                ])
                
            if not file_path:
                return

            annotations = self.annotation_canvas.get_annotations()
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.tma':
                self.pdf_handler.save_annotation_file(file_path, annotations)
            else:
                self.pdf_handler.save_annotations(file_path, annotations)

            messagebox.showinfo("Success", "File saved successfully!")
            
            # If current file was untitled, update it
            if self.current_file_index >= 0:
                self.open_files[self.current_file_index]['path'] = file_path
                self.open_files[self.current_file_index]['name'] = os.path.basename(file_path)
                self.title(f"Technical Drawing Annotator - {self.open_files[self.current_file_index]['name']}")
                self.update_window_menu()
                
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save file: {str(e)}")
            
    def show_ai_assistant(self):
        """Show AI Assistant dialog for generative AI features"""
        ai_window = tk.Toplevel(self)
        ai_window.title("AI Drawing Assistant")
        ai_window.geometry("600x500")
        ai_window.minsize(500, 400)
        
        # Make it modal
        ai_window.transient(self)
        ai_window.grab_set()
        
        # Create UI
        frame = ttk.Frame(ai_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="AI Drawing Assistant", font=("Arial", 16, "bold")).pack(pady=(0, 10))
        
        # Feature buttons
        features_frame = ttk.LabelFrame(frame, text="AI Features")
        features_frame.pack(fill=tk.X, pady=10)
        
        ttk.Button(
            features_frame, 
            text="Analyze Current Drawing", 
            command=lambda: self.ai_analyze_drawing(ai_window)
        ).pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(
            features_frame, 
            text="Generate Dimension Suggestions", 
            command=lambda: self.ai_suggest_dimensions(ai_window)
        ).pack(fill=tk.X, pady=5, padx=10)
        
        ttk.Button(
            features_frame, 
            text="Generate Technical Documentation", 
            command=lambda: self.ai_generate_documentation(ai_window)
        ).pack(fill=tk.X, pady=5, padx=10)
        
        # Text input area
        prompt_frame = ttk.LabelFrame(frame, text="Custom AI Prompt")
        prompt_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.ai_prompt_text = tk.Text(prompt_frame, wrap=tk.WORD, height=5)
        self.ai_prompt_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        self.ai_prompt_text.insert("1.0", "Describe what you want the AI to do with your drawing...")
        
        # Submit button
        ttk.Button(
            prompt_frame, 
            text="Submit Prompt", 
            command=lambda: self.ai_process_custom_prompt(ai_window)
        ).pack(pady=10)
        
        # Response area
        response_frame = ttk.LabelFrame(frame, text="AI Response")
        response_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.ai_response_text = tk.Text(response_frame, wrap=tk.WORD, state="disabled")
        self.ai_response_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Close button
        ttk.Button(frame, text="Close", command=ai_window.destroy).pack(pady=10)
        
    def ai_analyze_drawing(self, parent_window):
        """Perform AI analysis of current drawing"""
        if not self.annotation_canvas.annotations:
            self.update_ai_response("No annotations found. Please add some balloons to analyze.")
            return
            
        # This is where you would call an actual AI service
        # For now, we'll simulate a response
        response = "Drawing Analysis:\n\n"
        response += f"- {len(self.annotation_canvas.annotations)} annotations found\n"
        response += f"- Most common shape: {self.get_most_common_shape()}\n"
        response += f"- Most common color: {self.get_most_common_color()}\n"
        response += "- Balloon distribution: Mostly concentrated in center\n"
        response += "- Suggested improvements: Consider adding more details in the upper right section\n"
        
        self.update_ai_response(response)
        
    def ai_suggest_dimensions(self, parent_window):
        """Generate dimension suggestions based on balloon positions"""
        if not self.annotation_canvas.annotations:
            self.update_ai_response("No annotations found. Please add some balloons first.")
            return
            
        # Simulate AI dimension suggestions
        response = "Dimension Suggestions:\n\n"
        
        # Identify balloons without dimensions
        no_dimension_balloons = [b for b in self.annotation_canvas.annotations if not b.dimension]
        
        if no_dimension_balloons:
            response += f"Found {len(no_dimension_balloons)} balloons without dimensions. Suggestions:\n\n"
            
            for balloon in no_dimension_balloons[:5]:  # Limit to first 5 for brevity
                x, y = balloon.x, balloon.y
                # Generate fake dimension based on position
                suggested_dim = f"{int(x % 100)}.{int(y % 100)}"
                response += f"Balloon {balloon.number}: Suggested dimension: {suggested_dim} mm\n"
                
            if len(no_dimension_balloons) > 5:
                response += f"... and {len(no_dimension_balloons) - 5} more\n"
        else:
            response += "All balloons already have dimensions defined."
            
        self.update_ai_response(response)
        
    def ai_generate_documentation(self, parent_window):
        """Generate documentation based on annotations"""
        if not self.annotation_canvas.annotations:
            self.update_ai_response("No annotations found. Please add some balloons first.")
            return
            
        # Simulate documentation generation
        response = "Technical Documentation:\n\n"
        response += "Component Specifications\n"
        response += "------------------------\n\n"
        
        # Group by dimensions
        dimensions = {}
        for balloon in self.annotation_canvas.annotations:
            dim = balloon.dimension if balloon.dimension else "Unspecified"
            if dim not in dimensions:
                dimensions[dim] = []
            dimensions[dim].append(balloon)
            
        for dim, balloons in dimensions.items():
            response += f"Dimension: {dim}\n"
            response += f"Count: {len(balloons)}\n"
            response += f"Balloons: {', '.join(b.number for b in balloons)}\n"
            
            # Add tolerances if available
            tolerances = set(b.tolerance for b in balloons if b.tolerance)
            if tolerances:
                response += f"Tolerances: {', '.join(tolerances)}\n"
                
            response += "\n"
            
        self.update_ai_response(response)
        
    def ai_process_custom_prompt(self, parent_window):
        """Process custom AI prompt"""
        prompt = self.ai_prompt_text.get("1.0", tk.END).strip()
        
        if not prompt or prompt == "Describe what you want the AI to do with your drawing...":
            self.update_ai_response("Please enter a specific prompt.")
            return
            
        # Simulate AI processing
        response = f"Response to: \"{prompt}\"\n\n"
        response += "This is a simulated AI response. In a production environment, this would connect to an AI service like OpenAI's GPT or another large language model to process your request.\n\n"
        
        # Add some fake analysis based on words in the prompt
        if "dimension" in prompt.lower():
            response += "Dimension Analysis: The current drawing contains various dimension specifications that could be optimized.\n"
        if "improve" in prompt.lower() or "suggest" in prompt.lower():
            response += "Suggestions: Consider reorganizing the annotations to improve clarity. Group related components together.\n"
        if "explain" in prompt.lower() or "describe" in prompt.lower():
            response += "Drawing Description: This appears to be a technical drawing with multiple annotated components.\n"
            
        self.update_ai_response(response)
        
    def update_ai_response(self, text):
        """Update the AI response text area"""
        self.ai_response_text.config(state="normal")
        self.ai_response_text.delete("1.0", tk.END)
        self.ai_response_text.insert("1.0", text)
        self.ai_response_text.config(state="disabled")
        
    def get_most_common_shape(self):
        """Get the most common shape among annotations"""
        if not self.annotation_canvas.annotations:
            return "None"
            
        shapes = {}
        for balloon in self.annotation_canvas.annotations:
            shapes[balloon.shape] = shapes.get(balloon.shape, 0) + 1
            
        return max(shapes.items(), key=lambda x: x[1])[0].capitalize()
        
    def get_most_common_color(self):
        """Get the most common color among annotations"""
        if not self.annotation_canvas.annotations:
            return "None"
            
        colors = {}
        for balloon in self.annotation_canvas.annotations:
            colors[balloon.color] = colors.get(balloon.color, 0) + 1
            
        return max(colors.items(), key=lambda x: x[1])[0]
        
    def show_user_guide(self):
        """Show application user guide"""
        guide_window = tk.Toplevel(self)
        guide_window.title("User Guide")
        guide_window.geometry("600x500")
        guide_window.minsize(500, 400)
        
        # Make it modal
        guide_window.transient(self)
        guide_window.grab_set()
        
        frame = ttk.Frame(guide_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Technical Drawing Annotator User Guide", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        guide_text = tk.Text(frame, wrap=tk.WORD)
        guide_text.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = ttk.Scrollbar(guide_text, orient="vertical", command=guide_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        guide_text.configure(yscrollcommand=scrollbar.set)
        
        guide_content = """
User Guide for Technical Drawing Annotator

1. File Menu
   - Open: Open a PDF or image file to annotate
   - Save: Save the current annotations
   - Save As PDF: Export with annotations as PDF
   - Export to Excel: Export annotation data as Excel file
   - Close Current File: Close the active file
   - Exit: Quit the application

2. Navigation
   - Pan: Middle mouse button or Pan tool
   - Zoom: Mouse wheel or Zoom In/Out buttons
   - Fit to Screen: Ctrl+F or View menu

3. Annotation Tools
   - Select: Select and move annotations
   - Balloon: Add balloon markers
   - Properties: Change color, size, shape, etc.

4. Editable Index Mode
   - Enable/disable from sidebar
   - Allows custom balloon numbering
   - Double-click annotation in list to change number

5. AI Features
   - Drawing Analysis: Get insights about your annotations
   - Dimension Suggestions: AI-generated dimension proposals
   - Documentation: Generate technical specs from annotations

6. Working with Multiple Files
   - Open multiple files simultaneously
   - Switch between files using Window menu
   - Each file maintains its own annotations
        """
        
        guide_text.insert("1.0", guide_content)
        guide_text.config(state="disabled")
        
        ttk.Button(frame, text="Close", command=guide_window.destroy).pack(pady=10)
        
    def show_about(self):
        """Show about dialog"""
        messagebox.showinfo(
            "About", 
            "Technical Drawing Annotator\n\nVersion 1.0\n\nA tool for annotating technical drawings with balloon markers."
        )
        
    def analyze_annotations(self):
        """Analyze and show statistics about annotations"""
        if not self.annotation_canvas.annotations:
            messagebox.showinfo("Analysis", "No annotations to analyze.")
            return
            
        stats_window = tk.Toplevel(self)
        stats_window.title("Annotation Analysis")
        stats_window.geometry("400x300")
        stats_window.minsize(400, 300)
        
        # Make it modal
        stats_window.transient(self)
        stats_window.grab_set()
        
        frame = ttk.Frame(stats_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        ttk.Label(frame, text="Annotation Statistics", font=("Arial", 14, "bold")).pack(pady=(0, 10))
        
        # Calculate statistics
        annotations = self.annotation_canvas.annotations
        total = len(annotations)
        
        # Count by shape
        shapes = {}
        for balloon in annotations:
            shapes[balloon.shape] = shapes.get(balloon.shape, 0) + 1
            
        # Count by color
        colors = {}
        for balloon in annotations:
            colors[balloon.color] = colors.get(balloon.color, 0) + 1
            
        # Display statistics
        stats_text = f"Total annotations: {total}\n\n"
        
        stats_text += "Shapes:\n"
        for shape, count in shapes.items():
            percentage = (count / total) * 100
            stats_text += f"  {shape.capitalize()}: {count} ({percentage:.1f}%)\n"
            
        stats_text += "\nColors:\n"
        for color, count in colors.items():
            percentage = (count / total) * 100
            stats_text += f"  {color}: {count} ({percentage:.1f}%)\n"
            
        stats_text += "\nDimensions:\n"
        with_dim = sum(1 for b in annotations if b.dimension)
        without_dim = total - with_dim
        stats_text += f"  With dimension: {with_dim} ({(with_dim / total) * 100:.1f}%)\n"
        stats_text += f"  Without dimension: {without_dim} ({(without_dim / total) * 100:.1f}%)\n"
        
        stats_label = ttk.Label(frame, text=stats_text, justify=tk.LEFT)
        stats_label.pack(fill=tk.BOTH, expand=True)
        
        ttk.Button(frame, text="Close", command=stats_window.destroy).pack(pady=10)

if __name__ == "__main__":
    app = TechnicalAnnotator()
    app.mainloop()