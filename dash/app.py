
from server import app, server
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import json
import uuid
import time
from io import BytesIO
from utils.geocode_utils import GeocodeUtils
from utils.text_processing import FileProcessor
from dash.dependencies import Input, Output, State
import feffery_markdown_components as fmc
import feffery_utils_components as fuc
import feffery_antd_components as fac
import feffery_leaflet_components as flc
from datetime import datetime
from dash import html, dcc
import dash
import random
import string

from dotenv import load_dotenv, find_dotenv
_ = load_dotenv(find_dotenv())    # read local .env file

def generate_random_string(length):
    all_characters = string.ascii_letters + string.digits
    random_string = ''.join(random.choice(all_characters) for _ in range(length))
    return random_string

# 实例化geocode_utils和file_processor
geocode_utils = GeocodeUtils(user_agent=generate_random_string(9))
file_processor = FileProcessor()

# def create_geojson(geo_info_list):
#     features = []
#     for info in geo_info_list:
#         time.sleep(3)
#         geocode_result = geocode_utils.geocode(info["address"])
#         print('坐标为:', info["address"], geocode_result)
#         if 'error' not in geocode_result:
#             feature = {
#                 "type": "Feature",
#                 "properties": {
#                     "description": {
#                         "title": info["event_title"],
#                         "type": info["event_type"],
#                         "content": info["event_content"],
#                         "keys": info["keys"],
#                     }
#                 },
#                 "geometry": {
#                     "type": "Point",
#                     "coordinates": [geocode_result["longitude"], geocode_result["latitude"]]
#                 }
#             }
#             print(feature, "点位数据")
#             features.append(feature)
#             # 更新地图
#             update_map(feature)
#     return {
#         "type": "FeatureCollection",
#         "features": features
#     }


 # # 如果使用原生openai接口，可把这个注释取消，设置代理，根据你的实际情况调整端口
 # # 若是可以直连的第三方接口的话，直接在界面填一下api_base_url和api_key即可
# os.environ['HTTP_PROXY'] = 'http://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:7890'


