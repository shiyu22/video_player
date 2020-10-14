from yolov3_detector.paddle_yolo import run, YOLO_v3 as Detector
from common.config import DATA_PATH

def main():
    detector = Detector()
    datas = DATA_PATH + '/' + 'test-f1577db8-0dea-11eb-9433-ac1f6ba128da'
    result_images = run(detector, datas)


if __name__ == '__main__':
    main()