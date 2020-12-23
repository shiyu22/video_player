import logging

from video_player.src.common.config import MILVUS_HOST, MILVUS_PORT, TOP_K
from milvus import Milvus, MetricType


def milvus_client():
    try:
        milvus = Milvus(host=MILVUS_HOST, port=MILVUS_PORT)
        return milvus
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def create_table(client, table_name, dimension):
    param = {'collection_name': table_name, 'dimension': dimension, 'index_file_size': 1024,
             'metric_type': MetricType.L2}
    try:
        status = client.create_collection(param)
        return status
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def insert_vectors(client, table_name, vectors):
    try:
        ids = client.insert(collection_name=table_name, records=vectors)[-1]
        return ids
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


# def create_index(client, table_name, metric_type):
#     try:
#         status = client.create_index(table_name, "embedding",
#                                      {"index_type": "IVF_FLAT", "metric_type": metric_type, "params": {"nlist": 8192}})
#         return status
#     except Exception as e:
#         print("Milvus ERROR:", e)
#         logging.error(e)


def delete_collection(client, table_name):
    try:
        status = client.drop_collection(collection_name=table_name)
        return status
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def search_vectors(client, table_name, vectors):
    search_param = {'nprobe': 16}
    try:
        res = client.search(collection_name=table_name, query_records=vectors, top_k=1, params=search_param)[-1]
        return res
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def has_table(client, table_name):
    try:
        status = client.has_collection(collection_name=table_name)
        return status
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def count_collection(client, table_name):
    try:
        num = client.count_entities(collection_name=table_name)
        return num
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def delete_vectors(client, table_name, ids):
    try:
        status = client.delete_entity_by_id(table_name, ids)
        return status
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)


def get_vector_by_ids(client, table_name, ids):
    try:
        status, vector = client.get_entity_by_id(collection_name=table_name, ids=ids)
        return status, vector
    except Exception as e:
        print("Milvus ERROR:", e)
        logging.error(e)
