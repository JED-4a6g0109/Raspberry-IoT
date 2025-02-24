import time

import cv2
from ultralytics import YOLO
import os
from datetime import datetime

yolo_model = YOLO("yolov8n.pt")

DATA_DIR = "data"
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

if os.name == "posix":
    from picamera2 import Picamera2

    picam2 = Picamera2()
    config = picam2.create_still_configuration(main={"size": (640, 480)})
    picam2.configure(config)
    picam2.start()
    time.sleep(0.5)


def _is_overlapping(box1, box2, threshold=0.5):
    x1, y1, x2, y2 = box1
    x3, y3, x4, y4 = box2
    inter_x1, inter_y1 = max(x1, x3), max(y1, y3)
    inter_x2, inter_y2 = min(x2, x4), min(y2, y4)
    if inter_x1 < inter_x2 and inter_y1 < inter_y2:
        inter_area = (inter_x2 - inter_x1) * (inter_y2 - inter_y1)
        area1 = (x2 - x1) * (y2 - y1)
        area2 = (x4 - x3) * (y4 - y3)
        iou = inter_area / (area1 + area2 - inter_area)
        return iou > threshold
    return False


def _process_image(frame):
    frame = cv2.resize(frame, (640, 480))
    results = yolo_model(frame, conf=0.5, iou=0.6)

    boxes_list = []

    for result in results:
        boxes = result.boxes
        for box in boxes:
            if int(box.cls) == 0:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                boxes_list.append((x1, y1, x2, y2))

    filtered_boxes = []
    for i, box in enumerate(boxes_list):
        if not any(_is_overlapping(box, other_box) for other_box in filtered_boxes):
            filtered_boxes.append(box)

    people_count = len(filtered_boxes)

    for (x1, y1, x2, y2) in filtered_boxes:
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

    cv2.putText(frame, f"People: {people_count}", (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    snapshot_file = os.path.join(DATA_DIR, f"{timestamp}_snapshot.jpg")
    cv2.imwrite(snapshot_file, frame)
    print(f"Captured and saved as '{snapshot_file}', detected people: {people_count}")


def count_people_in_camera_rpi():
    global picam2
    frame = picam2.capture_array()
    frame = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
    _process_image(frame)


def count_people_in_camera(mock_image_path=None):
    if mock_image_path:
        frame = cv2.imread(mock_image_path)
        if frame is None:
            print(f"Failed to load image from path: {mock_image_path}")
            return
        print(f"Loaded mock image from {mock_image_path}")
    else:
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            print("Failed to open camera")
            return

        try:
            ret, frame = cap.read()
            if not ret:
                print("Failed to capture frame from camera")
                return
        finally:
            cap.release()

    _process_image(frame)
