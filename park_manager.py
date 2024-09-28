import cv2
import yaml
from infer_Detection import Managing_Parts


cap = cv2.VideoCapture("test_video.mp4")
infer_draw = True
assert cap.isOpened(), "Error reading video file"
w, h, fps = (int(cap.get(x)) for x in (cv2.CAP_PROP_FRAME_WIDTH, cv2.CAP_PROP_FRAME_HEIGHT, cv2.CAP_PROP_FPS))
cnt = 0
json_path = "frame_5_bounding_boxes.json"
yaml_path = "data.yaml"

with open(yaml_path, "r") as file:
    data = yaml.safe_load(file)
    classes = data["names"]

management = Managing_Parts(model_path = "0916_cpcm_S_KFold_v8.pt", class_info = classes, json_path = json_path)
video_writer = cv2.VideoWriter("parking management.avi", cv2.VideoWriter_fourcc(*"mp4v"), fps, (w, h))
# Loop through the video frames


while cap.isOpened():
    # Read a frame from the video
    success, frame = cap.read()
    if success:
        # Run YOLOv8 inference on the frame
        results = management.model.track(frame, persist=True, show=False)

        if results[0].boxes.id is not None:
            boxes = results[0].boxes.xyxy.cpu().tolist()
            clss = results[0].boxes.cls.cpu().tolist()
            conf = results[0].boxes.conf.cpu().tolist()

            management.process_data(frame, boxes, clss, conf, infer_draw)

        management.display_frames(frame)
        video_writer.write(frame)
        # Break the loop if 'q' is pressed
    else:
        break
cap.release()
video_writer.release()
cv2.destroyAllWindows()