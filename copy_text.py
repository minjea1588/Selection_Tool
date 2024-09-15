import tkinter as tk
from tkinter import filedialog, messagebox, simpledialog, ttk
from PIL import Image, ImageTk
import json
import yaml
import random

class Selection:
    def __init__(self):
        self.tk = tk
        self.master = tk.Tk()
        self.master.title("Zones Points Selector made by MJSUNG")
        self.master.resizable(False, False)

        # Setup canvas for image display
        self.canvas = self.tk.Canvas(self.master, bg="white", cursor="cross")  # Set initial cursor to cross

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

        # Initialize properties
        self.image_path = None
        self.image = None
        self.canvas_image = None
        self.bounding_boxes = []
        self.current_box = []
        self.img_width = 0
        self.img_height = 0
        self.draw_mode = False  # Initialize draw mode to False
        self.classes = []  # Initialize classes list
        self.yaml_loaded = False  # Flag to track if YAML file is loaded
        self.class_colors = {}  # Dictionary to store class colors

        # Setup class combo box
        self.class_combo = ttk.Combobox(self.master, values=self.classes, state="readonly")

        # Setup checkbox for rectangular mode
        self.rectangular_mode = tk.BooleanVar()
        self.rectangular_mode_checkbox = tk.Checkbutton(button_frame, text="Rectangular Mode", variable=self.rectangular_mode)
        self.rectangular_mode_checkbox.grid(row=0, column=7)

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
        self.class_selection_window = tk.Toplevel(self.master)
        self.class_selection_window.withdraw()  # Hide the window initially
        self.class_selection_window.title("Select Class")
        self.class_selection_label = tk.Label(self.class_selection_window, text="Select a class:")
        self.class_selection_label.pack(pady=10)
        self.class_selection_combobox = ttk.Combobox(self.class_selection_window, values=self.classes, state="readonly")
        self.class_selection_combobox.pack(pady=10)
        self.class_selection_button = tk.Button(self.class_selection_window, text="Select", command=self.on_class_select)
        self.class_selection_button.pack(pady=10)

        # Bind mouse events
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Button-4>", self.on_mouse_wheel)
        self.canvas.bind("<Button-5>", self.on_mouse_wheel)
        self.canvas.bind("<ButtonPress-1>", self.start_drag)
        self.canvas.bind("<B1-Motion>", self.drag)
        self.canvas.bind("<ButtonRelease-1>", self.end_drag)

        # Bind keyboard events
        self.master.bind("<Control-z>", self.undo_last_box)
        self.master.bind("b", self.toggle_draw_mode_key)

        self.master.mainloop()

    # ... [rest of the methods remain unchanged]

    def undo_last_box(self, event=None):
        self.remove_last_bounding_box()

    def toggle_draw_mode_key(self, event=None):
        self.toggle_draw_mode()

    def toggle_draw_mode(self):
        self.draw_mode = not self.draw_mode
        if self.draw_mode:
            self.canvas.config(cursor="plus")
            self.draw_box_button.config(relief="sunken")
        else:
            self.canvas.config(cursor="arrow")
            self.draw_box_button.config(relief="raised")

    # ... [rest of the class implementation]

if __name__ == "__main__":
    Selection()