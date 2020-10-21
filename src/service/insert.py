import logging
from common.config import LOGO_TABLE
from indexer.index import insert_vectors, create_table, create_index
from indexer.tools import create_table_mysql, insert_data_to_pg


def do_insert_logo(image_encoder, index_client, conn, cursor, table_name, filename, name, info):
    if not table_name:
        table_name = LOGO_TABLE
    if collection_name in index_client.list_collections():
        print("create table.")
        create_table_mysql(conn, cursor, table_name)
        create_table(index_client, table_name, dimension=1024)
    
    peint(filename)
    vector = image_encoder.execute(filename)
    print(vector)
    ids = insert_vectors(client, table_name, [vector])
    insert_data_to_pg(conn, cur, table_name, ids, name, info, filename)
    
    return status

