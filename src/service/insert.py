import logging
from common.config import LOGO_TABLE
from indexer.index import insert_vectors, create_table, create_index
from indexer.tools import create_table_mysql, insert_data_to_pg


def do_insert_logo(image_encoder, index_client, conn, cursor, table_name, filename, name, info):
    if not table_name:
        table_name = LOGO_TABLE
    # print("---------", table_name)
    if table_name not in index_client.list_collections():
        print("create table.")
        create_table_mysql(conn, cursor, table_name)
        create_table(index_client, table_name, dimension=2048)
    
    # print(filename)
    vector = image_encoder.execute(filename)
    # print(vector)
    ids = insert_vectors(index_client, table_name, [vector])
    print(ids)
    insert_data_to_pg(conn, cursor, table_name, ids[0], name, info, filename)
    
    return "insert successfully!"

