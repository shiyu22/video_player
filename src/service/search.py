import logging as log
from common.config import LOGO_TABLE
from indexer.index import milvus_client, search_vectors, get_vector_by_ids
from indexer.tools import connect_mysql, search_by_milvus_id
from frame_extract import extract_frame
import uuid
import os
from common.config import DATA_PATH
from yolov3_detector.paddle_yolo import run


def get_ids_info(conn, cursor, table_name, host, ids):
    if not table_name:
        table_name = MILVUS_TABLE
    info = search_by_milvus_id(conn, cursor, table_name, str(ids))
    info = json.loads(info[1], strict=False)
    img = "http://"+ str(host) + "/getImage?img=" + str(ids)
    print("============", img)
    return info, img


def get_object_vector(image_encoder, path):
    images = os.listdir(path)
    images.sort()
    vectors = []
    for image in images:
        vector = image_encoder.execute(path + '/' + image)
        vectors.append(vector)
    return vectors, images


def get_object_info(conn, cursor, table_name, results, obj_images):
    info = times = []
    i = 0
    for entities in results:
        print("-----milvus search status------", entities[0].id, entities[0].distance)
        if entities[0].distance>0.65:
            re = search_by_milvus_id(conn, cursor, table_name, entities[0].id)
            print(re)
            info.append(re)
            times.append(obj_images[i])
        i += 1
    return info, times


def do_search_logo(detector, image_encoder, index_client, conn, cursor, table_name, filename, host):
    if not table_name:
        table_name = LOGO_TABLE
    print(filename)
    prefix = filename.split("/")[2].split(".")[0] + "-" + uuid.uuid4().hex
    images = extract_frame(filename, 1, prefix)
    run(detector, DATA_PATH + '/' + prefix)
    
    vectors, obj_images = get_object_vector(image_encoder, DATA_PATH + '/' + prefix + '/object')
    print("vectors:", len(vectors))
    results = search_vectors(index_client, table_name, vectors, "L2")

    info, tiems = get_object_info(conn, cursor, table_name, results, obj_images)
    return info, tiems
