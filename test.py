import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import json
import yaml
import random
import re

class Selection:
    def __init__(self):
        self.tk = tk
        self.master = tk.Tk()
        self.master.title("Zones Points Selector made by MJSUNG")
        self.master.resizable(False, False)

        # Setup canvas for image display
        self.canvas = self.tk.Canvas(self.master, bg="white", cursor="cross")
        self.canvas.pack(side=self.tk.BOTTOM)

        # Setup buttons
        button_frame = self.tk.Frame(self.master)
        button_frame.pack(side=self.tk.TOP)

        self.tk.Button(button_frame, text="Upload Image", command=self.upload_image).grid(row=0, column=0)
        self.tk.Button(button_frame, text="Save", command=self.save_to_json).grid(row=0, column=2)
        self.tk.Button(button_frame, text="Reset View", command=self.reset_view).grid(row=0, column=3)
        self.draw_box_button = self.tk.Button(button_frame, text="Draw Box", command=self.toggle_draw_mode)
        self.draw_box_button.grid(row=0, column=4)
        self.tk.Button(button_frame, text="Load Classes", command=self.load_classes).grid(row=0, column=5)
        self.tk.Button(button_frame, text="Remove Last Box", command=self.remove_last_bounding_box).grid(row=0, column=6)
        self.tk.Button(button_frame, text="Load JSON", command=self.load_json).grid(row=0, column=7)

        # Label to indicate loaded classes file
        self.classes_loaded_label = self.tk.Label(button_frame, text="No classes file loaded", fg="red")
        self.classes_loaded_label.grid(row=1, columnspan=8)

        # Initialize properties
        self.image_path = None
        self.original_image = None
        self.displayed_image = None
        self.canvas_image = None
        self.bounding_boxes = []
        self.current_box = []
        self.canvas_box = []
        self.img_width = 0
        self.img_height = 0
        self.draw_mode = False
        self.classes = []
        self.yaml_loaded = False
        self.class_colors = {}

        # Setup class combo box
        self.class_combo = ttk.Combobox(self.master, values=self.classes, state="readonly")

        # Setup checkbox for rectangular mode
        self.rectangular_mode = tk.BooleanVar()
        self.rectangular_mode_checkbox = tk.Checkbutton(button_frame, text="Rectangular Mode", variable=self.rectangular_mode)
        self.rectangular_mode_checkbox.grid(row=0, column=8)

        # Constants
        self.canvas_width = 1280
        self.canvas_height = 720
        self.zoom_factor = 1.0
        self.zoom_x = 0
        self.zoom_y = 0

        # Variables for dragging
        self.drag_start_x = 0
        self.drag_start_y = 0
        self.dragging = False

        # Create a Toplevel window for class selection
        self.class_selection_create()

        # Bind mouse events
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)
        self.master.bind("<Control-z>", self.undo_last_box)
        self.master.bind("b", self.toggle_draw_mode_key)

        self.master.mainloop()

    def upload_image(self):
        self.image_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")])
        if not self.image_path:
            return

        self.original_image = Image.open(self.image_path)
        self.img_width, self.img_height = self.original_image.size

        # Resize image to fit canvas
        self.displayed_image = self.original_image.copy()
        self.displayed_image.thumbnail((self.canvas_width, self.canvas_height))
        self.reset_view()

    def reset_view(self):
        self.zoom_factor = 1.0
        self.zoom_x = 0
        self.zoom_y = 0
        self.refresh_image()

    def refresh_image(self):
        if self.displayed_image:
            # Calculate the region to display
            zoom_width = int(self.displayed_image.width / self.zoom_factor)
            zoom_height = int(self.displayed_image.height / self.zoom_factor)
            x1 = self.zoom_x
            y1 = self.zoom_y
            x2 = x1 + zoom_width
            y2 = y1 + zoom_height

            # Ensure the view stays within the image bounds
            x1 = max(0, min(x1, self.displayed_image.width - zoom_width))
            y1 = max(0, min(y1, self.displayed_image.height - zoom_height))
            x2 = min(self.displayed_image.width, x1 + zoom_width)
            y2 = min(self.displayed_image.height, y1 + zoom_height)

            self.zoom_x, self.zoom_y = x1, y1

            # Crop and resize the image
            zoomed_image = self.displayed_image.crop((x1, y1, x2, y2))
            zoomed_image = zoomed_image.resize((self.canvas_width, self.canvas_height), Image.LANCZOS)

            self.canvas_image = ImageTk.PhotoImage(zoomed_image)
            self.canvas.delete("all")
            self.canvas.create_image(0, 0, anchor=self.tk.NW, image=self.canvas_image)

            # Redraw bounding boxes
            self.redraw_bounding_boxes()

    def redraw_bounding_boxes(self):
        for box, class_name in self.bounding_boxes:
            self.draw_bounding_box(box, class_name)

    def on_mouse_wheel(self, event):
        if self.displayed_image:
            # Get mouse position
            x = self.canvas.canvasx(event.x)
            y = self.canvas.canvasy(event.y)

            # Calculate zoom center in image coordinates
            zoom_center_x = self.zoom_x + x / self.zoom_factor
            zoom_center_y = self.zoom_y + y / self.zoom_factor

            # Determine zoom direction
            if event.num == 5 or event.delta == -120:  # Scroll down
                self.zoom_factor = max(1.0, self.zoom_factor - 0.1)
            if event.num == 4 or event.delta == 120:  # Scroll up
                self.zoom_factor = min(5.0, self.zoom_factor + 0.1)

            # Recalculate zoom region
            self.zoom_x = max(0, min(zoom_center_x - self.canvas_width / (2 * self.zoom_factor), self.displayed_image.width - self.canvas_width / self.zoom_factor))
            self.zoom_y = max(0, min(zoom_center_y - self.canvas_height / (2 * self.zoom_factor), self.displayed_image.height - self.canvas_height / self.zoom_factor))

            self.refresh_image()

    def start_drag(self, event):
        self.drag_start_x = event.x
        self.drag_start_y = event.y
        self.dragging = True

    def drag(self, event):
        if self.dragging and self.displayed_image:
            dx = (event.x - self.drag_start_x) / self.zoom_factor
            dy = (event.y - self.drag_start_y) / self.zoom_factor
            self.zoom_x = max(0, min(self.zoom_x - dx, self.displayed_image.width - self.canvas_width / self.zoom_factor))
            self.zoom_y = max(0, min(self.zoom_y - dy, self.displayed_image.height - self.canvas_height / self.zoom_factor))
            self.drag_start_x = event.x
            self.drag_start_y = event.y
            self.refresh_image()

    def end_drag(self, event):
        if self.dragging:
            self.dragging = False
            if abs(event.x - self.drag_start_x) < 5 and abs(event.y - self.drag_start_y) < 5:
                self.on_canvas_click(event)

    def on_canvas_click(self, event):
        if not self.draw_mode:
            return

        # Convert click coordinates to original image coordinates
        x = (self.zoom_x + event.x / self.zoom_factor) / self.displayed_image.width
        y = (self.zoom_y + event.y / self.zoom_factor) / self.displayed_image.height

        self.current_box.append((x, y))
        self.canvas_box.append((x, y))

        # Draw point on canvas
        canvas_x = int((x * self.displayed_image.width - self.zoom_x) * self.zoom_factor)
        canvas_y = int((y * self.displayed_image.height - self.zoom_y) * self.zoom_factor)
        self.canvas.create_oval(canvas_x-3, canvas_y-3, canvas_x+3, canvas_y+3, fill="red", tags="temp")

        if len(self.current_box) == 4:
            self.draw_mode = False
            self.canvas.config(cursor="arrow")
            self.draw_box_button.config(relief="raised")
            self.process_completed_box()
        if len(self.current_box) > 4:
            self.current_box = []
            self.canvas_box = []

    def process_completed_box(self):
        if self.yaml_loaded:
            self.show_class_selection_window()
            self.isfirst_combo = False
            self.master.wait_window(self.class_selection_window)
        else:
            self.class_name = simpledialog.askstring("Input", "Enter class name for this bounding box:")

        if self.class_name:
            if self.class_name not in self.class_colors:
                self.class_colors[self.class_name] = self.get_random_color()
            
            if self.rectangular_mode.get():
                # Convert to rectangular bounding box
                x_coords, y_coords = zip(*self.current_box)
                x_min, x_max = min(x_coords), max(x_coords)
                y_min, y_max = min(y_coords), max(y_coords)
                self.current_box = [(x_min, y_min), (x_max, y_min), (x_max, y_max), (x_min, y_max)]
            
            self.bounding_boxes.append((self.current_box, self.class_name))
            self.draw_bounding_box(self.current_box, self.class_name)
            self.current_box = []
            self.canvas_box = []
            if self.yaml_loaded:
                self.class_combo.set(self.class_name)
        else:
            self.current_box = []
            self.canvas_box = []
        
        self.canvas.delete("temp")

    def draw_bounding_box(self, box, class_name):
        color = self.class_colors[class_name]
        for i in range(4):
            x1, y1 = box[i]
            x2, y2 = box[(i + 1) % 4]

            # Convert normalized coordinates to canvas coordinates
            canvas_x1 = int((x1 * self.displayed_image.width - self.zoom_x) * self.zoom_factor)
            canvas_y1 = int((y1 * self.displayed_image.height - self.zoom_y) * self.zoom_factor)
            canvas_x2 = int((x2 * self.displayed_image.width - self.zoom_x) * self.zoom_factor)
            canvas_y2 = int((y2 * self.displayed_image.height - self.zoom_y) * self.zoom_factor)

            self.canvas.create_line(canvas_x1, canvas_y1, canvas_x2, canvas_y2, fill=color, width=2, tags="box")

        # Draw class name
        x, y = box[0]
        canvas_x = int((x * self.displayed_image.width - self.zoom_x) * self.zoom_factor)
        canvas_y = int((y * self.displayed_image.height - self.zoom_y) * self.zoom_factor)
        self.canvas.create_text(canvas_x, canvas_y-10, text=class_name, fill=color, tags="box")

    # ... (rest of the methods remain the same)

    def load_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON Files", "*.json")])
        if file_path:
            try:
                with open(file_path, 'r') as f:
                    bounding_boxes_data = json.load(f)
                
                self.bounding_boxes = []
                for box_data in bounding_boxes_data:
                    points = box_data["points"]
                    class_name = box_data["class"]
                    
                    # Convert points to normalized coordinates
                    normalized_points = [(x / self.img_width, y / self.img_height) for x, y in points]
                    
                    self.bounding_boxes.append((normalized_points, class_name))
                
                self.refresh_image()
                messagebox.showinfo("Success", "Bounding boxes loaded from JSON file")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load JSON: {e}")

    # ... (rest of the class remains the same)

if __name__ == "__main__":
    Selection()