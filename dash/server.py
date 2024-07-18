import dash
import os
from flask import request, send_from_directory

app = dash.Dash(
    __name__,
    update_title=None,
    suppress_callback_exceptions=True
)

app.title = 'LLM-MapBook'

server = app.server

@server.route('/upload/', methods=['POST'])
def upload():
    '''
    构建文件上传服务
    :return:
    '''

    # 获取上传id参数，用于指向保存路径
    uploadId = request.values.get('uploadId')

    # 获取上传的文件名称
    filename = request.files['file'].filename

    # 基于上传id，若本地不存在则会自动创建目录
    try:
        os.mkdir(os.path.join('dash', 'caches', uploadId))
    except FileExistsError:
        pass

    # 流式写出文件到指定目录
    with open(os.path.join('dash', 'caches', uploadId, filename), 'wb') as f:
        # 流式写出大型文件，这里的10代表10MB
        for chunk in iter(lambda: request.files['file'].read(1024 * 1024 * 10), b''):
            f.write(chunk)

    return {'filename': filename}


@server.route('/download')
def download():
    '''
    构建文件下载服务
    :return:
    '''

    # 提取文件路径参数
    path = request.values.get('path'),

    # 提取文件名称参数
    file = request.values.get('file')
    print(send_from_directory(os.path.join('dash', 'caches', path[0]), file))

    return send_from_directory(os.path.join('dash', 'caches', path[0]), file)