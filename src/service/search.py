import logging as log
from common.config import LOGO_TABLE
from indexer.index import milvus_client, search_vectors, get_vector_by_ids
from indexer.tools import connect_mysql, search_by_milvus_id
from frame_extract import extract_frame


def get_ids_info(conn, cursor, table_name, host, ids):
    if not table_name:
        table_name = MILVUS_TABLE
    info = search_by_milvus_id(conn, cursor, table_name, str(ids))
    info = json.loads(info[1], strict=False)
    img = "http://"+ str(host) + "/getImage?img=" + str(ids)
    print("============", img)
    return info, img


def get_object_vector(images):
    vectors = []
    for image in images:
        vector = image_encoder.execute(image)
        vectors.append(vector)
    return vectors


def get_object_info(results):
    info = []
    for results_id in results.id_array:
        re = search_by_milvus_id(conn, cursor, movies_table, results_id[0])
        print(re)
        info.append(re)
    return info


def do_search_logo(image_encoder, index_client, conn, cursor, table_name, filename, host):
    if not table_name:
        table_name = LOGO_TABLE
    print(filename)
    images = extract_frame(filename, 1, filename.split("/")[2].split(".")[0])
    vectors = get_object_vector(images)
    results = search_vectors(index_client, table_name, vectors, "IP")
    print("-----milvus search status------", results)
    info = get_object_info(results)
    return info
