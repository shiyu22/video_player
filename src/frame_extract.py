from paddle_yolo import run, YOLO_v3 as Detector
import base64
import os
import cv2
import uuid

def extract_frame(file_path, fps, prefix):
    count, frame_count = 0, 0
    cap = cv2.VideoCapture(file_path)
    framerate = cap.get(cv2.CAP_PROP_FPS)
    print("framerate:", framerate)
    allframes = int(cv2.VideoCapture.get(cap, int(cv2.CAP_PROP_FRAME_COUNT)))
    print("allframes:", allframes)
    success, image = cap.read()
    os.mkdir("pic/" + prefix)
    images = []
    while success:
        if count % (int(framerate)/fps) == 0:
            file_name = "pic/%s/%d.jpg" % (prefix, frame_count+1)
            cv2.imwrite(file_name, image)
            frame_count += 1
            images.append(file_name)
        success, image = cap.read()
        count += 1
    cap.release()
    return images


def detect(datas):
    detector = Detector()
    result_images = run(detector, datas)


avi = "test.avi"
prefix = avi.split(".")[0] + "-" + str(uuid.uuid1())
images = extract_frame(avi, 1, prefix)
print("images:", images)
detect(images)