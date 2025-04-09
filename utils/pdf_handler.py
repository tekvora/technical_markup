import fitz  # PyMuPDF
from PIL import Image, ImageDraw, ImageFont
import io
import os
import json

class PDFHandler:
    def __init__(self):
        self.document = None
        self.current_page = None
        self.page_number = 0
        self.file_path = None

    def load_file(self, file_path):
        """Load file and convert first page to image"""
        try:
            self.file_path = file_path
            ext = os.path.splitext(file_path)[1].lower()

            if ext == '.pdf':
                self.document = fitz.open(file_path)
                self.page_number = 0
                self.load_page(self.page_number)
            elif ext in ['.tiff', '.tif', '.jpg', '.jpeg', '.png', '.bmp']:
                self.document = None
                self.current_page = Image.open(file_path)
                # Convert to RGB if needed
                if self.current_page.mode != 'RGB':
                    self.current_page = self.current_page.convert('RGB')
        except Exception as e:
            raise Exception(f"Error loading file: {str(e)}")

    def load_page(self, page_number):
        """Load specific page and convert to PIL Image"""
        if self.document is None:
            return

        page = self.document[page_number]
        pix = page.get_pixmap()

        # Convert to PIL Image
        img_data = pix.samples
        img = Image.frombytes("RGB", [pix.width, pix.height], img_data)
        self.current_page = img

    def save_annotations(self, file_path, annotations):
        """Save annotations by merging them into the image and exporting as a non-editable PDF."""
        if not self.current_page:
            return
        # Increase resolution by resizing the image
        scale_factor = 2  # Increase resolution by 2x
        new_width = self.current_page.width * scale_factor
        new_height = self.current_page.height * scale_factor
        # Resize image to increase resolution
        annotated_image = self.current_page.resize((new_width, new_height), Image.LANCZOS)
        draw = ImageDraw.Draw(annotated_image)
        # Draw each balloon onto the image
        for annotation in annotations:
            x, y, b_no, color, size, shape, dimension, tolerance, remarks = (
                annotation + (None,) * (9 - len(annotation))
            )
            # Scale coordinates
            x, y = int(x * scale_factor), int(y * scale_factor)
            radius = int(14 * size * scale_factor)  # Adjust balloon size
            # Dynamically set font size based on balloon size
            font_size = int(14 * size * scale_factor)  # Base size is 12
            try:
                font = ImageFont.truetype("arial.ttf", font_size)
            except IOError:
                font = ImageFont.load_default()
            fill_color = color  # Balloon color
            outline_color = "#000000"  # Black outline
            # Draw balloon shapes
            if shape == "circle":
                draw.ellipse((x - radius, y - radius, x + radius, y + radius), fill=fill_color, outline=outline_color)
            elif shape == "square":
                draw.rectangle((x - radius, y - radius, x + radius, y + radius), fill=fill_color, outline=outline_color)
            elif shape == "triangle":
                draw.polygon([(x, y - radius), (x - radius, y + radius), (x + radius, y + radius)], fill=fill_color, outline=outline_color)
            # Get text size for centering
            text_bbox = draw.textbbox((0, 0), str(b_no), font=font)  # Bounding box
            text_width = text_bbox[2] - text_bbox[0]
            text_height = text_bbox[3] - text_bbox[1]
            text_x = x - text_width // 2
            text_y = y - text_height // 1.2
            # Draw annotation b_no centered in balloon
            draw.text((text_x, text_y), str(b_no), fill="black", font=font)
        # Convert image to high-resolution PDF (600 DPI)
        annotated_image.convert("RGB").save(file_path, "PDF", resolution=600)
        print(f"Saved as a non-editable high-resolution PDF: {file_path}")

    def save_annotation_file(self, file_path, annotations):
        """Save annotations to custom .tma file"""
        annotation_data = {
            'source_file': self.file_path,
            'annotations': [
                {
                    'x': ann[0],
                    'y': ann[1],
                    'B_No#': ann[2],
                    'color': ann[3],
                    'size': ann[4],
                    'shape': ann[5] if len(ann) > 5 else 'circle',
                    'dimension': ann[6] if len(ann) > 6 else '',
                    'tolerance': ann[7] if len(ann) > 7 else '',
                    'remarks': ann[8] if len(ann) > 8 else ''
                }
                for ann in annotations
            ]
        }

        with open(file_path, 'w') as f:
            json.dump(annotation_data, f, indent=2)

    def load_annotation_file(self, file_path):
        """Load annotations from custom .tma file"""
        with open(file_path, 'r') as f:
            data = json.load(f)

        # Load source file if different
        if data['source_file'] != self.file_path:
            self.load_file(data['source_file'])

        return [
            (ann['x'], ann['y'], ann['b_no'], 
             ann['color'], ann['size'], ann.get('shape', 'circle'),
             ann.get('dimension', ''), ann.get('tolerance', ''), ann.get('remarks', ''))
            for ann in data['annotations']
        ]