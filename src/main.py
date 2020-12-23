import datetime
import logging
import os
import uuid
import zipfile

import cv2
import uvicorn
from common.config import UPLOAD_PATH
from face_encoder.deploy.encode import Encode
from fastapi import FastAPI
from fastapi import File
from fastapi import UploadFile
from indexer.index import milvus_client
from indexer.tools import connect_mysql
from resnet50_encoder.encode import CustomOperator
from service.count import do_count_table
from service.delete import do_delete_table
from service.format import format_info
from service.insert import do_insert_logo, do_insert_face
from service.search import do_search_logo, do_search_face, do_only_her
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import FileResponse

app = FastAPI()
image_encoder = CustomOperator()
face_encoder = Encode()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"])


def init_conn():
    conn = connect_mysql()
    cursor = conn.cursor()
    index_client = milvus_client()
    return index_client, conn, cursor


@app.get('/countTable')
async def do_count_images_api(table_name: str = None):
    try:
        index_client, conn, cursor = init_conn()
        rows_milvus, rows_mysql = do_count_table(index_client, conn, cursor, table_name)
        return "{0},{1}".format(rows_milvus, rows_mysql), 200
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


@app.delete('/deleteTable')
async def do_delete_table_api(table_name: str = None):
    try:
        index_client, conn, cursor = init_conn()
        status = do_delete_table(index_client, conn, cursor, table_name)
        return "{}".format(status)
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


@app.get('/getImage')
async def image_endpoint(img: str):
    try:
        print("load img:", img)
        return FileResponse(img, media_type="image/jpg")
    except Exception as e:
        logging.error(e)
        return None, 200


@app.post('/insertFace')
async def do_insert_face_api(name: str, image: UploadFile = File(...), info: str = None, table_name: str = None):
    try:
        content = await image.read()
        filename = UPLOAD_PATH + "/" + uuid.uuid4().hex + ".jpg"
        with open(filename, 'wb') as f:
            f.write(content)
        index_client, conn, cursor = init_conn()
        info = do_insert_face(face_encoder, index_client, conn, cursor, table_name, filename, name, info)
        return info, 200
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


def unzip_faces(zip_src, dst_src):
    r = zipfile.is_zipfile(zip_src)
    if r:
        fz = zipfile.ZipFile(zip_src, 'r')
        for file in fz.namelist():
            fz.extract(file, dst_src)
    else:
        print('This is not zip')


@app.post('/UploadFaceVideo')
async def upload_video(user_id: str, email: str, request: Request, video: UploadFile = File(...)):
    try:
        # is_register_user = check_user_info(user_id, email)
        # if is_register_user == False:
        #     status = False
        #     message = "You have not registered yet, please register first!"
        #     return {'status': status, 'msg': message}
        content = await video.read()
        filename = UPLOAD_PATH + '/' + user_id + uuid.uuid4().hex + '.avi'
        with open(filename, "wb") as f:
            f.write(content)
        return {'status': True, 'msg': filename}
    except Exception as e:
        print("Upload video failed: ", e)
        return {'status': False, 'msg': 'Upload video failed!'}


def new_file(testdir):
    list = os.listdir(testdir)
    list.sort(key=lambda fn: os.path.getmtime(testdir + '/' + fn))
    filetime = datetime.datetime.fromtimestamp(os.path.getmtime(testdir + list[-1]))
    filepath = os.path.join(testdir, list[-1])
    return filepath


@app.post('/UploadFaces')
async def do_upload_faces_api(user_id: str, email: str, file: UploadFile = File(...)):
    try:
        # is_register_user = check_user_info(user_id, email)
        # if is_register_user == False:
        #     status = False
        #     message = "You have not registered yet, please register first!"
        #     return {'status': status, 'msg': message}
        zip_file = await file.read()
        file_size = len(zip_file)
        if file_size > 20 * 1024 * 1024:
            status = False
            message = "The uploaded file size cannot exceed 20 MB."
            return {'status': status, 'msg': message}

        user_id = 'facedb_' + user_id
        dirs = UPLOAD_PATH + '/' + user_id
        if not os.path.exists(dirs):
            os.makedirs(dirs)
        fname = file.filename
        fname_path = dirs + '/' + fname
        with open(fname_path, 'wb') as f:
            f.write(zip_file)
        unzip_faces(fname_path, dirs)
        os.remove(fname_path)
        fpath = new_file(dirs + '/')
        index_client, conn, cursor = init_conn()
        for filename in os.listdir(fpath):
            name = filename.split('.', 1)[0]
            info = do_insert_face(face_encoder, index_client, conn, cursor, user_id, fpath + '/' + filename, name, name)
        return {'status': True, 'msg': 'Upload and decompress the dataset successfully!'}
    except Exception as e:
        logging.error(e)
        return {'status': False, 'msg': 'Upload dataset failed!'}


