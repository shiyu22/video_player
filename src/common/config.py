import os

MILVUS_HOST = os.getenv("MILVUS_HOST", "13.75.80.25")
MILVUS_PORT = os.getenv("MILVUS_PORT", 19530)
LOGO_DIMENSION = os.getenv("LOGO_DIMENSION", 256)
FACE_DIMENSION = os.getenv("FACE_DIMENSION", 512)
TOP_K = os.getenv("TOP_K", 10)

LOGO_TABLE = os.getenv("LOGO_TABLE", "logo")
FACE_TABLE = os.getenv("FACE_TABLE", "face")

MYSQL_HOST = os.getenv("MYSQL_HOST", "13.75.80.25")
MYSQL_PORT = os.getenv("MYSQL_PORT", 3306)
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PWD = os.getenv("MYSQL_PWD", "123456")
MYSQL_DB = os.getenv("MYSQL_DB", "mysql")

DATA_PATH = os.getenv("DATA_PATH", "/mnt/workspace/mia/user_demos/video_player/src/data")
UPLOAD_PATH = os.getenv("UPLOAD_PATH", "/mnt/workspace/mia/user_demos/video_player/src/upload_data")


COCO_MODEL_PATH = os.getenv("OBJECT_PATH", "./video_player/src/yolov3_detector/data/yolov3_darknet")
YOLO_CONFIG_PATH = os.getenv("OBJECT_PATH", "./video_player/src/yolov3_detector/data/yolov3_darknet/yolo.yml")