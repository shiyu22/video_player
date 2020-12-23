import logging
import time
from video_player.src.indexer.index import milvus_client, delete_collection
from video_player.src.indexer.tools import connect_mysql, delete_data, delete_table
import time


def do_delete_table(index_client, conn, cursor, table_name):
    logging.info("doing delete table, table_name:", table_name)
    delete_table(conn, cursor, table_name)
    status = delete_collection(index_client, table_name)
    return status