@app.post('/insertLogo')
async def do_insert_logo_api(name: str, image: UploadFile = File(...), info: str = None, table_name: str = None):
    try:
        content = await image.read()
        filename = UPLOAD_PATH + "/" + uuid.uuid4().hex + ".jpg"
        with open(filename, 'wb') as f:
            f.write(content)
        index_client, conn, cursor = init_conn()
        info = do_insert_logo(image_encoder, index_client, conn, cursor, table_name, filename, name, info)
        return info, 200
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


@app.post('/getLogoInfo')
async def get_item_info(request: Request, video: UploadFile = File(...), table_name: str = None):
    try:
        content = await video.read()
        filename = UPLOAD_PATH + "/" + video.filename
        with open(filename, "wb") as f:
            f.write(content)

        index_client, conn, cursor = init_conn()
        host = request.headers['host']
        info, times = do_search_logo(image_encoder, index_client, conn, cursor, table_name, filename)
        result_dic = {"code": 0, "msg": "success"}

        results = []
        for i in range(len(info)):
            re = {
                "milvus_id": info[i][0],
                "obj_name": info[i][1],
                "obj_info": info[i][2],
                "obj_image": "http://" + str(host) + "/getImage?img=" + info[i][3],
                "time": times[i].split("-")[0]
            }
            results.append(re)
        result_dic["data"] = results
        return result_dic, 200
    except Exception as e:
        logging.error(e)
        return "Error with {}".format(e), 400


@app.post('/WhoInVideo')
async def who_in_video(user_id: str, email: str, request: Request, filename: str):
    try:
        # is_register_user = check_user_info(user_id, email)
        # if is_register_user == False:
        #     status = False
        #     message = "You have not registered yet, please register first!"
        #     return {'status': status, 'msg': message}

        # content = await video.read()
        # filename = UPLOAD_PATH + "/" + video.filename
        # with open(filename, "wb") as f:
        #     f.write(content)

        index_client, conn, cursor = init_conn()
        host = request.headers['host']
        table_name = 'facedb_' + user_id
        info = do_only_her(face_encoder, index_client, conn, cursor, table_name, filename)
        # result_dic = {"code": 0, "msg": "success"}
        time_of_occur = {}
        time = 1
        for frame in info:
            for i in range(len(frame)):
                if not frame[i][1] in time_of_occur:
                    time_of_occur[frame[i][1]] = ["http://" + str(host) + "/getImage?img=" + frame[i][3], [time]]
                else:
                    time_of_occur[frame[i][1]][1].append(time)
            time += 1
        results = format_info(time_of_occur)
        # result_dic["data"] = results
        format_res = {'status': True, 'msg': results}
        return format_res
    except Exception as e:
        logging.error(e)
        return {'status': False, 'msg': 'Failed to search people.'}


@app.post('/getFaceInfo')
async def get_face_info(user_id: str, email: str, request: Request, filename: str, time: int):
    try:
        # is_register_user = check_user_info(user_id, email)
        # if is_register_user == False:
        #     status = False
        #     message = "You have not registered yet, please register first!"
        #     return {'status': status, 'msg': message}
        vc = cv2.VideoCapture(filename)
        vc.set(cv2.CAP_PROP_POS_MSEC, time)
        rval, frame = vc.read()
        fname = UPLOAD_PATH + "/frame" + uuid.uuid4().hex + ".jpg"
        cv2.imwrite(fname, frame)
        index_client, conn, cursor = init_conn()
        host = request.headers['host']
        info = do_search_face(face_encoder, index_client, conn, cursor, 'facedb_' + user_id, fname)
        results = []
        for i in range(len(info)):
            re = {
                "milvus_id": info[i][0],
                "face_name": info[i][1],
                "face_image": "http://" + str(host) + "/getImage?img=" + info[i][3]
            }
            results.append(re)
        return {'status': True, 'msg': results}
    except Exception as e:
        logging.error(e)
        print(e)
        return {'status': False, 'msg': e}

    # try:
    #     content = await image.read()
    #     filename = UPLOAD_PATH + "/" + image.filename
    #     with open(filename, "wb") as f:
    #         f.write(content)
    #     index_client, conn, cursor = init_conn()
    #     host = request.headers['host']
    #     info = do_search_face(face_encoder, index_client, conn, cursor, table_name, filename)
    #     result_dic = {"code": 0, "msg": "success"}
    #
    #     results = []
    #     for i in range(len(info)):
    #         re = {
    #             "milvus_id": info[i][0],
    #             "face_name": info[i][1],
    #             "face_info": info[i][2],
    #             "face_image": "http://" + str(host) + "/getImage?img=" + info[i][3]
    #         }
    #         results.append(re)
    #     result_dic["data"] = results
    #     return result_dic, 200
    # except Exception as e:
    #     logging.error(e)
    #     return "Error with {}".format(e), 400


if __name__ == '__main__':
    uvicorn.run(app=app, host='0.0.0.0', port=8030)
