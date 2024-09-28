import cv2
import numpy as np
from ultralytics import YOLO
import json
from ultralytics.utils.plotting import Annotator
from ultralytics.utils.checks import check_imshow
import random

class Managing_Parts:
    """Manages parking occupancy and availability using YOLOv8 for real-time monitoring and visualization."""

    def __init__(
        self,
        model_path,
        txt_color=(0, 0, 0),
        bg_color=(255, 255, 255),
        correct_region_color=(0, 255, 0),
        incorrect_region_color=(255, 0, 0),
        empty_region_color=(0, 0, 255),
        margin=10,
        json_path = None,
        class_info = None
    ):
        """
        Initializes the parking management system with a YOLOv8 model and visualization settings.

        Args:
            model_path (str): Path to the YOLOv8 model.
            txt_color (tuple): RGB color tuple for text.
            bg_color (tuple): RGB color tuple for background.
            occupied_region_color (tuple): RGB color tuple for occupied regions.
            available_region_color (tuple): RGB color tuple for available regions.
            margin (int): Margin for text display.
        """
        # Model path and initialization
        self.model_path = model_path
        self.model = self.load_model()
        self.default_color_list = [txt_color, bg_color, correct_region_color, incorrect_region_color, empty_region_color]
        # Labels dictionary
        self.labels_dict = {"Correct_parts": 0, "Inceorrect_parts":0, "Empty_parts": 0}
        self.env_check = check_imshow(warn=True)
        # Visualization details
        self.margin = margin
        self.bg_color = bg_color
        self.txt_color = txt_color
        self.correct_region_color = correct_region_color
        self.empty_region_color = empty_region_color
        self.incorrect_region_color = incorrect_region_color
        self.manager_json = self.parking_regions_extraction(json_path)
        self.class_info = class_info
        self.clas_dict = {self.class_info[i] : i  for i in range(len(self.class_info))}
        self.class_color = [self.get_random_color(i) for i in range(len(self.class_info))]
        self.window_name = "Ultralytics YOLOv8 Parking Management System"
        # Check if environment supports imshow

    def load_model(self):
        """Load the Ultralytics YOLO model for inference and analytics."""

        return YOLO(self.model_path)

    def load_class_info(self, json):
        if not json == None:
            class_list = []
            for region in json:
                class_list.append(region["class"])
            return class_list

    def get_random_color(self, seed):
        random.seed(seed)
        while True:
            r = random.randint(128, 255)
            g = random.randint(128, 255)
            b = random.randint(128, 255)
            if r + g + b > 500 and (r, g, b) not in self.default_color_list:  # 밝은 색상 조건
                return (r, g, b)

    def parking_regions_extraction(self, json_file):
        """
        Extract parking regions from json file.

        Args:
            json_file (str): file that have all parking slot points
        """
        with open(json_file, "r") as f:
            return json.load(f)

    def process_data(self, im0, boxes, clss, confs=None, infer_draw=False):
        """
        Process the model data for parking lot management.

        Args:
            json_data (str): json data for parking lot management
            im0 (ndarray): inference image
            boxes (list): bounding boxes data
            clss (list): bounding boxes classes list

        Returns:
            filled_slots (int): total slots that are filled in parking lot
            empty_slots (int): total slots that are available in parking lot
        """

        annotator = Annotator(im0)
        empty_slots, correct_filled_slots, incorrect_filled_slots = len(self.manager_json), 0, 0
        for region in self.manager_json:
            points_array = np.array(region["points"], dtype=np.int32).reshape((-1, 1, 2))
            class_name = self.clas_dict[region["class"]]
            correct_region = False
            incorrect_region = False
            emtpy_region = False

            for box, cls, conf in zip(boxes, clss, confs):
                x_center = int((box[0] + box[2]) / 2)
                y_center = int((box[1] + box[3]) / 2)
                text = f"{self.model.names[int(cls)]}"
                if infer_draw:
                    x1, y1, x2, y2 = map(lambda x: int(x), box)
                    label = f"{self.class_info[int(cls)]}: {conf:.2f}"
                    cv2.rectangle(im0, (x1, y1),(x2, y2), self.class_color[int(cls)], 2)
                    cv2.putText(im0, label, (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.class_color[int(cls)], 2)
                # annotator.display_objects_labels(
                #     im0, text, self.txt_color, self.bg_color, x_center, y_center, self.margin
                # )
                dist = cv2.pointPolygonTest(points_array, (x_center, y_center), False)
                if dist >= 0:
                    if class_name == cls:
                        correct_region = True
                        break
                    else:
                        incorrect_region = True
                        break
                else:
                    emtpy_region = True

            if correct_region:
                color = self.correct_region_color
            elif incorrect_region:
                color = self.incorrect_region_color
            elif emtpy_region:
                color = self.empty_region_color
            cv2.polylines(im0, [points_array], isClosed=True, color=color, thickness=2)
            if correct_region:
                correct_filled_slots += 1
                empty_slots -= 1
            if incorrect_region:
                incorrect_filled_slots += 1
                empty_slots -= 1

        self.labels_dict["Correct_parts"] = correct_filled_slots
        self.labels_dict["Empty_parts"] = empty_slots
        self.labels_dict["Inceorrect_parts"] = incorrect_filled_slots


        annotator.display_analytics(im0, self.labels_dict, self.txt_color, self.bg_color, self.margin)

    def display_frames(self, im0):
        """
        Display frame.

        Args:
            im0 (ndarray): inference image
        """
        if self.env_check:
            cv2.namedWindow(self.window_name)
            cv2.imshow(self.window_name, im0)
            # Break Window
            if cv2.waitKey(1) & 0xFF == ord("q"):
                return