app.layout = html.Div(
    [
        dcc.Store(
            id='mapinfo-store'
        ),        
        dcc.Store(
            id='geojson-store'
        ),        
        # 注入问题返回状态消息提示
        html.Div(
            id='response-status-message'
        ),
                
        # 页首布局，固定像素高度
        html.Div(
            fac.AntdCenter(
                'LLM-MapBook',
                style={
                    'width': '100%', 
                    'height': '100%',
                    'fontSize': '45px',
                },
            ),
            style={
                'height': '64px',
                'boxShadow': '0px 0px 12px rgba(0, 0, 0, .12)',
                'background': 'rgba(255, 255, 255, 0.8)'
            }
        ),

        # 下方主内容区域relative容器，利用calc撑满剩余高度
        html.Div(
            [
                # 底层在线地图，绝对定位撑满父容器
                flc.LeafletMap(
                    [
                        # 添加瓦片底图
                        flc.LeafletTileLayer(
                            id='tile-layer',
                            url='https://tiles1.geovisearth.com/base/v1/vec/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        ),
                        flc.LeafletFullscreenControl(
                        ),                        
                    ],
                    id='map-container',
                    # zoomControl=True,  # 隐藏自带的放大缩小控件
                    editToolbar=True,
                    # 关闭其他无关地图编辑功能
                    editToolbarControlsOptions={
                        'drawMarker': False,
                        'drawCircleMarker': False,
                        'drawPolyline': False,
                        'drawRectangle': False,
                        'drawPolygon': False,
                        'drawCircle': False,
                        'drawText': False,
                        'removalMode': False,
                        'rotateMode': False
                    },                    
                    style={
                        'position': 'absolute',
                        'width': 'calc(100vw - 810px)',
                        'height': 'calc(100vh - 74px)',
                        # 'top': 64,
                        'left': 410,                        
                    }
                ),
                

                
                # 在地图实例相同的相对容器内放入图层切换器
                flc.LeafletTileSelect(
                    id='tile-select',
                    selectedUrl='https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
                    urls=[
                        {
                            'url': 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png'
                        },
                        {
                            'url': 'https://tiles1.geovisearth.com/base/v1/vec/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        },
                        {
                            'url': 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}'
                        },
                        {
                            'url': 'https://tiles1.geovisearth.com/base/v1/vec/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        },
                        {
                            'url': 'https://tiles1.geovisearth.com/base/v1/img/{z}/{x}/{y}?format=webp&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        },
                        {
                            'url': 'https://tiles1.geovisearth.com/base/v1/cia/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        },
                        {
                            'url': 'https://tiles1.geovisearth.com/base/v1/ter/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        },
                        {
                            'url': 'https://tiles1.geovisearth.com/base/v1/cat/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
                        },
                        {
                            'url': 'http://webrd01.is.autonavi.com/appmaptile?lang=zh_cn&size=1&scale=1&style=8&x={x}&y={y}&z={z}'
                        },
                        {
                            'url': 'https://webst01.is.autonavi.com/appmaptile?style=6&x={x}&y={y}&z={z}'
                        },
                        {
                            'url': 'http://t0.tianditu.gov.cn/img_w/wmts?SERVICE=WMTS&REQUEST=GetTile&VERSION=1.0.0&LAYER=img&STYLE=default&TILEMATRIXSET=w&FORMAT=tiles&TILEMATRIX={z}&TILEROW={y}&TILECOL={x}&tk=dc583530609f195b53cf2773de8beae0'
                        },
                        {
                            'url': 'https://{s}.tile.openstreetmap.fr/hot/{z}/{x}/{y}.png'
                        },
                        {
                            'url': 'http://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png'
                        },
                        {
                            'url': 'https://d.basemaps.cartocdn.com/light_nolabels/{z}/{x}/{y}.png'
                        }
                    ],
                    # zoom=7,
                    containerVisible=False,
                    style={
                        'position': 'absolute',
                        'width': 'calc(100vw - 400px)',
                        'height': 'calc(100vh - 74px)',
                        # 'top': 64,
                        # 'right': 400,                        
                    }                    
                ),
                # 风格一折叠按钮，对应左侧面板
                html.Span(
                    fac.AntdIcon(
                        id='left-panel-fold-icon',
                        icon='antd-menu-fold'
                    ),
                    id='left-panel-fold',
                    style={
                        'position': 'absolute',
                        'top': 15,
                        'left': 8,
                        'zIndex': 9999,
                        'cursor': 'pointer',
                        'fontSize': 18
                    }
                ),

                # 左侧悬浮面板，绝对定位，拉高zIndex
                html.Div(
                    [
                        html.Div(
                            fuc.FefferyDiv(
                                html.Div(
                                    [
                                        html.Div(id='succes-result1'),
                                        html.H2(
                                            "上传文档",
                                            style={
                                                'font-weight': 'bolder'
                                                , 'color': 'rgb(64 126 255)'
                                                , 'textAlign': 'center'
                                            }
                                        ),

                                        fac.AntdDraggerUpload(
                                            id='upload',
                                            apiUrl='/upload/',
                                            uploadId='my-files',
                                            fileTypes=['pdf', 'txt'],
                                            multiple=True,
                                            # fileMaxSize=1,
                                            failedTooltipInfo='啊哦，上传过程出了问题...',
                                            showUploadList=False,
                                            text='上传pdf,txt文件',
                                            hint='点击或拖拽文件至此处进行上传',
                                            style={
                                                'maxHeight': '500px'
                                            }
                                        ),
                                        # fac.AntdCenter(
                                        #     fac.AntdButton(
                                        #         [
                                        #             # fac.AntdIcon(
                                        #             #     icon='md-fingerprint'
                                        #             # ),
                                        #             '解析文档'
                                        #         ],
                                        #         id="start-parse-button",
                                        #         type='primary',
                                        #         loadingChildren='解析中',
                                        #         autoSpin=True                                                
                                        #     ),
                                        #     style={
                                        #         'padding': '10px',
                                        #     }
                                        # ),                                        
                                        # fac.AntdCenter(
                                        #     fac.AntdButton(
                                        #         [
                                        #             # fac.AntdIcon(
                                        #             #     icon='md-fingerprint'
                                        #             # ),
                                        #             '生成地图'
                                        #         ],
                                        #         id="start-map-button",
                                        #         type='primary',
                                        #         loadingChildren='生成中',
                                        #         autoSpin=True                                                
                                        #     ),
                                        #     style={
                                        #         'padding': '10px',
                                        #     }
                                        # ),                                        

                                    ],
                                    style={
                                        # 'minHeight': '300px',
                                        # 'width': '1000px',
                                        # 'boxShadow': 'rgb(79 89 108 / 51%) 1px 4px 15px',
                                        # 'borderRadius': '2px',
                                        # 'padding': '25px'

                                    }
                                ),
                                shadow='always-shadow',
                                # className='chat-wrapper1'
                            ),
                            className='root-wrapper1'
                            # style={
                            #     'backgroundColor': 'rgba(64, 173, 255, 1)',
                            #     'color': 'white',
                            #     'height': '100px',
                            #     'display': 'flex',
                            #     'justifyContent': 'center',
                            #     'alignItems': 'center'
                            # }
                        ),

                    

                        # 受左侧面板折叠影响位置的悬浮工具条，利用绝对定位与左侧面板绑定
                        fac.AntdSpace(
                            [
                                fac.AntdButton(
                                    [
                                        # fac.AntdIcon(
                                        #     icon='md-fingerprint'
                                        # ),
                                        '解析文档'
                                    ],
                                    id="start-parse-button",
                                    type='primary',
                                    loadingChildren='解析中',
                                    autoSpin=True                                                
                                ),
                                fac.AntdButton(
                                    [
                                        # fac.AntdIcon(
                                        #     icon='md-fingerprint'
                                        # ),
                                        '生成地图'
                                    ],
                                    id="start-map-button",
                                    type='primary',
                                    loadingChildren='生成中',
                                    autoSpin=True                                                
                                ),                                            
                            ],
                            size=10,
                            style={
                                'position': 'absolute',
                                'top': 0,
                                'left': 'calc(100% + 60px)'
                            }
                        )
                    ],
                    id='left-panel',
                    style={
                        'position': 'absolute',
                        'left': 0,
                        'top': 10,
                        'bottom': 10,
                        'width': 400,
                        'background': 'rgba(255, 255, 255, 0.8)',
                        'boxShadow': '0 2px 2px rgb(0 0 0 / 15%)',
                        'zIndex': 999,
                        'borderBottomRightRadius': '6px',
                        'borderTopRightRadius': '6px',
                        'transition': 'left 0.3s ease'
                    }
                ),

                # 右侧悬浮面板，绝对定位，拉高zIndex
                html.Div(
                    html.Div(
                        [
                            # 风格二折叠按钮，对应右侧面板
                            html.Span(
                                fac.AntdIcon(
                                    id='right-panel-fold-icon',
                                    icon='antd-menu-unfold'
                                ),
                                id='right-panel-fold',
                                style={
                                    'cursor': 'pointer',
                                    'fontSize': 18,
                                    'position': 'absolute',
                                    'top': 8,
                                    'left': 8
                                }
                            ),
                            
                            html.Div(id='right-content'),

                            html.Div(
                                fuc.FefferyJsonViewer(
                                    id='json-geoinfo-viewer',
                                    data={
                                        'int示例': 999,
                                        'float示例': 0.999,
                                        'string示例': '我爱dash',
                                        '数组示例': [0, 1, 2, 3],
                                        '字典示例': {
                                            'a': 1,
                                            'b': 2,
                                            'c': 3
                                        }
                                    },
                                    editable=True,
                                    addible=True,
                                    deletable=True,
                                    style={
                                        'padding': '10px',
                                        'maxHeight': '600px',
                                        'overflow': 'auto',
                                        'background': 'rgba(255, 255, 255, 0.8)',
                                    }                                  
                                ),
                                style={
                                    'padding': '30px 20px',
                                    'background': 'rgba(255, 255, 255, 0.8)',
                                    # 'maxHeight': '600px',
                                }                            
                            ),                            


                            # fac.AntdResult(
                            #     status='info',
                            #     subTitle='右侧面板内容示例'
                            # ),

                            # # 受右侧面板折叠影响位置的悬浮工具条，利用绝对定位与右侧面板绑定
                            # fac.AntdSpace(
                            #     [
                            #         fac.AntdButton(
                            #             [
                            #                 fac.AntdIcon(
                            #                     icon='antd-zoom-in',
                            #                     style={
                            #                         'paddingRight': '5px'
                            #                     }
                            #                 ),
                            #                 '操作XX'
                            #             ],
                            #             style={
                            #                 'display': 'flex',
                            #                 'flexDirection': 'column',
                            #                 'height': 'auto',
                            #                 'alignItems': 'center',
                            #                 'padding': '3px 5px'
                            #             }
                            #         )
                            #     ] * 10,
                            #     size=0,
                            #     direction='vertical',
                            #     style={
                            #         'position': 'absolute',
                            #         'top': 25,
                            #         'right': 'calc(100% + 10px)'
                            #     }
                            # )
                        ],
                        style={
                            'position': 'relative',
                            'width': '100%',
                            'height': '100%'
                        }
                    ),
                    id='right-panel',
                    style={
                        'position': 'absolute',
                        'right': 0,
                        'top': 10,
                        'bottom': 10,
                        'width': 400,
                        'background': 'rgba(255, 255, 255, 0.8)',
                        'boxShadow': '0 2px 2px rgb(0 0 0 / 15%)',
                        'zIndex': 999,
                        'borderBottomLeftRadius': '6px',
                        'borderTopLeftRadius': '6px',
                        'transition': 'right 0.3s ease'
                    }
                )
            ],
            style={
                'height': 'calc(100vh - 64px)',
                'position': 'relative'
            }
        )
    ],
    style={
        'overflowX': 'hidden'
    }
)


@app.callback(
    [Output('start-parse-button', 'loading'), 
     Output('succes-result1', 'children'),
     Output('json-geoinfo-viewer', 'data')
     ], 
    Input('start-parse-button', 'nClicks'),
    State('upload', 'lastUploadTaskRecord'),
    prevent_initial_call=True
)
def parse_button(nClicks, lastUploadTaskRecord):
    print(lastUploadTaskRecord)
    if nClicks: 
        if lastUploadTaskRecord:
            try:
                file_path = os.path.join('dash', 'caches', lastUploadTaskRecord[0]['taskId'], lastUploadTaskRecord[0]['fileName'])
                with open(file_path, 'rb') as file:  # 使用 'rb' 模式读取二进制数据
                    file_content = file.read()
                file_stream = BytesIO(file_content)                
                file_type = file_path.split('.')[-1]
                if file_type == 'pdf':
                    text = file_processor.extract_text_from_pdf(file_stream)
                    print(text)
                elif file_type == 'txt':
                    text = file_processor.extract_text_from_txt(file_stream)                
                    print(text)
                geo_info_list = file_processor.process_text(text)
                print(geo_info_list)
                new_data_list = [{item['event_title']: {key: value for key, value in item.items() if key != 'event_title'}} for item in geo_info_list]
                print(new_data_list)
                print(type(new_data_list))
                json_geoinfo_data = {
                    '事件列表': {list(item.keys())[0]: list(item.values())[0] for item in new_data_list}
                }
                print(json_geoinfo_data)
            except Exception as e:
                print(e)
                return [
                    False, 
                    fac.AntdMessage(
                    content=f'解析失败！{e}',
                    duration=2,
                    type='warning'),
                    dash.no_update
                ]
            return [
                False, 
                fac.AntdMessage(
                content='解析成功！',
                duration=2,
                type='success'),
                json_geoinfo_data
            ]
    return dash.no_update

@app.callback(
    Output('mapinfo-store', 'data'),
    Input('json-geoinfo-viewer', 'data')
)
def updata_map_info(geoinfo):

    return geoinfo

@app.callback(
    [Output('geojson-store', 'data'),
     Output('start-map-button', 'loading'), 
     Output('map-container', 'children'), 
     ],
    Input('start-map-button', 'nClicks'),
    State('mapinfo-store', 'data'),
    prevent_initial_call=True
)
def updata_map(nClicks, mapinfo):
    if nClicks: 
        features = []
        for key, info in mapinfo['事件列表'].items():
            time.sleep(3)
            print(info)
            print(type(info))
            geocode_result = geocode_utils.geocode(info["address"])
            print('坐标为:', info["address"], geocode_result)
            if 'error' not in geocode_result:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "description": {
                            "title": key,
                            "type": info["event_type"],
                            "content": info["event_content"],
                            "keys": info["keys"],
                        }
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [geocode_result["longitude"], geocode_result["latitude"]]
                    }
                }
                print(feature, "点位数据")
                features.append(feature)
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        locations = []
        marklist = []
        for feature in geojson["features"]:
            coords = feature["geometry"]["coordinates"]
            locations.append([coords[1], coords[0]])         
            mark = flc.LeafletMarker(
                flc.LeafletPopup(
                    fac.AntdSpace(
                        [
                            fac.AntdText(
                                feature["properties"]["description"]["title"],
                                italic=True
                            ),
                            fac.AntdText(
                                feature["properties"]["description"]["type"],
                                italic=True
                            ),
                            fac.AntdText(
                                feature["properties"]["description"]["content"],
                                italic=True
                            ),
                            fac.AntdText(
                                feature["properties"]["description"]["keys"],
                                italic=True
                            ),
                        ],
                        direction='vertical'
                    ),
                    closeButton=True
                ),
                position={
                    'lng': coords[0],
                    'lat': coords[1]
                },
                editable=True
            )
            marklist.append(mark)
        chidren = [
            # 添加瓦片底图
            flc.LeafletTileLayer(
                id='tile-layer',
                url='https://tiles1.geovisearth.com/base/v1/vec/{z}/{x}/{y}?format=png&tmsIds=w&token=4524e0daf0879dc44f91fed17fd225466c3809fa3961deba2057ac5e5a710be3'
            ),
            flc.LeafletFullscreenControl(
            ),            
            # flc.LeafletGeoJSON(
            #     data=geojson
            # ),
            flc.LeafletFeatureGroup(marklist),
            flc.LeafletPolyline(
                positions=locations,
                editable=True
                # arrowheads=True
            ),                                    
        ]
        return [
            geojson,
            False, 
            chidren
        ]


@app.callback(
    Output('tile-layer', 'url'),
    Input('tile-select', 'selectedUrl')
)
def change_tile_layer(selectedUrl):

    return selectedUrl

# @app.callback(
#     [Output('tile-layer', 'url'),
#      Output('tile-layer', 'key')],
#     Input('tile-select', 'selectedUrl')
# )
# def change_tile_layer(selectedUrl):

#     return [selectedUrl, str(uuid.uuid4())]


# 左侧面板折叠回调，使用浏览器端回调提升交互顺畅性
app.clientside_callback(
    '''
    (n_clicks, oldStyle) => {
        if (n_clicks) {
            if (oldStyle?.left === 0) {
                return [
                    {
                        ...oldStyle,
                        left: -364
                    },
                    'antd-menu-unfold'
                ]
            }
            return [
                {
                    ...oldStyle,
                    left: 0
                },
                'antd-menu-fold'
            ]
        }
        return window.dash_clientside.no_update;
    }
    ''',
    [Output('left-panel', 'style'),
     Output('left-panel-fold-icon', 'icon')],
    Input('left-panel-fold', 'n_clicks'),
    State('left-panel', 'style')
)

# 右侧面板折叠回调，使用浏览器端回调提升交互顺畅性
app.clientside_callback(
    '''
    (n_clicks, oldStyle) => {
        if (n_clicks) {
            if (oldStyle?.right === 0) {
                return [
                    {
                        ...oldStyle,
                        right: -364
                    },
                    'antd-menu-fold'
                ]
            }
            return [
                {
                    ...oldStyle,
                    right: 0
                },
                'antd-menu-unfold'
            ]
        }
        return window.dash_clientside.no_update;
    }
    ''',
    [Output('right-panel', 'style'),
     Output('right-panel-fold-icon', 'icon')],
    Input('right-panel-fold', 'n_clicks'),
    State('right-panel', 'style')
)


if __name__ == '__main__':
    app.run(debug=True, host='localhost', port=8055)
